# KSTACK Switch Commands (detail)

Saved switch commands and what they yield. A compact topic pointer lives in
`../KNOWLEDGE.md`. Open this file when gathering switch data. All commands are
`impact: read-only` unless noted; S1HAL/IPSec output may contain secrets -- redact.
Single-writer rule (SKILL.md) covers this file too.

## Switch Commands

Commands the user has confirmed yield specific switch data. Reuse before asking
again. Format: `data needed` -> `command` (platform / context, source).

For switch access from this workspace, prefer the Nexus MCP connector when it is
available. Use `nexus_connect`, `nexus_execute_command(s)`, and
`nexus_disconnect`, and keep credentials out of files and command templates.
If MCP is unavailable, use `sshpass -e`. Template (use a **fresh `mktemp`**
known_hosts -- a stale key in a fixed shared `/tmp` file trips
`StrictHostKeyChecking` and fails with exit 255, especially across concurrent
agents/sessions):

```bash
KH=$(mktemp); SSHPASS='<password from user/session>' sshpass -e ssh -F /dev/null -T \
  -o PreferredAuthentications=password \
  -o PubkeyAuthentication=no \
  -o KbdInteractiveAuthentication=no \
  -o StrictHostKeyChecking=accept-new \
  -o UserKnownHostsFile="$KH" \
  -o ConnectTimeout=8 \
  <user>@<switch-ip> '<read-only nxos command>'; rm -f "$KH"
```

**Switch access from subagents -- verified working (2026-06-30).** A *non-readonly*
background subagent can reach the switch via **both** the `sshpass` template above and
the Nexus MCP (`CallMcpTool` -> `user-Nexus Device MCP` / `nexus_connect` ->
`nexus_execute_command` -> `nexus_disconnect`). Network egress to the box (TCP:22 and
the MCP server) is open from the subagent sandbox. Only **read-only / Ask-mode**
subagents cannot connect (no Shell-write, no MCP, no network). The subagent must
supply creds itself (pass the password explicitly; env-injected default-device
convenience may not propagate) and disconnect any MCP session it opens.

- **NX-OS identity check** (`impact: read-only`): use Nexus MCP or the template
  above with `show hostname` or `show version`. Verified on 2026-06-17 against
  `172.20.175.106` as `admin`: `show hostname` returned `des1infra`, and
  `show version` returned NX-OS `10.7(1)`. Re-verified via MCP on 2026-06-24.
  Do not save the password.
- **Card / ASIC identity** (`impact: read-only`; METHOD-016, FLOW-006, KSTACK-028):
  resolve the switch's ASIC family + platform BEFORE datapath reasoning (decap/encap
  is platform-specific, KSTACK-003).
  - `show module` -> per-slot Model (PID) + card type/state.
  - `show version` -> chassis string, CPU, running image.
  - `show inventory` -> PID + serial per chassis/module.
  - `show sprom module <mod> <idx> | include 'Mfg Bits'` -> ASIC variant bits
    (Confluence Eastlake/Krypton-Lite note: value `>4096` => E2 variant, else E1).
  - `show hardware internal` (platform-specific) -> ASIC instance detail when the
    PID alone is ambiguous.
  Then map PID/codename -> ASIC family via `references/hw-codenames-sone.md`
  (FLOW-006; SONE subset of the Confluence "Hardware codenames" page, Cisco Highly
  Confidential) and confirm a SONE card via `SW_CARD_ID_IS_WITH_SONE_FAMILY_ASIC`
  (KSTACK-028) -> Silicon One datapath. Example (verified 2026-06-30): `des1infra`
  PID `N9348Y2C6D-SE1U` = codename **Deschutes** = **Krypton (E100)** = SONE family.
