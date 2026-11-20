# KSTACK Entries (detail)

Full bodies for `KSTACK-*` verified facts/corrections. The compact index (id, title,
scope, status) and reuse counts live in `../KNOWLEDGE.md` and `../USAGE_COUNTS.md`. Open
this file only for the entry id you need. Dedup/next-ID greps and the single-writer rule
(SKILL.md) cover this file too.

## Entries

### KSTACK-001: SONE inband decap overwrites relay_id-derived vlan with the interface lc_vlan
- **scope**: `lcnd_sone_inband_decap` (SONE platform), `lcnd_n9k.c`
- **status**: verified
- **date**: 2026-06-10
- **tags**: lcnd, sone, decap, vlan, l2ra_vni, relay_id, lc_vlan
- **fact**: The local `vlan` is seeded from the SONE punt header `relay_id`
  (`vlan = outer_vlan = pkt_hdr.relay_id;`) and copied into `l2ra_cb->l2ra_vni`.
  But for any packet that is NOT egress-trap-SVI, the value is then
  **unconditionally overwritten** with the resolved interface's `lc_if_info.lc_vlan`:
  ```c
  if(!is_egress_trap_svi) {
      l2ra_cb->l2ra_vni = lcdev->lc_if_info.lc_vlan;
      vlan = l2ra_cb->l2ra_vni;
  }
  ```
  So the `l2ra_vni` printed at the final decap trace reflects the interface's
  programmed `lc_vlan`, NOT `relay_id`. `is_egress_trap_svi` defaults to false and
  is only set true on egress-trap paths.
- **evidence**: Anchored on the `if(!is_egress_trap_svi)` overwrite snippet in
  `lcnd_n9k.c` (grep to locate). Illustrative 2026-06-10 decap logs: a tunnel
  interface -> `l2ra_vni 0`, a loopback -> `l2ra_vni 65535` (per-session values).
- **notes**: To find where `l2ra_vni` really comes from on this path, trace the LAST
  write before the final decap trace -- the `if(!is_egress_trap_svi)` assignment.
  Anchor on the snippet, never a line number (drifts).

### KSTACK-002: lc_vlan is programmed by KIM; decap just copies it
- **scope**: `lc_if_info.lc_vlan` consumers in `lcnd_n9k.c`; writers in `kim/`
- **status**: verified
- **verification**: full (consumption + writer chain); the per-interface VALUE
  rationale (why 0 vs 0xFFFF) is still interface-config-specific, see notes
- **date**: 2026-06-11
- **tags**: lc_vlan, lc_if_info, kim, if-manager, sentinel, SIOCDEVMODLC
- **fact**: `lcnd_sone_inband_decap` copies `lcdev->lc_if_info.lc_vlan` verbatim; it
  does NOT compute or sanitize it. The **writer is KIM**: `kim_vlan_set(if_index,
  vlan)` (`kim/kim_msg_handler.c`) sets `lcinfo.lc_nd_mod_code = LC_ND_VLAN` +
  `lcinfo.lc_if_info.lc_vlan = vlan` and pushes it to LCND via the `SIOCDEVMODLC`
  ioctl, also caching `p_ii->if_info.lc_info.lc_vlan = vlan`. For VNI/segment
  interfaces the value is the switch BD: `lc_info.lc_vlan = sw_bd` (`kim/kim_mts.c`).
  `kim_vlan_set` is called from many sites in `kim_mts.c`. A sentinel `lc_vlan`
  of `0` or `65535 (0xFFFF)` both mean "no L2 VLAN/BD".
- **evidence**: read site = the `lc_if_info.lc_vlan` copy in `lcnd_sone_inband_decap`
  (`lcnd_n9k.c`); writer chain in `kim/kim_msg_handler.c` (`kim_vlan_set`) and
  `kim/kim_mts.c` (`lc_vlan = sw_bd`); `LC_ND_VLAN` + `kim_vlan_set` proto in
  `kim/export/isan/kim_utils.h`. Illustrative 2026-06-11: a tunnel interface showed
  `lc_vlan = 0`, a loopback showed `lc_vlan = 65535` (per-session values).
- **notes**: Remaining (config-specific, not a code defect): which KIM caller fires
  for a given interface type and what `vlan`/`sw_bd` it passes (L3/loopback with no
  BD -> 0 or 0xFFFF). To answer for a specific box, trace `kim_vlan_set` callers and
  correlate with `show interface`/PSS rather than the decap path.

### KSTACK-003: Do not cross-cite decap functions across platforms
- **scope**: methodology, all of `lcnd_n9k.c`
- **status**: verified
- **date**: 2026-06-10
- **tags**: methodology, per-platform, decap, pitfall
- **fact**: `lcnd_n9k.c` contains multiple independent decap/encap functions, one per
  platform/ASIC family. Code in one function does NOT describe another's behavior.
  Citing the "Set vlan to 0xffff for L3 interface" (CSCux29417) code to explain
  `lcnd_sone_inband_decap` was INCORRECT -- that code lives inside
  **`lcnd_tah_inband_decap`** (Tahoe), a different platform.
  Always confirm which function a log/question belongs to (match the `funcname`
  in the `funcname:NNN` trace prefix to the function body) before reasoning, and
  reason only within that function.
- **evidence**: The CSCux29417 "vlan 0xffff for L3 intf" block is inside
  `lcnd_tah_inband_decap`, NOT `lcnd_sone_inband_decap`; verified by
  function-def grep + user correction, sessions 2026-06-10/11.
- **notes**: This is the highest-frequency KSTACK mistake. See SKILL.md "Platform
  discipline".

### KSTACK-004: LC_FLAGS bit reference and observed interface flag decodes
- **scope**: `lc_if_info.lc_flags`; defs in `kim_utils.h`
- **status**: verified
- **date**: 2026-06-10
- **tags**: lc_flags, kim_utils.h, loopback, tunnel, reference
- **fact**: From `standalone/infra/kstack/kim/export/isan/kim_utils.h` (`LC_FLAGS_*`
  bit defs, code constants): `SWITCHPORT 0x1`, `PORTCHANNEL 0x2`, `SVI 0x4`,
  `SI 0x8`, `PCM 0x10`, `SI_PARENT 0x20`, `UP 0x40`, `LOOPBACK 0x80`,
  `TX_HDR_V7 0x2000`, `TUNNEL 0x10000`. AND a logged hex `lc_flags` against these
  to decode it (e.g. `0x2080 = TX_HDR_V7|LOOPBACK`;
  `0x12090 = TUNNEL|TX_HDR_V7|LOOPBACK|PCM`).
- **evidence**: bit defs in `kim_utils.h` (grep `LC_FLAGS_`). Illustrative
  2026-06-10 decap logs: a loopback printed `flags 0x2080`, a tunnel printed
  `flags 0x12090` (interface names/pi are per-session).
- **notes**: Note `kim_utils.h` reuses `0x10000` for both `TUNNEL` and
  `TRUNK_PROMISCUOUS`, and `0x1000` for both `TRUNK_ISOLATED` and
  `NETFLOW_DATAPATH_INTERFACE` -- interpret by interface context.

### KSTACK-005: Default platform is Silicon One
- **scope**: platform context, all KSTACK work
- **status**: verified (user-stated)
- **date**: 2026-06-10
- **tags**: platform, silicon-one, sone, default
- **fact**: Unless the user says otherwise, KSTACK work targets the **Silicon One**
  platform. Confirm the platform per query before reasoning. The `lcnd_sone_*`
  functions in `lcnd_n9k.c` are the inband path observed for Silicon One traces.
- **evidence**: User directive, session 2026-06-10; Silicon One traces emit
  `lcnd_sone_inband_decap:NNN`.
- **notes**: The literal expansion of the `sone` prefix is not independently
  confirmed from code -- do not assert it; just treat `lcnd_sone_*` as the
  Silicon One inband path until shown otherwise.

### KSTACK-006: NULL deref in lcnd_sone_get_netdev glean path (fixed)
- **scope**: `lcnd_sone_get_netdev` (static, inlined into `lcnd_sone_process_ipsec`), `lcnd_n9k.c`
- **status**: verified (root-caused + fix applied by user)
- **date**: 2026-06-10
- **tags**: sone, glean, ipsec, null-deref, crash, ip_dev_find, inlining
- **fact**: In the IPv4 glean branch, the local `lcnd` (`struct net_device *`)
  was declared `NULL` and never assigned: the code resolved the owning device into
  a separate `src_dev` via `__ip_dev_find(net, v4_saddr, false)` but then called
  `lcnd_get_netdev_priv(lcnd)` with the still-NULL `lcnd`. `lcnd_get_netdev_priv(NULL)`
  returns `NULL` (`lcnd.c`), so the `!lcdev` error path logged `lcnd->ifindex`
  -> `NULL->ifindex`. Crash signature: `BUG: kernel NULL pointer dereference, address
  0xe0` (`net_device->ifindex` offset), `RIP lcnd_sone_process_ipsec+0xb3c` (the
  static `lcnd_sone_get_netdev` is inlined), `__LINE__` const `0x4a26` (=18982).
  **Fix (user-applied)**: assign `lcnd = __ip_dev_find(net, dpi.v4_saddr, false);`
  and guard with `if (!lcnd)`, dropping the unused `src_dev`. `devref=false` takes
  no refcount, so nothing to release.
- **evidence**: crash trace (session 2026-06-10 16:56); the glean branch of
  `lcnd_sone_get_netdev` in `lcnd_n9k.c`; `lcnd_get_netdev_priv` in `lcnd.c`.
- **notes**: Found by METHOD-004. Same branch was independently flagged while
  debugging the VLAN-strip issue (KSTACK-007). Out of scope but noted:
  `net = dev_net(skb->dev)` assumes `skb->dev != NULL`.

### KSTACK-007: skb_vlan_pop is a no-op on reconstructed punt skbs (VLAN strip; fixed)
- **scope**: `lcnd_sone_get_netdev` VLAN-strip block, `lcnd_n9k.c`; kernel 6.6
- **status**: verified (root-caused + fix applied)
- **date**: 2026-06-10
- **tags**: sone, vlan, skb_vlan_pop, byte-order, punt, decap, kernel-6.6
- **fact**: The code detected the inline VLAN by reading the payload ethertype
  (`eth_hdr(skb)->h_proto == htons(ETH_P_8021Q)`) and called `skb_vlan_pop(skb)`,
  but the tag was NOT removed. `skb_vlan_pop()` decides what to strip from
  `skb->protocol` and the hwaccel tag (`skb->vlan_all`), NOT the payload bytes.
  The payload is only stripped by `__skb_vlan_pop()`, reachable only when
  `eth_type_vlan(skb->protocol)` is true. On these reconstructed punt skbs
  `skb->protocol` is host-order `0x8100` (not `htons(ETH_P_8021Q)=0x0081`), so
  `skb_vlan_pop()` hits `if(!eth_type_vlan(skb->protocol)) return 0;` and no-ops.
  Result: `lcnd_skb_parse` later sees `eth_proto=0x8100` -> not `ETH_P_IP` ->
  "Non-IP -> drop". Clearing hwaccel alone does NOT fix it (the second-stage strip
  is also gated on `skb->protocol`).
  **Fix (applied)**: replace `skb_vlan_pop()` with a self-contained payload strip
  that mirrors the kernel's `vlan_remove_tag()` and ignores `skb->protocol`:
  `skb_ensure_writable(skb, VLAN_ETH_HLEN)` guard, `__vlan_hwaccel_clear_tag`,
  `memmove(skb->data+VLAN_HLEN, skb->data, 2*ETH_ALEN)`, `__skb_pull(skb,VLAN_HLEN)`,
  `skb_reset_mac_header`, then `skb->protocol = eth_hdr(skb)->h_proto`.
- **evidence**: VLAN-strip session 2026-06-10 15:36; the VLAN-strip block of
  `lcnd_sone_get_netdev` in `lcnd_n9k.c` (grep the `skb_vlan_pop` call);
  kernel `skb_vlan_pop` (KSTACK-008).
- **notes**: `skb_pull` vs `__skb_pull`: `skb_pull` is the bounds-checked wrapper
  (`len > skb->len ? NULL : __skb_pull`); inside the `skb_ensure_writable`+
  `len>=VLAN_ETH_HLEN` guards the check is redundant, but `skb_pull` is the safer
  idiom. The leading `skb_reset_mac_header` is load-bearing (METHOD-006).

### KSTACK-008: Kernel 6.6 VLAN helper semantics and source locations
- **scope**: linux-6.6 kernel source in-repo
- **status**: verified (read from in-repo source)
- **date**: 2026-06-10
- **tags**: kernel-6.6, vlan, skbuff, if_vlan, reference
- **fact**: Tree: `standalone/third-party/src/kernel/nx-linux/linux-6.6/`
  (grep the symbol names below to locate them; kernel line numbers also drift).
  - `skb_vlan_pop(skb)` -- `net/core/skbuff.c`. Two-stage: if
    `skb_vlan_tag_present` clear hwaccel; else if `eth_type_vlan(skb->protocol)`
    call `__skb_vlan_pop`, else `return 0`; then promote any inner tag.
  - `__skb_vlan_pop(skb,&tci)` -- `net/core/skbuff.c`, `EXPORT_SYMBOL` (NOT static).
    `WARN_ONCE` + `-EINVAL` if `skb->data != skb_mac_header`; `skb_ensure_writable`;
    `vlan_remove_tag`; `mac_header += VLAN_HLEN`.
  - `vlan_remove_tag()` -- `include/linux/if_vlan.h`:
    `memmove(skb->data+VLAN_HLEN, skb->data, 2*ETH_ALEN)` + `vlan_set_encap_proto`
    + `__skb_pull(skb, VLAN_HLEN)`.
  - `eth_type_vlan(be16)` -- `include/linux/if_vlan.h`: true for
    `htons(ETH_P_8021Q|8021AD)`.
  - `skb_vlan_tag_present(skb)` -- `include/linux/if_vlan.h`: `!!(skb)->vlan_all`.
  - `__vlan_hwaccel_clear_tag(skb)` -- `include/linux/if_vlan.h`: `skb->vlan_all = 0`.
  - `skb->vlan_all` is a `u32` union field (`include/linux/skbuff.h`).
  - `net_device->ifindex` is at offset `0xe0` on this build (KSTACK-006).
- **evidence**: explore subagent read, session 2026-06-10; user confirmed kernel 6.6.
- **notes**: `bin/linux/final.x86e-6.6/include/linux/if_vlan.h` is a stub; use the
  `nx-linux/linux-6.6` source (METHOD-005).

### KSTACK-009: Reading ethertype/protocol byte order in LCND traces
- **scope**: trace interpretation, little-endian x86 punt path
- **status**: verified
- **date**: 2026-06-10
- **tags**: byte-order, trace, ethertype, vlan, skb-protocol
- **fact**: `__be16` fields read into a host `u16` and printed with `%x` show the
  byte-swapped value on little-endian x86. `eth_hdr(skb)->h_proto` bytes `81 00`
  print as `0x81` (== `htons(ETH_P_8021Q)=0x0081`), so a trace `proto: 0x81`
  means an 802.1Q tag is present. Conversely a trace that prints
  `htons(skb->protocol)` showing `0x81` means `skb->protocol = 0x8100` in **host**
  order. Always note whether a logged value was already `htons()`-converted.
- **evidence**: VLAN sessions 2026-06-10; `Checking for vlan tag proto: 0x81` vs
  `Drop: ... skb->protocol = 0x81` (printed via `htons`).
- **notes**: This byte-order distinction is exactly why `skb_vlan_pop` no-ops in
  KSTACK-007.

### KSTACK-010: IPsec/glean outer-IP strip malforms ESP packets (OPEN)
- **scope**: `lcnd_sone_process_ipsec` "Removing outer IP header" block, `lcnd_n9k.c`
- **status**: verified
- **verification**: full (defect located)
- **resolution**: open (fix direction undecided -- needs user intent)
- **date**: 2026-06-10
- **tags**: sone, ipsec, esp, glean, malformed, l2-ethertype, open
- **fact**: After the netdev lookup succeeds, the IPsec branch assumes the layout
  is `Eth | OuterIP(20) | InnerIP` and strips the outer IP:
  `memcpy(skb->data+20, skb->data, 14); skb_pull(skb,20); skb_reset_network_header;
  skb->protocol = htons(0xf104);`. But when the outer IP `protocol == 0x32` (ESP=50)
  the bytes after the outer IP are an **ESP header**, not an inner IP header -- the
  packet is still encrypted. Stripping yields `Eth(ethertype still 0x0800) | ESP`,
  and the in-buffer L2 ethertype is never updated -> malformed (first L3 byte `0x2d`,
  not `0x45`). Downstream parse fails -> "Got an unsupported protocol 0xf104".
  Secondary verified bug: the unsupported-proto check is a tautology
  `if(skb->protocol != htons(0xf102) || != htons(0xf103) || != htons(0xf104) ||
  != htons(0xfcfc))` (always true; should be `&&`), so that log always fires
  (noise, not the malformation).
- **evidence**: malformation session 2026-06-10 19:29; byte dump `Eth|0800|2d 8a..`;
  the tautological unsupported-proto check + the `skb->protocol = htons(0xf104)`
  strip (carries a `TODO: ... KLM_VDC` comment) in `lcnd_sone_process_ipsec`,
  `lcnd_n9k.c`.
- **notes**: OPEN -- fix depends on intended packet shape at this point (already
  decrypted inner IP vs still-ESP to re-forward vs strip-and-fix-ethertype). The
  ESP proto `0x32` strongly indicates it is still encrypted (decrypt likely did not
  happen upstream/HW). Do not assert a fix until the user confirms intent.
  Sibling, not the same bug: a tagged post-decrypt IPIP frame on the LIF-hit arm
  is KSTACK-059 (the 14-byte slide leaves the tag's TCI slot filled from the
  outer IPv4 destination).

### KSTACK-011: process_ipsec pulls 8 junk bytes before get_netdev
- **scope**: `lcnd_sone_process_ipsec` -> `lcnd_sone_get_netdev`, `lcnd_n9k.c`
- **status**: verified
- **date**: 2026-06-10
- **tags**: sone, ipsec, sec_sys_gid, skb_pull, mac_header, glean
- **fact**: On the IPsec/glean path, `lcnd_sone_process_ipsec` does
  `if (is_sec_sys_gid(pkt_hdr.source_sp)) { ... skb_pull(skb, 8); /* Remove 8 bytes
  of Junk Data */ ... is_drop = lcnd_sone_get_netdev(skb, &lcnd, &lcdev); }`. So on
  entry to `lcnd_sone_get_netdev`, `skb->data` points at the inner ethernet frame
  but `skb->mac_header` is stale -- which is why that function must
  `skb_reset_mac_header(skb)` before reading `eth_hdr()` (METHOD-006).
- **evidence**: the `is_sec_sys_gid(pkt_hdr.source_sp)` + `skb_pull(skb, 8)` block
  in `lcnd_sone_process_ipsec`, `lcnd_n9k.c` (grep the "8 bytes of Junk" comment);
  sessions 2026-06-10.
- **notes**: The "8 bytes of junk" precede the inner ethernet frame on the
  sec_sys_gid (IPsec) source path; confirm the constant if the header format changes.

### KSTACK-012: Post-decap RX delivery -- eth_type_trans -> flo_mgr -> clone/kim-data
- **scope**: SONE RX handoff after `lcnd_sone_inband_decap`, `lcnd_n9k.c`
- **status**: verified
- **verification**: partial (call sites + control-block types verified; full branch
  conditions for each fork not yet exhaustively traced)
- **date**: 2026-06-11
- **tags**: sone, delivery, flo_mgr, kim-data, netstack, clone, eth_type_trans
- **fact**: There is no `lcnd_skb_clone_to_netstack` symbol (only comments and a
  `CLONE_TO_NETSTACK` use in `lcnd_gre_handler`). The real RX delivery: after decap,
  the path runs `lcnd_eth_type_trans` then `lcnd_flo_mgr`, which forks to:
  (a) **kstack** -- `lcnd_skb_clone_to_kernel(skb, ..., l2_recv_attr_cb_t*, ...)`
  clones up via `netif_receive_skb`; (b) **kim-data** -- metadata is added
  and the original is sent on the `kim-data` netdev via `get_kimdata_device()`
  for kstack-client protocols; (c) exception/drop.
  LACP/LLDP get a copy on `kim-data`.
- **evidence**: in `lcnd_n9k.c`, `get_kimdata_device()` (kim-data dev registration),
  `lcnd_skb_clone_to_kernel`, the LACP/LLDP copy, and the inband intf-name module
  params; the `lcnd_skb_clone_to_netstack` symbol is absent (grep).
- **notes**: Answers "why did proto X reach netstack but not kstack?" -- check which
  `lcnd_flo_mgr` fork it took. Candidate flow: `references/l2-punt-to-kim-data.md`.

### KSTACK-013: Inband interface name map (ps-inb / ps-svc-inb / kim-data / ps-sup-eth1)
- **scope**: `lcnd_n9k.c` module params; punt/inject netdevs
- **status**: verified
- **date**: 2026-06-11
- **tags**: ps-inb, sup-inband, kim-data, netdevice, module-param
- **fact**: Verified module-param string constants in `lcnd_n9k.c`:
  `real_intfc="ps-inb"` (punt/inject path ASIC<->sup; TX target; what users call
  "sup-inband"), `real_app_intfc="ps-svc-inb"`, `kimdata_intfc="kim-data"`
  (post-decap handoff to kstack clients, owned by `klm_lcnd`),
  `eth_inb_intfc="ps-sup-eth1"`. Don't invent a `sup-inband` netdev name -- the
  kernel netdev is `ps-inb`. (These are code-level netdev names, not per-session.)
- **evidence**: the `real_intfc`/`kimdata_intfc`/... module params in `lcnd_n9k.c`
  + the `registered device %s` reg logs (grep the param names).
- **notes**: The ASIC->ps-inb RX modules (`klm_psdev`/`psinb_rx_handle_frame`,
  `klm_rni_lcnd`, `klm_sone_krypton`) are external to `standalone/infra/kstack/`.

### KSTACK-014: NX-internal VDC punt ethertypes (0xf102/0xf103/0xf104/0xfcfc)
- **scope**: punt ethertype handling, `lcnd_n9k.c` + KLM_VDC (`klm_vdc_char.c`)
- **status**: verified
- **verification**: full
- **date**: 2026-07-09
- **tags**: klm_vdc, ethertype, punt, 0xf104, vdc-ethtype-base, queue-mapping
- **fact**: `0xf102/f103/f104` are `VDC_ETHTYPE_BASE (0xf100)` + per-queue offset for
  vdc_id=1, computed by klm_vdc: `KLM_VDC_CHAR_Q_BPDU_ETH_TYPE = base+((vdc-1)*3)+2`
  (=0xf102, BPDU), `_Q0_ETH_TYPE = base+..+3` (=0xf103), `_Q1_ETH_TYPE = base+..+4`
  (=0xf104), all in `klm_vdc_char.c`. `get_q_mapping`/`klm_vdc_char_get_q_eth_type`
  pick the queue from bpdu/ARP(0x806)/cos (cos0-3->Q1, cos4-7->Q0). `0xfcfc` is the
  FCoE port (hardcoded `proto==ETYPE_FCOE` on the Broadcom-EOR arm). The default
  `*veobc_prot` in the SONE classifier is `htons(0xf102)`. These are the values
  `skb_protocol_get_inb` (klm_psdev, KSTACK-030/031) writes into `skb->protocol`.
  `lcnd_n9k.c` includes `<isan/klm_vdc_intf.h>` and its unsupported-proto check
  (KSTACK-010) tests exactly this 4-constant set; "Got an unsupported protocol
  0xf104" means the buffer reached delivery still tagged with the VDC ethertype.
- **evidence**: macros `KLM_VDC_CHAR_Q*_ETH_TYPE` + `VDC_ETHTYPE_BASE 0xf100`
  (`export/isan/klm_vdc_intf.h`); `get_q_mapping` / `klm_vdc_char_get_q_eth_type`
  and `*veobc_prot = htons(0xf102)` in `sone_si_vdc_eth_type_trans`, all in
  `klm_vdc_char.c`; the `<isan/klm_vdc_intf.h>` include + 4-constant check in
  `lcnd_n9k.c` (grep `0xf104`). (2026-07-09 source read.)
