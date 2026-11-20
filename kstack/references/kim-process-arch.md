# FLOW-011: KIM control-plane PROCESS spine (Silicon One)

**Companion to FLOW-005.** FLOW-005 (`references/kim-mts-map.md`) maps every inbound
`kim_notifs[]` opcode -> KIM handler -> `LC_ND_*` ioctl -> LCND hash-table/field. This
flow covers the three gaps FLOW-005 does NOT: **(1)** who writes KIM's OWN state, **(2)**
the MTS register/receive/dispatch/send spine, **(3)** coarse-SONE PID handling.

> **Thin flow index.** Deep design, block diagrams, and ADR-001..008 live in
> `architecture/kim-process-architecture.md`. This file is the ordered, stable-anchored
> spine + entry pointers (KSTACK-038..042). Platform = Silicon One (default). Anchor on
> function/struct-field names and branch shape -- **never on line numbers** (volatile).

---

## Gap 1 -- writers into KIM's OWN data structures (KSTACK-038/039)

Single global `kim_config_t g_kim_cfg` holds both AVL roots + per-type counters.

| KIM structure | Writer (stable anchor) | Programmed from |
|---|---|---|
| Interface AVL `g_kim_cfg.kim_intf_tree_root` (key `if_index_t`, node `lc_if_info_avl_t`) | `kim_insert_intf_in_db` / `kim_del_intf_from_db` / `kim_upd_intf_in_db` | MTS handlers `kim_create_if` (KIM_CREATE_NETDEV), `kim_remove_if`/`kim_remove_iflist` (IM_IF_REMOVED/IM_NVE_IF_REMOVED); PSS restore `kim_pss_restore_intf_db` |
| VLAN AVL `g_kim_cfg.kim_vlan_tree_root` (key `uint16 vlan`, node `vlan_info_avl_t`) | `kim_insert_vlan_in_db` / `kim_del_vlan_from_db` | vlan/dvif/vni handlers (`kim_process_dvif`, NVE_L3_VNI, VLAN_MGR_*); PSS restore `kim_pss_restore_vlan_db` |
| `num_{phy,pc,si,vlan,tn,inband,loopback,vni,sat_phy}_intf` + `num_intf` | `kim_update_intf_cnt(is_add, ifindex)` | inside DB insert/delete only |

**DB-writes-PSS coupling (KSTACK-038):** every AVL insert/delete ALSO journals PSS in the
same function -- `kim_insert_intf_in_db` -> `kim_pss_intf_info` (`pss_oper =
KIM_PSS_OPER_INTF_ADD`); `kim_del_intf_from_db` -> `kim_pss_delete_intf`;
`kim_insert_vlan_in_db` -> `kim_pss_vlan_info`; `kim_del_vlan_from_db` ->
`kim_pss_delete_vlan`. DB and PSS are not separable write paths.

**LPSS lnx<->nxos maps (KSTACK-039):** two DBs opened `LPSS_AM_WRITE` --
`kim_lnx_if_index_handle` (nxos `if_index_t` -> `lnx_ns_ifindex_t`; read
`kim_csco_to_lnx_ifindex`) and `kim_nxos_if_index_handle` (reverse; read
`kim_lnx_to_csco_ifindex`). Writers `kim_if_lpss_add`/`_delete` (both handles,
`LPSS_ADD_OVERWRITE`); `kim_if_lpss_init` destroys+recreates on
`sysmgr_is_upgrade_restart()`; `kim_if_lpss_enable_after_issu` writes magic key
`0xdeadbeef` (CSCvd39695) so FIB knows restore is done.

**Namespace/nsid table:** `ns_name_hash` (stathashe2, ns_name -> entry) + per-ns fd,
written by `kim_handle_netns_add` (`kim_ns_create_fd` + `kim_get_nsid` +
`kim_netns_set_nsid` -> pushes `LC_ND_SET_NSID_MAP`) / `kim_handle_netns_delete`, driven
by MTS `L3VM_CHANGE` -> `kim_process_vrf_update`.