- **KIM internal event histories** (`impact: read-only`): use KIM's internal
  event-history buffers for KIM debug macros; these messages may not appear in
  `show logging logfile`. Full option set (verified 2026-06-30 via `?`):
  `cli, errors, events, intf, ksink-ha, msgs, mts, packets, pss, vrf, vxlan,
  vxlan-error`.
  - `KIM_DBG_ERR` -> `show kim internal event-history errors`
  - `KIM_DBG_INTF` -> `show kim internal event-history intf`
  - **MTS subscription proof** -> `show kim internal event-history msgs` prints live
    `E_MTS_RX/E_MTS_TX [NOT] Opc:<NAME>(<num>)` with Src/Dst SAP + payload (verified
    2026-06-30: KIM received `MTS_OPC_L3VM(51201)`). `... mts` is the MTS-specific
    debug buffer (was empty in steady state).
  - **Capture-ordering gotcha** (verified 2026-06-30, G.4): these buffers print
    **newest-first**, so `| last <n>` returns the *OLDEST* lines and `| head <n>` is
    rejected (`% Invalid command`). To grab the newest entries for a specific event,
    filter by the interface token: `show kim internal event-history intf | include
    <nxos-ifindex>` (e.g. `0x140003df`) or `| include <ifname-digits>`. Use the same
    `| include` trick on `msgs` to find a given opcode/SAP.
  - **Live create/delete handler trace** (`impact: read-only`, observed via G.4
    config-churn): a loopback create shows, in `event-history intf`, `kim_create_if`
    -> `kim_if_lpss_add_{lnx,nxos}_handle` -> `kim_process_vrf_update`/`_move` ->
    `kim_set_router_mac` -> `kim_process_netdev_state_change`
    (`NETDEV_STATE_CHANGE_NOTIFY ... state 1`) -> `kim_set_if_link_state` (UP); delete
    shows `NETDEV_STATE_CHANGE_NOTIFY ... state 2` (DOWN) -> `kim_remove_if` (removes
    from internal db). The inbound MTS create/delete *opcode* is NOT logged in
    `msgs`/`mts` on 10.7(1) IMG9 -- handler side only.
  Verified on 2026-06-24 during CSCwv05793 fixed-image validation: filtering
  `show kim internal event-history errors` for
  `Rejecting|unauthorized|62579|SAP|SAT_FABRIC` returned
  `Rejecting unauthorized opc 62579 from SAP 8879` from
  `kim_process_sat_fabric_pc_port_state_change`.
  - **KIM `IM_IF_CREATED` unauthorized-SAP rejection decode** (`impact: read-only`,
    KSTACK-052; verified 2026-07-14 on Mustang-2 172.22.135.166): `show kim internal
    event-history errors | include unauthorized` prints
    `kim_is_msg_sender_authorized:360 IM_IF_CREATED: rejecting opcode 62467 from
    unauthorized SAP <n>`. `kim_process_if_created` (the ONLY create-time programmer of
    an L2 member netdev MTU: `kim_get_mtu`→`kim_set_ifmtu`) accepts `IM_IF_CREATED`
    (opc **62467**) ONLY from `MTS_SAP_IFMGR`(179) or `MTS_SAP_KIM` — gate added by
    commit `d1318a9ee70` = **CSCwv05804**. Rejections from ethpm(175)/eth_port_channel(378)/
    interface-vlan(210) mean the MTU handler never runs for those ifindexes ⇒ breakout
    members show `Linux=1500 / kim db=0`. The netdev is still created via the separate
    ethpm path `kim_process_if_create_netdev_req`→`kim_create_if` (tunnel-only MTU).
- **MTS SAP → process/component map** (`impact: read-only`, verified 2026-07-14 on
  Mustang-2): `show system internal sysmgr service all` — the **`SAP` column** is the
  per-service primary SAP. To resolve one SAP: capture the output and
  `awk '$4==<sap>'`. Confirmed: 179=`ifmgr`, 175=`ethpm`, 378=`eth_port_channel`,
  210=`interface-vlan`, 151=`pixm_gl`, 153=`pixm_vl`, 221=`l2fm`, 246=`pktmgr`. Use this
  to decode any `unauthorized SAP <n>` / `from SAP <n>` MTS reject or src-sap in KIM
  event-history. (`show system internal mts sap <n> [description|stats]` is NOT valid
  syntax on 10.7 IMG9 — use the sysmgr service table instead.)