- **notes**: The VDC tag only appears when the classifier resolves a vdc (src_index
  mapped, or the egress-trap/RCY force-vdc=1 branches); otherwise it returns 0 and
  the caller falls back to real `eth_type_trans`. Related KSTACK-010/030/031/033/034/035,
  FLOW-008.
- **short-circuit ethertype pair (2026-07-10)**: separate from the vdc-queue ethertypes above, the
  SONE classifier also emits `ETH_P_FPT = 0xfbfc` (FPT/INBOUND_MIRROR mirror-copy; `0xfbfc` also aliases
  `ETH_P_MACSEC_GOLD`, kept in sync with `lcnd_n9k.c`) and `ETH_P_BFD = 0xfbfd` (BFD short-circuit). See
  KSTACK-035 notes for the BFD UDP-port set + `INSIEME_SUP_CODE_BFDC` gate.

### KSTACK-018: EGRESS_TRAP decap takes one of 3 source_lp sub-branches before the dummy-eth add
- **scope**: `lcnd_sone_inband_decap` EGRESS_TRAP block, `lcnd_n9k.c`
- **status**: verified
- **date**: 2026-06-18
- **tags**: sone, egress-trap, source_lp, lif, dummy-eth, branch-analysis, dump_table, kim-data
- **fact**: Inside the EGRESS_TRAP block (gate `if(punt_source == EGRESS_TRAP)`),
  the dummy-eth push (`skb_push(ETH_HLEN)` + "Add the dummy eth header") is reached
  ONLY if one of three `source_lp`-keyed sub-branches succeeds; otherwise the
  trailing `else` hits `goto drop`. All three test `pkt_hdr.source_lp`:
  1. **L2 sparse**: `IS_l2SP_MSB_SET(source_lp) && lcnd_vlan_gid_htab_get(...)`,
     i.e. bit 19 set (`(value)&(1<<19)`, macro in `lcnd_sone.h`) -> sets vlan via
     `lcnd_vlan_gid_htab_get`, `is_egress_trap_svi=true`.
  2. **L2 dense**: `(source_lp > 0) && (source_lp < 4095)` -> `vlan=source_lp`,
     `is_egress_trap_svi=true`.
  3. **L3**: `lcnd_lif_htab_get(source_lp, &lc_if_info) == SUCCESS` ->
     `pi = lc_if_info.ltl`; SI sets `is_egress_trap_si`.
  Then the dummy push sets `h_proto` from `fwd_header_type`
  (`==4` -> IPv6, else IPv4) and random src+dst MACs via `eth_random_addr`.
  You CANNOT pick the satisfied branch from the packet alone -- branches 1/2 are
  arithmetic on `source_lp`, but branch 3 needs the runtime LIF table.
- **evidence**: branch structure anchored on the `if(punt_source == EGRESS_TRAP)`
  gate, `IS_l2SP_MSB_SET`/`lcnd_vlan_gid_htab_get`/`lcnd_lif_htab_get` calls, and the
  "Add the dummy eth header" comment in `lcnd_sone_inband_decap`, `lcnd_n9k.c`;
  `IS_l2SP_MSB_SET` macro in `lcnd_sone.h`.
  Illustrative VERIFIED CASE (2026-06-18, per-session values): a `source_lp` whose
  bit 19 was clear and whose value was >= 4095 ruled out branches 1/2
  arithmetically; branch 3 (L3) was PROVEN only via the `lcnd dump_table` LIF row,
  whose `ifindex`/`IOD` matched the outgoing kim-data metadata exactly. (The actual
  `source_lp`/ifindex/IOD/interface for that case are session-specific and not
  anchors -- re-derive from the current packet + dump_table.)
- **notes**: Branch 3 needs the runtime LIF table (`show system internal lcnd
  hash-tables`) to confirm `source_lp` is a registered LIF and to resolve it to
  ifindex/IOD/ltl, then cross-match against the outgoing/kim-data metadata. Always ask
  for `show system internal lcnd hash-tables` for egress-trap branch analysis
  (METHOD-012).

