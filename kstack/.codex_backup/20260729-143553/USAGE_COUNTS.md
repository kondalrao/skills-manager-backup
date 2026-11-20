# KSTACK Usage Counts

Tracks actual reuse of `METHOD-*`, `KSTACK-*`, and `FLOW-*`/reference records
from `KNOWLEDGE.md` and `references/`.

Baseline starts on 2026-06-23, when this sidecar was introduced. Do not backfill
older usage unless there is explicit evidence for a specific ID use. Do not
increment for merely reading, grepping, deduping, or checking ID collisions.

## Update Rules

- Increment an ID only when it materially influences the answer, command/data
  request, code-path reasoning, or a knowledge update.
- Count each ID at most once per assistant turn unless the same ID supports a
  distinct independent conclusion.
- Update `Last Used` with the date of the turn and keep `Last Context` to one
  short phrase.
- When adding a new `METHOD-*`, `KSTACK-*`, or `FLOW-*` entry to `KNOWLEDGE.md`,
  add a matching row here with count `0`.
- Count a `FLOW-*` when its `## References` index row or mapped
  `references/*.md` file materially influences the turn; keep the `Reference`
  column aligned to the current index row.
- If this file cannot be written, report `Would update KSTACK usage counts:
  <ids>` in the response.

## Methods

| ID | Count | Last Used | Last Context |
|----|------:|-----------|--------------|
| METHOD-001 | 0 | - | - |
| METHOD-002 | 1 | 2026-06-24 | CSCwv05793 handler anchoring |
| METHOD-003 | 0 | - | - |
| METHOD-004 | 0 | - | - |
| METHOD-005 | 2 | 2026-07-11 | Scoped Grep over urib/ + infra/kstack (not root grep) to re-verify urib_api.c terminal hop + KIM_NS_OPERATION sender absence (KFIB walk) |
| METHOD-006 | 0 | - | - |
| METHOD-007 | 1 | 2026-06-24 | CSCwv05793 line-drift check |
| METHOD-008 | 10 | 2026-07-17 | Nexus MCP copy-to-running CSCwv49648 repro discriminator on 172.20.175.106 |
| METHOD-009 | 0 | - | - |
| METHOD-010 | 0 | - | - |
| METHOD-011 | 0 | - | - |
| METHOD-012 | 0 | - | - |
| METHOD-013 | 0 | - | - |
| METHOD-014 | 9 | 2026-07-17 | cscope/subagent-assisted CSCwv49648 source trace for KIM MTU checker and IF_CREATED authorization |
| METHOD-015 | 2 | 2026-06-30 | Validated/fixed encap grouping vs lcnd_traces_v2 |
| METHOD-016 | 0 | - | - |
| METHOD-017 | 0 | - | - |
| METHOD-018 | 0 | - | - |

## Entries

| ID | Count | Last Used | Last Context |
|----|------:|-----------|--------------|
| KSTACK-001 | 0 | - | - |
| KSTACK-002 | 3 | 2026-07-18 | lc_vlan KIM->LCND programming in control-plane sequence diagram |
| KSTACK-003 | 0 | - | - |
| KSTACK-004 | 0 | - | - |
| KSTACK-005 | 0 | - | - |
| KSTACK-006 | 0 | - | - |
| KSTACK-007 | 0 | - | - |
| KSTACK-008 | 0 | - | - |
| KSTACK-009 | 0 | - | - |
| KSTACK-010 | 0 | - | - |
| KSTACK-011 | 0 | - | - |
| KSTACK-012 | 1 | 2026-07-18 | Post-decap flo_mgr fork in RX workflow diagram |
| KSTACK-013 | 1 | 2026-07-08 | ps-inb/ps-svc-inb netdev names for RX/TX trace |
| KSTACK-014 | 2 | 2026-07-09 | Derived 0xf10x from VDC_ETHTYPE_BASE+queue offset (klm_vdc) |
| KSTACK-015 | 1 | 2026-07-18 | TX encap chain in inject workflow diagram |
| KSTACK-016 | 0 | - | - |
| KSTACK-017 | 0 | - | - |
| KSTACK-018 | 0 | - | - |
| KSTACK-019 | 1 | 2026-07-08 | registration context for FLOW-007 RX datapath |
| KSTACK-020 | 1 | 2026-07-08 | extended with psdev_munge_pkt TX detail |
| KSTACK-021 | 6 | 2026-07-17 | Reapplied CSCwv05804/CSCwv05793 sender gates with explicit per-handler SAP allowlists |
| KSTACK-022 | 2 | 2026-06-24 | Converted sec_sys_gid values to hex |
| KSTACK-023 | 1 | 2026-07-11 | Extended with KIM standby/S1 lc_sw_card_id derivation note (KIM P5) |
| KSTACK-024 | 2 | 2026-06-30 | Verified TX encap 9-event unit + mid-chain skb swap |
| KSTACK-025 | 0 | - | - |
| KSTACK-026 | 0 | - | - |
| KSTACK-027 | 0 | - | - |
| KSTACK-028 | 1 | 2026-07-11 | SW_CARD_ID SONE-family classification referenced for KIM coarse-PID granularity (KSTACK-042) |
| KSTACK-029 | 0 | - | - |
| KSTACK-030 | 1 | 2026-07-09 | RX call site of skb_protocol_get_inb (klm_vdc reader) |
| KSTACK-031 | 1 | 2026-07-09 | fn-ptr setter re-confirmed in vdc_module_init/exit |
| KSTACK-032 | 0 | - | - |
| KSTACK-033 | 0 | - | - |
| KSTACK-034 | 1 | 2026-07-09 | Corrected+expanded to full verified writer map (FLOW-009) |
| KSTACK-035 | 0 | - | - |
| KSTACK-036 | 0 | - | - |
| KSTACK-037 | 0 | - | - |
| KSTACK-038 | 1 | 2026-07-11 | Extended with PSS insert/delete key MAIN/SUB symmetry note (KIM P8) |
| KSTACK-039 | 1 | 2026-07-11 | KFIB reads KIM's `volatile:kim_nxos_if_handle_db` LPSS map via lpss_lookup -- consumer of the producer in KSTACK-039 (KSTACK-049) |
| KSTACK-040 | 0 | - | - |
| KSTACK-041 | 1 | 2026-07-11 | KIM-as-sender catalog corroborates KIM does NOT emit MTS_OPC_KIM_NS_OPERATION -> supports KFIB "no in-tree sender" finding (KSTACK-050) |
| KSTACK-042 | 0 | - | - |
| KSTACK-043 | 0 | - | - |
| KSTACK-044 | 0 | - | - |
| KSTACK-045 | 1 | 2026-07-11 | KIM per-VRF netns/NETNS_RUN_DIR model is the producer twin of KFIB's setns(CLONE_NEWNET) per-VRF socket sub-flow (KSTACK-048) |
| KSTACK-046 | 4 | 2026-07-17 | KIM-CC source trace for CSCwv49648 MTU mismatch messages |
| KSTACK-047 | 0 | - | - |
| KSTACK-048 | 0 | - | - |
| KSTACK-049 | 0 | - | - |
| KSTACK-050 | 0 | - | - |
| KSTACK-051 | 1 | 2026-07-11 | KVFIB apply: kfib.conf limit/heap + phy_mem family + KIM-dep lineage notes |
| KSTACK-052 | 6 | 2026-07-17 | CSCwv49648 source RCA: kim_set_ifmtu missing leaves Linux MTU default and kim db MTU 0 |
| KSTACK-053 | 1 | 2026-07-16 | Updated CSCwv32090 from source/build-only partial verification to full fixed-image runtime verification; linked METHOD-018 |
| KSTACK-054 | 1 | 2026-07-26 | Netbroker RTNL trap walkthrough + KB authoring (FLOW-013) |