- **KIM programming verification suite** (`impact: read-only`, root/admin; FLOW-005
  Appendix G): all KIM internal CLIs live under `show kim internal <topic>` where
  `<topic>` in `event-history, ha-stats, info, issu-stats, mem-stats`. Verified
  2026-06-30 on `des1infra` (N9348Y2C6D-SE1U, 10.7(1)):
  - `show kim inconsistency` -- **primary validator**: cross-checks KIM DB vs actual
    kernel/LCND programming for all interfaces. Healthy =
    `Consistency test for all interfaces : PASSED`. First command to run when
    validating any KIM->LCND mapping or suspecting a programming drift.
    **MTU-mismatch decode (KSTACK-052, verified 2026-07-14 on Mustang-2 N9364E
    10.7(0)IMG9):** each line reports a three-way triad — `Linux MTU` = kernel netdev
    (`SIOCGIFMTU`), `NxOS MTU` = `im_get_if_mtu(iod)` (IM/hardware), `kim db MTU` =
    `lc_mtu`. Both `Linux` and `lc_mtu` are written ONLY by `kim_set_ifmtu` (triggered by
    an IM `IM_MSG_TLV_MTU` param-change), so **`Linux=1500 (default) + kim db=0` means the
    MTU setter never ran** for that ifindex. Seen for all breakout sub-ports (`0x38xxxxxx`,
    e.g. Eth1/5/1) carrying `mtu 9216`: they were `kim_create_if`-created AFTER the boot
    MTU flood (which only hit SVIs `0x901xxxx`) and never got a per-port MTU event.
    Confirm with `show kim internal event-history intf | include <ifindex>|MTU` (look for
    `Set MTU 9216 for Interface 0x38...`; absence == the smoking gun). ASIC datapath is
    unaffected (uses hardware 9216); only the punt/inband netdev MTU lags at 1500. Fix
    (disruptive): re-toggle `mtu` on the members to force `IM_MSG_TLV_MTU`.
  - `show consistency-checker kim {interface <ifid>} [brief|detail]` -- **cochk
    Python path** (KSTACK-058): `cochk.cmd` `show_cc_kim` ->
    `pm_cli_show_cc_kim` -> `cc_kim.py:kimConsistencyInterface`. Single
    ifindex only. Prints `consistency kim:` then `Consistency Check:
    PASSED|FAILED` plus longName lists. Gated `$notvalidinexbl`. Verified
    2026-09-22 Mustang-1: `show consistency-checker kim interface Ethernet1/49`
    -> FAILED / `Ethernet1/49`. `detail` dumps NxCC JSON. On Mustang-1
    Ethernet1/49 the only failures were `mtu_Im_Kernel` and `mtu_Im_Kim`
    (expected 9216 / actual 1500). Those come from:
    `show interface Ethernet1/49` (`i.get_mtu_frm_im()`),
    `show kim internal info kernel interface Ethernet1/49` (`kernelMtu`),
    `show kim internal info interface Ethernet1/49` (`MTU`).
  - Unqualified `show consistency-checker kim` can hit the **duplicate**
    `kim.cmd` registration of `kim_display_inconsistency` (KSTACK-046) instead
    of cochk. Discriminator: native banner `Checking Inconsistency status for
    all Interfaces....` vs Python `consistency kim:`. On Mustang-1 2026-09-22
    the no-interface form printed the native banner and Eth1/49+Eth1/50 MTU
    triad `Linux=1500 / NxOS=9216 / kim db=1500` (not KSTACK-052 `kim db=0`).
  - `show kim internal info [interface|kernel|lpss|namespace]` -- dumps live per-netdev
    `lc_if_info` (the struct the `LC_ND_*` SET verbs program): `Ifindex / Lnx Ifindex /
    Iod / MTU / Port mode / VLAN / eVLAN / Flags / dmod / dpid / qi / northstar_pid /
    lif / ltl / NS / SI Parent ifindex / PC members / CBL state / Vlan bmp`. This is the
    on-box mirror of FLOW-005 Q3/App E. (e.g. loopback `VLAN 65535`, tunnel `VLAN 0`,
    trunk/SI ports `CBL state: 4095`, Tunnel501 `lif 0x1104`). `info namespace` lists
    the per-NS socket/netlink fds.
  - `show kim internal issu-stats` -- restoration phase timestamps incl `LCND
    restoration`, `Inband restoration`, and KIM-sent opcodes
    `MTS_OPC_KIM_STATEFUL_RSTRT` (->pktmgr) / `MTS_OPC_KIM_L3_STATEFUL_RSTRT`
    (->netstack).
  - `show kim internal mem-stats` -- KIM shared-mem allocation stats (per-UUID).
  - `show kim internal ha-stats` -- active-sup-on-EOR only; on a ToR returns
    `Command only applicable on active sup on EOR`.
