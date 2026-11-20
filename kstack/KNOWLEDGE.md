# KSTACK Knowledge Base

Canonical, append-as-you-learn store for the NXOS KSTACK kernel-networking
domain. Read this **lean core** before answering KSTACK questions: it holds the
Domain Map, the Methods/Entries/Switch **INDEX** tables, the References flow index,
and Debugging Tools. **Full bodies live in detail files -- open them lazily, by id:**
`knowledge/methods.md` (METHOD-*), `knowledge/entries.md` (KSTACK-*),
`knowledge/switch-commands.md`, and `references/*.md` (flows). To capture: add a
one-line index row here **and** the body in the matching detail file (see `SKILL.md`
for the capture rules and entry format).
Actual reuse counts for `METHOD-*`, `KSTACK-*`, and `FLOW-*`/reference entries
live in the sidecar `USAGE_COUNTS.md`; do not store usage metrics in this file.

This is the lean core of the single shared brain for Cursor and Codex (the whole
`kstack/` skill directory -- this file plus `knowledge/` + `references/` +
`architecture/` + `scripts/` -- is one real directory, symlinked into both skill roots).

> **VOLATILE vs STABLE (read first).** The code changes frequently. Any **line
> number**, **interface name** (`EthX/Y`, `VlanN`, `PoNNNN`), or **per-session
> value** (ifindex, IOD, LIF/`source_lp`/`relay_id`, MAC, VLAN/VNI/BD, counts)
> anywhere in this file is a **VOLATILE "as-of" hint, NOT an anchor** -- it
> drifts across PID, image build, and session. Always start analysis fresh:
> anchor on **function / macro / struct-field names**, **branch/condition shape**
> (symbolic), and **trace-string / comment literals**; locate code by grepping
>   the function name (not a stored line number); and re-derive runtime values from
> the user's CURRENT packet + CURRENT `show system internal lcnd hash-tables`
> (the LCND runtime hash tables; formerly the `lcnd dump_table` dmesg dump).
> Never reuse a stored
> number/interface as a premise. (SKILL.md "Stable anchors only".)

---

## Domain Map (curated reference)

- **Default platform**: **Silicon One** (confirm per query). `lcnd_sone_*`
  functions are the path seen in the Silicon One inband traces
  (`lcnd_sone_inband_decap`). Other platforms have their own functions -- never
  cross-cite (KSTACK-003).
- **Expertise lens**: reason as Networking + Linux-kernel + NXOS-switch engineer.
- **Tree**: `standalone/infra/kstack/` -- NXOS kernel-space networking infra.
  - `kspace/lcnd/lcnd_n9k.c` -- LCND: punt (decap) + inject (encap) datapath.