### KSTACK-019: klm_psdev init on Krypton DPU-TOR -- is_dpu_tor effects + benign pie-eth0 double-register
- **scope**: `init_module` / `register_psinb_rx_handlers` / `sone_register_pltfm_rx_handlers` / `sone_netdev_event`, `psdev_main.c` (`klm_psdev`); Silicon One Krypton DPU-TOR
- **status**: verified
- **date**: 2026-06-18
- **tags**: psdev, ps-inb, ps-svc-inb, is_dpu_tor, deschutes, dansberg, card_index, sone, rx-handler, krypton
- **fact**: `klm_psdev` `init_module` sets `is_dpu_tor = true` for EXACTLY two
  card indices: `CARD_INDEX_DANSBERG` and `CARD_INDEX_DESCHUTES` (both "S1 Krypton
  based TOR with ... DPUs" in `card_data.h`; as-of values 21260 / 21271). The
  `is_dpu_tor` flag then changes psdev bring-up in three places:
  1. **Pseudo netdevs**: in addition to `ps-eobc` + `ps-inb`, a THIRD pseudo dev
     `ps-svc-inb` (`ins_app_inb`, the `app_inb` name) is created via
     `ins_psuedo_dev_create`.
  2. **`register_psinb_rx_handlers`** registers `psinb_rx_handle_frame` on BOTH
     `ins_ps_inb` AND `ins_app_inb` (the second only under `is_dpu_tor`).
  3. **`sone_register_pltfm_rx_handlers`** `is_dpu_tor` arm registers
     `ps_sone0_rx_handle_frame` on TWO underlying devs:
     `TOR_SONE_KPKT_DEV="leaba0_0"` and `TOR_SONE_PIE_DEV="pie-eth0"`. Parent
     wiring: PIE dev -> `ins_app_inb->parent_dev`; the kpkt (leaba) dev ->
     `ins_ps_inb->parent_dev`.
  After `sone_register_pltfm_rx_handlers`, `register_netdevice_notifier(
  &sone_netdev_notifier)` fires synthetic `NETDEV_REGISTER`s. The
  **"Cannot register RX handler on Silicon one device"** that appears for
  `pie-eth0` right after is BENIGN -- pie-eth0 was already registered moments
  earlier in `sone_register_pltfm_rx_handlers`, so the synthetic re-register
  returns `-EBUSY`. By contrast `leaba0_0` is usually "not found at init" (the
  leaba ASIC NIC driver loads later); its later `NETDEV_REGISTER` succeeds cleanly
  (no "Cannot register" line). So: a single "Cannot register ..." for the
  already-registered PIE dev is expected; a "Cannot register ..." for the kpkt
  (leaba) dev would be a real failure.
- **evidence**: anchored on the `CARD_INDEX_DANSBERG || CARD_INDEX_DESCHUTES` test
  + "setting is_dpu_tor to true", `register_psinb_rx_handlers` (the `if(is_dpu_tor)`
  second register), the `else if (is_dpu_tor)` arm of
  `sone_register_pltfm_rx_handlers` (`TOR_SONE_KPKT_DEV`/`TOR_SONE_PIE_DEV`), and
  the `netdev_rx_handler_register` failure log "Cannot register RX handler on
  Silicon one device" in `sone_netdev_event` (`psdev_main.c`); macro defs
  `TOR_SONE_KPKT_DEV`="leaba0_0" / `TOR_SONE_PIE_DEV`="pie-eth0";
  `CARD_INDEX_DESCHUTES`/`CARD_INDEX_DANSBERG` in `card_data.h`. Illustrative
  2026-06-18 Krypton DESCHUTES dmesg (`my_card_index=21271 is_dpu_tor=1`):
  full timeline captured in FLOW-004.
- **notes**: `klm_psdev` is the bottom of the SONE inband RX punt chain (Domain
  Map): ASIC -> `ps_sone0_rx_handle_frame` -> `ps-inb` -> `psinb_rx_handle_frame`
  -> LCND. `eth1` is the mgmt dev (`is_mgmt_dev`); on DPU-TOR it re-binds
  igb -> ionic -> veth during bring-up, and an `ionic`-bound mgmt dev is
  explicitly skipped ("ionic driver detected: Ignoring ..."). Full step-by-step in
  `references/psdev-init.md` (FLOW-004). Numeric card-index values and ifindex/MAC
  are as-of hints -- anchor on the `CARD_INDEX_*`/`TOR_SONE_*` macro names.

### KSTACK-015: TX/inject (encap) chain and l2xa_cb
- **scope**: SONE inject path, `lcnd_n9k.c` + `lcnd.c`
- **status**: verified
- **verification**: partial (call chain + control block verified; per-inject-type
  header field math not yet fully traced)
- **date**: 2026-06-11
- **tags**: sone, encap, inject, l2xa_cb, ps-inb, tx
- **fact**: Inject is the mirror of decap: `lcnd_xmit` (`lcnd.c`) -> `lcnd_plat_encap`
  (`lcnd_n9k.c`, builds the `l2_xmit_attr_cb_t` `l2xa_cb`) ->
  `lcnd_encap_fill_plat_hdr` -> per-platform `*_encap_fill_plat_hdr`
  (SONE: `lcnd_sone_encap_fill_plat_hdr`) -> `dev_queue_xmit` to `ps-inb`.
  The TX control block is `l2_xmit_attr_cb_t` (macro `L2_XMIT_CB`), distinct
  from the RX `l2_recv_attr_cb_t`.
- **evidence**: `lcnd_plat_encap`, `lcnd_sone_encap_fill_plat_hdr`, and the
  `L2_XMIT_CB` macro in `lcnd_n9k.c` (grep the names); `ps-inb` module param.
- **notes**: SONE inject header variants (DOWN/UP/TIME_EXT) and smod/sport/dmod/dport
  math not yet recorded -- capture into `references/sone-encap-tx.md` (FLOW-002) when
  next traced. l2xa_vni / phy_ifindex bugs live here.

### KSTACK-016: kim-data RX frame layout = topEth(14) + mdata(48) + stale headroom + pkt@offset
- **scope**: `lcnd_insert_metadata_hdroom` / `lcnd_skb_clone_to_kernel`, `lcnd_n9k.c`
- **status**: verified
- **date**: 2026-06-18
- **tags**: sone, kim-data, metadata, l2_recv_attr_cb_t, offset, decap, layout
- **fact**: The frame LCND delivers on `kim-data` is laid out as:
  `[top Eth 14B] [l2_recv_attr_cb_t metadata 48B] [stale headroom gap] [actual pkt @ offset]`.
  `lcnd_insert_metadata_hdroom` does: `skb_push(headroom)` ->
  `memcpy(skb->data, mac_hdr, ETH_HLEN)` (top Eth copy @ off 0) -> `skb_pull(ETH_HLEN)`
  -> `memcpy(skb->data, l2ra_cb, sizeof(cb))` (metadata @ off 14). It does NOT touch
  the bytes between metadata-end and the packet; `mdata.offset`
  (`= skb_headroom` after `lcnd_skb_get_eth_hdr` pushed back 14) records where the
  ACTUAL packet (its own Eth hdr) sits. So the top Eth (off 0) and the Eth at
  `offset` are the SAME 14 bytes (one is a copy of the other), and L3 payload is at
  `offset+14`. The metadata struct is exactly **48 bytes** (flags8, phy_ifinfex4,
  ifinfex4, phy_iod4, iod4, vni4, sw_bundle4, exception4, tv_sec4, tv_usec4,
  pm_vlan2, offset2); confirmed by the in-code comment "curr sz 48 ... eth hdr(14),
  total 62". Wireshark's "Padding" after the 48B mdata is the stale headroom gap,
  not part of the struct (often shows old outer-eth/punt bytes).
- **evidence**: `lcnd_insert_metadata_hdroom`, `lcnd_skb_get_eth_hdr` (+ `offset`
  set), the "curr sz 48 ... total 62" size comment, and `lcnd_extract_metadata`
  (`pull_len = offset - ETH_HLEN`) in `lcnd_n9k.c` (grep the names). Illustrative
  2026-06-18 INBOUND_MIRROR kim-data capture (per-session offsets): topEth at the
  frame start, 48B mdata next, then a stale headroom gap, then the packet's own Eth
  at `mdata.offset`, then L3 payload at `offset+14`. Concrete byte offsets /
  vni / pm_vlan are session-specific.
- **notes**: To find "what is the 14B chunk just before the payload in a kim-data
  dump?" -> it's the packet's own L2 header that `offset` points to (dup of top Eth),
  NOT something inserted there by the mdata code.

### KSTACK-017: SONE dummy-eth-header sites (only DPU + egress-trap); fingerprint
- **scope**: `lcnd_sone_inband_decap`, `lcnd_n9k.c`
- **status**: verified
- **date**: 2026-06-18
- **tags**: sone, dummy-eth, eth_random_addr, egress-trap, dpu, fwd_header_type
- **fact**: `eth_random_addr` is used in only TWO places in all of `lcnd_n9k.c`:
  (1) the DPU path (`skb_push(2*ETHER_ADDR_LEN)`, gated by inner ethertype `0x8989`);
  (2) the egress-trap "Add the dummy eth header" block (`skb_push(ETH_HLEN)`,
  `h_proto = (fwd_header_type==4)?ETH_P_IPV6:ETH_P_IP`, random src+dst), gated by
  `if(punt_source == EGRESS_TRAP)`. FINGERPRINT of a 14B synthetic Eth hdr with
  locally-administered/random MACs (LAA bit set, e.g. low nibble `0x2/0x6/0xa/0xe`
  in the first octet) + ethertype `0x86dd`/`0x0800` chosen by `fwd_header_type` ==>
  the egress-trap dummy-eth block. The INBOUND_MIRROR / OUTBOUND_MIRROR branch does
  NOT add a dummy Eth header in this source.
- **evidence**: grep `eth_random_addr` -> only the DPU block and the egress-trap
  "Add the dummy eth header" block in `lcnd_sone_inband_decap`, `lcnd_n9k.c`; the
  `if(punt_source == EGRESS_TRAP)` gate. Illustrative 2026-06-18: an INBOUND_MIRROR
  kim-data frame carried exactly this fingerprint (random LAA MACs, `0x86dd`,
  fwd_header_type=4) in front of the real mirrored frame -- a CONTRADICTION since the
  raw punt header decoded `source=0` (INBOUND_MIRROR), not egress trap.
- **notes**: CONTESTED origin of the dummy hdr on mirror packets: either running image
  differs from source (drift; widened/extra path) or the hdr is prepended upstream
  (ASIC/SDK mirror of a routed copy) and LCND only relays it. Discriminate with the
  LCND decap trace (`lcnd_pkt_decap_debug` -> `pkt_decap_trace`) + confirm image vs
  source. Do not assert the egress-trap block as the add-site for mirror until the
  trace shows it. The EGRESS_TRAP add-site is separately VERIFIED end-to-end in
  KSTACK-018 (incl. which source_lp sub-branch was taken) -- this entry stays about
  the sites/fingerprint only.

### KSTACK-020: psdev pseudo-dev TX forwards to parent_dev via dev_queue_xmit (ps-svc-inb -> pie-eth0)
- **scope**: `psdev_start_xmit` + parent wiring, `psdev_main.c` (`klm_psdev`); SONE Krypton DPU-TOR
- **status**: verified
- **verification**: full (TX path + wiring from source; running-image forwarding contested -- see notes)
- **date**: 2026-07-08
- **tags**: psdev, ps-svc-inb, ps-inb, parent_dev, dev_queue_xmit, ice, pie-eth0, tx, egress
- **fact**: The pseudo netdevs use `psdev_netdev_ops.ndo_start_xmit = psdev_start_xmit`.
  `psdev_start_xmit(skb, dev)`: if `netdev_priv(dev)->parent_dev` is non-NULL it does
  `skb->dev = parent_dev; dev->stats.tx_packets++` (so the PSEUDO dev's TX counter is
  bumped INSIDE the `if(parent_dev)` branch -- a climbing pseudo-dev TX proves
  parent_dev != NULL), then `psdev_munge_pkt(skb)` (non-fretta; only edits L2 MACs for
  RCPU/EPC, never reassigns `skb->dev` or frees), then `dev_queue_xmit(skb)`. The
  `else` frees and returns WITHOUT counting. The ONLY non-NULL writers of
  `ins_app_inb->parent_dev` are the two `strncmp(dev->name, TOR_SONE_PIE_DEV)`==pie-eth0
  branches (in `sone_register_pltfm_rx_handlers` + `sone_netdev_event` REGISTER), so
  `ps-svc-inb`'s parent is pie-eth0 or NULL; `ps-inb`'s parent is the kpkt dev
  (leaba0_0). On this box `pie-eth0` is an Intel E823-C BACKPLANE NIC on the `ice`
  driver (PCI parentdev, 96 txq) -- NOT a leaba/virtual dev.
- **evidence**: `psdev_start_xmit` body + `psdev_netdev_ops` (`.ndo_start_xmit`) +
  `ins_psuedo_dev_create` (sets `netdev_ops`) + the pie-eth0 parent branches in
  `psdev_main.c`; kernel 6.6 `__dev_queue_xmit` (`net/core/dev.c`, `q->enqueue ->
  __dev_xmit_skb`). 2026-06-18 runtime: `ethtool -i pie-eth0` -> `ice`, E823-C.
- **notes**: CONTESTED for the running image: 2026-06-18, `ps-svc-inb` TX climbed live
  but `pie-eth0`'s mq qdisc was cumulatively all-zero and ICE tx counters 0 -> the
  frames never reached `pie-eth0` (METHOD-013), which CONTRADICTS this source (which
  would enqueue to pie-eth0's qdisc). So the running klm_psdev either differs from this
  source (drift; user edits source between builds) or `ins_app_inb->parent_dev` is not
  pie-eth0 at runtime. SEPARATELY, `pie-eth0` link was DOWN (`Link detected: no`,
  NO-CARRIER) -- an independent egress blocker. Resolve which via printk in
  `psdev_start_xmit` (needs klm_psdev rebuild+reload) or a direct raw-socket send
  ON pie-eth0 (isolates the device from psdev forwarding).
- **CONFIRMED ROOT CAUSE (2026-06-18, direct raw-send test on pie-eth0)**: the
  "no egress" is NOT a psdev forwarding bug and NOT image/source drift. It is because
  the parent_dev `pie-eth0` is operationally DOWN (`<NO-CARRIER ... UP> state DOWN`).
  A direct AF_PACKET SOCK_RAW send of 50 frames ON pie-eth0 (`s.send()` all succeeded)
  produced ALL-ZERO downstream counters: dev `tx_packets`=0, ALL 96 pfifo_fast children
  `Sent/backlog/dropped`=0, ice `tx_dropped_link_down`=0, and `tcpdump -i pie-eth0 -Q out`=0.
  => On a down ice port the kernel TX path discards frames BEFORE the driver with no
  per-qdisc/driver accounting; this is identical for a direct send and for psdev's
  `dev_queue_xmit(pie-eth0)`. So an all-zero pie-eth0 qdisc is fully explained by the
  device being down -- it is NOT evidence that psdev failed to call dev_queue_xmit.
  pie-eth0 is a PLAIN ice PF (PCI 0000:89:00.0, E823-C), NOT a switchdev representor
  (empty phys_switch_id/phys_port_name, no master/vf), and has NO egress clsact/BPF/XDP.
  Synthetic MAC 00:00:00:00:01:00, MTU 9400 => internal host<->ASIC inband port.
  REAL problem to fix = why pie-eth0 has NO-CARRIER (and whether ps-svc-inb should even
  be parented to pie-eth0 vs leaba0_0, which is up and works for ps-inb).
- **FINAL CONCLUSION (2026-06-18)**: ps-svc-inb -> pie-eth0 wiring is GOOD; the fault is
  entirely inside pie-eth0. ethtool: `Supported ports: [ Backplane ]`,
  `Transceiver: internal`, `Auto-negotiation: off`, `Speed/Duplex: Unknown`,
  `Link detected: no`; sysfs `carrier=0`, `operstate=down`, `carrier_up_count=0`
  (link has NEVER trained since creation), `carrier_changes=1`. No ice link-up events in
  dmesg for 0000:89:00.0. (Side note: pie-eth0 ethtool ops are "Trapped ... Get stats"
  -> platform-virtualized ethtool shim on this inband port.) Driver/link bring-up of the
  backplane port is the remaining work, intentionally left out of scope.
- **METHOD: isolate parent_dev TX from psdev** -- raw-socket send directly on the
  parent_dev. If a direct send ALSO yields all-zero tx/qdisc/egress, the parent_dev
  itself (link/driver) is the blocker, not the pseudo-dev forwarding.
- **CORRECTION (2026-06-18, user)**: do NOT use the outer MAC/ethertype to identify
  WHICH netdev a frame egressed. Every frame leaving pie-eth0 OR leaba0_0 (the SONE
  inject/punt devs) is wrapped in the SAME SiliconOne platform header -- identical outer
  MACs (e.g. `..:1b:01 -> ..:01:08`) and ethertype `0x7103`. So a tcpdump match on those
  fields does not prove the egress device; only the capturing INTERFACE name (or that
  device's own TX counter / `tcpdump -i <dev> -Q out`) does. (Earlier reasoning that a
  dst MAC == leaba0_0's MAC implied the leaba path was WRONG.)
- **TX munge detail (2026-07-08, `psdev_munge_pkt`)**: `psdev_start_xmit` calls
  `psdev_munge_pkt(skb)` only when `!is_fretta_tor` (fretta re-targets via
  `get_knet_dev`, `mac_inst=(data[5]>>3)-1`, and skips munge). `psdev_munge_pkt`
  has three mutually-exclusive L2-only arms and never reassigns `skb->dev`/frees:
  (1) `is_knet0_dev(skb->dev) && data[0]==SOC_HIGIG2_START (0xfc)` -> return (HG
  header, nothing to do); (2) `is_knet0_dev(skb->dev) && memcmp(data, RCPU_LMAC)==0`
  -> `skb_push(4)`, shift first 12 bytes down by 4, write an 802.1Q tag
  (`0x8100`, vid=1) at data[12..15], return; (3) `memcmp(data+ETH_ALEN,
  PSDEV_EPC_SUP_SMAC)==0` -> rewrite dmac=`fm_dest_mac`, smac=`my_src_mac`,
  tpid=`htons(EPC_TPID=0x8833)`, cfi_vid=`htons(EPC_VID=0x3064)` at data[0..15].
  On a PLAIN SONE ps-inb inject (parent = leaba/pie, so `is_knet0_dev`=false) arms
  1-2 CANNOT fire; only the EPC-SMAC arm (3) can, and only if the source MAC equals
  `PSDEV_EPC_SUP_SMAC={00,0E,EE,01,1b,01}`. So for ordinary SONE punt-inject,
  `psdev_munge_pkt` is effectively a no-op and the frame reaches
  `dev_queue_xmit(parent_dev)` unmodified. Anchors: `psdev_munge_pkt`,
  `SOC_HIGIG2_START`, `RCPU_LMAC`, `PSDEV_EPC_SUP_SMAC`/`EPC_TPID`/`EPC_VID`,
  `is_knet0_dev`, `get_knet_dev`; EPC constants in
  `emon_psdev/kspace/export/platform/psdev.h`.

### KSTACK-021: CSCwv05793 KIM SAT fabric PC state-change parser crash path
- **scope**: KIM MTS handler
  `kim_process_sat_fabric_pc_port_state_change()` and libifmgr parser
  `im_parse_l2_protocol_state_change()`
- **status**: verified
- **verification**: runtime repro under gdb plus current-source patch inspection
- **date**: 2026-06-24
- **tags**: kim, mts, libifmgr, tlv, null-deref, source-sap, cscwv05793,
  ste0143083
- **fact**: A crafted
  `MTS_OPC_IM_SAT_FABRIC_PC_PORT_STATE_CHANGE` message to `MTS_SAP_KIM` can
  drive `kim` into the shared libifmgr parser with a payload that lacks the
  expected SDB context prefix. `fsrv_sdb_msg_payload_get()` returns `NULL`,
  `im_pld_tlv_info_get()` computes the TLV pointer as `NULL + 4`, and
  `tlv_array_get_num_tlvs(0x4)` faults before the caller's
  `ret_val != SUCCESS` / `msg == NULL` checks can protect the handler.
- **evidence**: 2026-06-24 runtime repro on `172.20.175.106`, NX-OS
  `10.7(1) [build 10.7(0)IMG9(0.166)]`: gdb attached to `/isan/bin/kim`
  PID `19189`; sending opcode `62579` to SAP `232` produced SIGSEGV in
  `tlv_array_get_num_tlvs()` from `/isan/lib/libutils.so` with `rdi=0x4`.
  Backtrace included `tlvu_table_get_struct_size_from_tlv()`,
  `im_l2_protocol_state_change_pld_get_struct_sz()`, and
  `im_parse_l2_protocol_state_change()`. GDB diverted three faults and detached;
  `kim` remained `SRV_STATE_HANDSHAKED` with `TracerPid: 0`. The stripped
  `/isan/bin/kim` frame above libifmgr appeared as `??`; attribution to
  `kim_process_sat_fabric_pc_port_state_change()` is by source correlation:
  opcode `62579` maps to that handler in `kim_notifs[]`, and this handler is the
  only KIM caller of `im_parse_l2_protocol_state_change()`.
- **fix status**: current branch adds a handler-level source-SAP gate before
  calling `im_parse_l2_protocol_state_change()`, accepting only
  `MTS_SAP_TEST_ETHPM` and `MTS_SAP_KIM`. Source verification passed for the
  branch. Fixed-image runtime validation had one failed attempt where the loaded
  binary did not show the reject string, then a rerun after a later reload of the
  same image passed: `bootflash:///nxos64-s1-dpu.10.7.0.IMG9.0.166.F.bin.mythos`
  contained `%s: Rejecting unauthorized opc %u from SAP %u`, `mts_send()` of the
  forged opcode still returned success, but gdb observed no SIGSEGV and KIM PID
  stayed unchanged. The reject message was not observed in `show logging logfile`,
  but was verified in `show kim internal event-history errors`:
  `Rejecting unauthorized opc 62579 from SAP 8879`.
- **notes**: The original Python PoC's `uid=65534` sender did not run on the
  tested image because `_ctypes.cpython-312-x86_64-linux-gnu.so` is
  `root:network-admin` `0770`, so `nobody` cannot import `_ctypes`. The crash
  path was reproduced with a privileged `admin/root` sender. An on-box C sender
  fallback was not completed because source staging hit MCP shell-quoting limits
  and on-box `clang` could not load `libclang-cpp.so.18.1`.
- **siblings (2026-07-11, same forged-MTS hardening class)**: current source generalizes the source-SAP
  check into a reusable gate `kim_is_msg_sender_authorized(msg, expected_sap, opc_str)` (logs "rejecting
  opcode %u from unauthorized SAP %u"), applied on handlers (e.g. `MTS_SAP_IFMGR` on the if-notify path) --
  the `IM_IF_CREATED` forged-message hardening (CSCwv05804). Separately, the array-parsing handlers
  `kim_process_if_create_netdev_req` / `kim_process_netdev_state_change` /
  `kim_process_netflow_dp_intf_update` now CLAMP an attacker-controlled TLV `if_payload->num` to
  `kim_tlv_parsed_array_count(ssz, payload)` before the indexing loop (heap OOB r/w fix, CSCwu64335). KIM
  pattern = validate sender SAP + bound every TLV count against the parsed array size before dereference.
  Source-verified 2026-07-11 (`kim_mts.c` `kim_is_msg_sender_authorized` L344, gate use L2065, clamp sites
  L1588/1689/1771; SAT-fabric gate `saddr.sap != MTS_SAP_TEST_ETHPM && != MTS_SAP_KIM` L4371). Anchor on
  the handler/helper names, not line numbers.

### KSTACK-022: IPsec sec_sys_gid table is card-id scoped for Krypton cards
- **scope**: `lcnd_ipsec.h` / `is_sec_sys_gid()` (Silicon One IPsec path)
- **status**: verified
- **date**: 2026-06-24
- **tags**: sone, ipsec, sec_sys_gid, lakefront, allagash, spacedust, dansberg,
  deschutes, card-id
- **fact**: `lcnd_ipsec.h` keeps hardcoded IPsec security-system-port GID lists per
  `sw_card_id_t`: `SW_CARD_ID_LAKEFRONT` uses `{0x0, 0x9f, 0xa3, 0xa7, 0xab,
  0xaf, 0xb3, 0xb7, 0xbb}`, `SW_CARD_ID_ALLAGASH` and `SW_CARD_ID_SPACEDUST`
  use `{0x0, 0x1bf, 0x1c3, 0x1c7, 0x1cb, 0x1cf, 0x1d3, 0x1d7, 0x1db}`,
  `SW_CARD_ID_DANSBERG` uses `{0x0, 0x93, 0x97, 0x9b, 0x9f, 0xa3, 0xa7, 0xab,
  0xaf}`, and `SW_CARD_ID_DESCHUTES` uses `{0x0, 0x113, 0x117, 0x11b, 0x11f,
  0x123, 0x127, 0x12b, 0x12f}`.
  `is_sec_sys_gid(gid, card_id)` first selects the matching `card_id` entry,
  then compares `gid` only within that row; unknown card IDs return false.
- **evidence**: Current `lcnd_ipsec.h` table and helper body; values were grounded
  against `hal_sone_get_ipsec_sysport_base()` and `hal_sone_create_ipsec_sys_port()`
  in `converged/platform/drivers/dchal_intf/dchal_server/hal/src/sone/`.
- **notes**: The hardcoded rows intentionally preserve the legacy leading `0`
  entry from the original Deschutes-only table.

### KSTACK-023: Card ID and card index header locations
- **scope**: card identity reference paths, workspace root
- **status**: verified
- **date**: 2026-06-24
- **tags**: sw-card-id, card-index, card-data, reference
- **fact**: `SW_CARD_ID_*` / `sw_card_id_t` definitions are found at
  `converged/global/constants/export/isan/sw_card_id.h` from the workspace root.
  `CARD_INDEX_*` definitions are found at
  `standalone/global/export/platform/card_data.h` from the workspace root.
- **evidence**: Verified by reading `standalone/global/export/platform/card_data.h`
  and grepping `converged/global/constants/export/isan/sw_card_id.h` for current
  `SW_CARD_ID_*` definitions.
- **notes**: Use `SW_CARD_ID_*` for software card-id keyed logic and `CARD_INDEX_*`
  for platform card-index checks; do not substitute one namespace for the other.
- **KIM standby/S1 card-id derivation (2026-07-11)**: KIM stamps `lc_if_info.lc_sw_card_id` on the
  standby/restore path (`kim_create_if_on_standby`, read by LCND for SUP-egress headers + recycle-port). It
  derives the id per node/platform, NOT TOR-only: `get_sw_card_id()` (local), slot ->
  `pdb_get_mod_info(&slot,&mod_info,PROCID_LINECARD)` for EOR/VP (CSCws60954), simulated/virtual VP via
  `libutils_get_sw_card_id_tahoe_vp()` (CSCwo26896), and mgmt-SUP interfaces skip module lookup. Source-
  verified: `kim.c` `pdb_get_mod_info` L1203/1228; `kim_msg_handler.c` `get_sw_card_id` L654/887/901/915,
  `pdb_get_mod_info` L1164/1177, `libutils_get_sw_card_id_tahoe_vp` L1168. Classify the result with the
  KSTACK-028 macros. Anchor on the function names, not line numbers.

### KSTACK-024: LCND perf trace chain order per punted packet (RX decap)
- **scope**: `lcnd_trace.h` tracepoints + `lcnd_sone_inband_decap`/`lcnd_flo_mgr` call order (Silicon One; Tahoe analogous)
- **status**: verified
- **date**: 2026-06-30
- **tags**: lcnd_traces, tracepoint, decap, perf, per-packet, ordering, clone, mgmt
- **fact**: All LCND perf tracepoints live in
  `standalone/infra/kstack/kspace/lcnd/lcnd_trace.h` (`#define TRACE_SYSTEM
  lcnd_traces`; `CREATE_TRACE_POINTS` is in `lcnd.c`). For ONE punted packet the
  RX decap chain emits, in order: `lcnd_decap` (ENTRY, "Inside decap routine",
  original skb) -> `lcnd_decap_punt_hdr` (no skb field) -> [conditional platform
  decap events: `lcnd_decap_vxlan_hdr`/`_dot1q`/`_subif`/`_portchannel*`/egress-trap]
  -> `lcnd_eth`(/`lcnd_ip`/`lcnd_ip6`) -> exactly one demux form: `lcnd_decap_eth_type_trans`
  OR (`lcnd_decap_flow_mgr_entry` + one of `_l2_swfwd`/`_filter_match`/`_exception`/
  `_vxlan_icmpv6`) -> [dual-stack clone: `lcnd_skb_clone_kstack(nskb)` (+`_lldp`/
  `_lacp(nskb)`) then `lcnd_skb_pktmgr(skb)` back on the ORIGINAL] -> `lcnd_decap_stack`
  (TERMINAL success, original skb). Drops end at a `*_drop` event with NO
  `lcnd_decap_stack`. `lcnd_plat_decap` itself emits no trace (pure dispatch).
  Clone events print the `skb_clone()` **nskb**, a different pointer than the
  original. `mgmt_lcnd_decap_fwd`/`mgmt_lcnd_decap_match` are a SEPARATE
  self-contained mgmt-inband path (`lcnd_eth_type_trans_mgmt`, `skb->dev ==
  mgmt_dev`), each fired once per mgmt packet, NOT part of the `lcnd_decap` chain.
  `lcnd_skb_exit` and `lcnd_skb_clone_ctp` are defined but have zero call sites.
- **evidence**: 2026-06-30 source read (explore subagent, cscope) confirmed
  `trace_lcnd_decap(skb)` at chain entry in `lcnd_sone_inband_decap`,
  `trace_lcnd_decap_stack(skb, ...)` at success return, `nskb = skb_clone(skb,...)`
  then `trace_lcnd_skb_clone_kstack(nskb)` before `netif_receive_skb(nskb)`, and
  the mgmt traces only under `lcnd_eth_type_trans_mgmt`. Cross-checked against the
  sample dump `lcnd_traces.log` (52 clean decap chains + 180 mgmt one-liners).
- **notes**: TX/inject mirror (VERIFIED 2026-06-30 against `lcnd_traces_v2.log`,
  SONE `lcnd_encap_inj_down_pkt_hdr` path): one egress/flood injection is a
  9-event unit -- `lcnd_eth [Out]` (parse emitted BEFORE the entry) -> `lcnd_encap`
  (ENTRY) -> `lcnd_encap_xmit_attr` -> `lcnd_encap_iftype` -> `lcnd_encap_multicast`
  -> `lcnd_eth [Out]` -> `lcnd_encap_dot1q` -> `lcnd_encap_inj_down_pkt_hdr` ->
  `lcnd_encap_added_platform_headers` (TERMINAL); drop terminals are
  `lcnd_encap_error` / `lcnd_encap_fdb_lookup_drop`. TWO gotchas that differ from
  RX: (1) the encap **skb pointer changes mid-chain** -- it starts on the original
  skb (`lcnd_encap`/`_xmit_attr`/`_iftype`) then switches to a REBUILT skb (with
  platform headroom) from `lcnd_encap_multicast` onward, ping-ponging between the
  two buffers across a flood; do NOT use skb-equality to bound a TX group. (2) the
  first `lcnd_eth [Out]` is emitted just BEFORE `lcnd_encap`, so a flood burst reads
  `...added_platform_headers, eth, lcnd_encap, ...` -- attach the leading eth to the
  following entry. A flood replicates the frame per egress port, each port its own
  encap unit (evidence: 60 `lcnd_eth [Out]` = 2x30 encaps). Basis for METHOD-015
  (offline grouping); **capture** uses METHOD-021 timed `lcnd_traces:*` pattern.
  Anchor on event NAMES; image line numbers and per-session skb/interface are volatile.

### KSTACK-025: LCND generic hash tables = RCU readers + spin_lock_bh writers (in-place update is a torn-read hazard)
- **scope**: `lcnd_hash_gen.c` (`lcnd_hash_add`/`_update`/`_del`/`_get`, `__lcnd_hash_get`, `lcnd_hash_lookup`); struct `lcnd_hash_table_t` in `export/isan/lcnd_common.h`
- **status**: verified
- **date**: 2026-07-07
- **tags**: locking, rcu, spinlock, spin_lock_bh, hash, concurrency, call_rcu, torn-read
- **fact**: The LCND generic hash tables use the classic Linux "RCU for readers,
  spinlock for writers" pattern over per-bucket RCU hlists.
  `lcnd_hash_table_t` carries `spinlock_t hash_lock`, `struct hlist_head *hash`,
  `struct rcu_head rcu`, `atomic_t count`.
  - Writers `lcnd_hash_add`/`lcnd_hash_update`/`lcnd_hash_del` serialize with
    `spin_lock_bh(&hash_table->hash_lock)`; publish/unlink with
    `hlist_add_head_rcu`/`hlist_del_rcu`; `del` defers the free with
    `call_rcu(&entry->rcu, lcnd_hash_rcu_free)` (unlink+unlock happen BEFORE
    `call_rcu`; `kfree` only after a grace period).
  - Reader `lcnd_hash_get` takes only `rcu_read_lock()` (NO spinlock) and walks
    with `hlist_for_each_entry_rcu`. `__lcnd_hash_get` (double-underscore) is the
    same lookup WITHOUT `rcu_read_lock` -- caller must already hold RCU (or the
    lock). Static `lcnd_hash_lookup` (used by add/update/del) also uses the RCU
    iterator but is only ever called under the spinlock.
  - `_bh` variant disables softirqs so a lock-holding writer in process context
    (control-plane ioctl) can't self-deadlock against a BH/datapath accessor on
    the same CPU. Readers never take the spinlock so are BH/preempt-safe via RCU.
  - `count` is `atomic_t`: inc/dec under lock (redundant for writers) but
    `lcnd_hash_get_count` reads it locklessly (`atomic_read`).
  - CAVEAT (real hazard): `lcnd_hash_update` and the duplicate branch of
    `lcnd_hash_add` mutate the LIVE entry IN PLACE under the spinlock
    (`memcpy(&entry->data[ksize], val, val_size)`), while `lcnd_hash_get` reads
    the same bytes holding ONLY rcu_read_lock. RCU prevents use-after-free but
    NOT torn reads -- a reader can see a half-updated value. Canonical fix is
    copy-on-update (`hlist_replace_rcu` + `call_rcu`), which this code does not do.
    The add-duplicate branch also overwrites with new `val_size` into the old
    allocation (in-source `XXX`/bug comment) -> data[] overrun if the new value
    is larger.
- **evidence**: 2026-07-07 source read of `lcnd_hash_gen.c`: `spin_lock_bh`/
  `spin_unlock_bh` bracketing add/update/del; `hlist_add_head_rcu` in add,
  `hlist_del_rcu`+`call_rcu(&entry->rcu, lcnd_hash_rcu_free)` in del; `get` uses
  `rcu_read_lock()`+`hlist_for_each_entry_rcu`; `__lcnd_hash_get` has no
  rcu_read_lock; struct fields confirmed in `export/isan/lcnd_common.h`
  (`typedef struct lcnd_hash_table_s { struct rcu_head rcu; spinlock_t hash_lock;
  ... atomic_t count; }`). In-place update memcpys at the `lcnd_hash_update` body
  and add duplicate branch; add-dup comment "THIS IS RISKY ! If val_size is >
  previous val_size then we will be overwriting memory".
- **notes**: Locking is platform-independent (generic helper; not a `lcnd_sone_*`
  path). Line numbers volatile -- anchor on function names, `hlist_*_rcu`,
  `call_rcu`, `spin_lock_bh`, `rcu_read_lock`. Table teardown
  (`lcnd_hash_table_fini`/`lcnd_ifindex_priv_fini`/`_del_all_entries`) holds the
  spinlock, `hlist_del_rcu` each entry, `call_rcu` per entry, and defers the table
  struct free via `call_rcu(&hash_table->rcu, lcnd_hash_table_rcu_free)`. Debug
  dumpers (`lcnd_debug_hash_dump*`, `lcnd_hash_dump`, `lcnd_debug_key_bucket_dump`)
  are readers -- rcu_read_lock (or `rcu_read_lock_bh` when `in_softirq()`).

### KSTACK-026: LCND per-device hash tables in `struct lc_device` -- real vs vestigial, layouts, lazy-alloc
- **scope**: `struct lc_device` in `standalone/include/isan/lcnd_common.h`; alloc/use in `lcnd.c` (`lc_dev_init`, `lcnd_vlan_htab_*`, VLAN-xlat / PVLAN / MPLS paths)
- **status**: verified
- **date**: 2026-07-07
- **tags**: lc_device, per-device, hash, vlan, fdb, xlat, pvlan, mpls, svi, si, netdev-state, debugging, lazy-alloc
- **fact**: `struct lc_device` (per-netdev priv; on `lc_dev_list`, keyed in
  `lcnd_ifindex_htab`) carries the per-interface L2 hash tables. A union
  `lc_htab_u` selects by `lc_if_info.lc_flags & LC_FLAGS_SVI`. REAL per-device
  tables (actually populated on the device):
  - SI (non-SVI) `lc_htab_u.lcnd_vlan_htab` -- key `u32 vlan`, val `u32 ifindex`.
    Lives on the **PARENT** (physical) lcdev, not the sub-interface: init
    `lcnd_vlan_htab_init(parent_lcdev)`, insert
    `lcnd_vlan_htab_insert(parent, vlan|lif, ifindex)`.
  - SVI `lc_htab_u.lcnd_fdb_htab` -- key `u8 mac[ETH_ALEN]`, val
    `lcnd_fdb_entry_t` (mac, v4_ref, v6_ref, phy_lnx_ifindex, phy_ns_id).
  - `lcnd_vlan_intf_htab` (ingress VLAN xlat) + `lcnd_bd_htab` (egress) -- key
    `u32 vlan`, val `u32 xlt_vlan`. **Lazily** `lcnd_hash_table_init(
    LCND_HASH_VLAN_XLT_BITS)` on first xlat add; FREED to NULL when count hits 0.
  - `lcnd_pvlan_intf_htab_tx` -- key `u32 pri_vlan`, val
    `struct lcnd_pvlan_map {sec_vlan, pri_vlan}`; created on first PVLAN insert,
    freed to NULL at count 0.
  - `lcnd_ldb_htab_nwkey` -- per-device MPLS label DB (network-key).
  VESTIGIAL per-device members (declared but never populated ON the device -- the
  LIVE table is a GLOBAL or the nwkey variant): `lcdev->lcnd_vlan_vp_htab` (live =
  global `lcnd_vlan_vp_htab`), `lcdev->lcnd_nve_peer_htab` (live = global
  `lcnd_nve_peer_htab`), `lcdev->lcnd_ldb_htab_lkey` (no assignment in `lcnd.c`;
  only `_nwkey` is used). `lc_dev_init` explicitly NULLs
  vlan_htab/bd/vlan_intf/vlan_vp/pvlan_tx at create.
  **Why it matters for debugging:** these tables ARE the current programmed L2
  state of each netdev (VLAN->ifindex, FDB, VLAN xlat both directions, PVLAN,
  MPLS). An empty table is a **NULL pointer** (lazy-alloc / freed-when-empty), NOT
  a zero-count table -- so a per-interface dump must NULL-check each pointer and
  print "None" (never call get_count on NULL; see KSTACK-027). Enumerate every
  LCND netdev's tables by walking `lcnd_ifindex_htab` -> `net_cbl.dev` ->
  `lcnd_get_netdev_priv(dev)` (pattern from `lcnd_debug_hash_dump_v2`).
  Consolidating this per-ifindex under `show system internal lcnd hash-tables`
  (`/proc/lcnd/lcnd_hash_tables`) is high-value for RX/TX branch debugging: the
  packet alone can't reveal which per-device lookup fired (cf. KSTACK-018,
  METHOD-012).
- **evidence**: 2026-07-07 source read -- struct + `lc_htab_u` union in
  `include/isan/lcnd_common.h`; `lc_dev_init` NULLs the per-device pointers;
  SI `lcnd_vlan_htab_init(parent_lcdev)` + `lcnd_vlan_htab_insert`; xlat
  `lcnd_hash_table_init(LCND_HASH_VLAN_XLT_BITS)` on `lcnd_bd_htab`/
  `lcnd_vlan_intf_htab` with free-at-count-0; PVLAN
  `lcnd_intf_pvlan_db_insert(&lcdev->lcnd_pvlan_intf_htab_tx, ...)` + free-at-0;
  globals `lcnd_vlan_vp_htab` / `lcnd_nve_peer_htab` declared and inited globally
  (`lcnd_nve_peer_htab_init`, `lcnd_htab_init(..., &lcnd_vlan_vp_htab)`), every VP
  insert uses the global; `lcnd_ldb_htab_lkey` has zero refs in `lcnd.c` (only
  `_nwkey`).
- **notes**: Line numbers volatile -- anchor on field names, `LC_FLAGS_SVI`,
  `lcnd_vlan_htab_init`, `lcnd_intf_pvlan_db_insert`, `lcnd_ldb_htab_nwkey`.
  Pairs with KSTACK-027 (entry memory layout / get_count NULL hazard) and
  KSTACK-025 (table locking).

### KSTACK-027: LCND generic hash entry layout = [key][value] contiguous; print cb gets `entry->data`; `lcnd_hash_get_count` has no NULL guard
- **scope**: `lcnd_hash_gen.c` (`lcnd_hash_add`, `lcnd_hash_get`, `lcnd_hash_get_count`, debug-dump `print_hash` callback path)
- **status**: verified
- **date**: 2026-07-07
- **tags**: hash, entry-layout, print-callback, seq_file, get_count, null-guard, dump
- **fact**: A hash entry stores key and value CONTIGUOUSLY in one flexible
  `data[]`: writers do `memcpy(new_entry->data, key, ksize); memcpy(
  &new_entry->data[ksize], val, val_size);`, and `lcnd_hash_get` reads the value
  at `&entry->data[ksize]`.
  - Debug dumpers invoke the per-table print callback as
    `print_hash(seq, entry->data)` -- the callback receives a pointer to the START
    of the packed `[key][value]` blob. So a `seq_file` print callback MUST cast
    `data` to a PACKED struct that leads with the key field(s) occupying `ksize`
    bytes, immediately followed by the value field(s). Reading value fields first
    (or omitting the key prefix) misaligns every column.
  - `lcnd_hash_get_count(void *table)` is
    `atomic_read(&((lcnd_hash_table_t *)table)->count)` -- it DEREFERENCES `table`
    with NO NULL check, so a NULL table pointer crashes. Because per-device tables
    are NULL when empty (KSTACK-026), any count/dump path must NULL-check first and
    print "None" for NULL.
- **evidence**: 2026-07-07 read of `lcnd_hash_gen.c`: `lcnd_hash_add` memcpys key
  then val at `data[ksize]` (both the fresh-entry and duplicate branches);
  `lcnd_hash_get` memcpys val from `&entry->data[ksize]`; dump loop calls
  `print_hash(seq, entry->data)`; `lcnd_hash_get_count` body is a bare
  `atomic_read` on `((lcnd_hash_table_t *)table)->count` (no guard); the
  `lcnd_ifindex_htab` dumper reads the `net_device*` at `&entry->data[ksize]`
  (`((val_s *)entry->data)->net_cbl.dev`), confirming the [key][value] layout.
- **notes**: Anchor on `entry->data`, `data[ksize]`, `print_hash`,
  `lcnd_hash_get_count`. Pairs with KSTACK-026 (per-device tables) and KSTACK-025
  (locking). Line numbers volatile.

### KSTACK-028: Identify N9K Silicon One ASIC family and TOR via SW_CARD_ID macros
- **scope**: `sw_card_id`-keyed platform classification; macros in `standalone/platform/apps/pltfm_manager/libcli/export/isan/platform_cmn_intf.h`
- **status**: verified
- **date**: 2026-07-08
- **tags**: sw-card-id, silicon-one, sone, tor, platform, classification, macro
- **fact**: To classify a Cisco Nexus 9000 by its software card id (`sw_card_id`):
  - **Silicon One ASIC family** -> `SW_CARD_ID_IS_WITH_SONE_FAMILY_ASIC(sw_card_id)`.
    True for the SONE card-id set (e.g. `SW_CARD_ID_WBOX_CHURCHILL`, `CROCODILE`,
    `TP_WBOX_THUNDER`, `LAKEFRONT`, `ALLAGASH`, `SPACEDUST`, `TERRAPIN`,
    `THE_CHILD_RP_1`, `GROGU_RP`, `BUD_LIGHTNING(_X)`, `OPTIMATOR(_X)`, `SARGO`,
    `DANSBERG`, `DESCHUTES`, `EASTLAKE`) plus the sub-macros
    `SW_CARD_ID_IS_MANDO_LC`, `SW_CARD_ID_IS_MANDO_FM`, and
    `SW_CARD_ID_IS_WITH_SONE_PL2_FAMILY_ASIC` (Palladium2 LC/SUP). Related sibling
    macros: `SW_CARD_ID_IS_WITH_SONE_FAMILY_ASIC_L2` (SONE cards with L2 support,
    a subset), `SW_CARD_ID_IS_WITH_SONE_GR2_FAMILY_ASIC` and
    `SW_CARD_ID_IS_WITH_SONE_PL2_FAMILY_ASIC` (GR2 vs PL2 sub-families, used e.g.
    in `PFM_GET_CELL_SIZE`).
  - **TOR (top-of-rack) switch** -> `SW_CARD_ID_IS_TOR(sw_card_id)`, which is
    `SW_CARD_ID_IS_TOR_WITH_GEM(sw_card_id) || SW_CARD_ID_IS_TOR_WITH_NO_GEM(sw_card_id)`.
    Many ASIC-specific TOR helpers exist (`SW_CARD_ID_IS_TOR_WITH_<ASIC>_ASIC`,
    `..._WBOX`, `..._GEM`, etc.); `SW_CARD_ID_IS_TOR` is the umbrella "is this a TOR box" test.
  These are the correct, maintained predicates -- do NOT hand-roll `sw_card_id ==`
  comparisons for these classes; the macros are the single source of truth and are
  updated as new cards are added.
- **evidence**: 2026-07-08 read of `platform_cmn_intf.h`:
  `#define SW_CARD_ID_IS_WITH_SONE_FAMILY_ASIC(sw_card_id)` (as-of ~L1786) OR-chain
  over the SONE card-id set + `MANDO_LC`/`MANDO_FM`/`SONE_PL2_FAMILY` sub-macros;
  `#define SW_CARD_ID_IS_TOR(sw_card_id)` (as-of ~L1001) = `IS_TOR_WITH_GEM ||
  IS_TOR_WITH_NO_GEM`; `PFM_GET_CELL_SIZE` (as-of ~L2727) branches
  `SW_CARD_ID_IS_WITH_SONE_FAMILY_ASIC` -> GR2/PL2 sub-family cell sizes.
- **notes**: `sw_card_id`/`SW_CARD_ID_*` enum definitions live at
  `converged/global/constants/export/isan/sw_card_id.h` (KSTACK-023). Line numbers
  and the exact card-id membership list are VOLATILE (new cards get added) --
  anchor on the macro NAMES and always call the macro rather than snapshotting its
  member set.   `SONE_FAMILY_ASIC` matches the KSTACK default platform (Silicon One,
  `lcnd_sone_*`, KSTACK-005); a card can be both SONE-family and TOR. To go from a
  live switch to `sw_card_id`/ASIC, see METHOD-016 (identity commands) and FLOW-006
  (`references/hw-codenames-sone.md`, codename -> model(PID) -> ASIC family, cached
  from the Confluence "Hardware codenames" page, Cisco Highly Confidential).
- **KIM standby derivation cross-ref (2026-07-11)**: KIM's standby/S1 `lc_sw_card_id` derivation sources
  (`get_sw_card_id`, `pdb_get_mod_info`/`PROCID_LINECARD`, `libutils_get_sw_card_id_tahoe_vp`) are recorded
  in the KSTACK-023 notes; use the macros here to classify the resulting id.

### KSTACK-029: psinb_rx_handle_frame is the Kstack RX entry + external rni handoff
- **scope**: `psinb_rx_handle_frame`, `psdev_main.c` (`klm_psdev`); Silicon One
- **status**: verified
- **date**: 2026-07-08
- **tags**: psdev, ps-inb, psinb_rx_handle_frame, rni_handle_platform, rx-handler, mbit, kallsyms, sone
- **fact**: `psinb_rx_handle_frame(pskb)` is the `netdev_rx_handler` on `ins_ps_inb`
  (and `ins_app_inb` under `is_dpu_tor`) and is the RX boundary where klm_psdev
  hands a punted frame to LCND. Order: (1) if `IS_MBIT_SUPPORTED(my_card_index)`
  and `mbit_tx_to_fp_dev(skb)` returns true -> `RX_HANDLER_CONSUMED` (mbit
  front-panel short-circuit). (2) Lazily resolve the fn-ptr
  `rni_handle_platform_lcnd = kallsyms_lookup_name("rni_handle_platform")`; if it
  cannot be resolved -> `RX_HANDLER_PASS` (KERN_CRIT "Unable to resolve
  rni_handle_platform_lcnd symbol. Aborting"). (3) `skb =
  rni_handle_platform_lcnd(skb)`; a NULL return -> `RX_HANDLER_CONSUMED` (LCND
  consumed it). (4) dpu: if `skb->dev` is neither `ins_app_inb` nor `ins_ps_inb`
  -> `RX_HANDLER_ANOTHER`; non-dpu: if `skb->dev != ins_ps_inb` ->
  `RX_HANDLER_ANOTHER`. Otherwise `RX_HANDLER_PASS`. `rni_handle_platform` is
  EXTERNAL (`klm_rni_lcnd`), resolved by symbol name at runtime, not link-time.
- **evidence**: `psinb_rx_handle_frame` body in `psdev_main.c` (anchors:
  `IS_MBIT_SUPPORTED`, `mbit_tx_to_fp_dev`, `kallsyms_lookup_name("rni_handle_platform")`,
  the `RX_HANDLER_CONSUMED/PASS/ANOTHER` returns, the `ins_app_inb`/`ins_ps_inb`
  dev checks); `register_psinb_rx_handlers` installs it (`netdev_rx_handler_register(
  ins_ps_inb, psinb_rx_handle_frame)`, +`ins_app_inb` under `is_dpu_tor`);
  `rni_handle_platform` def in `infra/kstack/kspace/rni_lcnd/rni_lcnd.c`
  (`EXPORT_SYMBOL(rni_handle_platform)`, forwards to `rnd_handle_platform`/
  `rnd_handle_platform_1`). (2026-07-08 source read.)
- **notes**: Complements FLOW-004/KSTACK-019 (registration) and FLOW-007 (full RX
  datapath). `mgmt_rx_handle_frame` (mgmt dev) is a sibling that also calls
  `rni_handle_platform_lcnd`. Resolution via `kallsyms_lookup_name` means a
  missing/renamed `rni_handle_platform` degrades to `RX_HANDLER_PASS` (frame not
  punted to LCND), not a crash.

### KSTACK-030: ps_sone0_rx_handle_frame redirects ASIC skb to ps-inb/ps-svc-inb and normalizes it
- **scope**: `ps_sone0_rx_handle_frame`, `psdev_main.c` (`klm_psdev`); Silicon One
- **status**: verified
- **date**: 2026-07-08
- **tags**: psdev, ps-inb, ps-svc-inb, ps_sone0_rx_handle_frame, skb_protocol_get_inb, vlan_tci, is_dpu_tor, gr2, sone, rx
- **fact**: `ps_sone0_rx_handle_frame(pskb)` is the `netdev_rx_handler` on the SONE
  ASIC kpkt/PIE netdevs. It re-homes the punted skb onto a klm_psdev pseudo dev and
  normalizes it, then `netif_receive_skb` + `RX_HANDLER_CONSUMED`: (1) if
  `is_dpu_tor && skb->dev->name==TOR_SONE_PIE_DEV` -> `is_app_pkt=true`,
  `skb->dev=ins_app_inb` (ps-svc-inb); else `skb->dev=ins_ps_inb` (ps-inb). (2)
  `is_app_pkt` -> `skb_push(ETH_HLEN)` + `skb_reset_mac_header` (IGB stripped the
  eth+.1q on the app path, restore it). (3) GR2 card set
  (`CARD_INDEX_BUD_LIGHTNING/OPTIMATOR/MUSTANG/BUD_LIGHTNING_X/OPTIMATOR_X/SARGO`)
  -> `skb_push(ETH_HLEN)` (GR2 eth already stripped); else -> `skb->vlan_tci=0`
  and `__vlan_hwaccel_clear_tag` (kernel 6.6). (4) `skb->pkt_type=PACKET_HOST`.
  (5) `if (!is_app_pkt && skb_protocol_get_inb) skb->protocol =
  skb_protocol_get_inb(skb, skb->dev)` (VDC queue classification; KSTACK-031). (6)
  `skb->vlan_tci=0` + clear-tag again "for GR2". Then bump dev rx stats and
  `netif_receive_skb`. NOTE the app path deliberately SKIPS the
  `skb_protocol_get_inb` classification.
- **evidence**: `ps_sone0_rx_handle_frame` body in `psdev_main.c` (anchors:
  `TOR_SONE_PIE_DEV`, `is_app_pkt`, `ins_app_inb`/`ins_ps_inb`, `skb_push(ETH_HLEN)`,
  the GR2 `CARD_INDEX_*` list, `skb->vlan_tci=0`, `__vlan_hwaccel_clear_tag`,
  `skb_protocol_get_inb`, `PACKET_HOST`, `netif_receive_skb`, `RX_HANDLER_CONSUMED`);
  installed by `sone_register_pltfm_rx_handlers` / `sone_netdev_event`
  (`netdev_rx_handler_register(dev, ps_sone0_rx_handle_frame)`). (2026-07-08 source read.)
- **notes**: The two dummy/skb_push sites here are ORTHOGONAL to the
  `lcnd_sone_inband_decap` dummy-eth sites (KSTACK-017) -- this is the ASIC->ps-inb
  handoff, before LCND. Sibling non-SONE handlers (`ps_tah_/ps_triton0_/ps_tof_/
  ps_tera0_rx_handle_frame`) hardcode `skb->protocol=htons(0xf102)` rather than
  calling `skb_protocol_get_inb`. Which redirect/GR2/mbit arm fires is
  card-index-dependent (unverified from code alone; decode `my_card_index`).

### KSTACK-031: skb_protocol_get_inb / skb_protocol_get_mgmt are klm_psdev-owned fn-ptrs SET by klm_vdc
- **scope**: `skb_protocol_get_inb`/`skb_protocol_get_mgmt` fn-ptrs; `psdev_main.c` (def) + `klm_vdc.c` (setter)
- **status**: verified
- **date**: 2026-07-08
- **tags**: psdev, klm_vdc, skb_protocol_get_inb, skb_protocol_get_mgmt, fn-ptr, export-symbol, eth_type_trans_inb, vdc, ethertype
- **fact**: `skb_protocol_get_inb` and `skb_protocol_get_mgmt` are global function
  pointers DEFINED and `EXPORT_SYMBOL`'d in `psdev_main.c` (`klm_psdev`), but their
  VALUES are installed by a DIFFERENT module, `klm_vdc`. In `psdev_main.c`:
  `skb_protocol_get_inb = NULL` initially; `skb_protocol_get_mgmt = eth_type_trans`
  initially. In `klm_vdc.c`, `vdc_module_init()` sets `skb_protocol_get_mgmt =
  eth_type_trans_mgmt; skb_protocol_get_inb = eth_type_trans_inb;` and
  `vdc_module_exit()` sets both back to `NULL` -- both under
  `#if defined(DC3_PLATFORM)||defined(INS_EOR)` && `#if defined(SUP2DC3)||defined(INS_EOR)`.
  Consequence: every klm_psdev RX handler guards the call with
  `if (skb_protocol_get_inb)`, so before klm_vdc loads the skb keeps its incoming
  `skb->protocol` (no VDC queue-ethertype classification), and some paths
  (mgmt/eobc) treat a NULL fn-ptr as a drop path ("skb_protocol_get_inb is null").
  This is why the SONE RX classification ties to the VDC punt ethertypes
  (`0xf102/f103/f104/fcfc`, KSTACK-014).
- **evidence**: `psdev_main.c`: `unsigned short (*skb_protocol_get_inb)(...) = NULL;
  EXPORT_SYMBOL(skb_protocol_get_inb);` and `(*skb_protocol_get_mgmt)(...) =
  eth_type_trans; EXPORT_SYMBOL(...)`; comment "klm_vdc (which sets up
  skb_protocol_get_inb) is installed"; drop trace "skb_protocol_get_inb is null".
  `standalone/platform/storage/sup/kspace/vdc/klm_vdc.c`: `vdc_module_init` assigns
  `eth_type_trans_inb`/`eth_type_trans_mgmt`; `vdc_module_exit` NULLs them (grep the
  symbol names -- cscope `-0` did NOT index `skb_protocol_get_inb`, so anchor by
  scoped grep of the fn-ptr name, not cscope). (2026-07-08 source read.)
- **notes**: Answers "who sets skb_protocol_get_inb" = klm_vdc's `vdc_module_init`
  (impl `eth_type_trans_inb`, in the vdc dir alongside klm_vdc.c). The
  klm_psdev<->klm_vdc split is load-order-sensitive: klm_psdev can be up and
  receiving before klm_vdc installs the pointer. Related: KSTACK-014 (VDC punt
  ethertypes), KSTACK-030 (the RX call site).

### KSTACK-032: SONE ASIC netdev(s) that carry ps_sone0_rx_handle_frame, keyed by card index
- **scope**: `sone_register_pltfm_rx_handlers` + `is_sone0_dev` + init_module SONE arm, `psdev_main.c` (`klm_psdev`); Silicon One
- **status**: verified
- **date**: 2026-07-09
- **tags**: psdev, ps_sone0_rx_handle_frame, leaba0_0, pie-eth0, leaba12_0, leaba11_5, leaba11_0, TOR_SONE_KPKT_DEV, card-index, is_dpu_tor, vmachine, sone, rx-registration
- **fact**: The upstream ASIC-side RX handler `ps_sone0_rx_handle_frame` (which redirects a
  punted frame onto `ins_ps_inb`/`ins_app_inb`, KSTACK-030) is installed on a card-index-dependent
  set of ASIC netdevs. Two registration sites resolve the SAME name set from `my_card_index`, so
  init and deferred paths do not diverge: (a) `sone_register_pltfm_rx_handlers()` at init
  (`netdev_rx_handler_register(dev, ps_sone0_rx_handle_frame, NULL)` for each name found via
  `dev_get_by_name`); (b) `sone_netdev_notifier`->`sone_netdev_event` on `NETDEV_REGISTER`, gated by
  `is_sone0_dev(dev)` (same switch). The init_module SONE arm is an EXPLICIT card-index allowlist:
  `TP_WBOX_CHURCHILL, TP_WBOX_THUNDER, LAKEFRONT, ALLAGASH, SPACEDUST, EASTLAKE, DANSBERG, DESCHUTES,
  CROCODILE, BUD_LIGHTNING, MUSTANG, BUD_LIGHTNING_X, SARGO, OPTIMATOR_X, OPTIMATOR` -> calls
  `sone_register_pltfm_rx_handlers()` + `register_netdevice_notifier(&sone_netdev_notifier)`.
  Dev-name macros (`psdev_main.c`): `TOR_SONE_KPKT_DEV="leaba0_0"`, `TOR_SONE_GR2_KPKT_DEV="leaba12_0"`,
  `TOR_SONE_P200_KPKT_DEV="leaba11_5"`, `TOR_SONE_PIE_DEV="pie-eth0"`, `TOR_SONE_GR2_AMD_KPKT_DEV="leaba11_0"`.
  Card-index -> netdev(s):
  - GR2 group `{BUD_LIGHTNING, OPTIMATOR, BUD_LIGHTNING_X, SARGO}` && `!vmachine` -> `leaba12_0`.
  - `MUSTANG` && `!vmachine` -> `leaba11_5`.
  - `is_dpu_tor` `{DESCHUTES, DANSBERG}` -> `leaba0_0` + `pie-eth0` (two devs).
  - `OPTIMATOR_X` -> `leaba11_0` + `leaba12_0` (two devs; no vmachine guard).
  - default (all other SONE-arm indices, incl. GR2/MUSTANG when `vmachine`) -> `leaba0_0`.
  Parent wiring: for a `pie-eth0` match under `is_dpu_tor`, `ins_app_inb->parent_dev = dev` (ps-svc-inb);
  otherwise `ins_ps_inb->parent_dev = dev` (ps-inb).
- **evidence**: `psdev_main.c` -- dev macros L175-179; `is_sone0_dev` card-index switch L181-208;
  `sone_register_pltfm_rx_handlers` name switch + `netdev_rx_handler_register(dev, ps_sone0_rx_handle_frame, NULL)`
  + parent_dev wiring L3385-3428; `sone_netdev_event` `NETDEV_REGISTER` gate `is_sone0_dev`/`is_mgmt_dev` and
  register L3222/L3282-3291; init_module SONE allowlist -> `sone_register_pltfm_rx_handlers()` +
  `register_netdevice_notifier(&sone_netdev_notifier)` L4490-4507. (2026-07-08 source read.)
- **notes**: Caveats that static readers miss: (1) the `!vmachine` gate means GR2/MUSTANG use their
  `leaba12_0`/`leaba11_5` dev only on bare metal; under `vmachine` they fall to default `leaba0_0`.
  OPTIMATOR_X has no vmachine guard. (2) `pie-eth0` (parent of `ins_app_inb`/ps-svc-inb) is DPU-TOR-only;
  every other SONE card feeds a single ASIC netdev into `ins_ps_inb`. (3) SONE-family ASIC != this handler:
  SONE cards OUTSIDE the allowlist do NOT get `ps_sone0_rx_handle_frame` -- N9800 sups (THE_CHILD_RP_1/GROGU_RP
  -> `init_mando_specific`), TITAN/TITAN_SUP -> `knet_netdev_notifier`, Nvidia TOR -> `register_nvdia_netdevice_notifier`,
  modular fabric/LC. (4) The mgmt netdev on these cards gets `mgmt_rx_handle_frame`, not `ps_sone0_...`.
  Codename->PID mapping lives in FLOW-006 (`references/hw-codenames-sone.md`); PIDs/card-index membership are
  VOLATILE -- anchor on the `CARD_INDEX_*`/`TOR_SONE_*_DEV` macros and re-derive live card via METHOD-016 /
  `SW_CARD_ID_IS_WITH_SONE_FAMILY_ASIC` (KSTACK-028). Registration-side companion to FLOW-004/KSTACK-019 and
  the RX datapath FLOW-007/KSTACK-030.
- **TX-parent coupling (2026-07-08)**: `psd_priv->parent_dev` (the dev `psdev_start_xmit` re-points TX to,
  KSTACK-020) is SET at these SAME rx-handler register sites, to the SAME ASIC `dev`: init
  `sone_register_pltfm_rx_handlers` (`ins_app_inb->parent_dev=dev` for `pie-eth0` under `is_dpu_tor`, else
  `ins_ps_inb->parent_dev=dev`) and deferred `sone_netdev_event` `NETDEV_REGISTER` (same, with `dev_hold`).
  So RX-capture dev == TX-egress dev. It starts NULL from `ins_psuedo_dev_create` (zeroed priv), so before
  registration `psdev_start_xmit` takes the `else` -> `dev_kfree_skb` DROP; it is cleared to NULL on
  `sone_netdev_event` `NETDEV_UNREGISTER` and in `psdev_unregister_rx_handlers` (module exit/cleanup;
  `dev_put`+`netdev_rx_handler_unregister`+`synchronize_rcu`). Other
  platforms set the same field at their own register sites (Tahoe/Teralynx/Tofino/Triton/MTC/kNET/Nvidia; TITAN
  via `psdev_active_gmac_set`). Anchors: `parent_dev`, `sone_register_pltfm_rx_handlers`, `sone_netdev_event`,
  `psdev_start_xmit`, `psdev_unregister_rx_handlers`.
- **CORRECTION (2026-07-09)**: an earlier draft of this note (and the psinb architecture doc) said
  `parent_dev` is cleared / handlers torn down in `psdev_swover_sone` "(ISSU)". That is WRONG for the
  CURRENT codebase: `psdev_swover_sone` is a NO-OP stub -- it only logs "psdev-sone:swover_trigger:
  Ignoring swover ISSU for intf %s" and returns 0. SONE deliberately does NOT re-install/tear-down on
  LXC/ISSU swover (persistent pseudo devs + `sone_netdev_notifier` keep handlers valid). The real teardown
  is `psdev_unregister_rx_handlers` (releases `ins_ps_inb`/`ins_app_inb` `parent_dev` + `mgmt_dev`) plus the
  `sone_netdev_event` `NETDEV_UNREGISTER` case. Tahoe/knet DO re-install on swover (`psdev_swover_tahoe`/
  `psdev_swover_knet`). NOTE per user: OLDER RELEASES still carry active SONE swover code here, so
  cross-release backports/comparisons must not assume the no-op. Evidence: `psdev_swover_sone` body
  (KERN_INFO "Ignoring swover ISSU"), `psdev_unregister_rx_handlers` body, `psdev_swover_trigger` dispatch
  table (calls `psdev_swover_sone` for SONE dev names). (2026-07-09 source read.)
- **dev-name churn lineage + non-bugs (2026-07-10)**: earlier releases briefly mapped GR2/Mustang to
  other `leaba*` names (CSCwq14353/CSCwq12457); CSCwu22649 settled Mustang on `leaba11_5` and commented
  it OUT of the GR2 (`leaba12_0`) arm — so seeing Mustang grouped with GR2 in `ps_sone0_rx_handle_frame`
  is only the eth-restore `skb_push(ETH_HLEN)` normalize, NOT a dev-name mapping. Two claimed latent bugs
  were CHECKED and RULED OUT against current `nx_main`: (a) each `strncmp(dev->name, TOR_SONE_*_DEV,
  sizeof(TOR_SONE_*_DEV))` uses its OWN macro's `sizeof`, so there is no shorter-literal length hazard;
  `leaba5_0` is fully retired (zero occurrences). (b) the `is_dpu_tor` app-inband path (`pie-eth0` →
  `ins_app_inb`/ps-svc-inb) is ACTIVE, not disabled — gating is `is_dpu_tor` (DESCHUTES/DANSBERG), not a
  `is_dansberg_tor` symbol (which does not exist). Diagnostics: `if (sdk_headroom_debug)` (extern int,
  default 0) in `ps_tahoe_rx_handle_frame`/`lcnd_n9k.c` stamps `skb->head[6]=0xc` (debug only, conflicts
  with app-hosting, CSCwf20380 — do not enable in production); `psdev.cmd` events node carries
  `tid 1 cid 298` so `sdw_get_history` resolves the app_id (CSCwd64632).
- **latent SW_CARD_ID vs CARD_INDEX namespace-mix in cleanup allowlist (2026-07-10, verified)**: The
  SONE arm of `psdev_cleanup_tor_specific` (the `else if` OR-chain that calls
  `psdev_unregister_rx_handlers()`) keys off `my_card_index`, which is a `CARD_INDEX_*` value
  (`card_data.h`), and every other term is `my_card_index == CARD_INDEX_*` — but TWO terms wrongly test
  the `SW_CARD_ID_*` namespace: `(my_card_index == SW_CARD_ID_TP_WBOX_THUNDER)` and
  `(my_card_index == SW_CARD_ID_GAMUT)`. `SW_CARD_ID_*` lives in a DIFFERENT header/value space
  (`sw_card_id.h`) from `CARD_INDEX_*` — this is exactly the mix KSTACK-023 warns against. Currently
  INERT (the Thunder/Gamut cleanup defect CSCwp31322 was Junked; `CARD_INDEX_TP_WBOX_THUNDER` is already
  present in the same chain, making the `SW_CARD_ID_TP_WBOX_THUNDER` term redundant as well as
  wrong-namespace) but a real latent correctness bug: if a live `my_card_index` ever equals one of those
  `SW_CARD_ID_*` numeric values, the SONE teardown arm fires for the wrong card (or the intended GAMUT
  card is silently skipped). Fix = compare against `CARD_INDEX_GAMUT` (or drop the redundant Thunder
  line). Evidence: `psdev_cleanup_tor_specific` SONE `else if` in `psdev_main.c` — the two
  `my_card_index == SW_CARD_ID_*` terms amid a `CARD_INDEX_*` chain. Anchor on
  `psdev_cleanup_tor_specific` + the `SW_CARD_ID_`/`my_card_index` mix, not line numbers.
  (2026-07-10 origin/nx_main @9b61f1c546f read; KLM_PS_INB Proposal 6.)

### KSTACK-033: klm_vdc module = /dev/klm_vdc char driver with 5 VDC lookup tables
- **scope**: `klm_vdc.c` (init/exit) + `klm_vdc_char.c` (char dev/tables); all platforms
- **status**: verified
- **date**: 2026-07-09
- **tags**: klm_vdc, char-device, ioctl, vdc-table, si_vdc_map_table, mgmt_vdc_table
- **fact**: `klm_vdc` is a char-only misc driver. `vdc_module_init` -> `vdc_char_init`
  registers chrdev name "klm_vdc" (node `/dev/klm_vdc`), then installs the klm_psdev
  fn-ptrs (KSTACK-031). `vdc_fops` wires ONLY `unlocked_ioctl=vdc_chr_ioctl` +
  `compat_ioctl=vdc_chr_compat_ioctl` (forwards unchanged); no read/write/open/release.
  It maintains 5 hash tables of doubly-linked entries: `si_vdc_map_table[4096]`
  (INBAND src_index->vdc), `ifindex_vdc_map_table[128]` (IPS), `ip_vdc_map_table[256]`
  (MGMT ip), `mgmt_vdc_table[32]` (vdc->state/ifindex/receive_lldp),
  `mgmt_mcast_table[32]` (mcast ip->vdcid_map bitmap); plus `vdc_global_q`,
  `vdc_global_cpuq_map`(INS_EOR), `global_stats`. Hash = `vdc_table_hash` (klm_vdc.h).
- **evidence**: `vdc_module_init`/`vdc_module_exit` (`klm_vdc.c`); `vdc_char_init`
  `vdc_register_chrdev(major,"klm_vdc",&vdc_fops)`, `vdc_fops`, the table arrays and
  `vdc_table_hash` (`klm_vdc_char.c`, `klm_vdc.h`); node `/dev/klm_vdc` in
  `libvdcklm.c`. (2026-07-09 source read.)
- **notes**: Bug candidate: `vdc_char_cleanup` unregisters name "vdc_klm" (register
  used "klm_vdc"). No /proc export -> tables only readable via getnext ioctl.

### KSTACK-034: klm_vdc ioctl surface + who programs each VDC table
- **scope**: `vdc_chr_ioctl` (`klm_vdc_char.c`) + `libvdcklm.c`; control plane
- **status**: verified
- **verification**: full (all writer chains resolved via scoped `rg`; see FLOW-009)
- **date**: 2026-07-09 (writer set corrected 2026-07-09; see notes)
- **tags**: klm_vdc, ioctl, interface-manager, pcm, mcec, mcm, ip, igmp, coppmgr,
  aclqos, lldp, poap, pnp, pm, gold, vdc-programming
- **fact**: Userspace programs klm_vdc via `libvdcklm.c` -> `ioctl(/dev/klm_vdc,
  VDC_IOC_*)` (a few callers open the dev + issue the ioctl directly). Verified
  programmers per table (full chains + conditions in **FLOW-009**): INBAND
  `si_vdc_map_table` (`vdc_add_src_index_mapping`) + IPS `ifindex_vdc_map_table`
  (`vdc_add_ifindex_mapping`) <- **Interface Manager** (module/LC/intf bring-up:
  `im_evseq_lc_inseor.c`, `im_module_fsm_ac.c`, `im_vdc_fsm_ac.c`, `im_c3.c`,
  `im_inseor.c`, `im_mds.c`), **PCM** (`eth_pcm_*`), **MCEC** (`mcecm_*`
  es_common_lid), **MCM** (`mcm_app.c`); MGMT ip map (`vdc_add_ipaddr_mapping`) <-
  **IP** (`ip_ui.c ip_address_add` on mgmt0, `ip_init.c` teardown; `ipconf_stub.c`
  is `#if 0` DEAD); mgmt_vdc_table (`mgmt_vdc_upd`/`mgmt_vdc_del`) <- **IM** mgmt-FSM
  + `vdc_mgr_ungraceful.c`; mgmt_mcast_table (`klm_vdc_add_mcast_entry`) <- **IP/IGMP**
  (`ip_init.c ip_join_group_internal`, mgmt iod only); LLDP `0x88cc`
  (`klm_vdc_rx_protocol_packets`) <- **LLDP via `dlopen`/`dlsym`** (`lldp_db.c`);
  `VDC_IOC_CPUQ_COSQ_MAP` <- **coppmgr** (`copp_cfg_fsm_ac.c copp_update_cosq_cpuq`) +
  per-ASIC **aclqos** (direct ioctl); q-remap/clear-stats/timestamp/GDB <- **PM CLI**
  (`pm_ui.c`); bcast <- **PnP/POAP**; diag-vlan <- **GOLD** (`diag_port_lb_diag.c`).
  `VDC_IOC_SET_DBG` (`klm_vdc_set_debug`) is **test-tool-only** (`klm_vdc_test.c`).
- **evidence**: `vdc_chr_ioctl` switch + opcodes in `export/isan/klm_vdc_intf.h`;
  scoped-`rg` caller reads (as-of 2026-07-09): `mgmt_vdc_upd` (im_db.c:928,
  im_mgmt_fsm_ac.c:583/635), `klm_vdc_add_mcast_entry` (ip_init.c:4555/4581),
  `vdc_add_src_index_mapping` (im_evseq_lc_inseor.c:4072, im_module_fsm_ac.c:7315,
  eth_pcm_msg_handlers.c:4490, mcm_app.c:796, mcecm_pd_intf.c:1066),
  `vdc_add_ipaddr_mapping` (ip_ui.c:2253), `klm_vdc_rx_protocol_packets`
  (lldp_db.c:520 via dlsym), `VDC_IOC_CPUQ_COSQ_MAP` (copp_cfg_fsm_ac.c:907,
  aclqos_*_copp.c), `klm_vdc_enable_mgmt_bcast_pkts` (pnp_net.c:119/241,
  poap_dhcpdiscover.c:2212/2275), PM wrappers (pm_ui.c). See FLOW-009.
- **notes**: CORRECTION (2026-07-09): the earlier "INBAND `si_vdc_map_table` writer
  has NO in-tree caller -> legacy/unprogrammed" was **WRONG** — an artifact of cscope
  `-3` silently under-reporting on this DB (METHOD-014). Scoped `rg` shows IM/PCM/MCEC/MCM
  program it heavily on interface/module lifecycle; it is a datapath-critical table, not
  legacy. `VDC_IOC_CTRL_TIMESTAMP` opcode: caller exists (`pm_ui.c`); whether the kernel
  `vdc_chr_ioctl` implements its `case` is a separate READ-side check, not re-confirmed
  this pass. Related KSTACK-035 (reader), FLOW-009 (full writer chains).
- **security note (2026-07-10)**: the `VDC_IOC_CTRL_Q_MAP` (q-remap, PM-CLI writer) case now
  bounds-checks the caller-supplied `ctrl_q_type` against `ARRAY_SIZE(vdc_global_q.map)` and dispatches
  `SET_Q_MAPPING`/`GET_Q_MAPPING`/`-EINVAL` explicitly — OOB-write fix, KSTACK-037 (CSCwu19801).

### KSTACK-035: si_vdc_eth_type_trans platform dispatch (all ASIC families) + SONE classifier
- **scope**: `si_vdc_eth_type_trans` + `sone_si_vdc_eth_type_trans`, `klm_vdc_char.c`;
  platform: Silicon One (others enumerated)
- **status**: verified
- **date**: 2026-07-09
- **tags**: klm_vdc, si_vdc_eth_type_trans, sone, my_card_index, source_sp, egress-trap,
  rcy-port, g200, gr2, platform-dispatch, eth_type_trans_inb
- **fact**: `eth_type_trans_inb` -> `eth_type_trans_with_port_type(PORT_TYPE_INBAND)`
  -> `si_vdc_eth_type_trans`, which dispatches on `my_card_index`/`lcnd_is_card_vp_*`
  to per-ASIC classifiers: SONE-VP (`sone_vp_*`), Tahoe (`tah_*`, big card list +
  `lcnd_is_tah_fabric`), Nvidia (`nvdia_*`), Titan (returns default), MTC (`mtc_*`,
  COLLINA), Barefoot (`bfn_*`, SHADOW_PUPPET/BODDINGTONS), Innovium (`inno_*`), SONE
  native (`sone_si_*`, card list incl. DESCHUTES/DANSBERG/BUD_LIGHTNING/MUSTANG/
  OPTIMATOR/SARGO...), and the INS_EOR Fretta/N3K-T+/Broadcom DCB path. In
  `sone_si_vdc_eth_type_trans`: outer eth+slot+card_id via external
  `lcnd_get_outer_eth_hdr`/`lcnd_get_slot_from_smac_eth_hdr`/`mod_card_ids`; punt hdr
  byte-swapped to `la_packet_punt_header_t`; FPT (INBOUND_MIRROR + mirror-GID range)
  and BFD (INSIEME_SUP_CODE_BFDC) short-circuits; `src_index = punt_hdr->source_sp`;
  `vdc_table_lookup(PORT_TYPE_INBAND)`; on hit -> `klm_vdc_char_get_q_eth_type`
  (bpdu/ARP/cos -> Q ethertype, KSTACK-014); on miss, force vdc_id=1 only for
  (THE_CHILD_RP_1/GROGU_RP EGRESS_TRAP MTU/TTL, source_sp=0xffff) or per-card RCY
  ports; else return 0 (caller falls back to real eth_type_trans). Per-PID branches:
  G200/GR2 set reads cos from outer PCP; G200 skips the egress-trap ttl++ workaround;
  MUSTANG keeps outer cos (CSCwu02678 dummy dot1q).
- **evidence**: `si_vdc_eth_type_trans` dispatch chain + `sone_si_vdc_eth_type_trans`
  body (anchors `lcnd_is_card_vp_sone_tor`, `CARD_INDEX_*` lists, `source_sp`,
  `LCND_SONE_LA_PACKET_PUNT_SOURCE_EGRESS_TRAP`, RCY hex ranges, `klm_vdc_char_get_q_eth_type`),
  `eth_type_trans_with_port_type`/`eth_type_trans_inb`, `klm_vdc_char.c` (2026-07-09).
- **notes**: Which arm fires is `my_card_index`-dependent (unverified from code; decode
  via show module/version, FLOW-006/METHOD-016). Non-SONE arms not deep-walked
  (backlog). RX twin of the punt chain FLOW-007; consumer of the table in KSTACK-034.
- **SONE classifier detail (2026-07-10, from KLM_VDC PR pass — verified @1c59b6e):**
  - **TTL++ egress-trap workaround** (repairs checksum for asic-decremented MTU/TTL punts) is SKIPPED
    for the G200 families via `!lcnd_is_card_id_sone_g200_family(card_id) && !lcnd_is_card_id_sone_g2ll_family(card_id)`,
    and the trap match is card-aware: `LCND_CHECK_TRAP_CODE(punt_hdr->code, L3_TX_MTU_FAILURE|L3_TTL_OR_HOP_LIMIT_IS_ONE, card_id)`
    (not a raw `LA_EVENT_*` compare). The VNX/VP handler mirrors it via `sone_vp_update_ipv4_ttl()`.
  - **Recycle-port (RCY) force `vdc_id=1`** ranges are card-gated `src_index` sets:
    `CARD_INDEX_LAKEFRONT` `0x9a–0x9d`, `CARD_INDEX_DANSBERG` `0x7a–0x7d`, `CARD_INDEX_DESCHUTES` `0xfa–0xfd`
    → `klm_vdc_char_get_q_eth_type(1, …)` (loopback/GQ punts that miss `vdc_table_lookup`).
  - **CoS source is per-family**: Nvidia/GAMUT path (`nvdia_si_vdc_eth_type_trans`) uses
    `cos = isx_hdr->etclass & 0x07`; SONE native reads outer-dot1q PCP (G200/GR2). `GAMUT`/`TP_WBOX_CABO`
    dispatch to the **Nvidia** classifier, not SONE-native (already in klm-vdc arch §7.4).
  - **Short-circuit ethertypes**: `ETH_P_FPT = 0xfbfc` (FPT/INBOUND_MIRROR mirror-copy; NOTE `0xfbfc`
    also aliases `ETH_P_MACSEC_GOLD` — kept in sync with `lcnd_n9k.c`) and `ETH_P_BFD = 0xfbfd`
    (returned when the UDP dport ∈ {`BFD_SH_PORT`=3784, `BFD_ECHO_PORT`=3785, `BFD_IETF_MICRO_PORT`=6784,
    `BFD_MH_PORT`=4784, `BFD_VXLAN_PORT`=4789} AND the punt decodes to `INSIEME_SUP_CODE_BFDC`). These pair
    with the KSTACK-014 VDC punt ethertypes.

### KSTACK-036: klm_psdev cleanup force-zeros ins_ps_inb refcnt (CSCwn95874) — symptom fix, UAF holder still open
- **scope**: `cleanup_module` teardown of `ins_ps_inb`, `psdev_main.c` (`klm_psdev`); Silicon One
- **status**: verified
- **verification**: full (current source read)
- **resolution**: open (root-cause holder unfixed; mitigation only)
- **date**: 2026-07-10
- **tags**: psdev, ps-inb, refcnt, pcpu_refcnt, unregister_netdevice, uaf, cscwn95874, teardown, cleanup_module
- **fact**: On module unload `cleanup_module` calls `unregister_netdevice(ins_ps_inb)` then
  `msleep(250)`; if `netdev_refcnt_read(ins_ps_inb)` is still non-zero it waits another 250ms
  (`KERN_EMERG "PSDEV refcnt %d (waited 500ms for rcu complete)"`) and, if STILL non-zero,
  FORCE-ZEROES the per-CPU refcount under `rtnl_lock`:
  `for_each_possible_cpu(cpu) *per_cpu_ptr(ins_ps_inb->pcpu_refcnt, cpu) = 0;`
  (`KERN_EMERG "PSDEV refcnt %d !=0 after 500ms, cleaning up!!!"`). This is a SYMPTOM mitigation
  for the `unregister_netdevice: waiting for ps-inb to become free` hang — it unblocks teardown but
  does NOT identify/release the leaked-reference HOLDER, so the root cause is unaddressed and
  force-freeing a still-referenced netdev is a UAF hazard. `psdev_swover_sone` is a no-op
  (KSTACK-032), so the leak is not a swover artifact.
- **evidence**: `cleanup_module` body in `psdev_main.c` — `unregister_netdevice(ins_ps_inb)`,
  the two `msleep(250)` + `netdev_refcnt_read` checks, the `for_each_possible_cpu` /
  `*per_cpu_ptr(ins_ps_inb->pcpu_refcnt, cpu) = 0` loop, and the `KERN_EMERG "...cleaning up!!!"`
  string; older `dev_put`-based attempt retained as `#if 0` dead code. (2026-07-08 origin/nx_main read.)
- **notes**: CSCwn95874 RCA attributes the leak to a soft-irq/RCU refcnt holder left over after
  ND-ISSU; that holder is not released here. Pre-unregister refcnt diagnostic log = CSCwo50755;
  the spurious post-cleanup log was removed by CSCwr61572. Teardown ordering (KSTACK-019/ADR-010):
  `tearing_down` guard (unconditional event drop, CSCwu25924) → `psdev_unregister_rx_handlers` +
  `unregister_netdevice_notifier(&sone_netdev_notifier)` → `unregister_psinb_rx_handlers` → this
  `ins_ps_inb` unregister + refcnt force-zero. Anchor on `pcpu_refcnt`/`netdev_refcnt_read`/the
  KERN_EMERG strings, not line numbers.

### KSTACK-037: klm_vdc VDC_IOC_CTRL_Q_MAP bounds-checks ctrl_q_type (CSCwu19801, OOB kernel write)
- **scope**: `vdc_chr_ioctl` case `VDC_IOC_CTRL_Q_MAP`, `klm_vdc_char.c` (`klm_vdc`); all platforms
- **status**: verified
- **verification**: full (current source read)
- **resolution**: fixed (CSCwu19801)
- **date**: 2026-07-10
- **tags**: klm_vdc, ioctl, vdc_global_q, ctrl_q_type, oob-write, security, cscwu19801, psirt
- **fact**: `VDC_IOC_CTRL_Q_MAP` used a caller-supplied `qmap_entry.ctrl_q_type` directly as an index
  into `vdc_global_q.map` (`ARRAY_SIZE(vdc_global_q.map)` == 6 entries: BPDU_Q/Q0/Q1/ARP_Q...) with no
  bound → out-of-bounds kernel read/write. The fix adds
  `if (qmap_entry.ctrl_q_type >= ARRAY_SIZE(vdc_global_q.map)) return -EINVAL;` inside the
  `SET_Q_MAPPING` arm (BEFORE both the debug `printk` that reads `vdc_global_q.map[ctrl_q_type]` and the
  assignment `vdc_global_q.map[ctrl_q_type] = qmap_entry.map_to_q`), and dispatches the op explicitly:
  `SET_Q_MAPPING` / `GET_Q_MAPPING` / else `return -EINVAL`. No `/dev/klm_vdc` permission/capability
  change (admin CLI/debug access preserved) — hardening of unvalidated userspace input only.
- **evidence**: `vdc_chr_ioctl` `case VDC_IOC_CTRL_Q_MAP` body in `klm_vdc_char.c` — the
  `ctrl_q_type >= ARRAY_SIZE(vdc_global_q.map)` guard, the `SET_Q_MAPPING`/`GET_Q_MAPPING`/`-EINVAL`
  branch shape, and `vdc_global_q.map[qmap_entry.ctrl_q_type] = qmap_entry.map_to_q`. Writer =
  `vdc_set_q_mapping` in `pm_ui.c` → `ioctl(VDC_IOC_CTRL_Q_MAP)` (`libvdcklm.c`; KSTACK-034/FLOW-009).
  `vdc_global_q` = 6-entry BPDU/Q0/Q1 remap table (KSTACK-033). Commit `CSCwu19801 Out-of-bounds kernel
  write in klm_vdc control queue map ioctl`. (2026-07-10 origin/nx_main @1c59b6e read.)
- **notes**: Anchor on `ARRAY_SIZE(vdc_global_q.map)` / `SET_Q_MAPPING` / `GET_Q_MAPPING`, not line
  numbers. The queue table itself and its ethertype mapping are KSTACK-033/KSTACK-014.

### KSTACK-038: KIM interface/vlan AVL DBs (g_kim_cfg) + DB-writes-PSS coupling
- **scope**: `kim_db.c` (KIM control-plane DB); platform-independent
- **status**: verified
- **verification**: full (re-verified against current source 2026-07-11)
- **date**: 2026-07-10
- **tags**: kim, avl, g_kim_cfg, pss, db
- **fact**: KIM's interface DB is an AVL `g_kim_cfg.kim_intf_tree_root` (key `if_index_t`,
  node `lc_if_info_avl_t`) and its vlan DB an AVL `g_kim_cfg.kim_vlan_tree_root` (key
  `uint16 vlan`, node `vlan_info_avl_t`), both inside the single global
  `kim_config_t g_kim_cfg` (which also holds `num_{phy,pc,si,vlan,tn,inband,loopback,vni,
  sat_phy}_intf` + `num_intf`). Writers: `kim_insert_intf_in_db` / `kim_del_intf_from_db` /
  `kim_upd_intf_in_db` (intf); `kim_insert_vlan_in_db` / `kim_del_vlan_from_db` (vlan).
  CRITICAL coupling -- each writer ALSO writes PSS in the SAME function: intf insert ->
  `kim_update_intf_cnt(1,..)` + `pss_oper = KIM_PSS_OPER_INTF_ADD` + `kim_pss_intf_info`;
  intf delete -> `kim_update_intf_cnt(0,..)` + `kim_pss_delete_intf`; vlan insert ->
  `kim_pss_vlan_info`; vlan delete -> `kim_pss_delete_vlan`. Counters change ONLY inside
  insert/delete. Roots created at sysmgr init by `kim_intf_db_init`/`kim_vlan_db_init`.
- **evidence**: 2026-07-11 read of `kim_db.c`: `kim_insert_intf_in_db` (L174:
  `ravl_insert(&g_kim_cfg.kim_intf_tree_root, ...)` L176, `kim_update_intf_cnt(1,..)`
  L182, `pss_oper=KIM_PSS_OPER_INTF_ADD` L183, `kim_pss_intf_info` L184);
  `kim_del_intf_from_db` (`kim_update_intf_cnt(0,..)` L197); vlan insert
  `ravl_insert(&g_kim_cfg.kim_vlan_tree_root,...)` L304.
- **notes**: DB and PSS are NOT separable write paths -- any code touching an AVL node
  journals PSS in the same breath. Programmed from MTS handlers (`kim_create_if` via
  KIM_CREATE_NETDEV, `kim_remove_if` via IM_IF_REMOVED/IM_NVE_IF_REMOVED) and from PSS
  restore (`kim_pss_restore_intf_db`/`_vlan_db`) on ISSU. Complements FLOW-005 App E and
  `architecture/kim-process-architecture.md` §4/§6. Line numbers volatile -- anchor on
  the function/field names.
- **PSS insert/delete key symmetry (2026-07-11, CSCwt27793)**: the `kim_pss_key_t` used to DELETE must
  match the one used to INSERT. L3-VNI (`IF_INDEX_TYPE_VNI_INTF`) is keyed `KIM_PSS_KEY_SUB_INTF` (grouped
  with `LC_FLAGS_SI`/`LC_FLAGS_PORTCHANNEL`); an asymmetric key leaves stale PSS on `no vrf context`.
  Source: `kim_pss.h` `KIM_PSS_KEY_{MAIN_INTF=0, SUB_INTF=1, PC_INTF=SUB_INTF}` L155-157; `kim_pss.c` the
  VNI->SUB grouping at insert L1078 and in `kim_pss_delete_intf` L1135. Anchor on the key enum +
  `IF_INDEX_TYPE_VNI_INTF`, not line numbers.

### KSTACK-039: KIM LPSS = two lnx<->nxos ifindex maps (bidir add/del; ISSU destroy+recreate; 0xdeadbeef)
- **scope**: `kim_lpss.c` (file carries a stale `kim_pss.c` header comment); platform-independent
- **status**: verified
- **verification**: full (re-verified against current source 2026-07-11)
- **date**: 2026-07-10
- **tags**: kim, lpss, ifindex, issu, deadbeef
- **fact**: KIM keeps two LPSS DBs opened `LPSS_AM_WRITE`: `kim_lnx_if_index_handle`
  (URI `KIM_LNX_IF_HANDLE_URI`, key = nxos `if_index_t` -> val = `lnx_ns_ifindex_t`; read
  by `kim_csco_to_lnx_ifindex`) and `kim_nxos_if_index_handle` (URI `KIM_NXOS_IF_HANDLE_URI`,
  key = `lnx_ns_ifindex_t` -> val = nxos `if_index_t`; read by `kim_lnx_to_csco_ifindex`).
  Writers: `kim_if_lpss_add` (-> `kim_if_lpss_add_lnx_handle` + `_add_nxos_handle`, both
  `lpss_add(..., LPSS_ADD_OVERWRITE)`), `kim_if_lpss_delete` (both). `kim_if_lpss_init`
  creates/opens both and, when `sysmgr_is_upgrade_restart()`, DESTROYS + RECREATES them.
  `kim_if_lpss_enable_after_issu` writes a magic key `0xdeadbeef` (CSCvd39695) into LPSS
  after restore so FIB knows KIM restore is done.
- **evidence**: 2026-07-11 read of `kim_lpss.c`: `kim_lnx_if_index_handle` L21,
  `kim_nxos_if_index_handle` L22; `sysmgr_is_upgrade_restart()` destroy branch L42/L93;
  `kim_if_lpss_add_lnx_handle` `lpss_add(...,LPSS_ADD_OVERWRITE)` L157, `_add_nxos_handle`
  L177, `kim_if_lpss_add` L185; `kim_if_lpss_enable_after_issu` L325 (`nxos_if_handle =
  0xdeadbeef` L327, `lnx_ifindex = 0xdeadbeef` L329).
- **notes**: Written from `kim_create_if` (add) / `kim_remove_if` (delete) -- corroborated
  live in FLOW-005 App G.4 (`kim_if_lpss_add_{lnx,nxos}_handle` on a loopback create).
  Complements `architecture/kim-process-architecture.md` §4. Anchor on the handle/URI
  names, not line numbers.

### KSTACK-040: KIM MTS process spine (3-queue bind / register / dispatch / 3-thread loop / standby-drop)
- **scope**: `kim_mts.c`; platform-independent (fretta-only `eth_pcm` sub-table)
- **status**: verified
- **verification**: full (re-verified against current source 2026-07-11)
- **date**: 2026-07-10
- **tags**: kim, mts, dispatch, threads, registration, fretta
- **fact**: `kim_mts_bind` binds 3 queues on `LNODE_SUP` (uuid `SRVUUID_KIM`):
  `smq = mts_bind(MTS_SAP_KIM_SYSMGR, "kim_sysmgr")`, `kimq = mts_bind(MTS_SAP_KIM, "kim")`
  (main notif queue), `kim_mts_stats_q = mts_bind(MTS_SAP_DYNAMIC)`, then registers each
  `kim_notifs[]` entry via `mts_options_set(kimq, opc, MTS_OPTION_REGISTER|MTS_OPTION_PERSISTENT)`.
  Sub-tables: `kim_notifs_mcecm[]` (`kim_mts_bind_mcecm`, always) and `kim_notifs_eth_pcm[]`
  (`kim_mts_bind_eth_pcm`, guarded `if(!is_fretta) return 0` = FRETTA-ONLY). Dispatch
  `kim_notifs_get` scans `kim_notifs` -> `kim_notifs_mcecm` -> `if(is_fretta)`
  `kim_notifs_eth_pcm`. Receive loop `kim_process_single_my_msg`: `mts_recv(kimq)` ->
  reject/`sdwrap`/`fsrv` filters -> `sdwrap_hist_mts_event(E_MTS_RX)` -> if STANDBY `goto
  done` (drop MTS; standby syncs via ksink PSS instead) -> `mpmts_gather` if multi-part ->
  `kim_notifs_get(opc)` -> handler; `kim_msg_relay` once `standby_sync_done`. `kim_active_loop`
  spawns 3 pthreads: `kim_process_heart_msg`(smq), `kim_process_my_msg`(kimq),
  `kim_nb_thread_main` (`kim_nb.c`, netlink/notifier ingress).
- **evidence**: 2026-07-11 read of `kim_mts.c`: `kim_mts_bind` L1068 (smq L1084, kimq
  L1096, stats_q L1106, register loop `mts_options_set` L1116); `kim_notifs_get` L323;
  `eth_pcm` `if(!is_fretta) return 0` L371; dispatch call `kim_notifs_get(opcode)` L3348;
  `kim_active_loop` L3385 with `pthread_create` x3 L3390/L3392/L3394 (`kim_nb_thread_main`
  L3395, def `kim_nb.c` L183).
- **notes**: The `E_MTS_RX` logging here is exactly the `show kim internal event-history
  msgs` stream (FLOW-005 App G). Leading `kim_notifs[]` `#if 0` block = dead old ops.
  Complements FLOW-005 mechanism spine + `architecture/kim-process-architecture.md` §3/§5.

### KSTACK-041: KIM-as-sender MTS opcodes (DOWNLOAD_ADJ/_ROUTE to ipfib; STATEFUL_RSTRT to pktmgr/netstack)
- **scope**: `kim_mts.c` / `kim.c` / `kim_sysmgr.c` senders; platform-independent
- **status**: verified
- **verification**: full (re-verified against current source 2026-07-11)
- **date**: 2026-07-10
- **tags**: kim, mts, sender, ipfib, issu, stateful-restart
- **fact**: KIM SENDS (not just receives): (1) `MTS_OPC_KIM_DOWNLOAD_ADJ` via
  `kim_send_msg_to_ipfib` -- `mts_send(kimq, mts_local_addr(MTS_SAP_REGISTRY), ...,
  ufib_kim_if_index_info_t)` on router-mac changes (HMM + port-param paths); (2)
  `MTS_OPC_KIM_DOWNLOAD_ADJ_ROUTE` (second send-site in the adj/router-mac area); (3) the
  ISSU restore-done notifs `MTS_OPC_KIM_STATEFUL_RSTRT` (-> pktmgr) and
  `MTS_OPC_KIM_L3_STATEFUL_RSTRT` (-> netstack) via `kim_issu_send_restore_done_notif`,
  called from `kim_do_stateful_restart` after `kim_pss_recover_state_on_standby` +
  client handshake (and from `kim_sysmgr.c`).
- **evidence**: 2026-07-11 read: `kim_send_msg_to_ipfib` `kim_mts.c` L653 (`MTS_OPC_KIM_DOWNLOAD_ADJ`
  L661; callers L981/L989/L1498); `MTS_OPC_KIM_DOWNLOAD_ADJ_ROUTE` send-site L826;
  `kim_issu_send_restore_done_notif` `kim.c` L1809 (STATEFUL_RSTRT branch L1823,
  L3_STATEFUL_RSTRT L1827; callers L1859/L1862; `kim_sysmgr.c` L472/L519); timestamps
  surfaced in `kim_debug.c` L2435-2436 (`show kim internal issu-stats`).
- **notes**: `kim_send_lconf`/`MTS_OPC_INTERNAL_KIM_PSS` is `#if 0` dead. Matches FLOW-005
  App G issu-stats CLI (STATEFUL_RSTRT->pktmgr, L3_STATEFUL_RSTRT->netstack) +
  `architecture/kim-process-architecture.md` §5.2.

### KSTACK-042: KIM platform/PID handling is coarse-SONE; kim_tor.c is dead; LC_ONLINE/OFFLINE = SONE-only LCND writers
- **scope**: KIM process platform branches (`kim_mts.c`/`kim_msg_handler.c`/`kim_tor.c`/`kim.c`); Silicon One
- **status**: verified
- **verification**: full (re-verified against current source 2026-07-11)
- **date**: 2026-07-10
- **tags**: kim, platform, sone, pid, mirror-gid, recycle-port, tor, flex-port
- **fact**: (1) `kim_tor.c` is ENTIRELY `#if 0` (L1..L87) -> `kim_is_tor_env` /
  `kim_get_container` / `kim_get_container_role` / `kim_update_to_kernel` are dead (no
  external callers); SONE ToR logic in this build runs via `container_id` /
  `libutils_vchassis_tor_env()` gates in `kim.c`/`kim_mts.c`, not this file. (2) The KIM
  process branches SONE only at COARSE granularity: `libutils_is_card_sone()` (generic
  family), `libutils_is_card_sone_gr2()` (G200/GR2 only; used at `kim.c` L1138 inside a
  `!libutils_is_card_innovium() && !libutils_is_card_sone_gr2()` guard),
  `libutils_is_card_sup_sone_virt_platform()` (VP, resolves card_id via
  `libutils_get_sw_card_id_tahoe_vp`). The FINE ASIC PIDs (Krypton/P200/Gibraltar/G2LL)
  are NOT branched in KIM -- that per-PID work lives in LCND/klm_vdc/SDK (`la_event.h`).
  (3) LC_ONLINE/LC_OFFLINE handlers are `if(!libutils_is_card_sone()) return`-gated and
  PROGRAM LCND: `kim_process_lc_online` -> `kim_program_mirror_gid(...,FALSE)`
  (`LC_ND_MIRROR_GID_SET`) + `kim_process_recycle_ports` (-> `libpixm_sone_get_recycle_port_details`
  -> `kim_fill_recycle_port_info` sets `LC_ND_RCY_PORT_GID_SET`); `kim_process_lc_removed`
  -> `kim_program_mirror_gid(...,TRUE)` (`LC_ND_MIRROR_GID_DEL`). (4) SONE-only extras:
  `g_kim_vxlan_mct_rsvd_vlan` (`LC_ND_RSVD_VLAN` via `kim_prgm_mct_rsvd_vlan`), flex-port-Q
  on `SW_CARD_ID_PARIS`/`SW_CARD_ID_BERLIN` && `port_num > KIM_FLEX_PORT_OFFSET_PLTFM_PARIS`
  (`kim_is_flex_port_supported` -> `kim_update_flex_port_qbase` -> `LC_ND_SET_FLEX_PORT_Q`).
- **evidence**: 2026-07-11 read: `kim_tor.c` `#if 0` L1 / `#endif` L87; `kim_mts.c`
  `kim_process_lc_online` L551, SONE gate L561, `kim_program_mirror_gid(...,FALSE)` L595,
  `kim_process_recycle_ports` L597; `kim_process_lc_removed` L610, gate L618,
  `kim_program_mirror_gid(...,TRUE)` L640; `LC_ND_RCY_PORT_GID_SET` in
  `kim_fill_recycle_port_info` L420; `g_kim_vxlan_mct_rsvd_vlan` gate L709;
  `kim_msg_handler.c` `kim_is_flex_port_supported` L923 (`SW_CARD_ID_PARIS||BERLIN` L929,
  `> KIM_FLEX_PORT_OFFSET_PLTFM_PARIS` L930), `LC_ND_SET_FLEX_PORT_Q` L998; `kim.c` L1138
  `libutils_is_card_sone_gr2`.
- **notes**: This CORRECTS the FLOW-005 tiering of LC_ONLINE/LC_OFFLINE (see the FLOW-005
  LC_ONLINE/OFFLINE note): on SONE they are Tier-1 LCND programmers, not Tier-2 DB-only.
  Per user, OLDER releases may still carry active `kim_tor.c` code (this build has it
  `#if 0`) -- cross-release comparisons must not assume the dead-code state. Full design:
  `architecture/kim-process-architecture.md` §8 + ADR-007. Anchor on the predicate/handler
  names, not line numbers.

### KSTACK-043: KIM seeds per-netns default sysctls + ip6tables MLD-drop at bring-up (kim_set_default_sysctl)
- **scope**: `lib/kim_intf.c` `kim_set_default_sysctl()`; platform-independent (n9kv/sup)
- **status**: verified
- **verification**: full (source-verified against current nx_main 2026-07-11)
- **date**: 2026-07-11
- **tags**: kim, sysctl, netfilter, ip6tables, mld, rp_filter, bring-up, cscwi46503, cscwq34143, cscuv05709
- **fact**: KIM seeds kernel network sysctls/netfilter at init via `kim_set_default_sysctl()` (helper
  `kim_sysctl(fmt, NET_IPV4_PATH|NET_IPV6_PATH, val)`): IPv6 `conf/default/{autoconf,accept_ra,
  router_solicitations,disable_ipv6}`, IPv4 `conf/default/arp_announce`, IPv4 `conf/default/rp_filter`
  (CSCwi46503 -- n9kv overrides the titan-sup LOOSE default), and `ignore_routes_with_linkdown` for BOTH
  `conf/default` and `conf/all` on IPv4 AND IPv6 (CSCuv05709). It ALSO shells
  `ip6tables -A OUTPUT -p ipv6-icmp --icmpv6-type {130,131,132,143} -j DROP` to block kernel-generated MLD
  (query / report / done / v2-report) so the sup MLD component -- not the kernel -- owns MLD (CSCwq34143;
  an earlier add of this block was reverted under CSCwp04543 before landing durably here). Note
  `sysctl.conf.default` only applies to the init netns; per-VRF netns are seeded explicitly.
- **evidence**: 2026-07-11 read `lib/kim_intf.c`: `kim_set_default_sysctl()` def L412; `rp_filter` L515;
  `ignore_routes_with_linkdown` default/all IPv6 L521/527 + IPv4 L533/539; `ip6tables ... --icmpv6-type
  130/131/132/143 -j DROP` L546-552.
- **notes**: Control-plane bring-up, distinct from the datapath entries. MLD ownership (kernel vs sup)
  hinges on this ip6tables DROP. Anchor on `kim_set_default_sysctl`/`kim_sysctl` + the sysctl path strings,
  not line numbers.

### KSTACK-044: KIM shares 4 kernel bridges/VXLAN netdevs across VRFs keyed by table_id % 4 (br-%d / vx%u)
- **scope**: `kim_msg_handler.c` VXLAN kernel create/move; Silicon One overlay
- **status**: verified
- **verification**: full (source-verified against current nx_main 2026-07-11)
- **date**: 2026-07-11
- **tags**: kim, vxlan, evpn, bridge, table-id, vrf, netdev, cscwb01375, cscwo37981, cscwo46939
- **fact**: KIM does NOT create one Linux bridge/VXLAN netdev per VRF. It shares a bounded pool of 4 kernel
  bridges `br-0..br-3` and 4 VXLAN devs `vx0..vx3` across VRFs, indexed by `table_id % 4` (source comment
  "max 1000 netdevices per bridge"); the VXLAN VNI id is set to `(table_id % 4) + 1` via
  `rtnl_link_vxlan_set_id`. Introduced to stop DSVNI/EVPN route-leak from per-VRF devs (CSCwb01375). Create
  path `kim_vxlan_intf_kernel_create` -> `kim_vxlan_intf_kernel_create_from_tbl_id` (builds `br-%d`/`vx%u`
  from `table_id%4`); VRF move `kim_vxlan_intf_vrf_move`. GOTCHA: a `br-1` hardcode regression (CSCwo37981)
  was fixed back to `br-%d` + proper VRF-move namespacing (CSCwo46939) -- do not reintroduce a fixed bridge
  name.
- **evidence**: 2026-07-11 read `kim_msg_handler.c`: `snprintf(br_name,IFNAMSIZ,"br-%d",(table_id%4))`
  L3288/L4646/L4780; `vx%u` `(table_id % 4)` L4645/L4790/L5058; `rtnl_link_vxlan_set_id(vxlan_link,
  (table_id % 4)+1)` L4805; `kim_vxlan_intf_vrf_move` L4630; `kim_vxlan_intf_kernel_create` L4917 /
  `_from_tbl_id` L4742.
- **notes**: A separate legacy `br-%d` with un-modded `table_id` exists at L6352 (non-shared path) -- the
  shared-pool model is the `%4` sites above. Cross-ref KSTACK-002 (KIM owns the VXLAN VRF plumbing) and
  FLOW-005 (`NVE_L3_VNI_NOTIFY`/`NVE_PD_IF_MSG`). Anchor on `table_id % 4` +
  `kim_vxlan_intf_kernel_create`/`_vrf_move`, not line numbers.

### KSTACK-045: KIM netns/nsid programming correctness (kernel auto-alloc -1; per-VRF ns socket via kim_get_ns_sock)
- **scope**: `kim_msg_handler.c` netns/nsid + VRF-scoped ioctl socket; ISSU-relevant
- **status**: verified
- **verification**: full (source-verified against current nx_main 2026-07-11)
- **date**: 2026-07-11
- **tags**: kim, netns, nsid, vrf, issu, kim_get_nsid, kim_get_ns_sock, cscwr20377, cscwe33477
- **fact**: KIM nsid/netns invariants: (1) `kim_get_nsid()` returns `-1` on purpose so the KERNEL
  auto-allocates the netns nsid (source comment "-1 : Kernel auto allocates a namespace id"), avoiding
  collisions with VRF/external namespaces (CSCwr20377); the value feeds
  `kim_netns_set_nsid(context_name, nsid)`. (2) An interface's ioctl to LCND/kernel for a NON-default VRF
  must run on THAT VRF's netns socket obtained via `kim_get_ns_sock(context_name, &s)` -- using the
  default-ns socket silently drops LIF/OIF programming (post-SSO multicast loss, CSCwe33477). (3) The
  fixed-width `ns_name` (`lnx_ns_ifindex_t.ns_name`, `L3VM_MAX_NAME_LEN`) is the netns hash key;
  `kim_netns_add_intf(old_ns_name, ...)` compares/moves on it (`strncmp(old_ns_name, ns_name,
  L3VM_MAX_NAME_LEN)`), so it must be a clean fixed-width string before compare or a stale key selects the
  wrong netns.
- **evidence**: 2026-07-11 read `kim_msg_handler.c`: `kim_get_nsid()` L124-128 (`return -1;` + auto-alloc
  comment); callers L1890 (`kim_netns_set_nsid`), L3447; `kim_get_ns_sock` def L2006, VRF-scoped use
  L1966/L4083; `kim_netns_add_intf(char *old_ns_name,...)` L3742, `strncmp(old_ns_name,ns_name,
  L3VM_MAX_NAME_LEN)` L3784.
- **notes**: Complements KSTACK-039 (LPSS ifindex maps) + `architecture/kim-process-architecture.md` §4
  (`ns_name_hash`). Anchor on `kim_get_nsid`/`kim_get_ns_sock`/`ns_name`, not line numbers.

### KSTACK-046: Native KIM-CC (`kim_inconsistent_interfaces`): veth excluded from MTU/MAC; Exablaze/Triton gated; PASSED syslog
- **scope**: `kim_debug.c` `kim_inconsistent_interfaces` + `libcli/kim.cmd`; Silicon One
- **status**: verified
- **verification**: full (source-verified against current tree 2026-09-22; live Mustang-1)
- **date**: 2026-09-22
- **tags**: kim, consistency-checker, cc, veth, exablaze, triton, cscwh81248, cscwh26754, cscwt38492
- **fact**: The **KIM-process** checker is `kim_display_inconsistency` ->
  `kim_inconsistent_interfaces`. It walks every IM iod (`im_get_next_if`) and
  compares IM vs kernel ioctl/`SIOCDEVGETLC` vs KIM AVL. Rules: (1)
  `IF_INDEX_TYPE_VETH` is excluded from MTU and MAC checks (CSCwh81248). (2) A
  clean run prints `Consistency test for all interfaces : PASSED` and
  `syslog_print(CC_RUN_STATUS,"CC_KIM","Consistency Check: PASSED")`
  (CSCwh26754); a failed run prints mismatch lines only and syslog FAILED (no
  CLI FAILED footer). (3) `kim.cmd` registers `show kim inconsistency` and a
  **duplicate** `show consistency-checker kim` (gated `$notvalidinexbl`,
  CSCwt38492) onto this same handler. The **public** `show consistency-checker
  kim {interface} [brief|detail]` lives in `cochk.cmd` and is **not** this
  function -- see KSTACK-058.
- **evidence**: `kim_debug.c` `kim_inconsistent_interfaces` /
  `kim_display_inconsistency` / `cli_register_cmd(KIM_CONSISTENCY_CHECKER_CMD,
  kim_display_inconsistency)`. Banner string `Checking Inconsistency status for
  all Interfaces....` exists only here. 2026-09-22 Mustang-1
  `show consistency-checker kim` (no interface) printed that banner + Eth1/49
  and Eth1/50 MTU triad Linux=1500 / NxOS=9216 / kim db=1500; syslog
  `CC_KIM: Consistency Check: FAILED`.
- **notes**: `show kim inconsistency` remains the FLOW-005 App G validator.
  Anchor on `IF_INDEX_TYPE_VETH`/`CC_KIM`/`notvalidinexbl`/`kim_inconsistent_interfaces`.
  `kim db=1500` means `kim_set_ifmtu` ran; do not decode as KSTACK-052
  `kim db=0`.
- **notes (2026-07-14)**: the MTU-check decode (three-way triad Linux `SIOCGIFMTU` vs `im_get_if_mtu`
  vs `lc_mtu`, and the `kim_set_ifmtu` single-writer invariant that makes `Linux=1500 + kim db=0` mean
  "the MTU setter never ran") is captured in **KSTACK-052**. The MCT MTU suppression special-case
  (CSCve86135) only hides mismatches when the port is a PC-MCT AND the kernel/`lc_mtu` side
  is already 9216 — it does NOT suppress the `kim db=0` breakout-port case.
- **notes (2026-07-14)**: the MTU-check decode (three-way triad Linux `SIOCGIFMTU` vs `im_get_if_mtu`
  vs `lc_mtu`, and the `kim_set_ifmtu` single-writer invariant that makes `Linux=1500 + kim db=0` mean
  "the MTU setter never ran") is captured in **KSTACK-052**. The MCT MTU suppression special-case at
  L1738/L1760 (CSCve86135) only hides mismatches when the port is a PC-MCT AND the kernel/`lc_mtu` side
  is already 9216 — it does NOT suppress the `kim db=0` breakout-port case.

### KSTACK-047: KFIB live direction is kernel->URIB only; reverse + notify paths are #if 0 dead
- **scope**: KFIB (`kfib.bin`, `standalone/infra/kstack/kfib/`) datapath direction
- **status**: verified
- **verification**: full (source-verified against current nx_main 2026-07-11)
- **date**: 2026-07-11
- **tags**: kfib, kvfib, urib, netlink, dead-code, direction
- **fact**: KFIB's only live datapath is **kernel netlink -> URIB** (import kernel
  routes into URIB). The reverse direction (program kernel/URIB from KFIB) and all
  URIB-notification handling are `#if 0` compiled out: `kfib_nl_fill_route`,
  `kfib_nl_request`, `kfib_nl_intf_addr` body, `kfib_process_notify_route` (+ the
  `kfib_notifs[]` MTS_OPC_URIB/U6RIB rows), `kfib_urib_process_notify_route`, and
  the standby `DO_IT_LATER` lconf sync. Critically `urib_notify_request` in
  `kfib_init_urib` is `#if 0`, so although KFIB does `urib_register`, it receives
  NO URIB route notifications in this image. CLI VXLAN/NVGRE/VNI help strings are
  copy-paste with no handlers.
- **evidence**: `kfib_urib.c kfib_init_urib` (`#if 0 ... urib_notify_request ... #endif`);
  `kfib_mts.c` `#if 0` around `kfib_process_notify_route` + `kfib_notifs[]`
  URIB/U6RIB rows; `kfib_netlink.c` `#if 0` `kfib_nl_fill_route`/`kfib_nl_request`
  and `kfib_nl_intf_addr` body. (as-of 2026-07-11 COV_10_7_0_IMG9)
- **notes**: KFIB is an incomplete/experimental daemon (many TODO/#if 0). Pairs with
  FLOW-012 + `architecture/kfib-library-architecture.md`. Do not treat dead paths as
  behavior.

### KSTACK-048: KFIB netlink socket + netns kernel-programming sequence
- **scope**: `kfib_netlink.c` (`kfib_nl_create_sock`, `kfib_nl_init`, `kfib_nl_ns_add`, `kfib_nl_route_change`)
- **status**: verified
- **verification**: full (source-verified against current nx_main 2026-07-11)
- **date**: 2026-07-11
- **tags**: kfib, netlink, netns, setns, rtnetlink, kernel-programming
- **fact**: KFIB opens `NETLINK_ROUTE` sockets to import kernel routes.
  `kfib_nl_create_sock`: `tsp_socket(AF_NETLINK, SOCK_RAW, NETLINK_ROUTE)` ->
  `nl_groups = RTMGRP_LINK|RTMGRP_IPV4_ROUTE|RTMGRP_IPV4_IFADDR` (IPv4-only, no v6
  group) -> `tsp_bind` -> `setsockopt(SO_RCVBUF=1MB)` -> `getsockname` ->
  `fcntl(F_SETFL, O_NONBLOCK)`. Default socket built in `kfib_nl_init` in the
  default netns (`default_ns_fd = open("/proc/self/ns/net")`), then `kfib_init_urib`
  + spawn `kfib-nl-thread`. Per-VRF sockets (`kfib_nl_ns_add`): `setns(ns_fd,
  CLONE_NEWNET)` into the VRF netns under `NETNS_RUN_DIR`, create the socket there,
  `setns(default_ns_fd, CLONE_NEWNET)` back, resolve `table_id` via
  `l3vm_context_get_table_id`. RX loop `kfib_nl_kernel_read` -> `kfib_wait_for_ip_input`
  (`tsp_select` over `nl_sock_list`) -> `tsp_recvmsg` -> `NLMSG_OK`/`NLMSG_NEXT` ->
  `kfib_nl_info_fetch` (drops `snl->nl_pid != 0`). `kfib_nl_route_change` accepts
  only `RTN_UNICAST` + `RT_TABLE_MAIN` + AF_INET, skipping `RTM_F_CLONED`,
  `RTPROT_REDIRECT`, `RTPROT_BIRD` (loop-guard), `rtm_src_len != 0`, `RT_SCOPE_LINK`.
- **evidence**: `kfib_netlink.c` `kfib_nl_create_sock` / `kfib_nl_ns_add` (setns x2) /
  `kfib_nl_route_change` (filter chain + `kfib_urib_add_one_route`/`kfib_urib_del_one_route`).
  addattr helpers (`addattr_l`/`rta_addattr_l`/`addattr32`) exist but are used only by
  the `#if 0` tx path (KSTACK-047). (as-of 2026-07-11)
- **notes**: multipath (`RTA_MULTIPATH`) routes are logged and dropped (unhandled).
  Del-path hard-codes `ifindex=0x1a101400` on lookup miss (TODO). Stable anchors only.

### KSTACK-049: KFIB lnx->nxos ifindex (KIM LPSS) + IOD (IM) + URIB IPC
- **scope**: `kfib_urib.c` (`kfib_urib_add_one_route`, `kfib_lnx_to_csco_ifindex`, `kfib_kim_lpss_init`) + `urib_api.c urib_add_one_route`
- **status**: verified
- **verification**: full (source-verified: kfib_urib.c + urib_api.c urib_add_one_route/urib_delete_one_route -> urib_send_to(MTS_SAP_URIB), 2026-07-11)
- **date**: 2026-07-11
- **tags**: kfib, urib, lpss, kim, im, ifindex, iod
- **fact**: Before programming URIB, KFIB translates the kernel `RTA_OIF` linux
  ifindex to an NXOS ifindex via `kfib_lnx_to_csco_ifindex` ->
  `lpss_lookup(kim_nxos_lpss_if_index_handle, ...)`, where that handle is opened
  read-only by `kfib_kim_lpss_init` on `lpss_open("volatile:kim_nxos_if_handle_db")`
  -- i.e. KFIB is a READER of KIM's LPSS ifindex DB (producer = KSTACK-039). It
  then gets the IOD via `im_get_iod_frm_ifindex` (IM), derives `nh_flags` from the
  route scope (`kfib_urib_get_nh_flags`: RT_SCOPE_LINK->ATTACHED|DIRECT,
  RT_SCOPE_HOST->ATTACHED|LOCAL), and calls `urib_add_one_route(urib_pib_hdl, tid,
  prefix, mask_len, next_hop, iod, ...)`. `urib_add_one_route`/`urib_delete_one_route`
  (`urib_api.c`) build a `urib_oneroute_msgtype` (`URIB_MTYPE_ADD/DELETE_ONE_ROUTE`)
  and send it FIRE-AND-FORGET via `urib_send_to(urib_get_qh_for_pib(pib),
  MTS_SAP_URIB, ...)` (no ack), guarded by `urib_is_urib_down()`/`urib_check_pib`.
- **evidence**: `kfib_urib.c` (`lpss_open` URIs `KIM_NXOS_IF_HANDLE_URI`/`KIM_LNX_IF_HANDLE_URI`;
  `kfib_urib_add_one_route` calls `kfib_lnx_to_csco_ifindex`/`im_get_iod_frm_ifindex`/
  `urib_add_one_route`); cscope: `lpss_lookup`->`infra/xos/lpss/shared/src/lpss_intf.c`,
  `im_get_iod_frm_ifindex`->`infra/interface_manager/lib/im_sdb_ext.c`,
  `l3vm_context_get_table_id`->`routing-sw/routing/l3vm/l3vm_api.c`;
  `urib_api.c urib_add_one_route`@~1859 / `urib_delete_one_route`@~1993 ->
  `urib_send_to(...,MTS_SAP_URIB,...)` (re-verified this pass). (as-of 2026-07-11)
- **notes**: both LPSS handles are opened with the same `KIM_LPSS_LNX_UUID` (copy-paste
  smell, inert). Consumer twin of KSTACK-039.

### KSTACK-050: KFIB MTS spine (2 SAPs) + 4-thread model; only KIM_NS_OPERATION live
- **scope**: `kfib.c` (`main`/`kfib_thread_init`), `kfib_mts.c` (`kfib_mts_bind`/`kfib_notifs[]`), `kfib_sysmgr.c`
- **status**: verified (opcode producer unverified)
- **verification**: full for KFIB side; producer-of-opcode = unverified (no in-tree sender indexed)
- **date**: 2026-07-11
- **tags**: kfib, mts, sap, threads, sysmgr, kim
- **fact**: KFIB binds TWO MTS SAPs (`kfib_mts_bind`): `smq = mts_bind(LNODE_SUP,
  MTS_SAP_KFIB_SYSMGR)` (sysmgr control) and `kfibq = mts_bind(LNODE_SUP,
  MTS_SAP_KFIB=234)` (data), both `SRVUUID_KFIB`/`MTS_OPTION_PERSISTENT`. On `kfibq`
  it registers (`mts_options_set REGISTER|PERSISTENT`) every `kfib_notifs[]` opcode
  -- but only ONE row is live: `MTS_OPC_KIM_NS_OPERATION -> kfib_process_kim_update`
  (the URIB/U6RIB rows are `#if 0`, KSTACK-047). When ACTIVE, `kfib_thread_init`
  spawns 4 threads: `kfib-sysmgr-thread` (`kfib_process_heart_msg`: heartbeat +
  `sysmgr_dispatch`, drops `MTS_OPC_VSH_ACFG_GEN`), `kfib-mts-thread`
  (`kfib_process_my_msg`: `sdwrap_process_msg` then `kfib_notifs_get`->handler),
  `kfib-nl-thread` (`kfib_nl_kernel_read`, via `kfib_nl_init`), and the active_timer
  library timer thread (`kfib_timer_init`->`active_timer_init`;
  `kfib_process_heartbeat_timer`).
- **evidence**: `kfib_mts.c kfib_mts_bind` (two `mts_bind` + register loop);
  `kfib_notifs[]` (only KIM_NS row outside `#if 0`); `kfib_process_kim_update`
  (KIM_NS_CREATE->`kfib_nl_ns_add`, KIM_NS_DELETE->`kfib_nl_ns_del`);
  `kfib.c kfib_thread_init` (2 pthreads + `kfib_nl_init`), `kfib_sysmgr.c`
  (`kfib_timer_init`/`active_timer_create`). Scoped grep over `standalone/infra`
  (re-verified this pass): `MTS_OPC_KIM_NS_OPERATION` appears ONLY in `kfib_mts.c`
  `kfib_notifs[]`. (as-of 2026-07-11)
- **notes**: [unverified] NO in-tree sender of `MTS_OPC_KIM_NS_OPERATION` found
  (kim/ has the `kim_ns_notif_t` type + enum but no `mts_send`; KSTACK-041 KIM-sender
  catalog omits it). So the per-VRF socket sub-flow is dormant in this image unless
  KIM emits it from a non-indexed path. Confirm: create a VRF and watch KFIB
  event-history for "Successfully added <ns>".

### KSTACK-051: kfib.conf sysmgr identity + dependencies + HA
- **scope**: `kfib.conf` (sysmgr service block)
- **status**: verified
- **verification**: full (source-verified against current nx_main 2026-07-11)
- **date**: 2026-07-11
- **tags**: kfib, sysmgr, kfib.conf, dependency, ha, standby
- **fact**: KFIB is a sysmgr service `SRVNAME_KFIB`, `executable=/isan/bin/kfib`,
  `uuid=SRVUUID_KFIB`, `run = conditional`, `mts = aware`, `eth_infra = yes`,
  `vdc_config srv_type = local`. Dependency `scope = control` on `SRVNAME_KIM`,
  `SRVNAME_URIB`, `SRVNAME_L3VM` (so it starts after those). Heartbeat
  `timeout = 8000` ms, `maxloss = 600`. HA: single_sup `restart = stateless with
  default_config` (minlife 10000, maxretry 5); dual_sup `standby_mode = sync`,
  `global_sync = no`, ha_policy stateful then switchover.
- **evidence**: `kfib.conf` service block (`run = conditional`; `dependency { scope =
  control; SRVNAME_KIM; SRVNAME_URIB; SRVNAME_L3VM; }`; `heartbeat { timeout = 8000;
  maxloss = 600; }`; `dual_sup { standby_mode = sync; ... }`). (as-of 2026-07-11)
- **notes**: `run = conditional` + `standby_mode = sync` matches `kfib.c` main()
  supstate machine and the `#if DO_IT_LATER` standby sync being disabled (KSTACK-047).
- **notes (2026-07-11, CSCwk55026/CSCwq16826)**: the `limit { }` block sets KFIB's
  sysmgr `RLIMIT_AS`. As of CSCwk55026 (PR #55952) the `heap` field is interpreted in
  **KB** (was bytes; `heap = 250000000 → 250000`, same ~250 MB cap) to let `.conf`
  express >4G caps. CSCwq16826 (PR #63763) added the optional per-platform-RAM knob
  family `phy_mem_{8,16,24,32,64,128,256,512}G_heap` (all default `0` → inherit the
  nearest lower defined value, else `heap`); KFIB ships all `0`, so no live cap change.
  Evidence: `kfib.conf limit { heap = 250000; … phy_mem_8G_heap = 0 … phy_mem_512G_heap = 0; }`
  + inheritance comment block (verified current nx_main).
- **notes (2026-07-11, CSCuv05709 lineage)**: the `dependency { scope = control; }` on
  `SRVNAME_KIM` has churn history — CSCuv05709 (`72c323fe`, a2g sync, 2022-03-15) **removed**
  `SRVNAME_KIM;`, and the `kerry_pre_git_cleanup` code-drop `577f4607c8d9` (2022-04-21)
  **restored** it (`git blame` on the current `SRVNAME_KIM;` line = `577f4607`). The
  KIM-present state above is therefore correct for the live tree; the removal did not
  persist. This `.conf` dependency only gates KFIB sysmgr launch ordering, not the runtime
  KFIB↔KIM handle/MTS relationship (KSTACK-047..050 / FLOW-012).

### KSTACK-052: KIM-CC MTU triad + kim_set_ifmtu single-writer invariant (breakout ports miss MTU at boot)
- **scope**: `kim_debug.c` `kim_inconsistent_interfaces` (KIM-CC) + `kim_mts.c` `kim_process_port_param_change` + `kim_set_ifmtu` (`kim_msg_handler.c`); Silicon One (N9364E "Mustang")
- **status**: verified
- **verification**: full (source-verified current nx_main + live switch 172.22.135.166 / 10.7(0)IMG9(0.221), 2026-07-14)
- **date**: 2026-07-14
- **tags**: kim, consistency-checker, mtu, breakout, fanout, lc_mtu, kim_set_ifmtu, im_get_if_mtu, siocsifmtu, boot-ordering, kim_process_if_created, kim_is_msg_sender_authorized, MTS_SAP_IFMGR, sap-authorization, CSCwv05804
- **fact**: `show kim inconsistency` compares a **three-way MTU triad** per KIM-DB interface in
  `kim_inconsistent_interfaces` (kim_debug.c): **Linux** = `ifr.ifr_mtu` from `SIOCGIFMTU` on the kernel
  netdev; **NxOS** = `mtu = im_get_if_mtu(iod)` (L1724; SAT fabric uses `ethpm_im_get_ifindex_mtu_list`
  L1715); **kim db** = `p_ii->if_info.lc_info.lc_mtu`. Two independent checks fire: Linux≠NxOS (L1731,
  prints "Linux MTU X does not match NxOS MTU Y" L1751) and NxOS≠kimdb (L1758, prints "NxOS MTU X does
  not match kim db MTU Y" L1773). **Single-writer invariant:** `lc_mtu` AND the Linux netdev MTU are only
  ever written together by `kim_set_ifmtu` (`SIOCSIFMTU`, then on success `lc_mtu=mtu` + PSS
  `KIM_PSS_OPER_INTF_CHG_MTU`). The normal runtime trigger is an IM `IM_MSG_TLV_MTU` param-change handled
  in `kim_process_port_param_change` (kim_mts.c L1492 → "Set MTU %u for Interface 0x%x" L1493 →
  `kim_set_ifmtu` L1496/1498). `kim_create_if` programs MTU only for tunnels. Therefore **`Linux=1500
  (kernel default) + kim db=0` == kim_set_ifmtu never ran for that ifindex** (the IM MTU event never
  arrived after the netdev was created in KIM's DB).
- **evidence**: Live 2026-07-14 on Mustang-2 (reloaded 09:23): `show kim inconsistency` flagged **all
  breakout sub-ports** Eth1/5/1..Eth1/16/8 + Eth1/64/1 (ifindex `0x38xxxxxx`) with `NxOS 9216 / Linux 1500
  / kim db 0`, plus Eth1/49-50 (`0x1a006xxx`) with `NxOS 1500 / kim db 0` (benign default-MTU variant).
  `show kim internal event-history intf`: at 09:25:31 `kim_process_port_param_change:1493 Set MTU 9216`
  fired for hundreds of **SVIs** (`0x901xxxx`; `0x9010097 = Vlan151`) — but NEVER for any `0x38xxxxxx`
  breakout port; the breakout ports were `kim_create_if`-created ~100s LATER (09:27:10) and got no MTU
  event afterward. `errors` buffer showed no `skip prog`/`ioctl failed` for these ifindexes (only the
  separate Po10 MCT case). Config: no `system jumbomtu`; each breakout port has explicit `mtu 9216`;
  `show interface eth1/5/1` operational `MTU 9216` (so IM/hardware = 9216). CDETS family (not exact):
  CSCvp68307/CSCvx38081 (`CC_ERR_KIM_MTU_IM_KIM_MISMATCH`), CSCvr58203 (2nd breakout lane MTU CC),
  CSCvq30775 (9216 not applied on breakout after config copy), CSCwv34272 (confirms ethpm/IM
  port-param-change is what sets the per-interface kernel netdev MTU).
- **notes**: Impact is scoped: front-panel ASIC datapath uses the hardware MTU (9216) and is unaffected;
  the gap is the **Linux/kim netdev** MTU (1500) which only constrains punt/inband/host-stack frames for
  those members. Workaround (disruptive, config change — not applied): re-toggle MTU on the members
  (`mtu 1500` then `mtu 9216`, or member flap) to force an `IM_MSG_TLV_MTU` → `kim_set_ifmtu`. The MCT
  suppression special-case (L1738/L1760, CSCve86135) does NOT hide these because `lc_mtu==0` (≠9216).
  Anchor on function names + message strings, not line numbers (they drift).
- **notes (2026-07-14, live experiment — PROVES boot-specific)**: reproduced the control on lab switch
  172.20.175.106 (N9348Y2C6D-SE1U, 10.7(0)IMG9(0.189)). Applied `interface breakout module 1 port 49 map
  10g-4x` then `interface Eth1/49/1-4 ; switchport ; switchport mode trunk ; mtu 9216` **interactively
  (post-boot, live)**. Result = **Outcome A**: all four sub-ports (ifindex `0x381e0000`-`0x381e3000`)
  came up with **Linux MTU 9216**, **no `show kim inconsistency` entry**, and KIM `intf` history logged
  `Set MTU 9216 for Interface 0x381e...` for each (a prior `Set MTU 1500` then re-set to 9216 — i.e.
  `kim_process_port_param_change`→`kim_set_ifmtu` fired). Notably `kim_create_if` ran (20:39:19) BEFORE
  the MTU programming (20:40:23-54), yet the live IM `IM_MSG_TLV_MTU` still reached KIM. Conclusion: the
  prod failure (`Linux=1500 / kim db=0`, no `Set MTU`) is **confined to the boot / config-replay
  create-ordering window** — the IM MTU notification for breakout members is lost only on that boot path,
  not on live config. Therefore the recommended prod workaround (live `mtu` re-toggle / member flap on the
  affected breakout ports) will force `kim_set_ifmtu` and clear the mismatch. Caveat: lab is a different
  chassis/build than prod (N9364E 0.221) but same NXOS/KIM family — treat as a strong control, not identical.
- **notes (2026-07-14, CORRECTED ROOT CAUSE — verified on prod, supersedes the "boot MTU-flood / lost
  IM_MSG_TLV_MTU notification" mechanism above)**: the real create-time MTU programmer for an L2 member
  netdev is **`kim_process_if_created` (kim_mts.c)** — on an `IM_IF_CREATED` (MTS opc **62467**) it calls
  `kim_get_mtu` (→ `ethpm_im_get_ifindex_mtu_list`) → `kim_set_ifmtu` for switchports. This handler is gated
  by **`kim_is_msg_sender_authorized(msg, MTS_SAP_IFMGR, ...)`** (kim_mts.c ~L355/L2065), which accepts ONLY
  `MTS_SAP_IFMGR` or `MTS_SAP_KIM` and `return`s early otherwise — **added by commit `d1318a9ee70` =
  CSCwv05804** ("kim crash loop / sup reset via forged interface-manager if-created"). On Mustang-2 the
  `IM_IF_CREATED` for the breakout PC-member ports arrives from **`ethpm` (SAP 175)**, **`eth_port_channel`
  (SAP 378)**, and **`interface-vlan` (SAP 210)** — never from **`ifmgr` (SAP 179)** — so every copy is
  rejected (`errors` buffer: `IM_IF_CREATED: rejecting opcode 62467 from unauthorized SAP 378/175/210`,
  100s of them, recurring on each config-replay incl the 11:17 churn). `kim_process_if_created` therefore
  never runs its MTU pull → `lc_mtu=0`, Linux=1500. The netdev itself is created by a SEPARATE path,
  **`kim_process_if_create_netdev_req` (ethpm request/response) → `kim_create_if`** (tunnel-only MTU), which
  is why `intf` history shows `kim_create_if` for `0x38028000` at 09:27:10 with NO MTU and NO
  `kim_process_if_created` body / `Set MTU 0x38028000` ever. `kim_process_pcm_change:3223` sets MTU only on
  the **port-channel** ifindexes (`0x160000xx`), never on the members. **Net: the MTU inconsistency is a
  side-effect of the CSCwv05804 SAP-authorization hardening** (or an ifmgr-side gap where ifmgr doesn't
  publish IF_CREATED for PC-member/breakout ports). SAP→process map obtained via `show system internal
  sysmgr service all` (SAP column): 179=ifmgr, 175=ethpm, 378=eth_port_channel, 210=interface-vlan.
  OPEN (kind: open-question): whether the intended IF_CREATED publisher for these member ports is ifmgr
  (gap) or ethpm/PCM (CSCwv05804 over-rejects = regression) — discriminate by checking a working non-breakout
  L2 port's `intf` history for an accepted `kim_process_if_created`, and/or the ifmgr side. This corrects the
  two earlier session hypotheses (tunnel-only-create and ethpm delta-publish race), both wrong.
- **notes (2026-07-14, working-setup contrast — build regression confirmed)**: verified `kim_process_if_created`
  runs for NO interface on prod (Mustang-2 0.221): `show kim internal event-history intf` had **0**
  `Setting switchport mac` lines; the ONLY MTU writer that fired was `kim_process_port_param_change`
  (":1493 Set MTU 9216 for Interface 0x901xxxx") in a ~14ms burst at 09:25:31 hitting **only SVIs** — no
  `Set MTU` for any physical `0x38`/`0x1a00` port. `show kim inconsistency`: 0 SVIs flagged; all mismatches
  are breakout PC-members `0x38xxxxxx` (+ benign `0x1a00xx` Eth1/49-50). Contrast on the WORKING setup (lab
  172.20.175.106, build **0.189**): **0** unauthorized-SAP rejections, `kim_process_if_created` DID run
  (`Setting switchport mac` ×10), and its breakout ports got `Set MTU 9216` via
  `kim_process_port_param_change:1472`. The CSCwv05804 gate commit `d1318a9ee70` (Jason Ren) is dated
  **2026-07-06** — present/effective in 0.221, not in 0.189. CONCLUSION (high-confidence): **CSCwv05804 is a
  regression** — the `MTS_SAP_IFMGR`-only gate disables the create-time MTU pull (`kim_process_if_created`
  →`kim_get_mtu`→`kim_set_ifmtu`) for interfaces whose `IM_IF_CREATED` is published by ethpm/eth_port_channel
  (PC-members/breakout members), which on prod (0.221) leaves `lc_mtu=0` because no post-create
  `IM_MSG_TLV_MTU` delta arrives either. Working prod interfaces (SVIs) are unaffected only because they
  received the boot `kim_process_port_param_change` burst. Residual ambiguity (build-gate vs
  PC-membership-changes-publisher): the lab experiment used PLAIN (non-PC) breakout switchports AND lacks the
  gate — to isolate, either confirm commit `d1318a9ee70` is absent from the 0.189 image, or reload the lab
  with breakout members inside a port-channel and re-check. Corrects this session's prior claim that a working
  port shows an *accepted ifmgr* `kim_process_if_created` — on prod it runs for nobody; working ports rely on
  the param-change path.
- **notes (2026-07-17, copy-to-running discriminator on unfixed 0.221 lab image)**:
  verified on 172.20.175.106 after loading `10.7(0)IMG9(0.221)` without the CSCwv49648 branch fix. A
  narrow `copy bootflash:cscwv49648_copy_repro.cfg running-config` containing only `interface breakout
  module 1 port 49 map 10g-4x` plus `mtu 9216` for the generated members reproduced
  `IM_IF_CREATED: rejecting opcode 62467 from unauthorized SAP 175`, but did **not** reproduce the KIM-CC
  MTU failure: KIM logged `kim_process_port_param_change` / `Set MTU 9216` for every generated member in
  the same replay window, both `show kim inconsistency` and `show consistency-checker kim` stayed PASSED,
  and `show interface Ethernet1/49/1-4 | include MTU` showed 9216. Therefore `copy ... running-config`
  alone is not sufficient to trigger the CSCwv49648 KIM-CC failure on this lab box; the remaining suspect
  is the boot/startup replay or prod-specific PC-member publisher/timing path where the post-create MTU
  param-change does not arrive.

### KSTACK-053: CSCwv32090 LCND raw-netlink mutation handlers require CAP_NET_ADMIN and bounded payloads
- **scope**: `lcnd_fdb_nl_recv_msg`, `lcnd_mpls_nl_recv_msg`,
  `lcnd_vlan_gid_nl_recv_msg`, and `kvfib_send_mpls_label`
- **status**: verified
- **verification**: full (source + platform-target build + patched-image
  runtime negative tests for unauthorized sender and privileged malformed payload)
- **resolution**: fixed
- **date**: 2026-07-16
- **tags**: lcnd, netlink, fdb, mpls, vlan-gid, cap-net-admin,
  payload-validation, ecmp-max-paths, kvfib, CSCwv32090
- **fact**: The three LCND private raw-netlink receive callbacks mutate global
  `init_net` FDB/MPLS/VLAN-GID state and are shared by each default/container
  protocol alias. They must reject a sender unless
  `netlink_capable(skb, CAP_NET_ADMIN)` succeeds before parsing the netlink
  header or payload. Authorized messages must advertise at least the full
  handler payload via `nlmsg_msg_size(sizeof(payload_type))` before
  `nlmsg_data()` is dereferenced. MPLS add/update and delete must bound their
  local `adjacency_count` to `ECMP_MAX_PATHS` before indexing
  `mpls_adj_info[]`. KvFIB's matching sender must set `nlmsg_len` to
  `NLMSG_LENGTH(sizeof(mpls_label_info))`, because `ufib_mpls_req_t` already
  contains the netlink header and using its full size as the payload
  double-counts that header.
- **evidence**: Current source (2026-07-16) shows the authorization and payload
  gates at the start of all three callbacks, the local MPLS clamps in
  `lcnd_add_update_mpls_entry2` and `lcnd_delete_mpls_entry2`, and the corrected
  sender length in `kvfib_send_mpls_label`. Generated platform builds
  `klm_lcnd.klm_ins_x86e_supe` and
  `libkvfib_pltfm.so_ins_x86_64_supe` completed successfully. A read-only lab
  check confirmed the legitimate IPFIB and KIM senders had effective
  `CAP_NET_ADMIN` on the checked image. Runtime validation on the fixed image
  sent 16-byte header-only `NLM_F_ACK` probes to `NETLINK_FDB`, `NETLINK_MPLS`,
  and `NETLINK_VLAN_GID`: ordinary admin bash (`CapEff=0`) got `send_ok` then
  `no_ack_timeout` for all three protocols; `run bash sudo -n python3`
  (`CapEff=000001ffffffffff`) got `NLMSG_ERROR` ACKs with `err=-22` (`EINVAL`)
  for all three protocols. Post-test IPFIB and KIM remained handshaked and had
  not crashed since reboot.
- **notes**: Keep malformed-envelope handling separate from payload-size ACK
  handling: `netlink_ack()` copies `nlmsg_len(nlh)` bytes for uncapped errors,
  so a header claiming more bytes than `skb->len` must be dropped without
  passing that untrusted length to `netlink_ack()`. Initialize per-message FDB
  cleanup state before any payload-validation jump. The official remediation
  specifies clamping oversized MPLS counts rather than rejecting the whole
  transaction. The safe runtime test pattern is now METHOD-018: use
  header-only ACK probes, first without effective caps for the authorization
  gate, then via `run bash sudo -n python3` for the privileged payload-size
  `-EINVAL` path.

### KSTACK-054: Netbroker traps third-party kernel admin; NXOS whitelist + nbproxy are source of truth
- **scope**: netbroker / `klm_cisco_nb` / nbproxy / libnetbroker (RTNL + ioctl + socket hooks)
- **status**: verified
- **verification**: full (source + runtime on 172.20.175.107: broker table, perf
  `cisco_nb_traces:*`, nbproxy event-history — METHOD-020 / FLOW-013 E2E test)
- **date**: 2026-07-26
- **tags**: netbroker, nbproxy, libnb, rtnl, rtnetlink, ioctl, source-of-truth, urib, netstack, ipfib, kim, whitelist, genl
- **fact**: NXOS installs a kernel **netbroker** framework (patches under
  `standalone/third-party/src/kernel/nx-linux/patches.x86e-6.6/netbroker-*.patch`)
  that hooks RTNL (`rtnetlink_rcv_msg` -> `netbroker_rtnl_doit`), legacy
  `dev_ioctl`, and socket ioctl/bind/connect/release **before** the normal kernel
  handlers run. The Cisco KLM `klm_cisco_nb` registers `cisco_nb_ops` and implements
  `cisco_nb_rtnl_doit`: if the sending process passes `cisco_nb_allow_by_current()`
  (whitelist of NXOS daemons such as `ipfib`, `kim`, `netstack:`, `urib`, `u6rib`,
  `ifmgr`, plus Smack/cgroup/user_ns rules), the hook returns
  `NETBROKER_CONTINUE` and kernel state changes proceed unchanged. Otherwise, for
  mapped RTNL types (`nb_rtnl_map`: interface, rib, rib6, static route, neighbor),
  the hook clones the skb and sends it to userspace via genl `nb_send_request`
  (`NB_API_RTNL`), returns `NETBROKER_HANDLED` with `-EINTR`, and the original
  kernel RTNL handler does **not** apply the change. The sysmgr service **nbproxy**
  registers one `libnb` broker per `NB_GRP_*` group; each `cfg_cb` translates the
  trapped message into NXOS control-plane APIs (e.g. `urib_cfg_req` -> urib route
  add/del; `int_cfg_req` -> vsh/netstack interface ops). Completion uses two
  statuses: `LIBNB_CFG_OK_PROCESSED` means NXOS handled it and will program the
  kernel through whitelisted writers; `LIBNB_CFG_OK` may additionally call
  `libnb_update_kernel`, replaying the original RTNL on the broker's registered
  `rtnl_sk` (hook bypasses when `NETLINK_CB.portid == ne->rtnl_pid`). Module params
  `block_*` can hard-deny trapped categories; `disable_*_hook` bypasses hooks for
  debug.
- **evidence**: Kernel patch `netbroker-hooks.patch` inserts
  `netbroker_rtnl_doit` in `rtnetlink_rcv_msg`; `cisco_nb_rtnl.c`
  `cisco_nb_rtnl_doit` + `nb_rtnl_map`; `cisco_netbroker.c`
  `cisco_nb_allow_by_current` whitelist + `register_netbroker(&cisco_nb_ops)`;
  `nbproxy.c` `nb_libnb_init_brokers` + `int_cfg_req`; `nbproxy_dynamic_rt.c`
  `urib_cfg_req`; `libnb-msgs.c` `request_msg_handler` + `libnb_update_kernel`;
  `libnetbroker.h` `LIBNB_CFG_OK` / `LIBNB_CFG_OK_PROCESSED` comments.
  **Runtime E2E (2026-07-26, 107, `10.7(0)IMG9(0.166)`):** METHOD-021 stimulus-bound
  `perf record -a -e 'cisco_nb_traces:*' -o /bootflash/nb.perf -- ip route add
  192.0.2.88/32 … dev lo` + `perf script -i /bootflash/nb.perf` captured 7 trace lines
  (`ip` trap → `nb_send_request` → nbproxy `nb_rcv_request` → `nb_rtnl_resp
  status=0` → nbproxy replay `nb_rtnl_doit`); same second in nbproxy event-history:
  operation 3, static route op 3, `-ENODEV` on `lo`, kernel FIB got route. See
  METHOD-020, METHOD-021, and FLOW-013 § E2E validation.
- **notes**: Distinct from KFIB (FLOW-012): KFIB observes kernel routes that
  reached the FIB; netbroker **prevents** unapproved processes from putting them
  there directly. `netbroker.c` in the same tree is a test harness, not the production
  agent. Uncovered backlog for future flows: ioctl-only `ifconfig` path, socket
  bind/connect hooks, HA uxrib replay. FLOW-013 walks the RTNL trap end-to-end.
  Runtime on 172.20.175.107 (2026-07-26): nbproxy event-history proved trapped
  static-route ops; `lo` routes hit `-ENODEV` and `libnb_update_kernel` replay
  (kernel FIB only). See KSTACK-055 for dmesg/trace observability limits.
  Architecture + usages + ADR-001..008: `architecture/netbroker-architecture.md`.

### KSTACK-055: Sup LXC plain `dmesg` empty; use `dmesg -F /dev/kmsg`; netbroker hot path is tracepoints
- **scope**: netbroker / kernel observability / NX-OS `run bash` / printk
- **status**: verified
- **verification**: runtime (172.20.175.107) + source
- **date**: 2026-07-26
- **tags**: dmesg, devkmsg, printk, console_loglevel, pr_info, tracepoint, cisco_nb_traces, lxc, netbroker, observability, nbproxy
- **fact**:
  - **Hot path logging is tracepoints, not printk.** RTNL trap/forward uses
    `TRACE_EVENT` in `cisco_nb_trace.h` (`trace_nb_rtnl_doit`, `trace_nb_send_request`,
    `trace_nb_rtnl_resp`, …). These go to **ftrace/perf** when enabled, **not** to the
    printk ring buffer / `dmesg`. Normal `ip route add` through the trap fires
    `trace_nb_rtnl_doit` only (`cisco_nb_rtnl.c`).
  - **`pr_info("cisco_nb: …")` is sparse:** module init/swover, whitelist blocks,
    hook-disabled messages (`NBPROXY_DEBUG`), and some ethtool branches — **not** on
    every trapped route.
  - **Plain `dmesg` on sup LXC is misleading, not because kmsg is empty.** On
    172.20.175.107 (`lxc-*-vdc1sup1`), `run bash sudo sh -c "dmesg -P"` returned
    **empty**, but **`/dev/kmsg` had content**: injected `<6>probe…` was readable via
    `dd if=/dev/kmsg` and via **`dmesg -F /dev/kmsg -P`**. Always use
    **`dmesg -F /dev/kmsg -P`** (or read `/dev/kmsg`) on sup LXC — not bare `dmesg`.
  - **`console_loglevel` tuning (user-validated).** Baseline `/proc/sys/kernel/printk`
    was `1 6 1 1` (low console verbosity). Writing
    `run bash sudo sh -c "echo 8 > /proc/sys/kernel/printk"` changed first field to
    `8 6 1 1`; `echo '8 6 1 8' > /proc/sys/kernel/printk` set `8 6 1 8`. This
    raises **physical console** printk visibility for **new** `pr_info`+ messages but
    **did not fix plain `dmesg`** and **did not produce `cisco_nb` lines** for a
    trapped `ip route add … dev lo` (nbproxy event-history still proved the trap).
    Optional: `echo on > /proc/sys/kernel/printk_devkmsg`.
  - **Userspace proof:** `show nbproxy internal event-history events` (+ `debug
    nbproxy events`) — correlated with `ip route add` on 107 while
    `dmesg -F /dev/kmsg -P | grep cisco_nb` returned 0 after the trap.
  - **Kernel proof (when exposed):** **METHOD-021** stimulus-bound or timed perf
    capture with `'cisco_nb_traces:*'` (not plain `dmesg`). On 107 build, events
    were available via `perf list` but not under `/sys/kernel/tracing/events/`.
- **evidence**: `cisco_nb_rtnl.c` `trace_nb_rtnl_doit`; `cisco_nb_trace.h`; 2026-07-26
  switch 107: plain `dmesg` empty, `dmesg -F /dev/kmsg` found kmsg probes, printk
  `8` write succeeded, route trap in nbproxy at `18:37:07`, zero `cisco_nb` in kmsg.
- **notes**: Requires **`run bash sudo sh -c '…'`** (METHOD-019). Distinct from LCND
  legacy `lcnd_table_dump` dmesg removal (switch-commands LCND section).

### KSTACK-056: NX-OS 10.7 s1-dpu (SONE) kernel has NO writable eBPF datapath hook; kprobe/BPF_EVENTS work
- **scope**: eBPF capability profile of the shipped NX-OS SONE kernel; klm_vdc→eBPF feasibility
- **status**: verified
- **verification**: full
- **date**: 2026-07-31
- **tags**: ebpf, bpf, klm_vdc, xdp, tc, clsact, kprobe, silicon-one, s1-dpu, ps-inb, kernel-config, 10.7
- **fact**: On image `nxos64-s1-dpu.10.7.0.IMG9.0.270` (N9348Y2C6D, kernel 6.6.140,
  BTF present), every WRITABLE eBPF datapath hook is disabled/absent, so eBPF cannot
  rewrite live packets: (1) `CONFIG_NET_SCH_INGRESS` is UNSET → `tc qdisc add … clsact`
  and `… ingress` both fail "Specified qdisc kind is unknown"; (2) only `SFQ`+`FIFO`
  qdiscs are compiled (classless, no `cls_bpf` classification) — `prio`/classful are
  absent, so there is no `cls_bpf` egress attach point either; (3) XDP generic AND
  native both SILENTLY no-op — `ip link set dev X xdp[generic] obj … sec xdp` returns
  rc=0 but `ip -d link` shows no prog and an `XDP_DROP` program does NOT drop. What
  DOES work: `bpf(BPF_PROG_LOAD)` + verifier (accepts TC/XDP/kprobe progs), and
  kprobe/tracepoint BPF (`CONFIG_KPROBES`/`KPROBE_EVENTS`/`BPF_EVENTS`=y). On-box
  toolchain is broken: `clang`+BCC dead (`libclang-cpp.so.18.1` missing), no
  `bpftool`, `bpftrace` missing `libbpf.so.1` → must compile eBPF objects OFF-box
  (CO-RE) and load with `ip`/`tc`/raw `bpf()`. Consequence for klm_vdc→eBPF: the
  intended TC-clsact-ingress-on-ps-inb replacement requires the kernel build to first
  enable `CONFIG_NET_SCH_INGRESS` (or fix XDP). eBPF can already OBSERVE the punt path:
  a kprobe on `eth_type_trans_inb` (the klm_vdc classifier, KSTACK-031) logged real
  punt frames (`kprobe_profile` 42 hits/0 miss, softirq `..s11`).
- **evidence**: 2026-07-30 switch 172.20.175.106: `zcat /proc/config.gz | grep
  NET_SCH_INGRESS` → "is not set"; `tc qdisc add dev vdcpoc0 clsact` → unknown kind;
  `ip link set dev vdcB xdpgeneric obj … ` rc=0 but `ip -d link show vdcB` no xdp +
  XDP_DROP prog did not drop; `bpf(PROG_LOAD)` returned prog_fd on the switch;
  kprobe on `eth_type_trans_inb` via perf_event_open+SET_BPF logged 42 hits. Files:
  `/bootflash/vdc_*` (see session README).
- **notes**: (1) The `bpf_trace_printk` output is DROPPED unless `tracing_on=1`
  (`/sys/kernel/debug/tracing/tracing_on`) — a run showing "0 log lines" but nonzero
  `kprobe_profile` nhit means tracing was off, not that the prog didn't fire. (2) On
  kernel 6.6, `bpf_trace_printk` writes to the ftrace ring buffer as `bpf_trace_printk`
  events (visible under `/sys/kernel/debug/tracing/events/bpf_trace/`). Reading via
  `trace_pipe` in non-blocking Python `readline()` silently misses events due to EAGAIN
  races; reliable approach: clear with `open(trace_path, 'w')` (truncates ring buffer),
  sleep, then snapshot the non-consuming `/trace` file. Verified 2026-07-31: 6-18 live
  hits/10s on `eth_type_trans_inb` in softirq `..s11` context. Related: KSTACK-014 (0xf104
  vdc ethertype), KSTACK-030/031 (psdev↔klm_vdc RX classify), METHOD-022.
  (3) eBPF USERSPACE TOOLCHAIN UPDATE (2026-07-31): `libbpf.so.1.3.0` built from
  `linux-6.6/tools/lib/bpf/` and installed to `/usr/lib64/` on switch; `bpftool v7.3.0`
  built with `feature-llvm=0 feature-libbfd=0 feature-libcap=0` (eliminates LLVM
  host/switch mismatch), installed to `/usr/sbin/bpftool` — fully operational, verified:
  `bpftool prog load vdc_kprobe_log.o /sys/fs/bpf/vdc_test type kprobe` succeeds,
  prog ID 1920, 432B xlated, 286B jited. `bpftool feature probe` confirms JIT enabled,
  BTF present, `NET_SCH_INGRESS`/`XDP_SOCKETS` still unset. Build on `/bootflash/Kondal/`
  (noexec mount); copy to `/tmp/` to execute.
  (4) RE-VERIFIED AFTER RELOAD (2026-07-31, NX-OS 10.7(1) build `IMG9(0.270)`,
  kernel `6.6.140`): `/bootflash/Kondal/ebpf/` survived reload and `setup.sh` restored
  `libbpf` + `bpftool` cleanly. The kprobe POC still works on the real
  `eth_type_trans_inb` datapath (`5` visible `bpf_trace_printk` lines in 8s,
  `kprobe_profile: vdcpoc 15 0`). The writable-hook verdict is unchanged:
  `CONFIG_NET_SCH_INGRESS` still unset and `tc qdisc add dev lo clsact` still fails
  "Specified qdisc kind is unknown"; XDP generic still attaches as a no-op on a safe
  veth pair (`ip -d link show vdcB` shows no `xdp`, `vdc_poc_selftest.py` still
  observes `0x0800` not `0xf104`, and an `XDP_DROP` prog still allows the packet
  through). This re-verifies that the blocker is the shipped kernel hook support,
  not the POC payload or userspace setup.

### KSTACK-057: `kim-data` can retain a stale `ndo_start_xmit` target if `lcnd_init_module()` fails after netdev registration
- **scope**: `lcnd_init_module` / `lcnd_reg_netdevices` / `rni_register_kimdata` / `rni_kimdata_ndo_start_xmit`; Silicon One local-build bring-up failure
- **status**: verified
- **verification**: full
- **date**: 2026-08-01
- **tags**: kim-data, rni_lcnd, lcnd, module-init, failed-init, stale-function-pointer, ndo_start_xmit, mld, ipv6-dad, mgmt-dev, psdev, proc-net-dev
- **fact**: `lcnd_init_module()` registers LCND-owned netdevs FIRST, then runs
  `lcnd_platform_init()`. During `lcnd_reg_netdevices()`, LCND calls
  `rni_register_kimdata(container_id, &kimdata_netdev_ops, ...)`, which copies
  LCND's `kimdata_netdev_ops` into `rni_kimdata_ops[cid]`; if `kim_data == NULL`,
  `rni_register_kimdata__()` also creates the shared `kim-data` netdev, attaches
  `rni_kimdata_netdev_ops`, registers it, and immediately `dev_open()`s it. The
  wrapper `rni_kimdata_ndo_start_xmit()` later indirect-calls
  `rni_kimdata_ops[rni_dev_ops_idx].ndo_start_xmit`.

  Therefore, if a later step in `lcnd_init_module()` fails — e.g.
  `lcnd_platform_init()` returns `-ENODEV` because `mgmt_dev_name` cannot be
  resolved — the `fail:` path returns the init error WITHOUT unwinding the
  previously-registered `kim-data` / `rni_kimdata_ops` state. Any asynchronous TX
  on the already-open `kim-data` device (observed via both the kernel MLD worker
  and IPv6 DAD/ND worker) can then execute `rni_kimdata_ndo_start_xmit()`, which
  jumps through a stale copied function pointer whose target belonged to the
  failed `klm_lcnd` image (`kimdata_start_xmit`). The fault shape is an
  instruction-fetch page fault at the indirect target address, not in the wrapper
  body itself.
- **evidence**: code order: `lcnd_init_module()` calls `lcnd_reg_netdevices()` at
  `lcnd.c:6446` BEFORE `lcnd_platform_init()` at `lcnd.c:6494`; mgmt failure
  returns `-ENODEV` from `lcnd_platform_init()` in `lcnd_n9k.c:13514-13527`;
  `rni_register_kimdata()` copies the ops vector at `rni_lcnd.c:471`;
  `rni_register_kimdata__()` installs `rni_kimdata_netdev_ops`, registers, and
  `dev_open()`s `kim-data` at `rni_lcnd.c:412-441`; the wrapper indirect call is
  `rni_kimdata_ndo_start_xmit()` at `rni_lcnd.c:357-360`. Two independent reboot
  logs hit the same pattern after the same mgmt-dev failure: (1)
  `mld_ifc_work -> mld_sendpack -> dev_hard_start_xmit ->
  rni_kimdata_ndo_start_xmit`, with `RIP = RAX = 0xffffffffc13e09c0`; (2)
  `addrconf_dad_work -> ndisc_send_ns -> ndisc_send_skb -> __dev_queue_xmit ->
  dev_hard_start_xmit -> rni_kimdata_ndo_start_xmit`, with
  `RIP = RAX = 0xffffffffc16459c0`. Both are `#PF: supervisor instruction fetch`
  faults at the indirect target, while the module list still shows
  `klm_rni_lcnd` but not `klm_lcnd`.
- **notes**: The panic may appear while "Installing psdev module ..." because the
  MLD/IPv6 worker races after `kim-data` is brought up; `psdev` is a timing
  witness, not the owner of the crashing xmit target. The discriminator versus
  an ordinary NULL-function-pointer bug is: wrapper present, indirect target
  non-NULL, instruction fetch from unmapped module text. A second post-oops crash
  in `grep` reading `/proc/net/dev` (`dev_seq_show -> dev_get_stats`) is
  consistent with the same zombie `kim-data` netdev still being present while the
  kernel is already dying; treat that `/proc` oops as collateral evidence of the
  leaked netdev, not a separate root cause.

### KSTACK-058: Public `show consistency-checker kim` is cochk -> `pm_cli_show_cc_kim` -> `cc_kim.py:kimConsistencyInterface`
- **scope**: `standalone/utils/libconsistency_checker/` (`cochk.cmd`, `cochk.c`, `cc_kim.py`); Silicon One
- **status**: verified
- **verification**: full (source + live Mustang-1 interface-scoped CLI 2026-09-22)
- **date**: 2026-09-22
- **tags**: kim, consistency-checker, cochk, cc_kim, python, pm_cli_show_cc_kim
- **fact**: The consistency-checker **framework** CLI is
  `cochk.cmd` `show_cc_kim`:
  `show consistency-checker kim {interface <ifid>} [brief|detail]`, gated
  `$notvalidinexbl`, handler `pm_cli_show_cc_kim` in process `cochk`. That C
  function sets `NX_CC_ENVVAR_TYPE=CC_TYPE_KIM`, optional brief/detail env,
  formats one ifindex name (`IF_INDEX_INVALID` when omitted), and calls
  `runPyFunc("cc_kim", "kimConsistencyInterface", ...)`. Python
  `kimConsistencyInterface` checks **only** `_ifindex[0]`/`_ifName[0]` (not a
  full IM walk). Data sources: `show kim internal info interface` +
  `show kim internal info kernel interface` (parsed text) plus
  `Nxos.Interface` IM APIs. It prints `consistency kim:` then
  `Consistency Check: PASSED|FAILED` and a longName list. FAILED also
  `cc_syslog("CC_KIM", "Consistency Check: FAILED")`; PASSED is CLI-only (no
  syslog PASSED). Ethernet or tunnel (`if_type == 0x18`) are checked; mgmt and
  non-KIM ifindexes return early. MTU pass is `imMtu == kernel/kim` or
  `imMtu - 12`. MCT/down-FEX skip is CSCve86135/CSCvw84878. There is **no**
  VETH MTU/MAC exclusion in this Python path (that skip is native-only,
  KSTACK-046).
- **evidence**: `cochk.cmd` command `show_cc_kim`; `cochk.c`
  `pm_cli_show_cc_kim` -> `runPyFunc("cc_kim", "kimConsistencyInterface", ...)`;
  `cc_kim.py` `kimConsistencyInterface` / `getKimInternal` / `getKimInfo`.
  2026-09-22 Mustang-1 `show consistency-checker kim interface Ethernet1/49`
  printed `consistency kim:` / `Consistency Check: FAILED` /
  `Inconsistencies found for following interfaces:` / `Ethernet1/49`. The
  no-interface `show consistency-checker kim` on the same box printed the
  native KIM banner (KSTACK-046) -- duplicate `kim.cmd` syntax can win that
  parse.
- **notes**: Do not treat `kim.cmd`'s duplicate `show consistency-checker kim`
  as the framework owner. To force the Python path, use `interface <ifid>`
  and/or `brief`/`detail`. Python does not walk all interfaces; native
  `show kim inconsistency` does.

### KSTACK-059: LIF-hit IPsec outer-IP slide ignores a customer 802.1Q tag
- **scope**: `lcnd_sone_process_ipsec` non-ESP strip, then the `ET_VLAN` reader in `lcnd_sone_inband_decap`; Silicon One
- **status**: verified
- **date**: 2026-10-13
- **tags**: sone, ipsec, vlan, dot1q, outer-ip, skb
- **fact**: On the `lcnd_lif_htab_get(source_lp)` success arm, `lcnd_sone_process_ipsec` does not call `lcnd_sone_get_netdev`, so a customer 802.1Q tag is still present. `dpi` stays zero, so `dpi.v4_proto != IPPROTO_ESP` is true and the strip always runs. That strip copies `ETH_HLEN` (14) bytes to `skb->data + sizeof(struct iphdr)` and pulls `sizeof(struct iphdr)` (20). That matches `Eth | OuterIP | payload` only. With `Eth | 802.1Q | OuterIP | payload`, the 4-byte tag sits in the discarded window. After the pull, offset 12 is still `0x8100`, and the TCI slot (offset 14, `vlan_hdr` at `sizeof(struct ethhdr)`) holds the first two octets of the outer IPv4 destination. The later reader `ntohs(vlan_hdr->h_vlan_TCI) & 0xfff` reports that value. The same slide drops the real IPv4 ethertype; the dot1q `memmove` then leaves the outer destination's last two octets as the ethertype, with the inner IP immediately after it.
- **evidence**: 2026-10-13 illustrative observation, re-derive per session. Trace strings `Got an ipsec decapped packet. Removing outer IP header.` then `l2ra_vni 0, proto 0x8100` then `Received dot1Q packet with vlan` matched the current `lcnd_sone_process_ipsec` strip and the `ET_VLAN` reader. A byte replay of `memcpy` 14 / `skb_pull` 20 on `Eth|8100|TCI|0800|OuterIP` put the outer destination's first two octets in the TCI slot; masking to 12 bits matched the logged VLAN. Post-`memmove` ethertype was those destination's last two octets and the next bytes were the inner IP (`0x45`). No glean/`Checking for vlan tag` trace fired, which matches the LIF-success arm (the 8-byte pull is KSTACK-011 and did not move this TCI).
- **notes**: Sibling of KSTACK-010 (still-ESP, untagged assumption). The glean arm can strip the tag inside `lcnd_sone_get_netdev` before this slide (FLOW-001 step 4); the LIF-hit arm does not. `l2ra_vni` printed just before the dot1q trace is still `lc_vlan` (KSTACK-001); the packet TCI overwrites `vlan` only inside the `ET_VLAN` block. Do not detect the inline tag through `skb->protocol`: the 8-byte-junk pull has already replaced it with `lcnd_get_default_vdc_proto()`. Walk the bytes at `skb->data + ETHER_TYPE_OFFSET` with `IS_VLAN_PROTO`, and move the resulting full L2 length. `eth_type_vlan()` also excludes the local `ET_VLAN_DOUBLE`/`ET_VLAN_OVLAN` values handled by `IS_VLAN_PROTO`.