- **Preferred module-level command path: Type 2 / `slot quoted`** (`impact:
  read-only`, output may contain secrets): use
  `slot <slot> quoted "<module command>" | no-more` from the supervisor CLI.
  Verified on 2026-06-17:
  `slot 1 quoted "show hardware internal s1hal ipsec tunnels all" | no-more`
  returned the S1HAL IPSec Tunnel Database from module 1. Prefer this for future
  one-shot collection, especially over SSH with METHOD-008's `sshpass -e`
  template.
- **Fallback module-level command path: Type 1 / `at mod`** (`impact: read-only`,
  output may contain secrets): run `at mod <slot>`, then run the module command
  at `module-<slot>#`, then `exit`. Verified on 2026-06-17:
  `at mod 1` -> `show hardware internal s1hal ipsec tunnels all | no-more`
  returned the same S1HAL IPSec Tunnel Database and `exit` returned cleanly to
  `des1infra#`. Use when an interactive module shell is specifically needed.
- **S1HAL IPSec tunnel database** (`impact: read-only`, sensitive output):
  `slot 1 quoted "show hardware internal s1hal ipsec tunnels all" | no-more`
  is the preferred collection command. It returns IPSec feature state, tunnel
  table, ingress/egress SA summaries, GID mapping, and total tunnel count. It
  also prints `Enc Key`, `Auth Key`, `Salt`, SA handles, and session handles; do
  not store unredacted output in `KNOWLEDGE.md` or final answers.
- **IPSec SUP control-plane ladder** (`impact: read-only`): run these before
  module/S1HAL commands to identify the tunnel, endpoint, if-handle, SPIs, and
  tunnel-manager state:
  - `show ip interface brief`
  - `show crypto ipsec internal endpoints`
  - `show crypto ipsec internal sa-db`
  - `show tunnel internal info global  detail`
  - `show tunnel internal database reachability`
  - `show tunnel internal database primary | no-more`
  Verified on 2026-06-17: Tunnel501 was up, sourced from Lo501 (`50.50.1.1`) to
  `50.50.1.6`, endpoint state was `established`, if-handle was `0x180101f5`, and
  the SA DB exposed ingress/egress SPIs used for S1HAL correlation.
- **IPSec S1HAL hardware ladder** (`impact: read-only`, sensitive output): prefer
  Type 2 with `slot 1 quoted "<command>" | no-more`:
  - `show hardware internal s1hal ipsec global`
  - `show hardware internal s1hal ipsec sdk info`
  - `show hardware internal s1hal ipsec sec-engines`
  - `show hardware internal s1hal ipsec tunnels all`
  - `show hardware internal s1hal ipsec tunnels tunnel-id <tunnel-id>`
  - `show hardware internal s1hal ipsec counter tunnels all`
  - `show hardware internal s1hal ipsec counter tunnels tunnel-id <tunnel-id>`
  - `show hardware internal s1hal ipsec counter sec-engines all`
  Verified on 2026-06-17 for tunnel ID `4356`: S1HAL feature status was enabled,
  global DB initialized, SDK saw one IPSec tunnel, tunnel GID was `0x1104`,
  ingress/egress SPIs matched SUP SA DB, ingress and egress SAs were placed on
  security engine indexes 4 and 5 respectively, tunnel counters exposed
  encrypted packets plus ingress authentication-error packets, and security-engine
  counters exposed per-engine input/output packet/byte counters plus auth-only,
  dummy, and offset-error counters.

Seeds below are derived from code (`lcnd_debug.c`); **confirm exact invocation on
the box with the user** before relying on them (proc paths/permissions vary).

- **LCND decap/encap trace toggles** (`impact: read-only`): debug vars
  `lcnd_pkt_decap_debug` / `lcnd_pkt_encap_debug` (defined in `lcnd_debug.c`),
  set via the `lcnd_debug` proc file; trace output appears in the proc files
  `pkt_decap_trace` / `pkt_encap_trace` (created in `lcnd_debug.c`, under the
  LCND proc dir). Other proc files: `pkt_mgmt_decap_trace`, `pkt_fip_trace`,
  `lcnd_proto_stats`, `pkt_dump_trace`, `lcnd_error_stats`.