**PSS (HA):** 7 files keyed by `kim_pss_key_type_e` (MAIN_INTF/SUB_INTF/VRF/VLAN/FEATURE/
GLOBAL/INBAND/DROP_NOTIFY_FEAT); generic `kim_pss_update`/`kim_pss_delete`; restored by
`kim_pss_recover_state_on_standby` on ISSU/stateful-restart.

---

## Gap 2 -- MTS process spine (KSTACK-040/041)

**Bind/register** (`kim_mts_bind`, `LNODE_SUP`, uuid `SRVUUID_KIM`): 3 queues --
`smq`(`MTS_SAP_KIM_SYSMGR` "kim_sysmgr"), `kimq`(`MTS_SAP_KIM` "kim", main notif),
`kim_mts_stats_q`(`MTS_SAP_DYNAMIC`) -- then `mts_options_set(kimq, opc,
REGISTER|PERSISTENT)` for each `kim_notifs[]` entry. Sub-tables: `kim_notifs_mcecm[]`
(always), `kim_notifs_eth_pcm[]` (`if(!is_fretta) return 0` = **fretta-only**).

**Dispatch** (`kim_notifs_get`): linear scan `kim_notifs` -> `kim_notifs_mcecm` ->
`if(is_fretta)` `kim_notifs_eth_pcm`.

**Receive loop** (`kim_process_single_my_msg`): `mts_recv(kimq)` -> reject/`sdwrap`/`fsrv`
filters -> `sdwrap_hist_mts_event(E_MTS_RX)` (= `show kim internal event-history msgs`) ->
**if STANDBY `goto done`** (drop MTS; standby syncs via ksink PSS) -> `mpmts_gather` if
multi-part -> `kim_notifs_get(opc)` -> handler; `kim_msg_relay` once `standby_sync_done`.

**Threads** (`kim_active_loop`): 3 pthreads -- `kim_process_heart_msg`(smq),
`kim_process_my_msg`(kimq dispatch), `kim_nb_thread_main`(`kim_nb.c`, netlink/notifier).
Standby uses `kim_standby_loop` (heartbeat-only until state -> ACTIVE).

**KIM as SENDER (KSTACK-041):**

| Opcode | Sender fn | Dest | Trigger |
|---|---|---|---|
| `MTS_OPC_KIM_DOWNLOAD_ADJ` | `kim_send_msg_to_ipfib` (`mts_send(kimq, MTS_SAP_REGISTRY, ufib_kim_if_index_info_t)`) | ipfib (REGISTRY) | router-mac change (HMM + port-param) |
| `MTS_OPC_KIM_DOWNLOAD_ADJ_ROUTE` | adj-route send-site (router-mac/adj area) | REGISTRY | router-mac/adj download |
| `MTS_OPC_KIM_STATEFUL_RSTRT` -> pktmgr; `MTS_OPC_KIM_L3_STATEFUL_RSTRT` -> netstack | `kim_issu_send_restore_done_notif(opc)` | REGISTRY | `kim_do_stateful_restart` after PSS recover + client handshake (also `kim_sysmgr.c`) |

(`kim_send_lconf`/`MTS_OPC_INTERNAL_KIM_PSS` = `#if 0` dead.)

**Init ordering** (`kim.c` main): `kim_mts_bind` -> `kim_if_lpss_init` -> [ACTIVE]
`kim_ha_init` -> `kim_init_sysmgr` -> `kim_intf_db_init` -> `kim_vlan_db_init` ->
switch(sup_state): ACTIVE `kim_do_stateful_restart` (ISSU: `kim_active_init` ->
`kim_pss_recover_state_on_standby` -> `kim_issu_send_restore_done_notif`) ->
`kim_active_loop`.

---

## Gap 3 -- PID / platform handling (deep on Silicon One) (KSTACK-042)

