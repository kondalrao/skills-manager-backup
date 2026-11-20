---
name: lcnd-debug-driver
description: >-
  Build the lcnd-debug standalone Linux kernel networking driver. Creates a
  virtual lcnd-debug network interface that redirects packets to a configurable
  target interface (ingress/egress) or drops them for tcpdump debugging. Use
  when asked to build, modify, or extend the lcnd-debug kernel module, or when
  referencing its design decisions. Triggers on "lcnd-debug", "debug driver",
  "debug interface", "lcnd_debug_dev".
---

# lcnd-debug Kernel Networking Driver

Standalone kernel module (`lcnd_debug_dev.ko`) that creates a `lcnd-debug` virtual network interface. Packets transmitted through it are redirected to a configured target interface (ingress or egress) or silently dropped. Always tcpdump-capable.

## Architecture

```
User Space (packet generator / tcpdump)
        |
        v  send packet
   lcnd-debug netdev  <-- tcpdump captures here
        |
   ndo_start_xmit
        |
   rcu_read_lock + rcu_dereference(cfg)
        |
   cfg->direction?
   /       |        \
INGRESS  EGRESS    NONE
  |        |         |
eth_type  skb->dev  dev_kfree_skb
_trans    =target     (drop)
  |        |
netif_   dev_queue
receive  _xmit
_skb       |
  |        v
  v    Target interface
Target interface
```

## Design Decisions (Resolved)

All decisions below were made through structured review and must be preserved.

### 1. Standalone module
Independent `.ko` (`klm_lcnd_debug.klm`), not part of `klm_lcnd`. Built via its own `nx_klm` Bazel target in the same BUILD file.

### 2. RCU-protected config struct
Solves three problems at once: use-after-free on param writes, TOCTOU between direction+ifname changes, and per-packet `dev_get_by_name` cost.

```c
enum lcnd_debug_dir {
    LCND_DEBUG_DIR_NONE,
    LCND_DEBUG_DIR_INGRESS,
    LCND_DEBUG_DIR_EGRESS,
};

struct lcnd_debug_cfg {
    enum lcnd_debug_dir  direction;
    char                 ifname[IFNAMSIZ];
    int                  nsid;         /* -1 = same ns as lcnd-debug */
    struct net_device   *target_dev;   /* cached, holds dev_hold() ref */
    struct net           *target_net;   /* cached ns ref, holds get_net() */
    struct rcu_head      rcu;
};

static struct lcnd_debug_cfg __rcu *lcnd_debug_active_cfg;
```

- **Writer** (sysfs `.set`): alloc new cfg, resolve ns + target dev, `rcu_assign_pointer`, `kfree_rcu` old after `dev_put`/`put_net`.
- **Reader** (`ndo_start_xmit`): `rcu_read_lock`, `rcu_dereference`, use `cfg->target_dev` directly, `rcu_read_unlock`. Zero contention.

### 3. Module parameters
Three params, all mode `0644`, custom `param_ops`:

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `debug_direction` | string | `"none"` | `"ingress"`, `"egress"`, or `"none"` |
| `debug_ifname` | string | `""` | Target interface name (e.g. `"Eth1-1"`) |
| `debug_nsid` | int | `-1` | Target namespace ID. `-1` = same as lcnd-debug |

Each `.set` callback triggers a full config recompute + atomic RCU swap.

### 4. Netdevice notifier
Handles target interface disappearing at runtime:
- Register `register_netdevice_notifier()` in module init.
- On `NETDEV_UNREGISTER`: if event device matches `cfg->target_dev`, swap to drop config (`direction=NONE, target_dev=NULL`), `dev_put` old target after grace period.

### 5. Self-targeting guard
- **Setter**: reject `-EINVAL` if `direction == EGRESS` and target == lcnd-debug (infinite recursion). Ingress-to-self is allowed (RX path, no loop).
- **Xmit**: defense-in-depth -- drop if `EGRESS && target_dev == self`.

### 6. Ingress path
Must call `eth_type_trans(skb, target_dev)` before `netif_receive_skb(skb)`. This sets `skb->dev`, `skb->protocol`, `skb->pkt_type` correctly for RX processing.

### 7. Egress path
Direct `dev_queue_xmit(skb)` from `ndo_start_xmit` on a different device. Same pattern as bridge/veth in the kernel. Safe when target != self.