- **lc_vlan / ifindex runtime tables** (`impact: read-only`): LCND keeps
  `lcnd_ifindex_htab` etc., dumpable via `lcnd_debug_hash_dump` (`lcnd_debug.c`);
  confirm the exact proc trigger with the user.
- **`show system internal lcnd hash-tables` -- LCND runtime hash tables**
  (`impact: read-only`, REQUIRED for branch analysis): dumps all LCND hash tables to
  the CLI. Backed by the seq_file proc entry `/proc/lcnd/lcnd_hash_tables`
  (ISSU-LXC: `/proc/lcnd1/lcnd_hash_tables`); the syscli handler
  `syscli_show_lcnd_hash_tables` (`syscli_lcsup_common.c`) `cat`s that file, and the
  kernel renders it via `lcnd_dump_hash_tables(struct seq_file *)` in `lcnd_debug.c`.
  Tables: **LIF Hash Table** (columns `LIF | Intf | LTL | ifindex | lnx_ifindex |
  phy_ifindex | IOD | PHY_IOD`), Ifindex Hash Table (ifindex->intf + VLAN list),
  PI(Port Index), VP, LDB(MPLS), Mirror GID, VLAN GID (`SP vlan GID | LTL | Vlan`),
  VLAN BD, NVE Peer, VNI VLAN, VRF Table. This is the runtime state needed to resolve
  `  source_lp`/`relay_id`/ifindex into a concrete interface and to decide which decap
  sub-branch fired (METHOD-012, KSTACK-018). Verified-useful 2026-06-18 (one LIF row
  resolved to a subinterface with matching ifindex/IOD; concrete values are
  session-specific).
  - **AVAILABILITY CAVEAT (image-gated, verified 2026-06-30 on `des1infra`,
    10.7(1) IMG9(0.166)):** this CLI and proc file were **NOT present** on that
    image. `show system internal lcnd hash-tables` returned `% Invalid command`;
    `show system internal lcnd` exposed only `error-stats | event-history |
    proto-stats`; and `/proc/lcnd/lcnd_hash_tables` did not exist
    (`No such file or directory`; no `/proc/lcnd1/` either). The other `/proc/lcnd/`
    entries WERE present (`lcnd_debug`, `lcnd_error_stats`, `lcnd_proto_stats`,
    `pkt_decap_trace`, `pkt_dump_trace`, `pkt_encap_trace`, `pkt_fip_trace`,
    `pkt_mgmt_decap_trace`). So the seq_file dump is source-real but build/branch-gated
    -- **do not assume it exists; probe `run bash ls /proc/lcnd/` first.** When it is
    absent, the KIM-side mirror `show kim internal info` (FLOW-005 App G) is the
    fallback for per-netdev lif/ifindex/iod/vlan/CBL state.
  - **Replaces the legacy dmesg dump**: the old `lcnd_table_dump=1` debug write
    (`echo lcnd_table_dump:1 > /proc/lcnd/lcnd_debug`) that printk'd the tables to the
    kernel log has been removed; the `lcnd_table_dump` var and its `lcnd_debug[]` entry
    are gone. Output now goes only to the CLI/proc file (no more dmesg roll-off on
  scale/bombardment setups).

### LACP peer-side timeout and recovery timeline

- **`show lacp internal info all`** (`impact: read-only`): emits each LACP
  interface's first/last TX/RX snapshot counters, configured timers, current
  protocol fields, and retained FSM transitions. Extract the target interface
  block and preserve the event timestamps/state names. A stable valid PDU may
  refresh `current_while_timer` without creating an FSM transition, so absence
  of a transition is not proof that no packet arrived.
- **`show logging logfile | include <member-interface>`** and
  **`show logging logfile | include <port-channel>`** (`impact: read-only`):
  correlate the LACP FSM with member down/up, suspension, first-operational-port
  movement, and whether the bundle survived on another member.