## Flows / References

| ID | Reference | Count | Last Used | Last Context |
|----|-----------|------:|-----------|--------------|
| FLOW-001 | `references/ipsec.md` | 0 | - | - |
| FLOW-002 | `references/sone-encap-tx.md` | 1 | 2026-07-18 | TX inject archify workflow diagram |
| FLOW-003 | `references/vxlan-decap-sone-rx.md` | 0 | - | - |
| FLOW-004 | `references/psdev-init.md` | 1 | 2026-07-08 | RX twin (FLOW-007) linked to psdev init/registration |
| FLOW-005 | `references/kim-mts-map.md` | 5 | 2026-07-18 | Control-plane sequence + overview architecture diagrams |
| FLOW-006 | `references/hw-codenames-sone.md` | 0 | - | - |
| FLOW-007 | `references/psinb-rx-sone.md` | 2 | 2026-07-18 | RX punt archify workflow diagram |
| FLOW-008 | `references/vdc-rx-classification-sone.md` | 1 | 2026-07-18 | VDC classify side-branch in RX workflow diagram |
| FLOW-009 | `references/vdc-ioctl-writers.md` | 0 | - | - |
| FLOW-010 | `references/monthly-pr-sweep.md` | 0 | - | - |
| FLOW-011 | `references/kim-process-arch.md` | 0 | - | - |
| FLOW-012 | `references/kfib-route-sync.md` | 1 | 2026-07-18 | KFIB route-sync arm in control-plane sequence diagram |
| FLOW-013 | `references/netbroker-rtnl-trap.md` | 1 | 2026-07-26 | Netbroker RTNL trap walkthrough + KB authoring |

## Change Log

- 2026-06-23: Created sidecar with zero-count baseline for all existing
  `METHOD-*` and `KSTACK-*` records.
- 2026-06-23: Added `FLOW-*`/reference tracking for the current `## References`
  index rows.
- 2026-06-24: Counted `METHOD-002` and `METHOD-007` reuse while evaluating and
  patching CSCwv05793 KIM handler source-SAP validation.
- 2026-06-24: Counted `METHOD-008` switch-access hygiene during CSCwv05793
  runtime repro on `172.20.175.106`; Nexus MCP was used instead of `sshpass -e`.
- 2026-06-24: Counted `METHOD-008` reuse while updating the KSTACK shared method
  to MCP-first switch access and added zero-count baseline row for `KSTACK-021`.
- 2026-06-24: Counted `METHOD-008` and `KSTACK-021` reuse during fixed-image
  validation on `172.20.175.106`; the crash path still reproduced.
- 2026-06-24: Counted `METHOD-008` and `KSTACK-021` reuse during fixed-image
  validation rerun after reload; forged opcode no longer triggered SIGSEGV.
- 2026-06-24: Counted `METHOD-008` and `KSTACK-021` reuse while verifying the
  KIM reject message in `show kim internal event-history errors`.
- 2026-06-24: Counted `KSTACK-021` reuse while recording the KIM debug macro
  event-history mapping: `KIM_DBG_ERR` -> `errors`, `KIM_DBG_INTF` -> `intf`.
- 2026-06-24: Added zero-count baseline row for `KSTACK-022`.
- 2026-06-24: Counted `KSTACK-022` reuse while expanding the hardcoded
  IPsec sec_sys_gid table to Lakefront, Allagash, and Spacedust.
- 2026-06-24: Counted `KSTACK-022` reuse while converting hardcoded
  IPsec sec_sys_gid literals from decimal to hex notation.
- 2026-06-24: Added zero-count baseline row for `KSTACK-023`.
- 2026-06-30: Counted `FLOW-005` and `METHOD-008` reuse during live-switch
  verification of the KIM MTS map on `des1infra` (172.20.175.106). Discovered the
  `show kim internal {event-history,ha-stats,info,issu-stats,mem-stats}` surface and
  `show kim inconsistency` (PASSED); added FLOW-005 Appendix G and expanded the
  KIM CLI block in `knowledge/switch-commands.md`.