### 8. Namespace resolution
- `debug_nsid == -1`: use `dev_net(lcnd_debug_ndev)` (same namespace).
- `debug_nsid >= 0`: use `get_net_ns_by_id(&init_net, nsid)`. Cached in config struct.

### 9. Stats
Full accounting: `tx_packets`, `tx_bytes`, `tx_dropped` in xmit. `rx_packets`, `rx_bytes` on successful ingress injection.

### 10. MAC address
`eth_hw_addr_random(dev)` after `alloc_netdev()`.

### 11. Safe C functions
All string ops use `strncmp`/`strncpy` with explicit bounds. No `strcpy`, `sprintf`, `strlen`.

## Files

| File | Purpose |
|------|---------|
| `standalone/infra/kstack/kspace/lcnd/lcnd_debug_dev.c` | Single-file kernel module (~250-300 lines) |
| `standalone/infra/kstack/kspace/lcnd/BUILD` | Add `nx_klm` target `klm_lcnd_debug.klm` |

## Key Code Patterns

### Config setter (writer path)

```c
static DEFINE_MUTEX(lcnd_debug_cfg_mutex);

static int lcnd_debug_set_config(const char *new_dir, const char *new_ifname, int nsid)
{
    struct lcnd_debug_cfg *old_cfg, *new_cfg;
    struct net_device *target = NULL;
    struct net *target_net = NULL;
    enum lcnd_debug_dir dir;

    if (strncmp(new_dir, "ingress", 7) == 0)
        dir = LCND_DEBUG_DIR_INGRESS;
    else if (strncmp(new_dir, "egress", 6) == 0)
        dir = LCND_DEBUG_DIR_EGRESS;
    else
        dir = LCND_DEBUG_DIR_NONE;

    if (dir != LCND_DEBUG_DIR_NONE && new_ifname[0] != '\0') {
        if (nsid >= 0) {
            target_net = get_net_ns_by_id(&init_net, nsid);
            if (!target_net)
                return -EINVAL;
        } else {
            target_net = get_net(dev_net(lcnd_debug_ndev));
        }
        target = dev_get_by_name(target_net, new_ifname);
        if (!target) {
            put_net(target_net);
            return -ENODEV;
        }
        if (dir == LCND_DEBUG_DIR_EGRESS && target == lcnd_debug_ndev) {
            dev_put(target);
            put_net(target_net);
            return -EINVAL;
        }
    }

    new_cfg = kzalloc(sizeof(*new_cfg), GFP_KERNEL);
    if (!new_cfg) {
        if (target) dev_put(target);
        if (target_net) put_net(target_net);
        return -ENOMEM;
    }

    new_cfg->direction = dir;
    strncpy(new_cfg->ifname, new_ifname, IFNAMSIZ - 1);
    new_cfg->nsid = nsid;
    new_cfg->target_dev = target;
    new_cfg->target_net = target_net;

    mutex_lock(&lcnd_debug_cfg_mutex);
    old_cfg = rcu_dereference_protected(lcnd_debug_active_cfg,
                lockdep_is_held(&lcnd_debug_cfg_mutex));
    rcu_assign_pointer(lcnd_debug_active_cfg, new_cfg);
    mutex_unlock(&lcnd_debug_cfg_mutex);

    if (old_cfg) {
        if (old_cfg->target_dev)
            dev_put(old_cfg->target_dev);
        if (old_cfg->target_net)
            put_net(old_cfg->target_net);
        kfree_rcu(old_cfg, rcu);
    }
    return 0;
}
```

### Xmit handler (reader path)

```c
static netdev_tx_t lcnd_debug_xmit(struct sk_buff *skb, struct net_device *dev)
{
    struct lcnd_debug_cfg *cfg;

    rcu_read_lock();
    cfg = rcu_dereference(lcnd_debug_active_cfg);

    if (!cfg || cfg->direction == LCND_DEBUG_DIR_NONE || !cfg->target_dev) {
        dev->stats.tx_dropped++;
        dev_kfree_skb(skb);
        goto out;
    }

    dev->stats.tx_packets++;
    dev->stats.tx_bytes += skb->len;

    if (cfg->direction == LCND_DEBUG_DIR_INGRESS) {
        skb->protocol = eth_type_trans(skb, cfg->target_dev);
        netif_receive_skb(skb);
    } else {
        if (unlikely(cfg->target_dev == dev)) {
            dev->stats.tx_dropped++;
            dev_kfree_skb(skb);
            goto out;
        }
        skb->dev = cfg->target_dev;
        dev_queue_xmit(skb);
    }

out:
    rcu_read_unlock();
    return NETDEV_TX_OK;
}
```