- **Evidence rule:** `LACP first/last pkt sent/recv` are snapshot extrema, not a
  packet trace. `RECEIVE_PARTNER_PDU_TIMED_OUT` is a directly logged FSM event;
  `timeout_timestamp - current_while_timer` is only a timer-derived last-refresh
  boundary and cannot identify a specific PDU without a packet capture or
  packet-level trace. Measure both switch clocks around the collection before
  combining DUT and peer timelines.

### Kernel perf trace capture (METHOD-021 — all tracepoint subsystems)
- **Discover events:** `run bash sudo sh -c "perf list | grep -E 'lcnd_traces|cisco_nb'"` (`impact: read-only`)
- **Timed capture (LCND / live traffic)** — ASK `<DUR>`, DEFAULT 10s:
  ```text
  run bash sudo sh -c "rm -f /bootflash/lcnd.perf /bootflash/lcnd_traces.txt; timeout <DUR> perf record -a -e 'lcnd_traces:*' -o /bootflash/lcnd.perf -- sleep <DUR>; perf script -i /bootflash/lcnd.perf > /bootflash/lcnd_traces.txt 2>&1"
  ```
- **Stimulus-bound capture (netbroker / single admin op):**
  ```text
  run bash sudo sh -c "rm -f /bootflash/nb.perf /bootflash/nb_traces.txt; perf record -a -e 'cisco_nb_traces:*' -o /bootflash/nb.perf -- <stimulus>; perf script -i /bootflash/nb.perf > /bootflash/nb_traces.txt 2>&1"
  ```
- **Inspect:** `run bash sudo cat /bootflash/<tag>_traces.txt` (`impact: read-only`)
- **Rules:** always `sudo sh -c`; `-o /bootflash/*.perf` then `perf script -i … > …txt`;
  never `perf script --no-pager` (invalid on NX-OS util-linux 2.39.x); never bare
  `run bash perf`. See METHOD-021 for remote SSH pull and subsystem table.

### NX-OS `run bash` privilege (METHOD-019 — read-only when probed)
- **Plain `run bash <cmd>` is unprivileged.** Do not use it for `dmesg`, `perf`,
  `/dev/kmsg`, or other root-only Linux introspection — you will get permission
  denied or misleading empty output from **plain `dmesg`**.
- **Privileged one-shot (MCP/SSH default):**
  `run bash sudo sh -c "<full pipeline>"` — keep pipes/redirection **inside** the
  quoted string. Examples:
  - `run bash sudo sh -c "dmesg -F /dev/kmsg -P | grep cisco_nb"` (sup LXC kmsg read)
  - `run bash sudo sh -c "cat /proc/sys/kernel/printk"`
- **When `-n` works on-box (verify first):** `run bash sudo -n python3 …` (METHOD-018).
- **Kernel perf traces:** use **METHOD-021** timed/stimulus patterns — not bare
  `run bash sudo timeout … perf record` without `-o /bootflash/*.perf` + separate
  `perf script -i … > …`.
- **Interactive:** `run bash sudo bash` → root `bash-#`.
- **Kernel log tuning (sup LXC, `impact: sysctl write` — session-local):** raise
  console verbosity before chasing sparse `pr_info` printk (KSTACK-055):
  - `run bash sudo sh -c "echo '8 6 1 8' > /proc/sys/kernel/printk"` (was `1 6 1 1`
    on 107; first field is `console_loglevel`)
  - optional: `run bash sudo sh -c "echo on > /proc/sys/kernel/printk_devkmsg"`
  - verify read path: `run bash sudo sh -c "printf '<6>probe\n' > /dev/kmsg &&
    dmesg -F /dev/kmsg -P | grep probe"`
- **Netbroker runtime proof:** prefer **`show nbproxy internal event-history events`**
  (+ `debug nbproxy events`) for trapped RTNL; **`dmesg -F /dev/kmsg`** only catches
  sparse `pr_info`, not tracepoint hot path (KSTACK-055).

### Netbroker (read-only)
- **`run bash cat /proc/net/cisco_nb_0`** (`impact: read-only`): lists registered
  netbroker groups with broker genl `pid` and RTNL socket `rtnl_pid` (ToR container 1
  may use `cisco_nb_1`). Empty table => no nbproxy brokers registered.
