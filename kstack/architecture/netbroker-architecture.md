# Netbroker Architecture

Kernel **administration gate** plus userspace **broker agent** that keeps third-party
Linux tools from programming network state directly. NX-OS control-plane daemons
remain the source of truth; shell `ip` / legacy `ifconfig` / socket admin is
**trapped**, forwarded to **nbproxy**, and applied through NX-OS APIs (URIB,
netstack, static-route PIB, neighbor mgr, …) before the kernel is updated.

> **Scope & boundary.** Everything under `standalone/infra/kstack/netbroker/` is
> **in scope** (`kspace/` KLM, `lib/` libnetbroker, `nbproxy/` sysmgr daemon).
> The generic kernel **netbroker framework** lives in
> `standalone/third-party/src/kernel/nx-linux/patches.x86e-6.6/netbroker-*.patch`
> applied to `linux-6.6` (`net/netbroker.c`, RTNL/ioctl/socket hook sites).
> **Out of scope:** URIB, ipfib, KIM, netstack, ifmgr implementations — they are
> **consumers or whitelist bypass writers** (§9). **KFIB** (FLOW-012) observes
> kernel routes **after** they exist; netbroker **reduces** how often unapproved
> processes put them there (KSTACK-054).
>
> **Volatile vs stable.** Whitelist comm names, genl family ids, `/proc/net/cisco_nb_*`
> layout, and line numbers drift across releases/containers. Anchor on **function
> names**, **`NB_GRP_*` / `LIBNB_CFG_*` symbols**, tracepoint names
> (`trace_nb_rtnl_doit`, …), and MTS/API names in nbproxy handlers. Runtime E2E
> verified 2026-07-26 on `172.20.175.107` (`10.7(0)IMG9(0.166)`); source read
> against workspace `space_kkomarag_COV_10_7_0_IMG9_0_231`.

---

## 1. Purpose

Netbroker answers one question at the Linux boundary: **"Should this admin
request from a non-NXOS process change kernel network state directly, or must
NX-OS approve and program it?"**

- **Trap path:** RTNL / legacy ioctl / selected socket ops from non-whitelisted
  senders are cloned and forwarded over **genl** to a registered broker
  (`nbproxy`). The original kernel handler is aborted (`NETBROKER_HANDLED`,
  `-EINTR`); completion is an explicit netlink ACK after nbproxy finishes.
- **Bypass path:** NX-OS daemons on the **whitelist** (`ipfib`, `kim`,
  `netstack:`, `urib`, …) and broker **replay** traffic (`rtnl_pid` match) pass
  through unchanged.