1. **`kim_tor.c` is DEAD** -- the whole file is `#if 0` (L1..L87); `kim_is_tor_env` /
   `kim_get_container` / `kim_get_container_role` / `kim_update_to_kernel` have no external
   callers. SONE ToR logic in this build runs via `container_id` /
   `libutils_vchassis_tor_env()` gates in `kim.c`/`kim_mts.c`.
2. **SONE granularity is COARSE** -- the only SONE predicates in the KIM tree:
   `libutils_is_card_sone()` (generic family), `libutils_is_card_sone_gr2()` (G200/GR2
   only), `libutils_is_card_sup_sone_virt_platform()` (VP, via
   `libutils_get_sw_card_id_tahoe_vp`). The fine ASIC PIDs
   (Krypton/P200/Gibraltar/G2LL) are **NOT** branched in KIM -- that lives in
   LCND/klm_vdc/SDK `la_event.h` (FLOW-006 / Domain Map).
3. **LC_ONLINE/LC_OFFLINE are SONE-only LCND programmers** (FLOW-005 tier correction):
   - `LC_ONLINE` -> `kim_process_lc_online` (`if(!libutils_is_card_sone()) return`) ->
     `kim_program_mirror_gid(...,FALSE)` = `LC_ND_MIRROR_GID_SET` +
     `kim_process_recycle_ports` (-> `libpixm_sone_get_recycle_port_details` ->
     `kim_fill_recycle_port_info` sets `LC_ND_RCY_PORT_GID_SET` -> `kim_send_recycle_port_ioctl`).
   - `LC_OFFLINE` -> `kim_process_lc_removed` (SONE-gated) ->
     `kim_program_mirror_gid(...,TRUE)` = `LC_ND_MIRROR_GID_DEL`.
4. **Other SONE-only KIM paths:** `g_kim_vxlan_mct_rsvd_vlan` (`LC_ND_RSVD_VLAN` via
   `kim_prgm_mct_rsvd_vlan` in `kim_handle_vlan_mgr_sdb_update` + PSS restore); flex-port-Q
   `kim_is_flex_port_supported` (`SW_CARD_ID_PARIS`/`BERLIN` &&
   `port_num > KIM_FLEX_PORT_OFFSET_PLTFM_PARIS`) -> `kim_update_flex_port_qbase` ->
   `LC_ND_SET_FLEX_PORT_Q`; LIF resolution `eltm_query_ifindex_to_lif` gated
   `is_fretta || is_card_sone || sup_sone_virt`; `kim_ifindex_to_dmod_dport` SONE
   dmod/dpid/ltl (`SW_CARD_ID_SKAGIT_RIVER_IFM` special-cased).

---

## Runtime-dependent branches (confirm live; do not assume)

| Branch | Why runtime | Confirm with |
|---|---|---|
| Which SONE predicate is true (`sone` vs `sone_gr2` vs `sup_sone_virt`) | installed card PID | `show module`/`show inventory` -> PID, FLOW-006 map (METHOD-016) |
| `is_fretta` (`pdb_is_fretta_family_switch`) | platform-fixed at boot | card family via `show module`/`show version` (KSTACK-028) |
| flex-port-Q arm fires | card = Paris/Berlin + phys port# > offset | `show kim internal info <if>` + card id |
| `kim_process_lc_online` mirror/recycle runs | SONE + `MODULE_TYPE_LC` LC-online event | `show kim internal event-history events` around an LC online |
| Which inbound opcode drove `kim_create_if`/`kim_remove_if` | opcode not surfaced on 10.7 IMG9 | `show kim internal event-history msgs` (best-effort; image-gated; FLOW-005 App G.4) |

---

**Entries:** KSTACK-038 (AVL DBs + PSS coupling), KSTACK-039 (LPSS maps), KSTACK-040 (MTS
spine), KSTACK-041 (KIM senders), KSTACK-042 (coarse-SONE PID + dead `kim_tor.c` +
LC_ONLINE/OFFLINE writers). **Deep design + block diagrams + ADRs:**
`architecture/kim-process-architecture.md`. **Notification->LCND map:** FLOW-005.