- **`run bash ls /sys/module/klm_cisco_nb/parameters/`** + **`cat .../disable_rtnl_hook`**
  (`impact: read-only`): hook bypass flags (`disable_rtnl_hook`, `disable_dev_ioctl_hook`,
  `disable_sock_*_hook`) and deny flags (`block_rib`, `block_interface`,
  `block_neighbor`, `block_ethtool`, …). Non-zero `disable_*` => corresponding hook
  passes all requests to kernel unchanged.
- **`grep register_netbroker /proc/kallsyms`** (`impact: read-only`): confirms kernel
  netbroker framework is present (see `kspace/S00nxos-nb.sh` startup check).
- **Use with FLOW-013 / KSTACK-054** when validating whether shell `ip`/`ifconfig`
  changes are trapped vs whitelisted NXOS writers (`ipfib`, `kim`, `netstack:`).
- **`show nbproxy internal event-history events`** (`impact: read-only`): primary
  userspace proof that a trapped RTNL/ioctl reached nbproxy (`IP Netbroker event for
  operation N`, handler lines). Enable **`debug nbproxy events`** first if the buffer
  is quiet. Filter: `| include "Netbroker|operation|static route"`.
- **`show nbproxy internal event-history errors`** / **`msgs`** (`impact: read-only`):
  auxiliary nbproxy trace buffers.

### Netbroker end-to-end validation (METHOD-020 — minimal config churn)
- **Prerequisites** (`impact: read-only`): nbproxy HANDSHAKED; `klm_cisco_nb` loaded;
  `/proc/net/cisco_nb_0` shows Static Routes → nbproxy pid; `disable_rtnl_hook=N`;
  `block_rib=N`; from **`run bash sudo bash`**: `perf list | grep cisco_nb` shows
  `cisco_nb_traces:*`.
- **Step 0:** `debug nbproxy events` (`impact: debug on`)
- **Step 1 — kernel + stimulus** (privileged bash):
  `run bash sudo sh -c "rm -f /bootflash/nb.perf /bootflash/nb_traces.txt; perf record -a -e 'cisco_nb_traces:*' -o /bootflash/nb.perf -- ip route add 192.0.2.88/32 via 127.0.0.1 dev lo; perf script -i /bootflash/nb.perf > /bootflash/nb_traces.txt 2>&1"`
- **Step 2 — NX-OS trace:** `show nbproxy internal event-history events | include "IP Netbroker|operation 3|static route|Netbroker failed"`
- **Step 3 — verify:** `run bash sudo cat /bootflash/nb_traces.txt` (expect **7 lines**:
  `nb_rtnl_doit` → `nb_send_request` → nbproxy `nb_rcv_request` → `nb_rtnl_resp status=0`)
- **Step 4 — cleanup:** `run bash ip route del 192.0.2.88/32 via 127.0.0.1 dev lo`
- **Pass criteria:** kernel 7-trace sequence + nbproxy `operation 3` / `static route op 3`
  in the same second. `-ENODEV` on `lo` is OK (replay to Linux FIB only). Full decode:
  FLOW-013 § E2E validation, METHOD-020.

### UDLD (point-to-point link validation)
- **Configure (both ends, symmetric)** (`impact: disruptive` — enables link monitoring; aggressive mode may err-disable port on unidirectional detection):
  ```
  configure terminal
  feature udld
  interface ethernet <id>
    udld aggressive
  end
  copy running-config startup-config
  ```
- **`show feature | include udld`** (`impact: read-only`): confirms global UDLD feature state (`enabled`/`disabled`).
- **`show udld neighbors`** (`impact: read-only`): neighbor table — Port, Device Name/ID, Port ID, Neighbor State (`bidirectional` = healthy).
- **`show running-config interface ethernet <id>`** (`impact: read-only`): verify per-interface `udld aggressive` (or `udld enable` for normal mode).
- **Note:** `show udld interface ethernet <id>` is invalid on NX-OS 10.7(1); use `show udld neighbors` instead. Both ends must participate; mismatch (one side only) stays non-bidirectional until peer is configured.

_When the user provides a command that produces useful data (interface state,
`lc_vlan`, BD/VNI tables, counters, configs, traces), save it here with what it
returns and its `impact:` label._