- **Completion:** nbproxy returns `LIBNB_CFG_OK` (may **replay** RTNL on the
  broker's registered `rtnl_sk` via `libnb_update_kernel`) or
  `LIBNB_CFG_OK_PROCESSED` (NX-OS owns kernel programming via whitelist writers).

So netbroker is the **admin-path enforcement layer**: third-party Linux admin in,
NX-OS control plane + controlled kernel programming out.

---

## 2. Module identity & build

| Item | Value |
|------|-------|
| Kernel module | `klm_cisco_nb` (`netbroker/kspace/`) |
| Userspace daemon | `nbproxy.bin` → `/isan/bin/nbproxy` (sysmgr) |
| Shared library | `libnetbroker.so` (`netbroker/lib/`) |
| sysmgr config | `nbproxy/nbproxy.conf` (`SRVNAME_NBPROXY`, `run = conditional`) |
| Show/CLI | `libcli/nbproxy_show.c`, `nbproxy.cmd` |
| Test harness | `netbroker.c` + `test/` (unit tests; **not** production agent) |
| Scope | **infra** (`standalone/infra/kstack/netbroker/`) |

**Object inventory** (translation unit → responsibility):

| Object | Responsibility |
|--------|----------------|
| `cisco_netbroker.c` | KLM init, `register_netbroker(&cisco_nb_ops)`, proc (`/proc/net/cisco_nb_*`), module params (`block_*`, `disable_*_hook`), whitelist `cisco_nb_allow_by_current` |
| `cisco_nb_rtnl.c` | RTNL trap: `cisco_nb_rtnl_doit`, `get_grp_map`, `nb_send_request`, `nb_rtnl_resp_cb` |
| `cisco_nb_ioctl.c` | Legacy `dev_ioctl` trap (`ifconfig`-style) |
| `cisco_nb_sock.c` | Socket bind/connect/release hooks → `NB_GRP_SOCKET` |
| `cisco_nb_genl.c` | genl family, request/response to userspace brokers |
| `cisco_nb_trace.h` | ftrace/perf tracepoints (`cisco_nb_traces:*`) — hot path observability |
| `libnb-msgs.c` | genl RX: parse `NB_A_ORIG_MSG`, encode `libnb_cfg_data`, invoke `cfg_cb`, `libnb_ack`, optional `libnb_update_kernel` |
| `libnb-register.c` | `libnb_open_*` per group, broker registration handshake with KLM |
| `libnb-rib.c`, `libnb-interface.c`, `libnb-neighbor.c`, `libnb-socket.c` | Group-specific encode/decode helpers |
| `nbproxy.c` | sysmgr main, `nb_libnb_init_brokers`, epoll loop, broker lifecycle |
| `nbproxy_ip.c` | `NB_GRP_STATIC_ROUTE` → static-route PIB (`ip_cfg_req`) |
| `nbproxy_dynamic_rt.c` / `nbproxy_dynamic_rt6.c` | `NB_GRP_RIB` / `NB_GRP_RIB6` → URIB / U6RIB |
| `nbproxy_am.c` | `NB_GRP_NEIGHBOR` → neighbor mgr |
| `nbproxy.c` (`int_cfg_req`) | `NB_GRP_INTERFACE` → vsh / netstack interface ops |
| `nbproxy_socket.c` | Socket policy handler |
| `nbproxy_uxrib.c` | HA replay helpers (`nb_uxrib_kernel_save` / replay — switchover path) |

Startup: `kspace/S00nxos-nb.sh` loads KLM; checks `register_netbroker` in kallsyms.

---

## 3. Layer map

```text
  [Third-party: ip, ifconfig, scripts]
           |
           v
  linux-6.6 + netbroker patches
    rtnetlink_rcv_msg -> netbroker_rtnl_doit
    dev_ioctl         -> netbroker_dev_ioctl
    sock hooks        -> netbroker_sock_*
           |
           v
  klm_cisco_nb (cisco_nb_rtnl_doit / ioctl / sock)
    whitelist? -> NETBROKER_CONTINUE (pass-through)
    trapped?   -> nb_send_request (genl) -> NETBROKER_HANDLED
           |
           v
  nbproxy (libnetbroker cfg_cb per NB_GRP_*)
    urib / u6rib / static-route PIB / AM / netstack / vsh
           |
           +-- LIBNB_CFG_OK_PROCESSED -> libnb_ack only (ipfib/kim/netstack program kernel)
           +-- LIBNB_CFG_OK           -> libnb_update_kernel (replay RTNL on rtnl_sk)
           |
           v
  Kernel FIB / netdev / neighbor state (possibly observed later by KFIB -> URIB)
```

---

## 4. Broker groups (`NB_GRP_*`)

One broker registration per group (`grp_tbl[]` in `cisco_netbroker.c`). nbproxy
registers all production groups in `nb_libnb_init_brokers()` (`nbproxy.c`).

| Group | ID | RTNL / API | nbproxy `cfg_cb` | NX-OS backend |
|-------|-----|------------|------------------|---------------|
| `NB_GRP_INTERFACE` | 1 | NEWLINK/DELLINK/SETLINK, NEWADDR/DELADDR | `int_cfg_req` | vsh / netstack IP |
| `NB_GRP_RIB` | 2 | IPv4 NEWROUTE/DELROUTE (dynamic) | `urib_cfg_req` | URIB |
| `NB_GRP_RIB6` | 3 | IPv6 NEWROUTE/DELROUTE | `u6rib_cfg_req` | U6RIB |
| `NB_GRP_STATIC_ROUTE` | 4 | Static routes (`RTPROT_STATIC` / BOOT) | `ip_cfg_req` | static-route PIB |
| `NB_GRP_NEIGHBOR` | 5 | NEWNEIGH/DELNEIGH | `am_cfg_req` | neighbor mgr |
| `NB_GRP_MCAST_GRP` | 6 | Multicast membership | (broker optional) | — |
| `NB_GRP_SOCKET` | 7 | bind/connect/release | `socket_cfg_req` | socket policy |
| `NB_GRP_ETHTOOL` | 8 | ethtool ioctls | ethtool handler | controlled ops |

Registration visibility: **`/proc/net/cisco_nb_0`** (container 0) or
**`cisco_nb_1`** (ToR container 1) — group name, broker genl `pid`, `rtnl_pid`.

---

## 5. RTNL trap decision tree (live path)

1. User sends RTNL (e.g. `RTM_NEWROUTE`) on `NETLINK_ROUTE`.
2. `netbroker_rtnl_doit` → `cisco_nb_rtnl_doit`.
3. **Continue (no trap)** if any:
   - `disable_rtnl_hook` module param set
   - `cisco_nb_allow_by_current()` whitelist match (comm, Smack `vmo`, LC LXC cgroup, …)
   - `get_grp_map` → `NB_GRP_NONE`
   - No broker registered for mapped group
   - Sender `portid == ne->rtnl_pid` (broker replay from `libnb_update_kernel`)
   - `check_interface_change` returns continue-only (e.g. NEWLINK size probe)
4. **Trap:** `nb_send_request` with cloned skb → genl to nbproxy; return
   `NETBROKER_HANDLED`, `*rc = -EINTR` (kernel RTNL handler does not apply change).
5. **nbproxy:** `request_msg_handler` → encode → `cfg_cb` → `libnb_ack` →
   `nb_rtnl_resp_cb` → netlink ACK to original user socket.

Ordered flow reference: **`references/netbroker-rtnl-trap.md`** (FLOW-013).

---

## 6. Completion semantics (`libnetbroker.h`)

| Return | Meaning | Kernel programming |
|--------|---------|-------------------|
| `LIBNB_CFG_OK` | Config accepted; allow kernel path to continue | nbproxy may call **`libnb_update_kernel`** — replays stored RTNL on broker `rtnl_sk`; hook sees matching `rtnl_pid` → pass-through |
| `LIBNB_CFG_OK_PROCESSED` | Config accepted and handled by broker | **No replay**; whitelisted NX-OS daemons (ipfib, netstack, kim, …) program kernel later |

Example (verified E2E): `ip route add … dev lo` → static-route handler returns
`-ENODEV` on `lo`, nbproxy still returns **`LIBNB_CFG_OK`** + replay → route in
Linux FIB, nbproxy event-history shows `operation 3` / `-19` (METHOD-020).

---

## 7. Module parameters (KLM tunables)

| Parameter | Effect |
|-----------|--------|
| `disable_rtnl_hook` | Bypass RTNL trap (debug) |
| `disable_dev_ioctl_hook`, `disable_sock_*_hook` | Bypass other hook surfaces |
| `block_rib`, `block_interface`, `block_neighbor`, `block_mcast_group` | Deny trapped category with `-EOPNOTSUPP` even when broker exists |
| `block_ethtool` | Block ethtool ops (not tied to a broker group) |
| `container_id`, `is_standby` | ToR / HA behavior |

Probe: `run bash ls /sys/module/klm_cisco_nb/parameters/` + `cat` (METHOD-019).

---

## 8. Usages (when to use netbroker artifacts)

| Goal | What to use | Method / entry |
|------|-------------|----------------|
| Understand **design + ADRs** | This document | `architecture/netbroker-architecture.md` |
| Walk **RTNL trap step-by-step** | FLOW-013 | `references/netbroker-rtnl-trap.md` |
| **E2E prove** trap on a switch | perf + nbproxy event-history | **METHOD-020**, **METHOD-021** |
| **Privileged Linux** on sup LXC | `run bash sudo sh -c '…'` | **METHOD-019** |
| Prove **kernel hook** fired | `perf record -a -e 'cisco_nb_traces:*' …` | **METHOD-021** (not plain `dmesg`) |
| Prove **nbproxy handled** request | `debug nbproxy events` + `show nbproxy internal event-history events` | switch-commands Netbroker block |
| Check **brokers registered** | `/proc/net/cisco_nb_0` | KSTACK-054 |
| **LCND datapath** perf (unrelated hot path) | `lcnd_traces:*` timed capture | METHOD-021 + METHOD-015 |
| Post-kernel route mirror to URIB | KFIB netlink reader | FLOW-012 (complementary, not substitute) |

**Canonical E2E sequence** (static-route probe, minimal churn):

```text
debug nbproxy events
run bash sudo sh -c "rm -f /bootflash/nb.perf /bootflash/nb_traces.txt; \
  perf record -a -e 'cisco_nb_traces:*' -o /bootflash/nb.perf -- \
  ip route add 192.0.2.88/32 via 127.0.0.1 dev lo; \
  perf script -i /bootflash/nb.perf > /bootflash/nb_traces.txt 2>&1"
show nbproxy internal event-history events | include "IP Netbroker|operation 3|static route"
run bash sudo cat /bootflash/nb_traces.txt
run bash ip route del 192.0.2.88/32 via 127.0.0.1 dev lo
```

Pass: **7 kernel trace lines** + nbproxy **`operation 3`** in the same second.

---

## 9. Boundaries & related components

| Component | Relationship |
|-----------|--------------|
| **ipfib / kim / netstack / urib / ifmgr** | Whitelist bypass — may program kernel directly |
| **KFIB** | Reads kernel FIB → URIB **after** routes exist; does not trap admin |
| **KIM** | Programs LCND/interfaces; separate from netbroker trap path |
| **LCND / psinb** | Datapath; no netbroker involvement on punt/inject |
| **`netbroker.c` test tree** | Test harness only — not production nbproxy |

---

## 10. Observability

| Signal | Hot path? | Tool |
|--------|-----------|------|
| RTNL trap / genl forward | **Yes** | perf `cisco_nb_traces:*` (METHOD-021) |
| nbproxy handler / errors | **Yes** (userspace) | `show nbproxy internal event-history {events,errors,msgs}` |
| Sparse KLM `pr_info` | No | `dmesg -F /dev/kmsg -P` (KSTACK-055) |
| Plain `dmesg` on sup LXC | **Misleading** | Often empty — do not use as negative proof |

Tracepoints (`cisco_nb_trace.h`): `trace_nb_rtnl_doit`, `trace_nb_send_request`,
`trace_nb_rtnl_resp`, … — **not** printk; `echo 8 > /proc/sys/kernel/printk` does
not surface them.

---

## 11. Architecture Decision Records (ADR)

**ADR-001 — Kernel hook + userspace broker split.** Admin interception lives in
the **patched kernel framework** + `klm_cisco_nb`; policy and NX-OS integration
live in **nbproxy** via genl. *Rationale:* keep fast path in kernel (clone +
forward + abort) while reusing existing NX-OS APIs for real configuration.
*Trade-off:* nbproxy must be up and registered or trapped categories fall through
(no broker) or fail (`block_*`).

**ADR-002 — Whitelist bypass for NX-OS writers.** `cisco_nb_allow_by_current()`
lets trusted comm names / labels / cgroups skip the trap. *Rationale:* ipfib, KIM,
and netstack already own kernel programming; re-trapping them would deadlock or
duplicate work. *Trade-off:* whitelist drift across images/containers must be
re-verified on each platform (comm parent, Smack, cgroup path).

**ADR-003 — Dual completion: `OK` vs `OK_PROCESSED`.** Brokers choose between
**kernel replay** (`libnb_update_kernel` on dedicated `rtnl_sk`) and **defer to
NX-OS daemons**. *Rationale:* static-route and interface paths often need immediate
kernel visibility; URIB-owned routes may already be programmed by ipfib.
*Trade-off:* readers must check which branch a given `cfg_cb` uses — same user
command can FIB-update without URIB update (E2E `lo` static route case).

**ADR-004 — Abort RTNL with `-EINTR` / `NETBROKER_HANDLED`.** Trapped requests do
not partially apply in the kernel handler; completion is async via genl ACK.
*Rationale:* prevents torn state when NX-OS rejects or transforms the request.
*Trade-off:* user tools see EINTR/interrupted semantics until nbproxy ACKs.

**ADR-005 — Group-per-broker registration.** Each `NB_GRP_*` has an independent
genl broker slot (`/proc/net/cisco_nb_*` row). *Rationale:* isolate static routes,
dynamic RIB, interfaces, neighbors for separate backends and restart.
*Trade-off:* nbproxy must register **all** groups it owns at init
(`nb_libnb_init_brokers`); partial registration leaves holes (trap with no handler).

**ADR-006 — Tracepoints over printk for hot path.** RTNL trap/forward uses
`TRACE_EVENT` (`cisco_nb_traces:*`), not `pr_info`. *Rationale:* low overhead,
perf capture on production images. *Trade-off:* `dmesg` is useless for proving trap
fired; agents must use METHOD-021 perf or nbproxy event-history (KSTACK-055).

**ADR-007 — `block_*` module params as emergency deny.** Even with a registered
broker, ops can be hard-denied per category. *Rationale:* operational kill-switch
without unloading KLM. *Trade-off:* `-EOPNOTSUPP` to user with no NX-OS side effect —
distinct from trap-and-forward.

**ADR-008 — Complement KFIB, do not merge.** KFIB imports kernel→URIB; netbroker
gates kernel **writers**. *Rationale:* different direction and trust model.
*Trade-off:* debugging "route missing in URIB" requires checking both whether
netbroker trapped/applied NX-OS policy **and** whether KFIB would import the
resulting kernel route.

---

## 12. Cross-reference

- **FLOW-013** — `references/netbroker-rtnl-trap.md`: ordered RTNL trap walk +
  E2E validation table (7 perf lines + nbproxy events).
- **KSTACK-054 / KSTACK-055** — verified entries in `knowledge/entries.md`.
- **METHOD-019 / METHOD-020 / METHOD-021** — privileged bash, E2E test, perf capture.
- **FLOW-012 / `architecture/kfib-library-architecture.md`** — kernel→URIB import
  after netbroker/whitelist writers have programmed the kernel.
- **switch-commands.md** — Netbroker / kernel perf command blocks.

> Runtime numbers (PIDs, seq ids, timestamps) in FLOW-013 E2E section are
> **illustrative** from 2026-07-26 switch 107; anchor on event **names** and
> pass criteria, not literal seq values.