- 2026-06-30: Corrected `KSTACK-018`/`METHOD-012` availability claim: `show system
  internal lcnd hash-tables` + `/proc/lcnd/lcnd_hash_tables` are IMAGE-GATED and were
  absent on 10.7(1) IMG9 (verified via `run bash ls /proc/lcnd/`). Added availability
  caveat to `knowledge/switch-commands.md`, softened the KNOWLEDGE.md tool entry, and
  updated FLOW-005 App G.3. Also made subagent fan-out a standing default in SKILL.md
  rule 12 (with the readonly-subagent MCP/no-network caveat).
- 2026-06-30: Counted `FLOW-005` + `METHOD-008` reuse during LIVE config-churn capture
  on `des1infra`: created+deleted throwaway `loopback991` to capture the KIM create
  (`kim_create_if` -> lpss/vrf/router-mac -> `NETDEV_STATE_CHANGE_NOTIFY` up) and delete
  (`NETDEV_STATE_CHANGE_NOTIFY` down -> `kim_remove_if`) handler ordering. Added FLOW-005
  App G.4; recorded the newest-first/`| include <ifindex>` capture gotcha in
  `knowledge/switch-commands.md`. Loopback reverted; `show kim inconsistency = PASSED`.
  Honest limit: inbound create/delete MTS opcode not logged in `msgs`/`mts` on this image.
- 2026-06-30: Added METHOD-015 (per-packet grouping of perf lcnd_traces) + KSTACK-024
  (LCND RX decap trace chain order) after building `group_by_packet.py` for the user's
  `lcnd_traces.log`; counted METHOD-014 reuse (explore subagent + cscope traced
  `lcnd_trace.h`/`lcnd_n9k.c` emit order). Baseline rows for METHOD-015/KSTACK-024.
- 2026-06-30: Validated the TX/encap branch against `lcnd_traces_v2.log` (692 events ->
  222 pkts: 33 RX-decap + 30 TX-encap + 159 mgmt, 0 orphans). Discovered/fixed two
  encap-specific behaviors: skb pointer is REBUILT mid-chain (`lcnd_encap_multicast`
  onward) so skb-equality split must be RX-only, and `lcnd_eth [Out]` is emitted BEFORE
  `lcnd_encap` (leading-parse pending buffer). Updated METHOD-015 + KSTACK-024 notes;
  counted both (=2). v1 output unchanged (regression check).
- 2026-07-07: Added KSTACK-026 (per-device hash tables in `struct lc_device`: real vs
  vestigial, key/value layouts, lazy-alloc + freed-when-empty) and KSTACK-027 (generic
  hash entry `[key][value]` layout; print cb gets `entry->data`; `lcnd_hash_get_count`
  has no NULL guard) from source verification of `lcnd.c`/`lcnd_hash_gen.c` while adding a
  per-interface section to `show system internal lcnd hash-tables`. Baseline rows (count 0).
  Also backfilled the missing index/usage rows for KSTACK-025 (locking; body added same day
  by the shared-brain concurrent session but not indexed).   Bazel/klm build gotcha
  deliberately NOT captured (unverified, environment-specific, out of KSTACK scope).
- 2026-07-08: Added KSTACK-028 (identify N9K Silicon One ASIC family via
  `SW_CARD_ID_IS_WITH_SONE_FAMILY_ASIC` and TOR via `SW_CARD_ID_IS_TOR`) from source
  verification of `platform_cmn_intf.h` (macro OR-chains + `PFM_GET_CELL_SIZE`
  GR2/PL2 sub-family branch). Baseline row (count 0). Links to KSTACK-023
  (sw_card_id header location) and KSTACK-005 (default platform Silicon One).
- 2026-07-08: Added METHOD-016 (grab ASIC/card identity from a live switch, then
  classify SONE vs TOR) and FLOW-006 (`references/hw-codenames-sone.md`: KSTACK-relevant
  SONE subset of the Confluence "Hardware codenames" page, pageId 561414869, cached
  codename->model(PID)->ASIC family). Added card/ASIC identity command block to
  `knowledge/switch-commands.md` (`show module`/`version`/`inventory`/`sprom ... Mfg Bits`),
  cross-linked KSTACK-028. Verified mapping against `des1infra` (N9348Y2C6D-SE1U =
  Deschutes = Krypton E100 = SONE). Baseline rows (count 0). Confluence content kept
  local (Cisco Highly Confidential).
- 2026-07-08: Extended METHOD-016 with (a) step 0 parallel switch data collection via
  `handoff` dispatch-mode subagents (non-readonly; read-only scope; primary
  re-verifies/synthesizes) and (b) a cache-refresh protocol. Created full-page local
  cache `references/hw-codenames-confluence-cache.md` (verbatim snapshot, page_version
  422, cached 2026-07-08) as loss-of-access fallback; wired refresh-on-fetch +
  cache-fallback into METHOD-016, FLOW-006 (`hw-codenames-sone.md`), KNOWLEDGE.md
  (Debugging Tools + FLOW-006 row), and SKILL rule 12. No count increments (skill
  authoring, not reuse).
