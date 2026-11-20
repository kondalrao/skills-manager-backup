# FLOW-012: KFIB kernel -> URIB route sync (KvFIB userspace daemon)

- **flow**: FLOW-012
- **protocol**: IPv4 unicast route sync (netlink RTM_NEWROUTE/DELROUTE -> URIB)
- **platform**: platform-agnostic userspace (workspace default Silicon One; no per-ASIC dispatch in KFIB)
- **status**: verified (static/source); runtime arms unverified (see notes)
- **date**: 2026-07-11
- **component**: KFIB = `kfib.bin` sysmgr daemon, `standalone/infra/kstack/kfib/`
- **entries**: KSTACK-047, KSTACK-048, KSTACK-049, KSTACK-050, KSTACK-051
- **architecture**: `architecture/kfib-library-architecture.md` (deep design + ADR-001..008)

## Direction reality (read first)
KFIB's ONLY live datapath is **kernel -> URIB** (one-way). The reverse
(URIB/kernel program) and URIB-notify paths are `#if 0` dead (KSTACK-047).
`urib_notify_request` is `#if 0`, so despite `urib_register`, KFIB receives
NO URIB route notifications in this image.

## Threads (4; created when sysmgr role = ACTIVE)
- `kfib-sysmgr-thread` = `kfib_process_heart_msg` -> `kfib_process_single_heart_msg`
  (smq heartbeat + `sysmgr_dispatch`; drops `MTS_OPC_VSH_ACFG_GEN`).
- `kfib-mts-thread` = `kfib_process_my_msg` -> `kfib_process_single_my_msg`
  (kfibq: `sdwrap_process_msg` first, then `kfib_notifs_get(opcode)` dispatch).
- `kfib-nl-thread` = `kfib_nl_kernel_read` (created in `kfib_nl_init`).
- active_timer library timer thread (`kfib_timer_init` -> `active_timer_init`;
  `kfib_process_heartbeat_timer` re-arms `kfib_heartbeat_timer`).

## LIVE flow: kernel route change -> URIB
1. `kfib_nl_kernel_read` -> `kfib_wait_for_ip_input` (`tsp_select` over every
   `nl_sock_info_t.nl_sock` in `nl_sock_list`) -> `tsp_recvmsg` ->
   `NLMSG_OK`/`NLMSG_NEXT` loop (`NLMSG_DONE`/`NLMSG_ERROR`/ACK handling).
2. `kfib_nl_info_fetch`: drop `snl->nl_pid != 0`; dispatch on `nlmsg_type`:
   - RTM_NEWROUTE/RTM_DELROUTE -> `kfib_nl_route_change`
   - RTM_NEWADDR/RTM_DELADDR -> `kfib_nl_intf_addr` (body `#if 0` DEAD)
   - RTM_NEWLINK/RTM_DELLINK -> empty
3. `kfib_nl_route_change`: `kfib_nl_parse_rtattr` (`RTA_OK`/`RTA_NEXT`), then
   skip-filters (return if): `rtm_type != RTN_UNICAST`; `RTM_F_CLONED`;
   `RTPROT_REDIRECT`; `RTPROT_BIRD` (loop-guard vs URIB-origin routes);
   `rtm_src_len != 0`; `rtm_table != RT_TABLE_MAIN`; `rtm_scope == RT_SCOPE_LINK`.
   Extract `RTA_OIF`->index, `RTA_DST`->dest, `RTA_GATEWAY`->gate,
   `RTA_PREFSRC`->src, `RTA_PRIORITY`->metric. **AF_INET only.**
   - [branch] RTM_NEWROUTE && !RTA_MULTIPATH -> `kfib_urib_add_one_route`
   - [branch] RTM_NEWROUTE && RTA_MULTIPATH -> log only (UNHANDLED)
   - [branch] RTM_DELROUTE -> `kfib_urib_del_one_route`
