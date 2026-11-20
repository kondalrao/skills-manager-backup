# FLOW-007: SONE ps-inb RX datapath (ASIC punt -> ps-inb -> psinb -> rni handoff)

- **FLOW**: FLOW-007
- **protocol**: (infra) inband punt RX datapath through klm_psdev (SONE)
- **platform**: Silicon One (DPU-TOR arm verified on Krypton DESCHUTES; non-DPU + GR2/P200 siblings noted)
- **status**: verified
- **date**: 2026-07-08
- **source**: `standalone/platform/insieme/drivers/emon_psdev/kspace/psdev_main.c`
  (`klm_psdev`, EXTERNAL to `standalone/infra/kstack/`). External RX boundary:
  `rni_handle_platform` in `standalone/infra/kstack/kspace/rni_lcnd/rni_lcnd.c`
  (`klm_rni_lcnd`). Setter of `skb_protocol_get_inb`: `klm_vdc`
  (`standalone/platform/storage/sup/kspace/vdc/klm_vdc.c`).

This is the RX-side twin of FLOW-004 (which covers driver bring-up / rx-handler
REGISTRATION). FLOW-004 = who installs the handlers; FLOW-007 = what a punted
frame does once a handler fires. It is the klm_psdev segment of the Domain Map
SONE punt chain (ASIC -> ps_sone0_rx_handle_frame -> ps-inb ->
psinb_rx_handle_frame -> rni_handle_platform -> handle_platform [klm_lcnd] ->
lcnd_plat_decap -> lcnd_sone_inband_decap; see FLOW-001).

> All card-index numbers / ifindex / MAC / line numbers below are VOLATILE as-of
> hints. Anchor on the **function names**, **`CARD_INDEX_*`/`TOR_SONE_*_DEV`
> macros**, **`RX_HANDLER_*` return enums**, and **trace-string literals**.
> Re-derive per session. (KNOWLEDGE.md VOLATILE-vs-STABLE banner.)

## Ordered steps

1. **ASIC kpkt/PIE netdev RX.** The real ASIC netdev's `netdev_rx_handler` is
   `ps_sone0_rx_handle_frame`, installed by `sone_register_pltfm_rx_handlers`
   (init) / `sone_netdev_event` `NETDEV_REGISTER` (deferred `leaba0_0`). DPU-TOR
   installs it on BOTH `TOR_SONE_KPKT_DEV`("leaba0_0") and
   `TOR_SONE_PIE_DEV`("pie-eth0"). (Registration detail = FLOW-004 / KSTACK-019.)

2. **`ps_sone0_rx_handle_frame(pskb)`** — ASIC->pseudo-dev redirect + normalize
   (KSTACK-030):
   - Redirect: `is_dpu_tor && skb->dev->name==TOR_SONE_PIE_DEV` -> `is_app_pkt=true`,
     `skb->dev = ins_app_inb` (ps-svc-inb); else `skb->dev = ins_ps_inb` (ps-inb).
   - `is_app_pkt` -> `skb_push(ETH_HLEN)` + `skb_reset_mac_header` (IGB stripped
     eth+.1q; restore).
   - GR2 card set (`CARD_INDEX_BUD_LIGHTNING/OPTIMATOR/MUSTANG/BUD_LIGHTNING_X/
     OPTIMATOR_X/SARGO`) -> `skb_push(ETH_HLEN)`; else -> `skb->vlan_tci=0` +
     `__vlan_hwaccel_clear_tag` (kernel 6.6).
   - `skb->pkt_type = PACKET_HOST`.
   - `if (!is_app_pkt && skb_protocol_get_inb) skb->protocol =
     skb_protocol_get_inb(skb, skb->dev)` — EXTERNAL fn-ptr owned by klm_vdc
     (KSTACK-031). If NULL, protocol is left as-is (no VDC queue classification).
   - `skb->vlan_tci=0` again (+clear tag) "for GR2".
   - bump `skb->dev->stats.rx_*`; `netif_receive_skb(skb)`; `return RX_HANDLER_CONSUMED`.