- **KSTACK components + source locations** (user-provided, dirs verified 2026-07-09):

  | Component | KLM / role | Source dir |
  |-----------|------------|------------|
  | **LCND** (`klm_lcnd`) | punt (decap) + inject (encap) datapath; per-platform dispatch | `standalone/infra/kstack/kspace/lcnd/` |
  | **KIM** | control plane; programs `lc_if_info` (LCND reads it) | `standalone/infra/kstack/kim/` |
  | **KVFIB / LIBKVFIB** | kernel VFIB (`kfib.c`, `kfib_mts.c`, `kfib_urib.c`, `kfib_netlink.c`) | `standalone/infra/kstack/kfib/` |
  | **KLM_VDC** (`klm_vdc`) | `/dev/klm_vdc` VDC queue/ethertype classifier | `standalone/platform/storage/sup/kspace/vdc/` |
  | **KLM_PS_INB** (`klm_psdev`) | `ps-inb`/`ps-svc-inb` pseudo-netdev punt/inject driver (`psdev_main.c`, `psdev_create.c`) | `standalone/platform/insieme/drivers/emon_psdev/kspace/` |
  | **Netbroker** (`klm_cisco_nb` + nbproxy) | Trap RTNL/ioctl/socket admin from third-party tools; broker to NXOS CP | `standalone/infra/kstack/netbroker/` (`kspace/`, `lib/`, `nbproxy/`) |

  Note: LCND/KIM/KVFIB live under the shared `infra/kstack/` tree; KLM_VDC and
  KLM_PS_INB are **platform** KLMs outside it (external deps from LCND's view).
  Netbroker kernel hooks are in `standalone/third-party/src/kernel/nx-linux/patches.x86e-6.6/netbroker-*.patch` applied to `linux-6.6`.
- **Kernel source (in-repo)**: `standalone/third-party/src/kernel/nx-linux/linux-6.6/`
  (`net/core/skbuff.c`, `include/linux/if_vlan.h`, `include/linux/skbuff.h`).
  Kernel version is **6.6** (user-confirmed). The `bin/linux/final.x86e-6.6/...`
  headers are stubs -- use the `nx-linux/linux-6.6` source (METHOD-005, KSTACK-008).
- **SONE inband RX punt module chain** (from crash `Call Trace`, KSTACK-006):
  ASIC RX `[klm_sone_krypton]` -> `ps_sone0_rx_handle_frame [klm_psdev]` ->
  `netif_receive_skb` -> `psinb_rx_handle_frame [klm_psdev]` ->
  `rni_handle_platform [klm_rni_lcnd]` -> `handle_platform [klm_lcnd]` ->
  `lcnd_plat_decap` -> `lcnd_sone_inband_decap` -> `lcnd_sone_process_ipsec` ->
  `lcnd_sone_get_netdev` (static, inlined). `klm_vdc` provides queue/eth-type
  helpers on this path.
- **Inband interface names** (module-param string constants in `lcnd_n9k.c`;
  these netdev names are code constants, not per-session values):
  - `real_intfc = "ps-inb"` -- the punt/inject netdev between ASIC and supervisor
    (TX target via `dev_queue_xmit`; RX source). This is what "sup-inband" means.
  - `real_app_intfc = "ps-svc-inb"` -- service/app inband variant.
  - `kimdata_intfc = "kim-data"` -- post-decap handoff netdev for kstack-client
    protocols (LACP/LLDP copies cloned here); owned by `klm_lcnd`.
  - `eth_inb_intfc = "ps-sup-eth1"` -- sup eth inband.
  - Upper RX modules (`klm_psdev`/`psinb_rx_handle_frame`, `klm_rni_lcnd`,
    `klm_sone_krypton`) live OUTSIDE `standalone/infra/kstack/` (external deps).
- **Control blocks** (typedefs in `lcnd_n9k.c`): RX/decap uses
  `l2_recv_attr_cb_t` (macro `L2_RECV_CB`, the `l2ra_cb`); TX/encap uses
  `l2_xmit_attr_cb_t` (macro `L2_XMIT_CB`, the `l2xa_cb`). They carry derived
  fields such as `l2ra_vni`, `l2ra_pm_vlan`, `l2ra_sw_bd`, `phy_ifindex`.
- **CRITICAL -- platform dispatch index**: hub `lcnd_plat_decap` selects a
  per-platform `*_inband_decap`; encap mirrors via `lcnd_encap_fill_plat_hdr` ->
  `*_encap_fill_plat_hdr`. These do NOT share behavior -- confirm the exact one
  before reasoning (KSTACK-003). Function-name map (grep the name to locate;
  line numbers intentionally omitted -- they drift):

  | Platform | decap fn | encap fn | file |
  |----------|----------|----------|------|
  | Silicon One | `lcnd_sone_inband_decap` | `lcnd_sone_encap_fill_plat_hdr` | `lcnd_n9k.c` |
  | Tahoe (TAH) | `lcnd_tah_inband_decap` | `lcnd_tah_encap_fill_plat_hdr` | `lcnd_n9k.c` |
  | T+ / 56840 | `lcnd_tplus_inband_decap` | `lcnd_tplus_tor_encap_fill_plat_hdr` | `lcnd_n9k.c` |
  | MTC | `lcnd_mtc_inband_decap` | `lcnd_mtc_encap_fill_plat_hdr` | `lcnd_n9k.c` |
  | BFN | `lcnd_bfn_inband_decap` | `lcnd_bfn_encap_fill_plat_hdr` | `lcnd_n9k.c` |
  | Innovium | `lcnd_innovium_inband_decap` | `lcnd_innovium_encap_fill_plat_hdr` | `lcnd_n9k.c` |
  | Fretta | `lcnd_fretta_inband_decap` | `lcnd_fretta_encap_fill_plat_hdr` | `lcnd_n9k.c` |
  | Triton | `lcnd_triton_inband_decap` | `lcnd_triton_encap_fill_plat_hdr` | `lcnd_n9k.c` |
  | Nvidia | `lcnd_nvdia_inband_decap` | `lcnd_nvdia_encap_fill_plat_hdr` | `lcnd_nvdia.c` |
  | Titan | `lcnd_titan_inband_decap` | `lcnd_titan_encap_fill_plat_hdr` | `lcnd_enxosv.c` |

  Note: the CSCux29417 "set vlan 0xffff for L3 intf" code is inside
  **`lcnd_tah_inband_decap`** (Tahoe), NOT SONE -- a classic cross-citation trap
  (KSTACK-003).
- **SiliconOne trap-code / `la_event.h` decode**: trap-code, punt-source and
  `fwd_header_type` enum names (`enum class la_event_e`) live **per-PID** at
  `standalone/third-party/src/siliconone-sdk/<sdk-dir>/include/api/types/la_event.h`.
  PID -> sdk-dir: **G200=gr2, Krypton=krypton, P200=palladium2, G2LL=g2ll**. The
  numeric code->name mapping is **PID/build specific** -- always decode against the
  correct PID's header, never reuse a number from another PID/session. Use
  `scripts/trap_code.py` (see Debugging Tools) to resolve codes to names.
- **TX / inject (encap) chain**: `lcnd_xmit` (`lcnd.c`) -> `lcnd_plat_encap`
  (`lcnd_n9k.c`, builds `l2xa_cb`) -> `lcnd_encap_fill_plat_hdr` ->
  `lcnd_sone_encap_fill_plat_hdr` -> `dev_queue_xmit` to `ps-inb`
  (KSTACK-015, FLOW-002).
- **Post-decap delivery (RX handoff)**: after a platform decap, SONE runs
  `lcnd_eth_type_trans` then `lcnd_flo_mgr`, which forks to: clone to kstack via
  `lcnd_skb_clone_to_kernel` (`netif_receive_skb`) / metadata + `kim-data`
  via `get_kimdata_device()` / exception. (KSTACK-012.) There is no
  `lcnd_skb_clone_to_netstack` symbol -- only comments; `CLONE_TO_NETSTACK` is used
  in `lcnd_gre_handler`.
- **Control plane (KIM)**: `standalone/infra/kstack/kim/` programs `lc_if_info`;
  LCND only reads it. `lc_vlan` is set by `kim_vlan_set()`
  (`kim_msg_handler.c`) which pushes `LC_ND_VLAN` + `lc_if_info.lc_vlan` to
  LCND via the `SIOCDEVMODLC` ioctl; for VNI/segment interfaces
  `lc_vlan = sw_bd` (`kim_mts.c`). (KSTACK-002.) Full KIM process design +
  ADRs: `architecture/kim-process-architecture.md`.
- **KLM_VDC ethertypes**: NX-internal punt ethertypes `0xf102 / 0xf103 / 0xf104 /
  0xfcfc` are VDC queue ethertypes (`<isan/klm_vdc_intf.h>`, included in
  `lcnd_n9k.c`). The `skb->protocol = htons(0xf104)` set in the IPsec strip has
  a `TODO: ... KLM_VDC` (KSTACK-010/014). Impl lives in
  `standalone/platform/storage/sup/kspace/vdc/klm_vdc_char.c` (unverified pointer).
- **`lc_if_info`** (`struct`, per netdevice) holds programmed interface state used
  by the datapath: `lc_vlan`, `lc_ifindex`, `lc_iod`, `lc_flags`, `lc_ifname`,
  `lc_portindex[]`. Programmed by KIM (above), not by `lcnd_n9k.c`.

---

## Methods Library

Reusable debugging/analysis techniques. **Full bodies in `knowledge/methods.md`** --
open it for the method you need; reuse the technique, not the session-specific
inference it once produced. Dedup/next-ID greps MUST include `knowledge/methods.md`.

| ID | Method | Topic | Status |
|----|--------|-------|--------|
| METHOD-001 | Last-write-wins value tracing | tracing, value-flow | verified |
| METHOD-002 | Identify the platform function from the trace prefix | platform, trace-prefix | verified |
| METHOD-003 | Decode lc_flags against kim_utils.h | lc_flags, decode | verified |
| METHOD-004 | Decode a kernel oops/panic to the exact source line | oops, panic, kernel | verified |
| METHOD-005 | Locate the in-repo kernel source (don't grep from root) | kernel-source, search | verified |
| METHOD-006 | skb header-pointer reasoning (eth_hdr vs skb_pull) | skb, headers | verified |
| METHOD-007 | Pick the platform function before any line lookup | platform, discipline | verified |
| METHOD-008 | Access NX-OS switches with MCP first, sshpass -e fallback | switch-access, mcp, ssh | verified |
| METHOD-009 | Prefer slot quoted for module-level data collection | module, collection | verified |
| METHOD-010 | IPSec SUP-to-S1HAL RCA command ladder | ipsec, rca | verified |
| METHOD-011 | Decode la_packet_punt_header_t from raw on-wire bytes | punt-header, decode | verified |
| METHOD-012 | Branch analysis needs lcnd dump_table + SiliconOne PID, not just the packet | branch, dump_table, pid | verified |
| METHOD-013 | Diagnose pseudo-inb TX not egressing its parent (no rebuild) | tx, psdev | verified |
| METHOD-014 | cscope-first navigation + parallel subagent fan-out | cscope, subagents, search | verified |
| METHOD-015 | Group perf lcnd_traces output on a per-packet basis | perf, lcnd_traces, grouping | verified |
| METHOD-016 | Grab ASIC/card identity from a live switch, classify SONE vs TOR | asic, card-id, sone, tor, identity | verified |
| METHOD-017 | Monthly incremental PR sweep (watermark + verify-before-advance, propose-only KB) | pr-sweep / maintenance | verified |
| METHOD-018 | Validate private raw-netlink hardening with least-mutating header-only ACK probes | netlink, validation, cap-net-admin, payload-bounds | verified |
| METHOD-019 | Privileged NX-OS `run bash` via `sudo sh -c`; sup LXC kmsg read uses `dmesg -F /dev/kmsg -P` | nxos, run-bash, sudo, dmesg, devkmsg, perf | verified |
| METHOD-020 | End-to-end netbroker validation: perf `cisco_nb_traces:*` + nbproxy event-history | netbroker, perf, nbproxy, e2e, validation | verified |
| METHOD-021 | Canonical NX-OS kernel perf capture/decode for all tracepoint subsystems | perf, tracepoint, lcnd_traces, cisco_nb_traces, bootflash | verified |
| METHOD-022 | Run eBPF on NX-OS with no bcc/bpftool/libbpf: off-box clang compile + raw bpf() ctypes kprobe loader (perf_event_open+SET_BPF) | ebpf, kprobe, raw-syscall, ctypes, off-box | verified |

---

## References (end-to-end flows)

Index of end-to-end datapath flows and protocol-wide command references. A
direction-specific flow generally lives in its own file under `references/`,
named for protocol and direction, e.g. `references/cdp-ingress.md`. Shared
protocol state that applies to TX and RX can live in a protocol-level file, e.g.
`references/ipsec.md`. Flows with **no specific protocol** go in the catch-all
file `references/catch-all.md`. When a current problem matches a flow, open its
file, walk it, and report past-vs-present differences (that delta is usually the
bug). Default platform: Silicon One.

| FLOW | Protocol | File | Platform | One-liner |
|------|----------|------|----------|-----------|
| FLOW-001 | IPsec/ESP (shared TX/RX commands + glean RX flow) | `references/ipsec.md` | Silicon One | IPsec reference: shared SUP/S1HAL RCA ladder for TX/RX plus ESP/glean RX punt flow ASIC -> psinb -> lcnd_sone_inband_decap -> process_ipsec -> get_netdev. |
| FLOW-002 | (infra) inject/TX | `references/sone-encap-tx.md` | Silicon One | STUB: lcnd_xmit -> lcnd_plat_encap (l2xa_cb) -> lcnd_sone_encap_fill_plat_hdr -> dev_queue_xmit ps-inb. (KSTACK-015; header math TBD.) |
| FLOW-003 | VXLAN decap (RX) | `references/vxlan-decap-sone-rx.md` | Silicon One | STUB: SONE VXLAN decap branch in lcnd_sone_inband_decap (lcnd_resolve_vxlan_gid, MPLS sibling). (To trace.) |
| FLOW-004 | (infra) psdev/ps-inb driver init + RX-handler registration | `references/psdev-init.md` | Silicon One (Krypton DPU-TOR) | klm_psdev bring-up: init_module -> create ps-eobc/ps-inb(/ps-svc-inb) -> register_psinb_rx_handlers -> sone_register_pltfm_rx_handlers (leaba0_0+pie-eth0) -> sone_netdev_notifier (benign pie-eth0 double-reg; deferred leaba0_0). (KSTACK-019.) |
| FLOW-005 | (control plane) KIM MTS notification map | `references/kim-mts-map.md` | Silicon One | Maps every `kim_notifs[]` MTS opcode to verified initiator(s) (cscope) -> KIM handler (`kim_process_*`/`kim_handle_*`) -> `LC_ND_*` ioctl push -> `lcnd_ioctl` case + LCND hash-table/field. Tier-1 (programs LCND/kernel) full Q1-Q4 incl. CBL (`SIOCSCBL`->`lcnd_ifindex_htab` vlan_bmp); Tier-2 brief. App A: LC_ND verb->table; App B: verified initiators (multi-sender flagged); App C: LCND htabs; App D: control-plane field -> RX/TX datapath consumer (`lcnd_sone_inband_decap` / `lcnd_sone_encap_fill_plat_hdr`); App E: netdev create/delete lifecycle (`SIOCDEVADDLC`/`SIOCDEVDELLC` -> `add_lc_net_device`/`del_lc_net_device`); App F: platform deltas (verb programming is common; `lcnd_plat_decap`/`lcnd_encap_fill_plat_hdr` dispatch + SI/Fretta/Triton/SONE exceptions). (KSTACK-002.) KIM-side producer design: `architecture/kim-process-architecture.md`. |
| FLOW-006 | (hardware identity) Silicon One card codename/model/ASIC map | `references/hw-codenames-sone.md` (+ full-page cache `references/hw-codenames-confluence-cache.md`) | Silicon One | KSTACK-relevant SONE subset of the Confluence "Hardware codenames" page: codename -> model(PID) -> ASIC family (Krypton/Graphene/Graphene2/G200_X/Palladium2/Gibraltar/Argon/Iron) + how to grab identity from a live switch, parallelized via handoff subagents (METHOD-016) and confirm via `SW_CARD_ID_IS_WITH_SONE_FAMILY_ASIC` (KSTACK-028). Full page cached locally (refresh on access; fallback if access lost). Cisco Highly Confidential. |
| FLOW-007 | (infra) inband punt RX datapath (SONE) | `references/psinb-rx-sone.md` | Silicon One | SONE ps-inb RX: ASIC handler `ps_sone0_rx_handle_frame` redirects skb->dev to ps-inb/ps-svc-inb (eth restore, vlan clear, `skb->protocol` via klm_vdc's `skb_protocol_get_inb`), `netif_receive_skb` -> `psinb_rx_handle_frame` (mbit short-circuit; resolve+call external `rni_handle_platform`; PASS/CONSUMED/ANOTHER) -> `rni_handle_platform` [klm_rni_lcnd] -> handle_platform [klm_lcnd]. RX twin of FLOW-004. (KSTACK-029/030/031.) |
| FLOW-008 | (infra) VDC RX queue-ethertype classification | `references/vdc-rx-classification-sone.md` | Silicon One | klm_vdc RX: `skb_protocol_get_inb`==`eth_type_trans_inb` -> `eth_type_trans_with_port_type` -> `si_vdc_eth_type_trans` -> `sone_si_vdc_eth_type_trans` -> `src_index`(`source_sp`) lookup in `si_vdc_map_table` -> `klm_vdc_char_get_q_eth_type` -> `0xf10x` (else fall back to real `eth_type_trans`). Sub-flow of FLOW-007 step 2.5. (KSTACK-014/033/034/035.) |
| FLOW-009 | (infra) VDC ioctl WRITER chains | `references/vdc-ioctl-writers.md` | platform-common (SONE default) | klm_vdc WRITE path: who issues each `VDC_IOC_*` and when. INBAND SI/LTL + IPS ifindex maps <- IM/PCM/MCEC/MCM (intf/module lifecycle); MGMT ip/entry/mcast <- IP/IGMP + IM mgmt-FSM (mgmt0); LLDP `0x88cc` <- LLDP via `dlopen`/`dlsym`; `CPUQ_COSQ` <- coppmgr + per-ASIC aclqos (direct ioctl, name-collides libvdcklm); q-remap/clear/timestamp/GDB <- PM CLI; bcast <- PnP/POAP; diag-vlan <- GOLD; `SET_DBG` test-tool-only; `ipconf_stub` mgmt path is `#if 0` DEAD. Writer twin of FLOW-008. (KSTACK-034; METHOD-014 cscope -3 under-report caveat.) |
| FLOW-011 | (control plane) KIM process spine (own-state writers + MTS spine + coarse-SONE PID) | `references/kim-process-arch.md` | Silicon One | Process-side companion to FLOW-005's notification->LCND map: the ordered spine of KIM's OWN state (intf/vlan AVL in `g_kim_cfg` + coupled PSS journal, LPSS lnx<->nxos maps, `ns_name_hash` nsid table, 7 PSS files), the MTS spine (3-queue bind, `kim_notifs[]` + fretta `eth_pcm` register, `kim_notifs_get` dispatch, 3-thread loop, standby-drop, senders DOWNLOAD_ADJ/_ROUTE + STATEFUL_RSTRT/L3_STATEFUL_RSTRT), and coarse-SONE PID handling (`sone`/`sone_gr2`/`sup_sone_virt`; `kim_tor.c` `#if 0` dead; LC_ONLINE/OFFLINE = SONE-only mirror/recycle-GID LCND writers). Thin flow index; deep design + ADRs in `architecture/kim-process-architecture.md`. (KSTACK-038..042.) |
| FLOW-010 | (operational) monthly incremental PR sweep | `references/monthly-pr-sweep.md` | platform-independent | Monthly incremental PR-sweep operational ladder: per-component watermark in `_sweep_state.json` -> SHA-range delta (`git log <last_sha>..origin/nx_main -- <path>`, `--since` fallback) -> subject-CSCID extract + dedup by existing `<CSCID>.md` -> enrich (GHE+CDETS) -> Summary row + `_kb_verification.md` -> verify-before-advance. Local-cron only (GHE/CDETS MCPs user-local; clone workstation-only); KB writes stay human-gated. Optional Confluence publish stage mirrors mapped components (`tools/confluence_publish.py`; TOC + full-width; page-level wide width via the Cloud v2 `content-appearance-published=full-width` page-property route since the MCP can't set it; creds from `~/.config/kstack/confluence.env`, token never persisted). (METHOD-017.) |
| FLOW-012 | (control plane) KFIB kernel->URIB route sync | `references/kfib-route-sync.md` | platform-agnostic userspace (SONE default) | KvFIB daemon `kfib.bin`: ONLY live path is kernel netlink -> URIB. `kfib_nl_kernel_read` (select/recvmsg over per-netns NETLINK_ROUTE socks) -> `kfib_nl_info_fetch` -> `kfib_nl_route_change` (RTM_NEWROUTE/DELROUTE, RTN_UNICAST, RT_TABLE_MAIN, skip CLONED/REDIRECT/BIRD/src_len/SCOPE_LINK, AF_INET) -> `kfib_urib_add/del_one_route` (lnx->nxos ifindex via KIM LPSS `volatile:kim_nxos_if_handle_db`; IOD via `im_get_iod_frm_ifindex`; nh_flags from scope) -> `urib_add_one_route`/`urib_delete_one_route` build URIB_MTYPE_ADD/DELETE_ONE_ROUTE, fire-and-forget `urib_send_to(MTS_SAP_URIB)`. KIM-ns sub-flow (`kfib_process_kim_update`->`kfib_nl_ns_add` setns/CLONE_NEWNET per-VRF socket) has NO in-tree opcode sender (unverified/dormant). Reverse+notify paths `#if 0` dead (KSTACK-047..051). |
| FLOW-013 | (control plane) Netbroker RTNL trap -> nbproxy | `references/netbroker-rtnl-trap.md` | platform-agnostic (NXOS userspace + kernel 6.6 hooks) | Third-party RTNL/ioctl/socket admin is intercepted in kernel (`netbroker_rtnl_doit` -> `cisco_nb_rtnl_doit`); NXOS whitelist (`ipfib`/`kim`/`netstack:`/…) bypasses; else nbproxy `cfg_cb` updates urib/netstack/vsh and acks via genl. `LIBNB_CFG_OK` may replay RTNL on broker rtnl_sk; `LIBNB_CFG_OK_PROCESSED` leaves kernel programming to whitelisted NXOS daemons. Complements FLOW-012 (KFIB observes kernel after the fact). Design + ADRs: `architecture/netbroker-architecture.md`. (KSTACK-054.) |

_To add a flow: create `references/<protocol>-<direction>.md`, a protocol-level
`references/<protocol>.md` when TX/RX data is shared, or append to
`references/catch-all.md`; give it `FLOW-NNN`, list ordered steps (function ->
function, key `file:line`, field transformations), then add a row above._

## Architecture docs (`architecture/`)

Deeper, code-grounded architecture write-ups (module-level design + ADRs). Open by
file; anchor on names/macros, not line numbers.

| Doc | Scope | One-liner |
|-----|-------|-----------|
| `architecture/psinb-driver-architecture.md` | `klm_psdev` / `ps-inb` (SONE datapath) + `mgmt_dev` (all platforms) | Pseudo-netdev punt/inject driver: lifecycle, RX (§6, FLOW-007) + mgmt punt (§7) + TX (§8, KSTACK-020) datapaths, `parent_dev` coupling (§9, KSTACK-032), external boundaries, and ADR-001..010 (incl. ADR-010: SONE ISSU/LXC swover `psdev_swover_sone` is a no-op in current code; older releases differ). Two builds: Bazel `BUILD` (current) + gmake `module.mk` (legacy). |
| `architecture/klm-vdc-driver-architecture.md` | `klm_vdc` (`/dev/klm_vdc`, VDC queue/ethertype classifier; SONE inband focus) | VDC classifier KLM: `/dev/klm_vdc` ioctl WRITE surface (§6) programming 3 `port_type`-keyed maps (si/ip/ifindex) + mgmt-vdc/mcast/qmap/stats; who programs them (§7, libvdcklm->ioctl->`vdc_chr_ioctl`->`vdc_table_entry_add`; verified out-of-dir programmers IM/PCM/MCEC/MCM/IP/IGMP/coppmgr/aclqos/PM/PnP/POAP/LLDP-dlsym/GOLD, FLOW-009); READ path `skb_protocol_get_inb`->`eth_type_trans_inb`->`si_vdc_eth_type_trans` dispatch (§7.4) with deep SONE `sone_si_vdc_eth_type_trans` (§7.5: trap/FPT/BFD/BPDU, `source_sp` lookup, per-PID TTL/COS/forced-vdc fix-ups, Krypton/GR2/P200/GB/G2LL). Emits `0xf1xx`/`0xfcfc` (KSTACK-014). fn-ptrs owned by psdev, set by VDC (KSTACK-031). ADR-001..008 (incl. ADR-004 lock-free torn-read risk, ADR-005 SONE card-allowlist drift, ADR-008 e1000 hardcoded enum). Builds: Bazel/gmake/Kbuild. |
| `architecture/kfib-library-architecture.md` | KVFIB / KFIB (`kfib.bin`, userspace sysmgr daemon, `standalone/infra/kstack/kfib/`; platform-agnostic) | Kernel-FIB route importer: syncs Linux-kernel routes -> NX-OS URIB. 4 threads (`kfib_process_heart_msg`/`kfib_process_my_msg`/`kfib_nl_kernel_read` + heartbeat timer); per-VRF NETLINK_ROUTE sockets (`RTMGRP_LINK\|IPV4_ROUTE\|IPV4_IFADDR`, `setns(CLONE_NEWNET)` netns hop) driven by KIM `MTS_OPC_KIM_NS_OPERATION` (create/delete). LIVE datapath = kernel->URIB only: `kfib_nl_kernel_read`->`kfib_nl_route_change` (filters: UNICAST/!CLONED/!REDIRECT/!RTPROT_BIRD-anti-loop/table==MAIN/!SCOPE_LINK)->`kfib_urib_add/del_one_route`->`urib_*`; ifindex xlate lnx->nxos via KIM LPSS `kim_nxos_if_handle_db` + IOD via `im_get_iod_frm_ifindex`; VRF->table via `l3vm_context_get_table_id`. Reverse URIB->kernel (`kfib_nl_fill_route`), URIB-notify handlers, and DO_IT_LATER standby-sync are all `#if 0` dead; CLI VXLAN/NVGRE help is dead boilerplate. ADR-001..008 (incl. ADR-002 RTPROT_BIRD anti-loop, ADR-003 registered-but-silent URIB client, ADR-007 `0x1a101400` hardcoded ifindex fallback, ADR-008 lock-free `nl_sock_list` torn-walk). LIVE = kernel->URIB only; per-VRF socket sub-flow driven by `MTS_OPC_KIM_NS_OPERATION` is **dormant** (no in-tree sender indexed, `unverified`). (FLOW-012; KSTACK-047..051.) |
| `architecture/kim-process-architecture.md` | KIM (`kim.bin`, userspace sysmgr daemon, `standalone/infra/kstack/kim/`; SONE-focused PID matrix) | Interface-state compiler daemon: `main()` state machine + 3-pthread active loop (`kim_process_heart_msg`/`kim_process_my_msg`/`kim_nb_thread_main`) vs single-thread PSS-synced standby (§3); owns `g_kim_cfg` twin AVL trees (`kim_intf_tree_root`=`lc_if_info_avl_t` by ifindex, `kim_vlan_tree_root`) + `ns_name_hash` + LPSS + 7 PSS records (§4); MTS bind/register/dispatch (`smq`/`kimq`/`stats_q`, `kim_notifs[]`~40 opcodes + mcecm always + eth_pcm on Fretta, `kim_notifs_get`->handler->`kim_msg_relay`, §5) with sender catalog (`kim_send_msg_to_ipfib`=`KIM_DOWNLOAD_ADJ`, §5.2); who-programs deep chain (handler->`kim_create_if`->`kim_intf_add` AVL + `SIOCDEVADDLC`/`MODLC`/`DELLC`+`SIOCSIFMTU/FLAGS`->LCND + PSS journal, §6, LCND side=FLOW-005); pseudo-netdev factory (§7); coarse PID gates (`is_fretta`/`libutils_is_card_sone()`/`_sone_gr2`=G200/`_innovium`/`SW_CARD_ID_IS_EOR_FM`/`container_id`) with deep-SONE recycle-port GID (`kim_process_recycle_ports`->`libpixm_sone_get_recycle_port_details`->`LC_ND_RCY_PORT_GID_SET`), mirror-GID, MCT rsvd-vlan `g_kim_vxlan_mct_rsvd_vlan` (§8); `kim_tor.c` is dead `#if 0` (ADR-007). ADR-001..008. |
| `architecture/netbroker-architecture.md` | Netbroker (`klm_cisco_nb` + `nbproxy` + `libnetbroker`; kernel patches + `standalone/infra/kstack/netbroker/`) | Admin-path gate: kernel RTNL/ioctl/socket hooks trap third-party Linux admin -> genl -> nbproxy `cfg_cb` per `NB_GRP_*`; NXOS whitelist bypass for ipfib/kim/netstack; completion via `LIBNB_CFG_OK` (kernel replay) vs `LIBNB_CFG_OK_PROCESSED`. Usages table (§8), observability (perf `cisco_nb_traces:*`, nbproxy event-history), boundaries vs KFIB/KIM/LCND. ADR-001..008. Deep flow: FLOW-013; E2E: METHOD-020/021 (KSTACK-054/055). |

---

## Switch Commands

Saved switch commands + what they yield. **Full list in `knowledge/switch-commands.md`**
-- open it when gathering switch data. All `impact: read-only` unless noted;
S1HAL/IPSec output may contain secrets (redact). Prefer Nexus MCP; `sshpass -e`
fallback (METHOD-008). New commands: append to `knowledge/switch-commands.md`. Topics:

- Switch access template (Nexus MCP / `sshpass -e`) + NX-OS identity (`show hostname` / `show version`)
- KIM internal event-history: `show kim internal event-history errors|intf|msgs|mts` (METHOD-008)
- KIM programming verification: `show kim inconsistency` (native all-intf walk, KSTACK-046) vs public `show consistency-checker kim {interface}` (cochk Python, KSTACK-058) + `show kim internal {info,issu-stats,mem-stats}` (FLOW-005 App G)
- Module collection: `slot <n> quoted "<cmd>" | no-more` (Type 2, preferred) / `at mod <n>` (Type 1) (METHOD-009)
- IPSec SUP control-plane ladder + S1HAL hardware ladder (sensitive) (METHOD-010)
- LCND decap/encap trace toggles (`lcnd_pkt_decap_debug` / `_encap_debug`, `lcnd_debug.c` proc files)
- `show system internal lcnd hash-tables` -> `/proc/lcnd/lcnd_hash_tables` (REQUIRED for branch analysis; METHOD-012, KSTACK-018)
- Card/ASIC identity: `show module` / `show version` / `show inventory` / `show sprom module <m> <i> | include 'Mfg Bits'` -> map PID/codename to ASIC family (FLOW-006, METHOD-016, KSTACK-028)
- LACP peer timeline: `show lacp internal info all` + interface/port-channel syslog filters; distinguish direct FSM events and snapshot counters from timer-derived last-refresh boundaries
- Netbroker registration + hook state: `/proc/net/cisco_nb_0` (or `cisco_nb_1` on container 1), `/sys/module/klm_cisco_nb/parameters/disable_rtnl_hook`, `block_rib`, `block_interface` (FLOW-013, KSTACK-054)
- UDLD: `feature udld` + interface `udld aggressive`; verify with `show udld neighbors` (NX-OS 10.7 — no `show udld interface`)

---

## Debugging Tools

Tools and scripts available for KSTACK debugging. Add tools the user introduces.

- **nxos-cscope** (skill, PRIMARY navigation) -- symbol/caller/callee navigation on
  the NXOS tree. Use this, NOT root `rg`/`grep`/`find` (multi-GB NFS -> root searches
  time out + flood context). Recipe:
  `/router/bin/cscope-64 -d -L -1|-0|-2|-3 "<sym>" -f standalone/cscope.out`
  (`-1` def, `-0` all refs incl. fn-ptr/static, `-2` callees, `-3` callers); anchor on
  names not lines; pair with parallel `explore` subagents for breadth (METHOD-014).
  Locates per-platform functions and where `lc_vlan`/`lc_if_info` is programmed by the
  control plane.
- **`scripts/`** (this skill) -- python helpers for data fetch/parse when MCP is
  unavailable. (No scripts yet; e.g. an `lc_flags` decoder per METHOD-003.)
- **Nexus MCP / `sshpass` for NX-OS access** -- prefer Nexus MCP
  `nexus_connect` -> `nexus_execute_command(s)` -> `nexus_disconnect` when
  available. Use `sshpass -e` with `SSHPASS` set for the single command, plus
  `ssh -F /dev/null`, when direct switch SSH is needed from this workspace
  (METHOD-008). Keep credentials out of saved files.
- **Module-level NX-OS collection** -- prefer `slot <slot> quoted "<module command>"
  | no-more` for repeatable non-interactive collection over SSH; use `at mod
  <slot>` only when an interactive module shell is needed (METHOD-009). Treat
  S1HAL IPSec output as sensitive because it can include keys and handles.
- **IPSec RCA command ladder** -- use the SUP control-plane commands plus
  preferred Type 2 S1HAL commands in METHOD-010 to correlate Tunnel interface,
  endpoint handle, SPIs, S1HAL tunnel ID/GID, security engine placement, and
  counters before concluding root cause.
- **In-repo kernel source** -- `standalone/third-party/src/kernel/nx-linux/linux-6.6/`
  is the authoritative kernel-6.6 source for skb/net helper bodies; locate with
  Glob, not root grep (METHOD-005, KSTACK-008).
- **Subagents for context control** -- if the runtime supports subagents, dispatch
  scoped explorers/workers for broad independent KSTACK tasks: code-path search,
  reference-link audits, switch-output summarization/redaction, or separate TX vs
  RX flow tracing. For parallel LIVE switch data collection use **non-readonly**
  subagents driven by `handoff` dispatch-mode prompts (read-only command scope, own
  creds, fresh `mktemp` known_hosts, return raw output only; METHOD-016 step 0,
  SKILL rule 12). Keep final synthesis and knowledge writes in the primary
  agent; subagents reduce context load but do not relax evidence or redaction
  rules. If unavailable, fall back to scoped Glob/Grep/Read (METHOD-005).
- **Hardware-codenames Confluence cache** -- `references/hw-codenames-confluence-cache.md`
  is a verbatim local snapshot (Cisco Highly Confidential) of the "Hardware codenames"
  page (pageId 561414869) for offline/loss-of-access fallback. REFRESH it on every
  successful live fetch (bump `page_version`/`cached_at`); on access loss, use it and
  cite its version/date (METHOD-016, FLOW-006).
- **KLM_VDC source (pointer)** -- `standalone/platform/storage/sup/kspace/vdc/
  klm_vdc_char.c` for VDC queue ethertype mapping (`0xf102/f103/f104/fcfc`,
  KSTACK-014). UNVERIFIED -- read before citing specifics.
- **`/proc/lcnd` trace knobs** -- see `## Switch Commands` for decap/encap trace
  toggles (`lcnd_debug.c`).
- **`show system internal lcnd hash-tables` (best-effort; image-gated)** -- dumps
  LCND's runtime hash tables (LIF/ifindex/PI/VP/MPLS/mirror-GID/vlan-GID/vlan-BD/NVE/
  VNI/VRF) via the seq_file proc file `/proc/lcnd/lcnd_hash_tables` (replaces the old
  `lcnd_table_dump=1` dmesg dump). **NOT present on all builds** -- verified absent on
  10.7(1) IMG9 (CLI invalid; proc file missing); probe `run bash ls /proc/lcnd/` first
  and fall back to `show kim internal info` (KIM-side mirror). When present, pair it
  with the SiliconOne PID/trap info
  (`la_event.h`) for almost every decap/inject branch question -- the packet alone
  can't reveal which hash-table lookup branch fired (METHOD-012, KSTACK-018,
  Switch Commands entry).
- **SiliconOne PID + `la_event.h` + `scripts/trap_code.py`** -- map a trap code /
  punt source / `fwd_header_type` to its `la_event_e` name for a specific PID.
  Header path template:
  `standalone/third-party/src/siliconone-sdk/<sdk-dir>/include/api/types/la_event.h`.
  PID -> sdk-dir: **G200=gr2, Krypton=krypton, P200=palladium2, G2LL=g2ll**.
  Decode with `scripts/trap_code.py --pid g200 --code 4` (prints a name such as
  `ETHERNET_ARP`). Flags: `--all` lists every alias at that value; passing a name to
  `--code` does a reverse name->value lookup; `--header <path>` bypasses PID/repo
  resolution; repo is auto-detected from CWD (or pass `--repo` / set `$KSTACK_REPO`).
  When a punt header shows `punt_source = PUNT_SOURCE_INGRESS_TRAP` (or any trap
  source), decode its `trap_code` with this script **for reference**. Needed
  alongside the dump_table to ground branch analysis. IMPORTANT: the numeric
  code->name mapping is **PID/build specific** (the same code resolves to different
  names across PIDs) -- do NOT store decoded values here; record only this usage.
- **`scripts/group_by_packet.py`** -- group a `perf script` dump of `lcnd_traces:*`
  into one block per packet (per-CPU entry->terminal state machine; METHOD-015 /
  KSTACK-024). **Capture (METHOD-021 timed pattern):**
  ```text
  run bash sudo sh -c "rm -f /bootflash/lcnd.perf /bootflash/lcnd_traces.txt; \
    timeout <DUR> perf record -a -e 'lcnd_traces:*' -o /bootflash/lcnd.perf -- sleep <DUR>; \
    perf script -i /bootflash/lcnd.perf > /bootflash/lcnd_traces.txt 2>&1"
  ```
  Pull with `run bash sudo cat /bootflash/lcnd_traces.txt` or SSH redirect (see
  METHOD-021). **`<DUR>` = capture seconds; ASK the user, DEFAULT 10.** Then
  `scripts/group_by_packet.py /tmp/lcnd_traces_fresh.log` (or the bootflash copy).
  `-q/--query k=v` filters (mandatory `dir`=in|out|mgmt; keys fold aliases, hex==dec, MAC
  colon==dotted); `--list-params` lists all keys grouped by direction. Output is
  written beside the INPUT as `<input>.grouped.log` (or `<input>.<dir>.grouped.log`
  under a query). **No partial match**: if the exact AND-query returns 0, the packet
  was not seen -- report that; never dump a subset-match block as if relevant.
  Grouping is stable on event NAMES; sample skb/if values are volatile -- reference
  only, never stored here.

---

## Entries

Verified facts / corrections. **Full bodies in `knowledge/entries.md`** -- open it for
the id you need; re-derive this session's inference, reuse only the recorded fact's
method. Dedup/next-ID greps MUST include `knowledge/entries.md`.

| ID | Fact | Scope | Status |
|----|------|-------|--------|
| KSTACK-001 | SONE inband decap overwrites relay_id-derived vlan with interface lc_vlan | `lcnd_sone_inband_decap` | verified |
| KSTACK-002 | lc_vlan is programmed by KIM; decap just copies it | lc_vlan KIM->decap | verified |
| KSTACK-003 | Do not cross-cite decap functions across platforms | methodology | verified |
| KSTACK-004 | LC_FLAGS bit reference + observed interface flag decodes | `lc_if_info.lc_flags` | verified |
| KSTACK-005 | Default platform is Silicon One | platform context | verified (user-stated) |
| KSTACK-006 | NULL deref in lcnd_sone_get_netdev glean path | `lcnd_sone_get_netdev` | verified (fixed) |
| KSTACK-007 | skb_vlan_pop is a no-op on reconstructed punt skbs | `lcnd_sone_get_netdev` | verified (fixed) |
| KSTACK-008 | Kernel 6.6 VLAN helper semantics + source locations | linux-6.6 | verified |
| KSTACK-009 | Reading ethertype/protocol byte order in LCND traces | trace, endianness | verified |
| KSTACK-010 | IPsec/glean outer-IP strip malforms ESP packets | `lcnd_sone_process_ipsec` | verified (OPEN) |
| KSTACK-011 | process_ipsec pulls 8 junk bytes before get_netdev | `lcnd_sone_process_ipsec` | verified |
| KSTACK-012 | Post-decap RX delivery: eth_type_trans -> flo_mgr -> clone/kim-data | SONE RX handoff | verified |
| KSTACK-013 | Inband interface name map (ps-inb / ps-svc-inb / kim-data / ps-sup-eth1) | inband netdevs | verified |
| KSTACK-014 | NX-internal VDC punt ethertypes = VDC_ETHTYPE_BASE+queue offset (klm_vdc) | punt ethertype / klm_vdc | verified |
| KSTACK-015 | TX/inject (encap) chain and l2xa_cb | SONE inject | verified |
| KSTACK-016 | kim-data RX frame layout = topEth(14)+mdata(48)+headroom+pkt@offset | `lcnd_insert_metadata_hdroom` | verified |
| KSTACK-017 | SONE dummy-eth-header sites (DPU + egress-trap); fingerprint | `lcnd_sone_inband_decap` | verified |
| KSTACK-018 | EGRESS_TRAP decap takes 1 of 3 source_lp sub-branches before dummy-eth | `lcnd_sone_inband_decap` | verified |
| KSTACK-019 | klm_psdev init on Krypton DPU-TOR (+benign pie-eth0 double-register) | `klm_psdev` init | verified |
| KSTACK-020 | psdev pseudo-dev TX forwards to parent via dev_queue_xmit | `psdev_start_xmit` | verified |
| KSTACK-021 | CSCwv05793 KIM SAT fabric PC state-change parser crash path | KIM MTS handler | verified |
| KSTACK-022 | IPsec sec_sys_gid table is card-id scoped for Krypton cards | `is_sec_sys_gid()` | verified |
| KSTACK-023 | Card ID and card index header locations | card identity | verified |
| KSTACK-024 | LCND perf trace chain order per punted packet (RX decap) | lcnd_trace.h + decap order | verified |
| KSTACK-025 | LCND generic hash tables = RCU readers + spin_lock_bh writers (in-place update torn-read hazard) | `lcnd_hash_gen.c` locking | verified |
| KSTACK-026 | Per-device hash tables in struct lc_device: real vs vestigial, layouts, lazy-alloc/free-when-empty | `struct lc_device` | verified |
| KSTACK-027 | Hash entry layout [key][value] contiguous; print cb gets entry->data; get_count has no NULL guard | `lcnd_hash_gen.c` | verified |
| KSTACK-028 | Identify N9K Silicon One ASIC family (`SW_CARD_ID_IS_WITH_SONE_FAMILY_ASIC`) and TOR (`SW_CARD_ID_IS_TOR`) via SW_CARD_ID macros | sw_card_id classification | verified |
| KSTACK-029 | psinb_rx_handle_frame is the Kstack RX entry + external rni handoff (mbit/kallsyms/PASS-CONSUMED-ANOTHER) | `psinb_rx_handle_frame` | verified |
| KSTACK-030 | ps_sone0_rx_handle_frame redirects ASIC skb to ps-inb/ps-svc-inb + normalizes (eth/vlan/protocol) | `ps_sone0_rx_handle_frame` | verified |
| KSTACK-031 | skb_protocol_get_inb/_mgmt are klm_psdev fn-ptrs SET by klm_vdc (eth_type_trans_inb) | skb_protocol_get_inb fn-ptr ownership | verified |
| KSTACK-032 | SONE ASIC netdev(s) carrying ps_sone0_rx_handle_frame per card index (leaba0_0/pie-eth0/leaba12_0/leaba11_5/leaba11_0; !vmachine + DPU + allowlist caveats) | `sone_register_pltfm_rx_handlers` / `is_sone0_dev` | verified |
| KSTACK-033 | klm_vdc = /dev/klm_vdc char driver + 5 VDC lookup tables (si/ifindex/ip/mgmt/mcast) | klm_vdc module/char dev | verified |
| KSTACK-034 | klm_vdc ioctl writers (full, FLOW-009): INBAND/IPS maps<-IM/PCM/MCEC/MCM; mgmt ip/entry/mcast<-IP/IGMP+IM; LLDP<-dlsym; CPUQ_COSQ<-coppmgr/aclqos; CLI<-PM; bcast<-PnP/POAP | klm_vdc ioctl / control plane | verified |
| KSTACK-035 | si_vdc_eth_type_trans dispatches per ASIC family; SONE arm keys on source_sp + egress-trap/RCY vdc=1 | si_vdc_eth_type_trans / SONE | verified |
| KSTACK-036 | klm_psdev cleanup force-zeros ins_ps_inb pcpu_refcnt (CSCwn95874) — symptom fix; leaked-ref holder + UAF open | `cleanup_module` teardown | verified |
| KSTACK-037 | klm_vdc VDC_IOC_CTRL_Q_MAP bounds-checks ctrl_q_type (CSCwu19801, OOB kernel write) | `vdc_chr_ioctl` | verified |
| KSTACK-038 | KIM intf/vlan AVL DBs live in g_kim_cfg; every DB insert/delete also journals PSS in the same fn | `kim_db.c` DB writers | verified |
| KSTACK-039 | KIM LPSS = two lnx<->nxos ifindex maps (bidir add/del); ISSU destroy+recreate; 0xdeadbeef magic key | `kim_lpss.c` | verified |
| KSTACK-040 | KIM MTS spine: 3-queue bind, kim_notifs[] register (+mcecm, +fretta eth_pcm), kim_notifs_get dispatch, 3-thread loop, standby drops MTS | `kim_mts.c` | verified |
| KSTACK-041 | KIM-as-sender opcodes: DOWNLOAD_ADJ/_ROUTE (ipfib) + STATEFUL_RSTRT/L3_STATEFUL_RSTRT (pktmgr/netstack, ISSU) | `kim_mts.c`/`kim.c` senders | verified |
| KSTACK-042 | KIM PID handling is coarse-SONE (sone/sone_gr2/sup_sone_virt); kim_tor.c is #if 0 dead; LC_ONLINE/OFFLINE program LCND mirror/recycle-GID on SONE only | KIM platform branches | verified |
| KSTACK-043 | KIM seeds per-netns default sysctls (rp_filter, ignore_routes_with_linkdown) + ip6tables MLD-drop (icmpv6 130/131/132/143) at bring-up | `kim_set_default_sysctl` (`lib/kim_intf.c`) | verified |
| KSTACK-044 | KIM shares 4 kernel bridges/VXLAN netdevs (br-0..3 / vx0..3) across VRFs keyed by table_id % 4; VNI id = (table_id%4)+1 | `kim_vxlan_intf_kernel_create`/`_vrf_move` | verified |
| KSTACK-045 | KIM nsid = kernel auto-alloc (kim_get_nsid returns -1); non-default-VRF ioctl must use VRF-ns socket kim_get_ns_sock; ns_name is fixed-width hash key | `kim_msg_handler.c` netns/nsid | verified |
| KSTACK-046 | Native KIM-CC (`kim_inconsistent_interfaces`): veth excluded from MTU/MAC; PASSED syslog; `kim.cmd` duplicate of `show consistency-checker kim` | `kim_debug.c` + `kim.cmd` | verified |
| KSTACK-047 | KFIB live direction is kernel->URIB only; reverse/notify paths #if 0 dead; urib_notify_request #if 0 => no URIB notifications | KFIB direction | verified |
| KSTACK-048 | KFIB netlink socket + netns kernel-programming sequence (kfib_nl_create_sock; setns CLONE_NEWNET per VRF; select/recvmsg; route_change filters) | `kfib_netlink.c` | verified |
| KSTACK-049 | KFIB lnx->nxos ifindex via KIM LPSS db + IOD via IM + nh_flags from scope; urib_add/delete_one_route fire MTS to MTS_SAP_URIB | `kfib_urib.c` | verified |
| KSTACK-050 | KFIB MTS spine (2 SAPs: KFIB_SYSMGR + KFIB=234) + 4-thread model; only KIM_NS_OPERATION live; no in-tree sender of that opcode (dormant) | KFIB MTS/threads | verified (sender unverified) |
| KSTACK-051 | kfib.conf sysmgr identity: run=conditional, mts=aware, deps KIM/URIB/L3VM (scope control), standby_mode=sync, heartbeat 8s | `kfib.conf` | verified |
| KSTACK-052 | KIM-CC MTU triad (Linux SIOCGIFMTU vs im_get_if_mtu vs lc_mtu) + kim_set_ifmtu single-writer; `Linux=1500 + kim db=0` == MTU setter never ran; breakout ports miss IM_MSG_TLV_MTU at boot | `kim_debug.c`/`kim_mts.c`/`kim_msg_handler.c` | verified |
| KSTACK-053 | CSCwv32090: LCND FDB/MPLS/VLAN-GID raw-netlink mutations require CAP_NET_ADMIN, complete payloads, and bounded MPLS adjacency iteration; KvFIB advertises payload-only nlmsg length | LCND private netlink + KvFIB sender | verified |
| KSTACK-054 | Netbroker traps third-party RTNL/ioctl/socket admin; NXOS whitelist + nbproxy are source of truth | netbroker / klm_cisco_nb / nbproxy | verified (E2E METHOD-020) |
| KSTACK-055 | Sup LXC: plain dmesg empty; use `dmesg -F /dev/kmsg`; printk console_loglevel tune; netbroker hot path tracepoints | netbroker observability / run bash | verified |
| KSTACK-056 | NX-OS 10.7 s1-dpu (SONE) kernel: NO writable eBPF hook (NET_SCH_INGRESS unset, XDP generic+native no-op, no classful qdisc); kprobe/BPF_EVENTS + BPF load work; klm_vdc→eBPF needs kernel config change | ebpf / klm_vdc / xdp / tc / kprobe | verified |
| KSTACK-057 | `lcnd_init_module()` can leave `kim-data` wired to a stale copied `ndo_start_xmit` target when netdev registration succeeds but later mgmt-dev lookup makes init fail; later MLD TX faults on indirect fetch | kim-data / failed init / stale xmit pointer | verified |
| KSTACK-058 | Public `show consistency-checker kim {interface} [brief|detail]` is cochk `pm_cli_show_cc_kim` -> `cc_kim.py:kimConsistencyInterface` (single-ifindex, parses KIM show text) | `cochk.c` + `cc_kim.py` | verified |
| KSTACK-059 | LIF-hit IPsec outer-IP slide ignores a customer 802.1Q tag; the dot1q reader then reports the outer IPv4 destination prefix as the VLAN | `lcnd_sone_process_ipsec` non-ESP strip | verified |

_Entries are ordered by id here; bodies in `knowledge/entries.md` keep discovery order._