### Notifier (target removal)

```c
static int lcnd_debug_netdev_event(struct notifier_block *nb,
                                   unsigned long event, void *ptr)
{
    struct net_device *event_dev = netdev_notifier_info_to_dev(ptr);
    struct lcnd_debug_cfg *cfg;

    if (event != NETDEV_UNREGISTER)
        return NOTIFY_DONE;

    rcu_read_lock();
    cfg = rcu_dereference(lcnd_debug_active_cfg);
    if (cfg && cfg->target_dev == event_dev) {
        rcu_read_unlock();
        lcnd_debug_set_config("none", "", -1);
        return NOTIFY_DONE;
    }
    rcu_read_unlock();
    return NOTIFY_DONE;
}
```

## Module lifecycle

**init**: `alloc_netdev` -> `eth_hw_addr_random` -> `register_netdev` -> `register_netdevice_notifier` -> alloc initial cfg (NONE).

**exit**: `unregister_netdevice_notifier` -> swap NULL cfg (release refs) -> `unregister_netdev` -> `free_netdev`.

## Usage

```bash
# Load (drop mode, tcpdump-only)
insmod lcnd_debug_dev.ko

# tcpdump on debug interface
tcpdump -i lcnd-debug -nn

# Ingress redirect (same namespace)
echo "Eth1-1" > /sys/module/lcnd_debug_dev/parameters/debug_ifname
echo "ingress" > /sys/module/lcnd_debug_dev/parameters/debug_direction

# Cross-namespace target (nsid 3)
echo 3 > /sys/module/lcnd_debug_dev/parameters/debug_nsid
echo "Eth1-1" > /sys/module/lcnd_debug_dev/parameters/debug_ifname
echo "ingress" > /sys/module/lcnd_debug_dev/parameters/debug_direction

# Switch to egress
echo "egress" > /sys/module/lcnd_debug_dev/parameters/debug_direction

# Back to drop mode
echo "none" > /sys/module/lcnd_debug_dev/parameters/debug_direction

# Check stats
ip -s link show lcnd-debug
```

## Build

From the `standalone/` directory:

```bash
bazel --output_user_root=../bazel_cache build \
    --disk_cache=/nobackup/$USER/bzl_disk_cache \
    -s --verbose_failures \
    //infra/kstack/kspace/lcnd:klm_lcnd_debug.klm_all
```

The `_all` suffix builds for all configured `bzl_platforms` (both `ins_x86_64_supe` and `ins_x86e_supe`). Individual platforms can be targeted via `_ins_x86e_supe` or `_ins_x86_64_supe` suffixes.

### BUILD target

Add to `standalone/infra/kstack/kspace/lcnd/BUILD`:

```python
nx_klm(
    name = "klm_lcnd_debug.klm",
    srcs = [
        "lcnd_debug_dev.c",
        "//third-party/bin/linux/final.x86e-6.6/include.klm:x86_6_6_include_klm_hdrs",
        "//third-party/bin/linux/final.x86e-6.6/include.klm/generated/uapi:x86_6_6_include_klm_gen_uapi_hdrs",
        "//third-party/bin/linux/final.x86e-6.6/include.klm/linux:x86_6_6_include_klm_linux_hdrs",
        "//third-party/bin/linux/final.x86e-6.6/include.klm/uapi:x86_6_6_include_klm_uapi_hdrs",
    ],
    bzl_platforms = [
        "//config/bzl/platforms:ins_x86_64_supe",
        "//config/bzl/platforms:ins_x86e_supe",
    ],
    visibility = ["//visibility:public"],
    deps = [
        "//link/third-party:module.lds.so",
    ],
)
```

The module requires the kernel header filegroups in `srcs` for Bazel sandbox visibility:
- `x86_6_6_include_klm_hdrs`
- `x86_6_6_include_klm_gen_uapi_hdrs`
- `x86_6_6_include_klm_linux_hdrs`
- `x86_6_6_include_klm_uapi_hdrs`

No explicit `copts` for kernel includes -- the `nx_klm` macro injects them via `_ARCH_KERNEL_INCLUDES`.