- 2026-07-08: Added FLOW-007 (`references/psinb-rx-sone.md`, SONE ps-inb RX datapath) + KSTACK-029/030/031
  (psinb_rx_handle_frame RX entry; ps_sone0_rx_handle_frame ASIC->ps-inb redirect; skb_protocol_get_inb/_mgmt
  owned by klm_psdev but SET by klm_vdc's `vdc_module_init` = `eth_type_trans_inb`/`_mgmt`). Extended KSTACK-020
  with psdev_munge_pkt TX-munge detail (HG/RCPU/EPC arms; SONE-only EPC arm). Walked via kstack-flow-walker
  (propose-only) over `standalone/platform/insieme/drivers/emon_psdev/kspace/`; primary re-verified every anchor
  (incl. klm_vdc.c setter + psdev_main.c fn-ptr defs) before writing. Counted METHOD-014, FLOW-004, KSTACK-013/014/019/020
  reuse. Baseline rows (count 0) for KSTACK-029/030/031 + FLOW-007.
- 2026-07-08: Added KSTACK-032 (SONE ASIC netdev set carrying `ps_sone0_rx_handle_frame` keyed by
  `my_card_index`: GR2->leaba12_0, MUSTANG->leaba11_5, DPU-TOR->leaba0_0+pie-eth0, OPTIMATOR_X->leaba11_0+leaba12_0,
  default->leaba0_0; init_module SONE allowlist L4490-4504; `!vmachine`/DPU-only-pie/SONE-family!=handler/mgmt-separate
  caveats). Registration-side companion to FLOW-004/KSTACK-019, RX datapath FLOW-007/KSTACK-030. Grounded via direct
  psdev_main.c reads (macros L175-179, is_sone0_dev L181-208, sone_register_pltfm_rx_handlers L3385-3428,
  sone_netdev_event L3222/3282-3291, init arm L4490-4507). Baseline row (count 0).
- 2026-07-08: Extended KSTACK-032 with the TX-parent coupling note (`psd_priv->parent_dev` set at the SAME
  SONE rx-handler register sites to the SAME ASIC dev -> RX-capture dev == TX-egress dev; starts NULL so
  pre-registration TX drops via `dev_kfree_skb`; cleared on NETDEV_UNREGISTER/`psdev_swover_sone`/exit).
  Grounded via psdev_main.c reads (parent_dev set L3288/3290/3425/3427, psdev_start_xmit L860-877, clears
  L3319-3321/4047-4069/4756). No count increment (same-session correction ladder).
- 2026-07-09: CORRECTED KSTACK-032 (correction ladder, date bumped 07-08->07-09): removed the WRONG claim that
  `parent_dev`/handlers are torn down in `psdev_swover_sone` "(ISSU)". Verified `psdev_swover_sone` (L4033-4039)
  is a NO-OP stub in the CURRENT codebase (logs "Ignoring swover ISSU", returns 0); real teardown is
  `psdev_unregister_rx_handlers` (L4041-4086) + `sone_netdev_event` NETDEV_UNREGISTER. SONE does NOT re-install on
  swover; Tahoe/knet DO (`psdev_swover_tahoe`/`psdev_swover_knet`). Per user: OLDER releases still carry active
  SONE swover code. No count increment (same-session correction).
- 2026-07-09: Walked the `klm_vdc` driver end-to-end (kstack-flow-walker, propose-only;
  primary re-verified next IDs + every anchor before writing). UPGRADED KSTACK-014
  (verification partial->full: 0xf10x = `VDC_ETHTYPE_BASE`+queue offset via
  `klm_vdc_char_get_q_eth_type`/`get_q_mapping`). Added KSTACK-033 (klm_vdc =
  /dev/klm_vdc char driver + 5 VDC lookup tables), KSTACK-034 (ioctl writers: IM mgmt
  state, IGMP mcast, PnP/POAP bcast; INBAND `si_vdc_map_table` programmer has NO
  in-tree caller -> unverified/legacy), KSTACK-035 (`si_vdc_eth_type_trans` per-ASIC
  dispatch + SONE `source_sp`/egress-trap/RCY classifier), and FLOW-008
  (`references/vdc-rx-classification-sone.md`, SONE inband RX queue-ethertype
  classification; sub-flow of FLOW-007). Counted KSTACK-014/030/031, FLOW-007,
  METHOD-014; baseline rows (count 0) for KSTACK-033/034/035 + FLOW-008. Authored the
  `architecture/klm-vdc-driver-architecture.md` companion (ADR-001..008) + KNOWLEDGE.md
  Architecture-docs index row.
- 2026-07-09: Added `architecture/` as a new KB artifact dir + `architecture/psinb-driver-architecture.md`
  (klm_psdev/`ps-inb` SONE datapath + `mgmt_dev` all-platform punt; lifecycle, RX/mgmt/TX datapaths,
  `parent_dev` coupling, external boundaries, ADR-001..010). MOVED here from the driver tree
  (`standalone/platform/insieme/drivers/emon_psdev/kspace/ARCHITECTURE.md`, deleted). Incorporated user
  corrections: build = Bazel `BUILD` (current) + gmake `module.mk` (legacy); `psdev_swover_sone` no-op
  (ADR-010); added §7 `mgmt_dev`/`mgmt_rx_handle_frame`/`is_mgmt_dev` (platform-common punt straight to
  `rni_handle_platform`, no pseudo-dev redirect; static + per-notifier + swover registration) + ADR-009.
  Added KNOWLEDGE.md "Architecture docs" index row + `architecture/` in the dir list. Grounded via
  psdev_main.c reads (mgmt_rx_handle_frame L1673-1693, is_mgmt_dev L567-570, register_mgmt_rx_handlers
  L2176-2220, psdev_swover_sone L4033-4039, psdev_unregister_rx_handlers L4041-4086) + `BUILD`.
- 2026-07-09: Deep-walked the klm_vdc ioctl WRITER path beyond the driver boundary. Added FLOW-009
  (`references/vdc-ioctl-writers.md`): every `VDC_IOC_*` write mapped to its programmer + trigger
  condition (INBAND/IPS maps<-IM/PCM/MCEC/MCM lifecycle; mgmt ip/entry/mcast<-IP/IGMP+IM mgmt-FSM;
  LLDP 0x88cc<-dlopen/dlsym; CPUQ_COSQ<-coppmgr+per-ASIC aclqos direct ioctl w/ libvdcklm name
  collision; q-remap/clear/timestamp/GDB<-PM CLI; bcast<-PnP/POAP; diag-vlan<-GOLD; SET_DBG
  test-tool-only; ipconf_stub #if 0 DEAD). CORRECTED KSTACK-034 (correction ladder, count 0->1):
  its v1 "INBAND src_index has NO in-tree caller -> legacy/unprogrammed" was a cscope -3
  under-report artifact; scoped rg proved IM/PCM/MCEC/MCM program it. Refined METHOD-014 (count
  4->5) with the "-3 silently under-reports; cross-check with scoped rg over source dirs; dlsym
  callers invisible" caveat + evidence. Updated KNOWLEDGE.md (FLOW-009 row, KSTACK-034 row, klm-vdc
  arch one-liner) and expanded `architecture/klm-vdc-driver-architecture.md` §6/§7.2 (verified
  programmer table + cscope caveat) + §4 diagram + §13 cross-ref. Baseline row (count 0) for FLOW-009.

- 2026-07-10 (KLM_PS_INB PR-analysis KB pass): ADDED **KSTACK-036** (`cleanup_module` force-zeros
  `ins_ps_inb` pcpu_refcnt after bounded 500ms wait, CSCwn95874 — symptom fix; leaked-ref holder +
  UAF still open) to `knowledge/entries.md` + KNOWLEDGE.md index + ADR-010/§14 cross-ref; baseline
  row (count 0). ADDED arch §15 "Kernel-version compatibility (LINUX_VERSION_CODE guards)"
  (`eth_hw_addr_set`/`ndo_siocdevprivate`/`psdev_select_queue`/`.ndo_change_mtu`; CSCwp62964/
  CSCwp83497/CSCuv05709). APPENDED KSTACK-032 lineage note (dev-name churn CSCwq14353/CSCwq12457→
  CSCwu22649 Mustang `leaba11_5`; ruled OUT the per-macro `sizeof` hazard and the "app-path disabled"
  claim; diagnostics `sdk_headroom_debug`/CSCwf20380 + `psdev.cmd` tid/cid CSCwd64632). Verified vs
  `origin/nx_main` @1c59b6e; drafts in `bug_reports/KLM_PS_INB/_kb_verification.md`. All net-new
  (no reuse increment). Deferred: P6 Thunder/Gamut `SW_CARD_ID` namespace-mix note (defect junked),
  P9 helper-name into ADR-005 (already ~covered).

- 2026-07-10 (KLM_VDC PR-analysis KB pass): ADDED **KSTACK-037** (`VDC_IOC_CTRL_Q_MAP` bounds-checks
  `ctrl_q_type` vs `ARRAY_SIZE(vdc_global_q.map)`, explicit SET/GET/`-EINVAL`; OOB kernel-write fix,
  CSCwu19801) to `knowledge/entries.md` + KNOWLEDGE.md index + KSTACK-034 security cross-ref; baseline
  row (count 0). EXTENDED **KSTACK-035** notes (verified @1c59b6e): TTL++ egress-trap skip via
  `lcnd_is_card_id_sone_g200_family`/`_g2ll_family` + `LCND_CHECK_TRAP_CODE(...,card_id)` + VP
  `sone_vp_update_ipv4_ttl`; RCY force-vdc=1 ranges LAKEFRONT `0x9a-0x9d`/DANSBERG `0x7a-0x7d`/DESCHUTES
  `0xfa-0xfd`; per-family CoS (Nvidia `isx_hdr->etclass&0x07`); short-circuit ethertypes
  `ETH_P_FPT=0xfbfc`(=`ETH_P_MACSEC_GOLD`)/`ETH_P_BFD=0xfbfd` + BFD port set + `INSIEME_SUP_CODE_BFDC`.
  EXTENDED **KSTACK-014** with the `0xfbfc`/`0xfbfd` short-circuit pair. Verified vs `origin/nx_main`
  @1c59b6e; drafts in `bug_reports/KLM_VDC/_kb_verification.md`. All net-new (no reuse increment).
  NOT written: GAMUT→Nvidia "correction" (already correct in arch §7.4), P11 build-divergence + P9
  card-drift + SP4_TODO gating (not re-verified this pass).

- 2026-07-10 (monthly PR-sweep mechanism): ADDED **METHOD-017** (monthly incremental PR sweep:
  per-component watermark in `bug_reports/_sweep_state.json` -> SHA-range delta w/ `--since`
  fallback -> subject-CSCID extract + dedup by existing `<CSCID>.md` -> full-gated enrich ->
  verify-before-advance; local-cron only, KB stays propose-only) to `knowledge/methods.md` +
  KNOWLEDGE.md `## Methods Library`. ADDED **FLOW-010** (`references/monthly-pr-sweep.md`,
  operational step ladder) + KNOWLEDGE.md `## References` row. Companion tooling built by a
  dispatch subagent under `bug_reports/tools/` (`kstack_pr_sweep.sh`/`monthly_sweep.sh`/
  `enrich_prompt.tmpl`/`crontab.example`/`README.md`) + seeded `_sweep_state.json`
  (KLM_PS_INB/KLM_VDC baselined @9b61f1c546f; KIM/KVFIB/LCND `baseline_pending`). Verified via
  `--dry-run` = 0 new at head. Baseline rows (count 0) for METHOD-017/FLOW-010. All net-new
  (no reuse increment). Cursor Automation ruled out (verified): GHE/CDETS MCPs user-local,
  clone workstation-only.

- 2026-07-10 (KB reconciliation pass — propose-only gate lifted for VERIFIED items): reconciled all
  outstanding proposals in `bug_reports/{KLM_PS_INB,KLM_VDC}/_kb_verification.md` +
  `bug_reports/tools/_skill_method_proposal.md` against the current skill KB and live
  `origin/nx_main` @9b61f1c546f (repo `/nobackup/kkomarag/COV_10_7_0_IMG9_0_201`, validated:
  work-tree + branch resolve). Found the substantive bulk ALREADY-PRESENT from the three prior
  2026-07-10 passes (KSTACK-036, KSTACK-037, KSTACK-035/014 note extensions, arch §15 kernel-compat,
  KSTACK-032 churn note, METHOD-017, FLOW-010; arch §7.4 already lists GAMUT/TP_WBOX_CABO under Nvidia
  so VDC-P10 "correction" is a confirmed no-op). APPLIED one net-new VERIFIED item: KLM_PS_INB
  Proposal 6 — appended a `notes:` block to **KSTACK-032** documenting the `SW_CARD_ID_*` vs
  `CARD_INDEX_*` namespace-mix in `psdev_cleanup_tor_specific` (two `my_card_index == SW_CARD_ID_{TP_WBOX_THUNDER,GAMUT}`
  terms in an otherwise `CARD_INDEX_*` chain; KSTACK-023 hazard; inert since CSCwp31322 junked but a
  latent correctness bug). Verified in `psdev_main.c` `psdev_cleanup_tor_specific` (opens L4599; mix at
  L4682-4683). Note append only (no new ID, no reuse increment). DEFERRED (annotated in the component
  `_kb_verification.md`, NOT written): VDC-P11 build divergence (`la_event_p200_hdr_gen` Bazel side
  verified in `vdc/BUILD`, but the gmake-drop half is git-history not current-source, and it is a
  build/packaging fact, not datapath); VDC-P9 & PSINB-P9 card-enrollment drift (already covered by
  ADR-005); VDC-P10 `#ifdef SP4_TODO` enablement history (build detail; arch already correct).

- 2026-07-10 (KIM process walk): Walked `standalone/infra/kstack/kim/` end-to-end (kstack-flow-walker,
  propose-only; primary re-verified anchors). Authored `architecture/kim-process-architecture.md` (KIM
  = interface-state compiler daemon: `main()` state machine + 3-pthread active vs single-thread
  PSS-synced standby; `g_kim_cfg` twin AVL trees + `ns_name_hash` + LPSS + 7 PSS records; MTS
  bind/register/dispatch `kim_notifs[]`; who-programs deep chain handler->`kim_create_if`->
  `kim_intf_add`+`SIOCDEVADDLC/MODLC/DELLC`->LCND; pseudo-netdev factory; coarse PID gates +
  deep-SONE recycle-port GID / mirror-GID / MCT rsvd-vlan; `kim_tor.c` dead `#if 0`; ADR-001..008).
  Added KNOWLEDGE.md `## Architecture docs` index row + cross-refs (Domain Map KIM bullet, FLOW-005
  row). LCND-side push already covered by FLOW-005 (`references/kim-mts-map.md`). Counted KSTACK-002
  (lc_vlan programmed by KIM) + FLOW-005 + METHOD-014 reuse. No new IDs.

- 2026-07-11 (KIM process-walk propose-only diff APPLIED after re-verification): the kstack-flow-walker
  run from the 07-10 KIM walk returned a propose-only diff; primary re-verified EVERY anchor against
  current source (`kim_db.c`/`kim_lpss.c`/`kim_mts.c`/`kim_tor.c`/`kim_msg_handler.c`/`kim.c`) then
  applied. ADDED **KSTACK-038** (intf/vlan AVL in `g_kim_cfg` + DB-writes-PSS coupling), **KSTACK-039**
  (LPSS two lnx<->nxos ifindex maps, ISSU destroy+recreate, `0xdeadbeef` magic key), **KSTACK-040**
  (MTS spine: 3-queue bind, `kim_notifs[]` register +mcecm/+fretta `eth_pcm`, `kim_notifs_get` dispatch,
  3-thread loop, standby-drop), **KSTACK-041** (KIM-as-sender: DOWNLOAD_ADJ/_ROUTE->ipfib +
  STATEFUL_RSTRT/L3_STATEFUL_RSTRT->pktmgr/netstack), **KSTACK-042** (coarse-SONE PID: sone/sone_gr2/
  sup_sone_virt; `kim_tor.c` `#if 0` dead; LC_ONLINE/OFFLINE = SONE-only mirror/recycle-GID LCND
  writers; flex-port Paris/Berlin) to `knowledge/entries.md` + KNOWLEDGE.md index rows. ADDED **FLOW-011**
  (`references/kim-process-arch.md`) as a THIN flow-index companion to FLOW-005 (deep design deferred to
  `architecture/kim-process-architecture.md` — deliberately NOT a duplicate of the arch doc the walker
  proposed, since that doc already existed) + KNOWLEDGE.md `## References` row. APPLIED **FLOW-005**
  correction: reclassified LC_ONLINE/LC_OFFLINE from Tier-2 "DB" to **Tier-1 (SONE)** in
  `references/kim-mts-map.md` master table + added a correction note (handler SONE-gated, programs
  `LC_ND_MIRROR_GID_SET/DEL` + `LC_ND_RCY_PORT_GID_SET`). Counted METHOD-014 (anchor re-verify),
  METHOD-005 (scoped Grep/Read on 200KB files), KSTACK-002 (writer-attribution model), KSTACK-028
  (SONE-family classification), FLOW-005 (correction). Baseline rows (count 0) for KSTACK-038..042 +
  FLOW-011.

- 2026-07-11 (KIM per-bug KB proposals APPLIED after re-verification, P1-P9): user authorized applying all
  verified-applicable KIM `_kb_verification.md` items; primary re-verified every anchor against current
  `origin/nx_main` source, then wrote. ADDED **KSTACK-043** (`kim_set_default_sysctl` seeds rp_filter /
  ignore_routes_with_linkdown + ip6tables MLD-drop icmpv6 130/131/132/143; CSCwi46503/CSCwq34143/CSCuv05709),
  **KSTACK-044** (4 shared bridges/VXLAN devs `br-%d`/`vx%u` keyed `table_id % 4`, VNI id `(table_id%4)+1`;
  CSCwb01375 + CSCwo37981->CSCwo46939 gotcha), **KSTACK-045** (nsid kernel auto-alloc `kim_get_nsid`=-1;
  per-VRF ioctl socket `kim_get_ns_sock`; `ns_name` fixed-width hash key; CSCwr20377/CSCwe33477),
  **KSTACK-046** (CC_KIM: veth excluded from MTU/MAC, PASSED syslog, `show consistency-checker kim` gated off
  Exablaze/Triton via `$notvalidinexbl`; CSCwh81248/CSCwh26754/CSCwt38492) to `knowledge/entries.md` +
  KNOWLEDGE.md index rows + baseline USAGE rows. EXTENDED notes: **KSTACK-021** (forged-MTS siblings --
  `kim_is_msg_sender_authorized` SAP gate CSCwv05804 + TLV `num` clamp `kim_tlv_parsed_array_count`
  CSCwu64335), **KSTACK-023** (KIM standby/S1 `lc_sw_card_id` derivation: `get_sw_card_id`/`pdb_get_mod_info`
  PROCID_LINECARD/`libutils_get_sw_card_id_tahoe_vp`; CSCws60954/CSCwo26896), **KSTACK-028** (standby
  derivation cross-ref), **KSTACK-038** (PSS insert/delete `kim_pss_key_t` MAIN/SUB symmetry; VNI_INTF ->
  KIM_PSS_KEY_SUB_INTF; CSCwt27793). EXTENDED `references/kim-mts-map.md`: VMCT `SIOCSTUNNSMAP`
  (`= SIOCDEVPRIVATE+15`, `kim_mcec.c`; CSCwn08623) in the non-`LC_ND_*` ioctl list, and the VDC_ONLINE row
  with the MTC/SONE `ethpm_sdb_get_tag_native_state` gate (CSCwr90590->CSCwr96699). P2 was otherwise
  already-present (8/9 opcode rows landed in a prior pass); F1 stays flag-only. Counted KSTACK-021/023/038
  (note extensions) + baselines for 043-046. Backup: `~/workspace/codex_backup/kstack-skill/20260711-010223/`.

- 2026-07-11 (KVFIB/KFIB library walk): Walked `standalone/infra/kstack/kfib/` end-to-end
  (kstack-flow-walker, propose-only; primary re-verified anchors before writing). Authored
  `architecture/kfib-library-architecture.md` (KFIB = kernel->URIB route importer; §1-§13 + 4 mermaid
  block diagrams + ADR-001..008) and `references/kfib-route-sync.md` (**FLOW-012**). ADDED **KSTACK-047**
  (live direction kernel->URIB only; reverse/notify paths `#if 0` dead; `urib_notify_request` `#if 0` =>
  no URIB notifications), **KSTACK-048** (netlink socket + netns kernel-programming seq: `kfib_nl_create_sock`
  `RTMGRP_LINK|IPV4_ROUTE|IPV4_IFADDR`, `setns(CLONE_NEWNET)` per-VRF, select/recvmsg, route_change filters),
  **KSTACK-049** (lnx->nxos ifindex via KIM LPSS `volatile:kim_nxos_if_handle_db` + IOD via
  `im_get_iod_frm_ifindex` + nh_flags from scope; `urib_add/delete_one_route` build
  `URIB_MTYPE_ADD/DELETE_ONE_ROUTE` + fire-and-forget `urib_send_to(MTS_SAP_URIB)`), **KSTACK-050** (MTS spine
  2 SAPs `MTS_SAP_KFIB_SYSMGR`+`MTS_SAP_KFIB=234` + 4-thread model; only `MTS_OPC_KIM_NS_OPERATION` live),
  **KSTACK-051** (`kfib.conf` identity: run=conditional, deps KIM/URIB/L3VM scope control, heartbeat 8s,
  standby_mode=sync) to `knowledge/entries.md` + KNOWLEDGE.md index rows + `## Architecture docs` one-liner.
  MATERIAL FINDING (re-verified via scoped grep over `standalone/infra`): **NO in-tree sender of
  `MTS_OPC_KIM_NS_OPERATION`** (symbol appears ONLY in KFIB's own `kfib_notifs[]`; KSTACK-041 KIM-sender
  catalog omits it) -> KFIB's per-VRF socket sub-flow is **dormant/`unverified`** in this image, same class
  as the `#if 0` paths. Corrected the arch doc §9 + §13 accordingly (was drafted as "KIM = verified sender").
  Re-verified the out-of-dir terminal hop: `urib_api.c urib_add_one_route`@~1859/`urib_delete_one_route`@~1993
  -> `urib_send_to(qh, MTS_SAP_URIB, ...)` (no ack). Counted METHOD-014 (7->8), METHOD-005 (1->2), KSTACK-039
  (0->1, consumer of KIM LPSS), KSTACK-041 (0->1, sender-catalog corroboration), KSTACK-045 (0->1, per-VRF
  netns twin) reuse. Baseline rows (count 0) for KSTACK-047..051 + FLOW-012.
- 2026-07-11 (KVFIB KB apply): extended **KSTACK-051** with two dated `notes:` (no new id/index row —
  these sharpen the existing `kfib.conf` entry): (1) CSCwk55026/CSCwq16826 — `limit { heap }` is now KB
  (`250000000→250000`, same ~250 MB) for >4G `.conf`, plus the `phy_mem_{8..512}G_heap` family (default 0,
  nearest-lower inheritance); (2) CSCuv05709 lineage — `SRVNAME_KIM;` dep removed by a2g sync `72c323fe`
  then restored by code-drop `577f4607` (blame-verified), so the KIM-present state is correct for the live
  tree. KSTACK-051 count 0->1. Both anchors re-confirmed in current `kfib.conf` on `origin/nx_main`.
- 2026-07-14 (KIM-CC MTU-mismatch RCA, live 172.22.135.166 / N9364E 10.7(0)IMG9(0.221)): added **KSTACK-052**
  (KIM-CC MTU triad + `kim_set_ifmtu` single-writer; `Linux=1500 + kim db=0` == setter never ran; breakout
  sub-ports `0x38xxxxxx` never received `IM_MSG_TLV_MTU` at boot while SVIs `0x901xxxx` did, and were
  `kim_create_if`-created after the MTU flood). Extended **KSTACK-046** with the triad decode + MCT-suppression
  clarification (count 0->1). Source re-anchored to `kim_inconsistent_interfaces` L1724/1731/1751/1758/1773
  (kim_debug.c) and `kim_process_port_param_change` L1492/1493/1496/1498 (kim_mts.c), confirmed against the
  running image's own event-history line numbers. CDETS: no exact match; family = CSCvp68307/CSCvx38081
  (`CC_ERR_KIM_MTU_IM_KIM_MISMATCH`), CSCvr58203 (breakout-lane MTU CC), CSCvq30775, CSCwv34272 (mechanism).
  Added switch-commands KIM MTU-triad decode block. Counted METHOD-008 (Nexus MCP read-only) + METHOD-014 reuse.
- 2026-07-14 (live breakout experiment, lab 172.20.175.106 / N9348Y2C6D-SE1U 10.7(0)IMG9(0.189), via subagent
  write-access MCP): applied `interface breakout module 1 port 49 map 10g-4x` + `mtu 9216` on Eth1/49/1-4
  interactively => **Outcome A** (Linux MTU 9216, no inconsistency, `Set MTU 9216 for Interface 0x381e000x`
  logged for all four). Proves the prod KIM-CC MTU mismatch is **boot/config-replay-window-specific**, not a
  general breakout defect, and validates the live `mtu` re-toggle workaround. Appended dated note to KSTACK-052
  (count 0->1). Lab left in repro state (idle port 49); revert = `default interface Eth1/49/1-4` + `no interface
  breakout module 1 port 49 map 10g-4x`.
- 2026-07-16: Added KSTACK-053 for CSCwv32090 LCND private-netlink
  authorization, payload bounds, MPLS adjacency clamping, and the paired KvFIB
  sender-length correction. Counted METHOD-008 reuse for read-only Nexus MCP
  verification that legitimate IPFIB/KIM senders retain effective
  `CAP_NET_ADMIN`; no switch credentials or runtime identifiers were persisted.
- 2026-07-16: Added METHOD-018 for least-mutating private raw-netlink hardening
  validation with header-only ACK probes. Updated KSTACK-053 with fixed-image
  runtime proof: unauthorized admin-bash senders got no ACK, and privileged
  `run bash sudo -n python3` malformed-payload probes got `NLMSG_ERROR/-EINVAL`;
  post-test IPFIB/KIM health stayed handshaked. Counted KSTACK-053 reuse/update.
- 2026-07-17: Counted METHOD-008, KSTACK-046, and KSTACK-052 during CSCwv49648
  live repro attempt on 172.20.175.106. The currently loaded image reproduced
  unauthorized SAP 175 logs during Eth1/49 breakout creation, but the MTU
  updates arrived for all generated members and KIM-CC stayed PASSED.
- 2026-07-17: Counted METHOD-008, KSTACK-046, and KSTACK-052 during a
  copy-to-running CSCwv49648 discriminator on 172.20.175.106. Applying a
  bootflash config file with breakout+MTU via `copy ... running-config`
  reproduced unauthorized SAP 175 logs, but KIM received the generated-member
  MTU updates and KIM-CC stayed PASSED.
- 2026-07-17: Counted METHOD-014, KSTACK-046, and KSTACK-052 while tracing
  CSCwv49648 source behavior: KIM-CC compares Linux/NxOS/KIM DB MTU, and the
  likely failure mode is a non-tunnel interface DB entry whose `kim_set_ifmtu`
  path never ran after netdev creation.
- 2026-07-26: Walked netbroker end-to-end (kstack-flow-walker). ADDED **KSTACK-054**
  (netbroker trap + NXOS whitelist + nbproxy source-of-truth model) and **FLOW-013**
  (`references/netbroker-rtnl-trap.md`, RTNL trap -> nbproxy -> urib/netstack).
  Updated KNOWLEDGE.md Domain Map (Netbroker component row), `## References`,
  `## Entries`, Switch Commands topic; extended SKILL.md Tier A/B triggers
  (`netbroker`, `nbproxy`, `libnetbroker`). Added netbroker read-only switch
  commands to `knowledge/switch-commands.md`. Counted KSTACK-054 + FLOW-013 reuse.
- 2026-07-26: After netbroker runtime on 172.20.175.107 exposed bare `run bash dmesg`
  permission denied and empty sudo `dmesg`, ADDED **METHOD-019** (privileged
  `run bash sudo sh -c '<pipeline>'` hard rule) and **KSTACK-055** (sup LXC empty
  kmsg + netbroker hot path tracepoints not printk; nbproxy event-history as proof).
  Updated SKILL.md rule 11, switch-commands, FLOW-013 observability table.
  Counted METHOD-019 + KSTACK-055 reuse.
- 2026-07-26: Refined **KSTACK-055** + **METHOD-019** after printk/`dmesg -F /dev/kmsg`
  follow-up on 107: plain `dmesg` empty but kmsg has records; `echo 8 > printk` works
  but does not surface netbroker RTNL traps (tracepoints); nbproxy event-history remains
  primary userspace proof. Updated switch-commands (printk tune + `dmesg -F`), FLOW-013
  observability table, SKILL.md rule 11.
- 2026-07-26: ADDED **METHOD-020** (E2E netbroker validation: perf 7-trace sequence +
  nbproxy event-history on 107). Expanded FLOW-013 § E2E validation, switch-commands,
  KSTACK-054 full runtime verification. Re-run confirmed kernel + NX-OS traces match
  user perf capture. Counted METHOD-020 reuse.
- 2027-07-26: ADDED **METHOD-021** — canonical NX-OS kernel perf capture/decode for all
  tracepoint subsystems (`-o /bootflash/*.perf` + `perf script -i … > …txt`; timed vs
  stimulus-bound). Updated METHOD-015/020, switch-commands, SKILL.md, KNOWLEDGE.md
  Debugging Tools, scripts/README.md, group_by_packet.py header, FLOW-013, KSTACK-055.
  Counted METHOD-021 reuse.
- 2026-07-27: ADDED **`architecture/netbroker-architecture.md`** — netbroker design,
  usages table (§8), observability, boundaries vs KFIB, ADR-001..008. Linked from
  KNOWLEDGE.md Architecture + FLOW-013 row; KSTACK-054 notes. Confluence PAGE_TREE +
  sync. Counted netbroker architecture doc reuse.