3. **`netif_receive_skb`** re-enters the stack on the pseudo dev, whose own
   `rx_handler` is `psinb_rx_handle_frame` (installed by
   `register_psinb_rx_handlers` on `ins_ps_inb`, and `ins_app_inb` under
   `is_dpu_tor`).

4. **`psinb_rx_handle_frame(pskb)`** — Kstack RX entry + external handoff
   (KSTACK-029):
   - `IS_MBIT_SUPPORTED(my_card_index) && mbit_tx_to_fp_dev(skb)` ->
     `RX_HANDLER_CONSUMED` (mbit front-panel short-circuit; skb leaves this chain).
   - Lazily resolve `rni_handle_platform_lcnd =
     kallsyms_lookup_name("rni_handle_platform")`; if still NULL ->
     `RX_HANDLER_PASS` (trace "Unable to resolve rni_handle_platform_lcnd symbol").
   - `skb = rni_handle_platform_lcnd(skb)` -> EXTERNAL. `NULL` return ->
     `RX_HANDLER_CONSUMED` (LCND took ownership).
   - dpu: `skb->dev != ins_app_inb && != ins_ps_inb` -> `RX_HANDLER_ANOTHER`;
     non-dpu: `skb->dev != ins_ps_inb` -> `RX_HANDLER_ANOTHER`. Else `RX_HANDLER_PASS`.

5. **`rni_handle_platform` [EXTERNAL, rni_lcnd.c / klm_rni_lcnd]** — dispatches via
   fn-ptrs `rnd_handle_platform` / `rnd_handle_platform_1` (selected by
   `rni_dev_ops_idx == RNI_TYPE_NODE_0`) into `klm_lcnd` `handle_platform` ->
   `lcnd_plat_decap` -> `lcnd_sone_inband_decap` (FLOW-001, KSTACK-012). RX leaves
   klm_psdev here.

## Field transformations (RX)

`skb->dev`: ASIC dev -> `ins_ps_inb` (ps-inb) or `ins_app_inb` (ps-svc-inb).
mac header: pushed back for app pkts + GR2 (`skb_push(ETH_HLEN)`).
`skb->vlan_tci` -> 0 (+`__vlan_hwaccel_clear_tag` on 6.6).
`skb->pkt_type` -> `PACKET_HOST`.
`skb->protocol` <- `skb_protocol_get_inb(skb, skb->dev)` (klm_vdc's
`eth_type_trans_inb`; NULL until klm_vdc loads).

## Divergence points / sibling branches (do NOT cross-apply)

- **app vs main dev** (step 2): DPU-TOR PIE frames -> ps-svc-inb (`is_app_pkt`,
  eth restored); everything else -> ps-inb.
- **GR2/P200 eth handling**: GR2 set pushes ETH_HLEN; other SONE clears vlan_tci.
- **mbit short-circuit** (step 4): mbit-capable cards divert to the front-panel
  dev via `mbit_tx_to_fp_dev` before reaching rni.
- **skb_protocol_get_inb NULL** (step 2): pre-klm_vdc frames are NOT VDC-classified;
  on some sibling handlers (mgmt/eobc) a NULL fn-ptr is a drop path.
- Non-SONE ASICs use different handlers (`ps_tah_/ps_triton0_/ps_tof_/ps_tera0_/
  mgmt_/ps_eobc_rx_handle_frame`, kNET, Nvidia) — out of scope; several hardcode
  `skb->protocol = htons(0xf102)` instead of calling the fn-ptr.

## Illustrative (2026-07-08 source read; values volatile)

DPU-TOR path: pie-eth0 frame -> is_app_pkt -> ps-svc-inb (eth pushed);
leaba0_0 frame -> ps-inb (vlan_tci cleared, protocol via skb_protocol_get_inb).
Card-index membership and whether klm_vdc is loaded are per-box; re-derive.