4. `kfib_urib_add_one_route` field transforms:
   - lnx ifindex (RTA_OIF) -> `kfib_lnx_to_csco_ifindex` ->
     `lpss_lookup(kim_nxos_lpss_if_index_handle=..."volatile:kim_nxos_if_handle_db")`
     -> nxos `if_index` (KFIB reads KIM's LPSS DB read-only; consumer of KSTACK-039)
   - nxos if_index -> `im_get_iod_frm_ifindex` -> `iod`
   - scope -> `kfib_urib_get_nh_flags`: RT_SCOPE_LINK -> ATTACHED|DIRECT;
     RT_SCOPE_HOST -> ATTACHED|LOCAL
   - -> `urib_add_one_route(urib_pib_hdl, tid, prefix, mask_len, next_hop, iod,
     tag, pref, metric, nh_flags, route_type, nib_data, rnh_present, rnh_addr,
     rnh_masklen)`
5. [out-of-dir terminal, re-verified] `urib_api.c urib_add_one_route` (~L1859): build
   `urib_oneroute_msgtype` (`msgid_set(MSGID_MJR_URIB, URIB_MTYPE_ADD_ONE_ROUTE)`),
   `qh = urib_get_qh_for_pib(pib)`, fire-and-forget `urib_send_to(qh,
   MTS_SAP_URIB, ...)` (no ack; `urib_send_to`->`urib_send_to_opt` w/
   MTS_SEND_OPTIONS_DEFAULT). Delete (~L1993) mirrors with URIB_MTYPE_DELETE_ONE_ROUTE.
   Guards: `urib_is_urib_down()`, `urib_check_pib(pib)`.

## Kernel-programming primitive: `kfib_nl_create_sock`
`tsp_socket(AF_NETLINK, SOCK_RAW, NETLINK_ROUTE)` ->
`nl_groups = RTMGRP_LINK|RTMGRP_IPV4_ROUTE|RTMGRP_IPV4_IFADDR` (IPv4-only) ->
`tsp_bind` -> `setsockopt(SO_RCVBUF, 1MB)` -> `getsockname` ->
`fcntl(F_SETFL, O_NONBLOCK)`. Default socket set up in `kfib_nl_init`
(default netns; `default_ns_fd = open("/proc/self/ns/net")`; then
`kfib_init_urib()` + spawn kfib-nl-thread).

## Sub-flow: KIM ns event -> per-VRF socket (live consumer; producer NOT found)
`kfib_process_kim_update` (kfibq handler for MTS_OPC_KIM_NS_OPERATION) ->
`kim_ns_notif_t` -> KIM_NS_CREATE -> `kfib_nl_ns_add(ns_name)` /
KIM_NS_DELETE -> `kfib_nl_ns_del(ns_name)`.
`kfib_nl_ns_add`: `tsp_open(NETNS_RUN_DIR/ns_name)` ->
`setns(ns_fd, CLONE_NEWNET)` (into VRF netns) -> `kfib_nl_create_sock()`
(socket created inside VRF netns) -> `setns(default_ns_fd, CLONE_NEWNET)`
(back to default) -> `l3vm_context_get_table_id(ns_name, L3VM_AF_IPV4,
L3VM_DEF_TABLE_NAME)` -> `LIST_INSERT_HEAD(nl_sock_list)`; `max_nl_socks++`.
[unverified] No in-tree sender of MTS_OPC_KIM_NS_OPERATION exists (scoped grep of
`standalone/infra` = KFIB's own `kfib_notifs[]` table only; nothing in kim/;
KSTACK-041 KIM-sender catalog omits it). This sub-flow is therefore currently
un-exercised in this image unless KIM emits the opcode from a non-indexed path.
Confirm at runtime: create a non-default VRF, then look for KFIB event-history
"Successfully added <ns>, num_socks N".

## Dead / `#if 0` code (present but NOT live)
- `kfib_nl_fill_route` (reverse URIB->kernel netlink program path)
- `kfib_nl_request`, `kfib_nl_intf_addr` body
- `kfib_process_notify_route` + kfib_notifs[] MTS_OPC_URIB/U6RIB rows;
  `kfib_urib_process_notify_route` reachable only from that dead handler
- `urib_notify_request` (=> no URIB notifications received)
- standby DO_IT_LATER lconf sync (`kfib_send_lconf`/`kfib_recv_lconf`/`kfib_standby_loop`)
- CLI VXLAN/NVGRE/VNI help strings = copy-paste, no handlers

## Notes
- Stable anchors only; the del path's hard-coded `ifindex = 0x1a101400` fallback
  (lookup-miss TODO) and the `SO_RCVBUF` `< -1` check are code smells, not flow.
- Runtime arms (add/del/multipath, lpss/im success, per-VRF path) are `unverified`
  -- confirm via KFIB sdwrap event-history (`libcli/kfib.cmd` tids
  DBG_KFIB_HIST_EVENTS/_ERROR/_MSGS).