## On-Device Test Procedure

### Prerequisites

- Build the module: `bazel build //infra/kstack/kspace/lcnd:klm_lcnd_debug.klm_all`
- Copy the `.klm` to the target device (e.g. via SCP to `/bootflash/`)
- Have at least two interfaces available (e.g. `Eth1-1`, `Eth1-2`)

### Test 1: Module load / drop mode

```bash
insmod /bootflash/klm_lcnd_debug.klm
# Verify: dmesg should show "lcnd_debug_dev: loaded (drop mode)"
ip link show lcnd-debug
# Verify: interface exists, MAC is non-zero, state DOWN

ip link set lcnd-debug up
# Verify: dmesg shows "lcnd_debug_dev: interface up"

cat /sys/kernel/debug/lcnd_debug/config
# Verify: direction=none, ifname=(none), nsid=-1, target_dev=(none)
```

### Test 2: Drop path + tcpdump visibility

```bash
# Terminal 1: capture on lcnd-debug
tcpdump -i lcnd-debug -nn -c 5 &

# Terminal 2: send a packet to lcnd-debug
ping -I lcnd-debug -c 1 192.0.2.1

# Verify: tcpdump sees the packet
# Verify: ip -s link show lcnd-debug shows tx_dropped incremented
```

### Test 3: Ingress redirect (same namespace)

```bash
echo "Eth1-1" > /sys/module/lcnd_debug_dev/parameters/debug_ifname
echo "ingress" > /sys/module/lcnd_debug_dev/parameters/debug_direction
# Verify: dmesg shows config change log

cat /sys/kernel/debug/lcnd_debug/config
# Verify: direction=ingress, target_dev=Eth1-1

# Terminal 1: capture on target interface
tcpdump -i Eth1-1 -nn -c 5 &

# Terminal 2: send a packet to lcnd-debug
# The packet should appear on Eth1-1 as received (ingress)

# Verify: ip -s link show lcnd-debug shows tx_packets, tx_bytes, rx_packets, rx_bytes
```

### Test 4: Egress redirect

```bash
echo "egress" > /sys/module/lcnd_debug_dev/parameters/debug_direction
# Verify: config shows direction=egress

# Terminal 1: capture on target interface
tcpdump -i Eth1-1 -nn -c 5 &

# Terminal 2: send a packet to lcnd-debug
# The packet should go out through Eth1-1 (egress)

# Verify: ip -s link show lcnd-debug shows tx_packets, tx_bytes
```

### Test 5: Egress-to-self rejection

```bash
echo "lcnd-debug" > /sys/module/lcnd_debug_dev/parameters/debug_ifname
echo "egress" > /sys/module/lcnd_debug_dev/parameters/debug_direction
# Verify: dmesg shows "egress to self rejected"
# Verify: echo returns non-zero exit code
```

### Test 6: Cross-namespace target

```bash
# Determine the nsid of a target namespace
# (e.g. ip netns list-id, or check /var/run/netns/)
echo 3 > /sys/module/lcnd_debug_dev/parameters/debug_nsid
echo "Eth1-1" > /sys/module/lcnd_debug_dev/parameters/debug_ifname
echo "ingress" > /sys/module/lcnd_debug_dev/parameters/debug_direction

cat /sys/kernel/debug/lcnd_debug/config
# Verify: nsid=3, target_dev shows the interface name
```

### Test 7: Target interface removal

```bash
# Configure lcnd-debug to target an interface, then remove that interface
echo "Eth1-2" > /sys/module/lcnd_debug_dev/parameters/debug_ifname
echo "ingress" > /sys/module/lcnd_debug_dev/parameters/debug_direction
# Now remove or admin-down Eth1-2

# Verify: dmesg shows "target 'Eth1-2' unregistered, reverting to drop mode"
cat /sys/kernel/debug/lcnd_debug/config
# Verify: direction=none, target_dev=(none)
```

### Test 8: Module unload

```bash
echo "none" > /sys/module/lcnd_debug_dev/parameters/debug_direction
ip link set lcnd-debug down
rmmod lcnd_debug_dev
# Verify: dmesg shows "lcnd_debug_dev: unloaded"
# Verify: ip link show lcnd-debug fails (interface gone)
# Verify: /sys/kernel/debug/lcnd_debug/ is removed
```
