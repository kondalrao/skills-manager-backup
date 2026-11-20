# KSTACK Methods Library (detail)

Full bodies for `METHOD-*`. The compact index (id, title, tags, status) and reuse
counts live in `../KNOWLEDGE.md` and `../USAGE_COUNTS.md`. Open this file only for the
method you need. Dedup/next-ID greps and the single-writer rule (SKILL.md) cover this
file too.

## Methods Library

Reusable debugging/analysis techniques. Reuse these; do NOT reuse the
session-specific inferences they once produced (each problem is different).

### METHOD-001: Last-write-wins value tracing
- **status**: verified
- **date**: 2026-06-10
- **method**: To explain the value of a field at a specific trace line, find the
  FINAL assignment to that field/variable before the trace point, within the
  confirmed platform function. Walk branches in order; a later unconditional
  write (or a taken `if` branch like `if(!is_egress_trap_svi){...}`) overrides
  earlier seeds (e.g. a header-derived value). Report the winning write by its
  function + code snippet (not an absolute line).
- **evidence**: Used to show `l2ra_vni` came from `lc_if_info.lc_vlan` (the
  `if(!is_egress_trap_svi)` write in `lcnd_sone_inband_decap`), not `relay_id`
  (KSTACK-001).

### METHOD-002: Identify the platform function from the trace prefix
- **status**: verified
- **date**: 2026-06-10
- **method**: NXOS datapath traces print `funcname:NNN`. Match the function NAME
  (ignore the `NNN` line number -- it drifts) to the function body before
  reasoning. Reason ONLY inside that function -- do not borrow logic from another
  platform's decap/encap function.
- **evidence**: A `lcnd_sone_inband_decap:NNN` trace -> work only within
  `lcnd_sone_inband_decap`; the "set vlan 0xffff for L3 intf" code that looks
  similar belongs to `lcnd_tah_inband_decap`, a different function (KSTACK-003).

### METHOD-003: Decode lc_flags against kim_utils.h
- **status**: verified
- **date**: 2026-06-10
- **method**: Interpret a hex `lc_flags` value by AND-ing against the `LC_FLAGS_*`
  bit definitions in `kim_utils.h` (see KSTACK-004). Candidate for a python
  helper in `scripts/` (see Debugging Tools).
- **evidence**: `0x2080 = TX_HDR_V7|LOOPBACK` (Lo501); `0x12090 =
  TUNNEL|TX_HDR_V7|LOOPBACK|PCM` (Tunnel501).

### METHOD-004: Decode a kernel oops/panic to the exact source line
- **status**: verified
- **date**: 2026-06-10
- **method**: Pin a NULL-deref/oops to one C line using the register dump:
  1. `RIP: func+0xOFF/0xSIZE [module]` -> the crashing function and module
     (note: `static` callees are inlined, so the symbol may be the *caller* --
     check for a `static` helper near that offset, see KSTACK-006).
  2. `CR2` = faulting address. A small value (e.g. `0xe0`) is a struct **field
     offset** off a NULL base -> `NULL->field`. Map the offset to the struct
     field (e.g. `net_device->ifindex` is at `0xe0` on kernel 6.6).
  3. In the `Code:` disasm, an immediate like `mov $0xNNNN,%r8d` is usually a
     `__LINE__` constant (decode the hex to decimal) passed to a log macro ->
     the faulting `LCND_ERR(...)`/trace call; grep that format string/literal to
     locate it (do not trust a stored line).
  4. The register holding the NULL base names the bad pointer.
  Cross-check the `Call Trace` for the punt module chain (see Domain Map).
- **evidence** (2026-06-10, illustrative): `lcnd_sone_process_ipsec+0xb3c`,
  `CR2=0xe0`, `mov $0x4a26` (=18982) -> the NULL `lcnd->ifindex` log in
  `lcnd_sone_get_netdev` (KSTACK-006).

### METHOD-005: Locate the in-repo kernel source (don't grep from root)
- **status**: verified
- **date**: 2026-06-10
- **method**: To read the real kernel implementation of an skb/net helper, use
  Glob `**/net/core/skbuff.c` and `**/include/linux/if_vlan.h` (or
  `include/linux/skbuff.h`), then Read/Grep only those files. Do NOT grep the
  repo from root -- it times out on this NFS workspace. The authoritative tree is
  `standalone/third-party/src/kernel/nx-linux/linux-6.6/`. WARNING: the
  `standalone/third-party/bin/linux/final.x86e-6.6/include/linux/if_vlan.h` copy
  is a ~67-line STUB, not the full header -- use the `nx-linux/linux-6.6` source.
  For big/slow searches, dispatch an `explore` subagent scoped to the kernel dirs
  when the runtime supports subagents; otherwise use scoped `rg`/Read in the
  relevant kernel directories.
- **evidence**: Found `skb_vlan_pop`/`__skb_vlan_pop` in
  `.../linux-6.6/net/core/skbuff.c`; `eth_type_vlan`/`__vlan_hwaccel_clear_tag`/
  `skb_vlan_tag_present` in `.../linux-6.6/include/linux/if_vlan.h` (KSTACK-008).

### METHOD-006: skb header-pointer reasoning (eth_hdr vs skb_pull)
- **status**: verified
- **date**: 2026-06-10
- **method**: When a punt path mutates an skb, separate the two cursors:
  `skb->data`/`skb->len` (moved by `skb_pull`/`__skb_pull`) vs the stored
  `skb->mac_header` offset (NOT moved by pull). `eth_hdr(skb)` reads
  `skb_mac_header(skb) = skb->head + skb->mac_header`, so after a `skb_pull` the
  MAC header is stale -- call `skb_reset_mac_header(skb)` (sets
  `mac_header = skb->data - skb->head`) before any `eth_hdr()` read or in-place
  L2 edit. `__skb_vlan_pop()` even `WARN_ONCE`s and returns `-EINVAL` if
  `skb->data != skb_mac_header(skb)`.
- **evidence**: `lcnd_sone_process_ipsec` does `skb_pull(skb, 8)` (junk) before
  calling `lcnd_sone_get_netdev`, which must `skb_reset_mac_header` so
  `eth_hdr()->h_proto` reads the inner frame (KSTACK-011).

### METHOD-007: Pick the platform function before any line lookup
- **status**: verified
- **date**: 2026-06-11
- **method**: Before reasoning about a decap/encap log, map it to the right
  function: (1) read the `funcname:NNN` trace prefix; (2) look the function NAME
  up in the Domain Map "platform dispatch index"; (3) grep that function name to
  locate its current body. Only then read code. This prevents the #1 KSTACK
  mistake (cross-platform citation, KSTACK-003) and survives line drift (anchor
  on the function name, never an absolute line).
- **evidence**: The "set vlan 0xffff for L3 intf" (CSCux29417) code lives in
  `lcnd_tah_inband_decap`, NOT `lcnd_sone_inband_decap` -- the name index makes
  the platform boundary obvious (KSTACK-003).

### METHOD-008: Access NX-OS switches with MCP first, sshpass -e fallback
- **status**: verified
- **date**: 2026-06-24
- **method**: Prefer the Nexus MCP connector for switch access when it is
  available: `nexus_connect`, then `nexus_execute_command(s)`, then
  `nexus_disconnect`. Start with read-only identity/service checks and only run
  disruptive commands after explicit user approval. If MCP is unavailable, use
  `sshpass -e` and pass the password through `SSHPASS` for the single command
  being run. Use `ssh -F /dev/null` to bypass the local OpenSSH config issue,
  disable public-key attempts for password-only device checks, and keep
  credentials out of `SKILL.md`, `KNOWLEDGE.md`, scripts, continuity files, and
  command templates.
- **evidence**: On 2026-06-17, direct SSH to `172.20.175.106` failed locally with
  `Bad owner or permissions on /etc/ssh/ssh_config.d/05-redhat.conf`, and
  interactive password entry was intercepted by GUI askpass. The command pattern
  `SSHPASS=<redacted> sshpass -e ssh -F /dev/null ... admin@172.20.175.106
  'show hostname'` succeeded and returned `des1infra`; `show version` returned
  NX-OS `10.7(1)` on a Nexus9000 `N9348Y2C6D-SE1U`.
- **evidence**: On 2026-06-24, Nexus MCP connected to `172.20.175.106` and
  collected `show version`, `show system internal sysmgr service name kim`,
  `/proc/<kim-pid>/status`, `/dev/mts0` permissions, and post-repro cleanup
  checks without storing credentials in local files.

### METHOD-009: Prefer slot quoted for module-level data collection
- **status**: verified
- **date**: 2026-06-17
- **method**: For module-level NX-OS data, prefer Type 2:
  `slot <slot> quoted "<module command>" | no-more`. It runs from the supervisor
  CLI, is one-shot, works well with `sshpass -e`, and avoids managing an
  interactive module shell. Use Type 1 (`at mod <slot>`, run commands at
  `module-<slot>#`, then `exit`) only when an interactive module shell is needed
  or Type 2 cannot express the workflow. For commands that expose secrets, record
  only command shape and redacted evidence.
- **evidence**: On 2026-06-17 against `des1infra` (`172.20.175.106`), Type 2
  `slot 1 quoted "show hardware internal s1hal ipsec tunnels all" | no-more`
  returned the S1HAL IPSec Tunnel Database. Type 1 `at mod 1` followed by
  `show hardware internal s1hal ipsec tunnels all | no-more` returned the same
  database and `exit` closed the module session cleanly. The verified output had
  IPSec feature status `ENABLED`, one displayed tunnel (`Tunnel-ID 4356`, VRF 1,
  state `DELETE_COMMIT`), ingress/egress ESP SAs, and a `PORT-GID/TNL-DEST-GID`
  row. The output includes `Enc Key`, `Auth Key`, `Salt`, and handle/session
  values; redact before saving or sharing.

### METHOD-010: IPSec SUP-to-S1HAL RCA command ladder
- **status**: verified
- **date**: 2026-06-17
- **method**: For IPSec analysis/RCA, collect SUP control-plane state first, then
  module S1HAL hardware state using Type 2 `slot quoted` commands. Correlate in
  this order: tunnel interface/source/destination -> endpoint handle/SA DB SPIs
  -> tunnel manager primary/reachability -> S1HAL tunnel ID/GID/SPIs -> security
  engine placement -> tunnel counters. Use tunnel ID from S1HAL for focused
  `tunnels tunnel-id <id>` and `counter tunnels tunnel-id <id>` checks. Treat
  S1HAL IPSec tunnel/SDK output as sensitive because it can include key material;
  record only redacted summaries.
- **evidence**: Verified on 2026-06-17 against `des1infra` (`172.20.175.106`).
  SUP outputs connected Tunnel501 to source `50.50.1.1`, destination `50.50.1.6`,
  if-handle `0x180101f5`, ingress SPI `0xb980a1be`, and egress SPI `0x93067ef1`.
  S1HAL outputs connected the same endpoint/SPIs to tunnel ID `4356` / GID
  `0x1104`, ingress security engine index 4, egress security engine index 5,
  underlay nexthop GID `0x10`, and counters showing egress encrypted packets and
  ingress authentication-error packets.
- **notes**: Useful RCA branches: endpoint/SA present on SUP but missing in S1HAL
  suggests programming sync; SPIs differ between SUP and S1HAL suggests stale or
  mismatched SA programming; S1HAL counters identify datapath direction and error
  class, but do not by themselves prove root cause without matching traffic/logs.

### METHOD-011: Decode la_packet_punt_header_t from raw on-wire bytes
- **status**: verified
- **date**: 2026-06-18
- **method**: To read SONE punt fields (source/code/ssp/...) straight from a hex dump
  when a Wireshark dissector is misaligned: the `la_packet_punt_header_t` union
  (`lcnd_sone.h`, 40B / `SIZEOF_LA_PACKET_PUNT_HEADER`) is a packed bitfield
  whose WIRE order is the REVERSE of C declaration order -- the last-declared field
  (`next_header`, 5b) is first on the wire, `future_use` (64b) is last. MSB-first bit
  packing from the first punt byte (right after the `0x7106` ethertype): next_header5,
  fwd_header_type4, padding3, next_header_offset8, **source4**, code8, lpts_flow_type8,
  source_sp16, destination_sp16, source_lp20, destination_lp20, padding2, relay_id14,
  time_stamp64, receive_time32, version4, ... So `source` (punt_source) = low nibble
  of punt-byte index 2; `code` = punt-byte 3; `source_sp` = bytes 5-6; etc. Verify by
  back-checking a known field (e.g. source_sp) before trusting the decode.
- **evidence**: 2026-06-18, decoded an INBOUND_MIRROR punt: byte2 low nibble = 0
  (`source=0`=INBOUND_MIRROR), byte3=`0x07` (code=7), bytes5-6=`00 a6` (ssp=166),
  bytes7-8=`00 c4` (dsp=196), source_lp `0x1867`, dst_lp `0x7fff`, relay_id `0x19` --
  all matched the dissector, proving punt_source genuinely INBOUND_MIRROR despite the
  dissector misaligning timestamp/counter.

### METHOD-012: Branch analysis needs the lcnd dump_table + SiliconOne PID, not just the packet
- **status**: verified
- **date**: 2026-06-18
- **method**: A punt/inject datapath branch (which `if/else-if` arm in a decap block
  fires, why the `else`/drop did NOT) almost always depends on RUNTIME state that the
  packet bytes cannot reveal -- hash-table lookups (`lcnd_lif_htab_get`,
  `lcnd_vlan_gid_htab_get`, ifindex/PI/VNI/BD/mirror-GID tables) and the
  SiliconOne PID/trap meaning. So, before concluding a branch:
  1. Get the **SiliconOne PID** (e.g. G200) and decode trap/punt-source/`fwd_header_type`
     from `la_event.h` for that PID + the raw punt header (METHOD-011).
  2. Ask the user for the **`show system internal lcnd hash-tables`** output
     (LIF/ifindex/PI/VLAN-GID/BD/VNI/VRF/mirror-GID hash tables; formerly the
     `lcnd dump_table` dmesg dump). Resolve the relevant key (e.g. `source_lp`,
     `relay_id`, `ifindex`) IN those tables.
  3. Evaluate each branch condition with the actual values; prove the taken branch by
     cross-matching a resolved field (ifindex/IOD/ltl/vlan) against the
     outgoing/kim-data metadata.
  Do NOT assert which branch fired (or that a drop path was avoided) from the packet
  alone -- if the dump_table is missing, ask for it and mark the branch `unverified`.
- **evidence**: 2026-06-18, EGRESS_TRAP decap: `source_lp=0x1867` ruled out branches 1/2
  arithmetically, but branch 3 (L3 `lcnd_lif_htab_get`) was only PROVABLE via the
  `lcnd dump_table` LIF row `0x1867 = Eth1/21/3.3 / ifindex 0x380ca003 / IOD 0x1e1`,
  which matched the outgoing kim-data metadata `Ifinfex 0x380ca003 / IOD 481` (KSTACK-018).

### METHOD-013: Diagnose pseudo-inb TX not egressing its parent (no rebuild)
- **status**: verified
- **date**: 2026-06-18
- **method**: When a psdev pseudo netdev (`ps-inb`/`ps-svc-inb`) shows TX climbing
  but the expected parent real-dev shows nothing, localize WITHOUT a kernel
  rebuild using read-only Linux state (all work under NX-OS `run bash`):
  1. `cat /sys/class/net/<dev>/statistics/tx_packets` twice ~2s apart for the
     pseudo dev AND every candidate parent -> see which moves in lockstep.
  2. `tc -s qdisc show dev <parent>`: if root mq + child pfifo_fast are ALL
     `Sent 0 / dropped 0 / backlog 0 / requeues 0` CUMULATIVELY, then
     `dev_queue_xmit(skb, parent)` was NEVER executed for those frames -- because
     kernel 6.6 `__dev_queue_xmit` enqueues via `__dev_xmit_skb` whenever
     `q->enqueue` is set (mq), and a carrier-DOWN device would still show
     backlog/requeues (drop happens at dequeue, not before enqueue). So an
     all-zero qdisc PROVES the skb never reached the parent (it was consumed/
     diverted earlier in the pseudo dev's `ndo_start_xmit` = `psdev_start_xmit`).
  3. `ethtool -S <parent> | grep -E 'tx_.*(drop|err|link_down|busy)'`: if
     `tx_dropped_link_down.nic`/`tx_busy`/`tx_errors` are 0 too, the parent's
     driver xmit was never invoked either (corroborates step 2).
  4. `ethtool <parent>` + `ip -d link show <parent>`: `Link detected: no` /
     `<NO-CARRIER ... UP> state DOWN` means the parent's PHY link is down (an
     INDEPENDENT problem that blocks egress regardless of forwarding).
  CAVEAT: NX-OS `run bash` runs WITHOUT `CAP_NET_RAW`, so `tcpdump` fails
  ("Attempt to create packet socket failed - CAP_NET_RAW may be required") and
  `tcpdump -i any` can't compile an `ether proto` filter -- packet CAPTURES must
  use **`run bash sudo sh -c 'tcpdump …'`** or an interactive **`run bash sudo bash`**
  root shell (METHOD-019); `/sys`,`ip`,`ethtool`,
  `tc` all work fine over the unprivileged `sshpass -e` `run bash` path (METHOD-008).
- **evidence**: 2026-06-18 on `des1infra` (172.20.175.106, Krypton DESCHUTES):
  `ps-svc-inb` tx_packets climbing live (cum ~2400, +1/2s, tx_dropped 0) while
  `pie-eth0` mq qdisc + all 96 pfifo_fast children read Sent/dropped/backlog 0
  and ICE `tx_dropped_link_down.nic=0` -> proved the frames never reached
  `pie-eth0`. `ethtool pie-eth0`: driver `ice`, `Link detected: no` (E823-C
  backplane). Values are session-specific; the technique is the reusable part.

### METHOD-014: cscope-first navigation + parallel subagent fan-out
- **scope**: methodology (NXOS-tree code navigation) (platform default: Silicon One)
- **status**: verified
- **date**: 2026-06-30
- **tags**: cscope, navigation, subagents, search, nxos-cscope
- **method**:
  - The workspace is a multi-GB NFS tree; root `rg`/`grep`/`find` TIME OUT (~25s) and
    flood context. Use the prebuilt cscope index (`nxos-cscope` skill) as the PRIMARY
    code-navigation tool instead.
  - DB: `standalone/cscope.out` (covers `standalone/` + `converged/`). Run from
    `standalone/` or pass `-f cscope.out`. Non-interactive `-L` form:
    `/router/bin/cscope-64 -d -L -<n> "<sym>" -f cscope.out` where `-1`=def,
    `-0`=symbol/all-refs, `-2`=callees, `-3`=callers, `-4`=text, `-6`=egrep, `-7`=file.
  - Anchor on function/struct/macro names (STABLE), never line numbers (drift, rule 7);
    the cscope text column gives the snippet to re-anchor by content.
  - **Verify/triage an anchor:** `-1` finds real function defs. If `-1` MISSES, the
    symbol is almost always a global **fn-ptr / RNI-wired / static / macro** -- confirm
    with `-0` (shows the `<global>` decl + assignment sites). Seen for
    `lcnd_encap_fill_plat_hdr` + `lcnd_netdev_destructor` (fn-ptrs set in
    `lcnd_platform_init` / `lcnd_set_rni_vectors`).
  - **Sender vs subscriber** for an MTS opcode / `LC_ND_*` verb: `-0` lists every ref;
    a WRITER assigns it (`x.lc_nd_mod_code = LC_ND_*;` then ioctl, or `mts_send`/
    `fu_mts_send_notify`); a SUBSCRIBER is a registration table or `case`/handler.
    Multiple legitimate senders are common -- classify each ref, don't stop at the first.
  - **`-3` (callers) can SILENTLY UNDER-REPORT -- cross-check before trusting "no
    caller".** On the klm_vdc walk, `-3` returned *empty* for `vdc_add_src_index_mapping`,
    `vdc_add_ifindex_mapping`, `vdc_add_ipaddr_mapping`, `vdc_set_q_mapping`,
    `vdc_clear_global_inband_q_stats`, `vdc_set_base_diag_vlan` -- every one of which has
    real callers (IM/PCM/MCEC/MCM/IP/PM). `-0/-4` on the same DB segfaulted/hung. When a
    "no caller" result would change a conclusion (e.g. "legacy/dead API"), **confirm with
    a SCOPED `rg`** over source dirs only -- e.g.
    `rg -nw 'vdc_add_src_index_mapping' standalone/{feature,infra,platform,routing-sw}`
    -- explicitly EXCLUDING `third-party/` + `bazel-*` (their bulk is what makes an
    unscoped root `rg` time out). Also remember `-3`/`-0` never see **`dlopen`/`dlsym`**
    call sites (e.g. LLDP loads `libvdcklm.so` at runtime) -- grep the `dlsym("<name>")`
    string literal for those.
  - **Fan-out:** for breadth (dozens of opcodes/symbols/flows), dispatch parallel
    read-only `explore` subagents, each given a SCOPED symbol list + this cscope recipe +
    the sender/subscriber rubric, returning name anchors only. The primary re-verifies
    the few anchors that matter (`-1`/`-0`) and owns synthesis + the knowledge write.
- **evidence**: 2026-06-30 FLOW-005 -- root `rg` timed out at 25s; switched to
  `standalone/cscope.out` (6.0G, Jun-28). ~40 App E/F anchors validated via `-L -1`;
  4 fn-ptr/static symbols missed `-1` and were confirmed via `-0`
  (`vlan_set_lcnd_flags`, `lcnd_encap_fill_plat_hdr`, `lcnd_netdev_destructor`,
  `rni_register_kimdata`). Initiator verification + Appendices A-F were traced by
  parallel `explore` subagents each running cscope. 2026-07-09 klm_vdc walk (FLOW-009):
  `-3` under-reported the mapping/queue/stats wrapper callers (returned empty despite
  IM/PCM/MCEC/MCM/IP/PM callers); scoped `rg` over `standalone/{feature,infra,platform,
  routing-sw,converged}` recovered them in ~1s, and the LLDP `dlsym` caller was found by
  grepping the `libvdcklm.so`/symbol literals.
- **notes**: **Scope = the NXOS source tree only** (`standalone/`, `converged/` via
  `standalone/cscope.out`). The skill's OWN markdown KB (`KNOWLEDGE.md`,
  `knowledge/*.md`, `references/*.md`) is NOT in `cscope.out` -- locate an id/body there
  with Grep/Read (e.g. `grep -n '^### <ID>:' knowledge/entries.md`), never cscope.
  Complements METHOD-005 (scoped Glob/Read fallback when cscope is unavailable). If the
  index is missing/stale, ASK before rebuilding (`cscope-64 -b -q -k` is slow on the
  full tree, per `nxos-cscope`). Decoded/runtime values stay session-only; persist only
  the technique.

### METHOD-015: Group perf `lcnd_traces` output on a per-packet basis
- **scope**: methodology (offline analysis of `perf script` lcnd_traces dumps)
- **status**: verified
- **date**: 2026-06-30
- **tags**: perf, lcnd_traces, tracepoint, per-packet, grouping, skb-reuse, offline
- **method**:
  - **Capture** using the canonical on-box perf pattern (**METHOD-021**). While
    traffic is live (or during the user's repro window), run a **timed** capture:
    ```text
    run bash sudo sh -c "rm -f /bootflash/lcnd.perf /bootflash/lcnd_traces.txt; \
      timeout <DUR> perf record -a -e 'lcnd_traces:*' -o /bootflash/lcnd.perf -- sleep <DUR>; \
      perf script -i /bootflash/lcnd.perf > /bootflash/lcnd_traces.txt 2>&1"
    ```
    `<DUR>` = capture seconds — **ASK the user; DEFAULT 10**. Pull the decoded text
    with `run bash sudo cat /bootflash/lcnd_traces.txt` or SCP from bootflash.
    **Remote pull alternative** (decode on switch, stream text locally):
    ```text
    sshpass -e ssh -F /dev/null admin@<switch> \
      'run bash sudo sh -c "timeout <DUR> perf record -a -e '"'"'lcnd_traces:*'"'"' -o /bootflash/lcnd.perf -- sleep <DUR>; perf script -i /bootflash/lcnd.perf"' \
      > /tmp/lcnd_traces_fresh.log
    ```
    Legacy pipe `perf record … -o - | perf script -i -` still works on some hosts but
    prefer METHOD-021 file-based capture (reliable on sup LXC; avoids `--no-pager` pitfall).
  - Input is that `perf script` dump: each non-blank line is
    `comm pid [cpu] ts: lcnd_traces:<event>: <TP_printk msg>`. The LCND datapath
    emits an ordered BURST of tracepoints per packet within a single call chain
    (KSTACK-024); goal is to re-emit those bursts as one block per packet.
  - **Do NOT bucket by `skb=` globally** -- three traps: (1) the original `skb`
    pointer is RECYCLED across later packets, so a global skb bucket merges
    distinct packets; (2) the RX clone tracepoints (`lcnd_skb_clone_kstack/_lldp/
    _lacp/_ctp`) print the `skb_clone()` **nskb**, a DIFFERENT pointer, so a
    skb-equality rule would split the clone out of its own packet; (3) the
    TX/encap path REBUILDS the skb mid-chain (platform headroom), so the encap
    skb changes at `lcnd_encap_multicast` onward -- apply the skb-equality check
    to RX groups ONLY, never to TX.
  - **Use a per-CPU entry->terminal state machine** instead:
    - ENTRY opens a group: `lcnd_decap` (RX) / `lcnd_encap` (TX). Key it by
      cpu + the entry's original skb.
    - MEMBERS attach to the open group on that cpu (punt_hdr has no skb; parse/
      flow-mgr/pktmgr carry the original skb -> require skb match; clone events
      carry nskb -> attach unconditionally while a group is open).
    - TERMINAL closes it: `lcnd_decap_stack`/`lcnd_skb_exit` (RX ok),
      `lcnd_encap_added_platform_headers` (TX ok), any `*_drop` (drop). A new
      ENTRY on the same cpu, or EOF, also closes (verdict `truncated`).
    - SELF-CONTAINED events are their own 1-line packet: `mgmt_lcnd_decap_fwd/
      _match` (mgmt-inband path), plus bookkeeping families `lcnd_fdb_*`,
      `lcnd_pvlan_*`, `lcnd_hash_*`, `*_error` (but `lcnd_encap_error` is a TX
      drop terminal, not standalone).
  - **Leading parse line before an entry**: encap emits `lcnd_eth [Out]` just
    BEFORE `lcnd_encap` (a flood burst reads `...added_platform_headers, eth,
    lcnd_encap, ...`). Hold members that arrive with no open group in a per-CPU
    PENDING buffer and prepend them to the group the next ENTRY opens; if a
    terminal arrives with only pending (no entry), emit the buffer as an orphan.
  - A non-clone RX member whose skb != the open RX group's skb (address reuse
    without a captured ENTRY) -> split into an orphan group. (RX only.)
  - Deliverable script: `scripts/group_by_packet.py` in THIS skill (run as
    `python3 <skill>/scripts/group_by_packet.py /tmp/lcnd_traces_v2.log`). Mandatory
    `input` positional; output defaults to `<input>.grouped.log` (written beside the
    INPUT, not the script), or `<input>.<dir>.grouped.log` when a query is given.
    Classification sets are grounded in `lcnd_trace.h` + `lcnd_n9k.c` call sites,
    not in the sample data. See scripts/README.md `## Written scripts`.
  - **Query/filter mode** (`-q/--query k=v ...`, repeatable/comma/space-sep):
    mandatory `dir` selects direction by group kind -- `in`=decap (RX-decap/orphan),
    `out`=encap (TX-encap), `mgmt`=mgmt path (`mgmt_lcnd_decap_fwd/_match`). Other
    keys filter by any-line field match with ALIAS folding across the differently
    -named spellings (`if`<-ifname/interface/name; `ifindex`<-ifidx/phy_ifindex;
    `iod`<-phy_iod/lc_iod; `vlan`<-pm_vlan/vlan_id; `proto`<-protocol/pm_proto/
    ethtype/etype/skb->protocol; plus vni/sw_bd/smac/dmac/saddr/daddr/skb/len/flags/
    cpu). Value match normalizes hex==dec and canonicalizes MACs (`aa:bb..`==`aabb.`).
  - **Direction-specific params** (fields that only appear in one path): decap-only
    SONE punt-header keys `relay_id/slp/dlp/ssp/dsp/punt-code/punt-source/
    fwd_header_type` (canonical short names; the long spellings source_lp/
    destination_lp/source_sp/destination_sp/code/source still fold in as aliases);
    encap-only inject platform-header keys `dmod/slot/inst/dest/qos/phb_tc/l3_dlp/
    down_nh`; interface canonical is `intf` (if/ifname/interface/name fold in).
    `punt-source` uses a `source(?!_)` lookahead so it never captures source_lp/
    source_sp. `--list-params` prints every queryable key grouped by direction
    (common / in / out / mgmt) with its aliases; querying a param outside its dir
    emits a stderr warning (it will match nothing). This is how you slice branch
    decisions offline, e.g. `-q dir=in slp=0x4019 relay_id=1` (see METHOD-012 for
    lp/relay keys).
  - **Interpreting results (no partial match)**: a query is an AND of every param.
    If the EXACT query returns 0 matches, CONCLUDE the packet was not seen in that
    capture and report that plainly -- do NOT re-query a subset of the params and
    then present a partially-matching packet's block as if it were relevant (a
    packet that differs in even one field, e.g. `punt-code`, is a different flow).
    If the user wants that packet, re-capture (a longer `<DUR>` window and/or while
    the target flow is live), then re-run the exact query.
- **evidence**: 2026-06-30 `lcnd_traces.log` (595 events) -> 232 packets: 52
  RX-decap (51 delivered + 1 truncated at EOF) + 124 mgmt-fwd + 56 mgmt-match, 0
  unparsed; every RX group starts at `lcnd_decap`, both demux variants intact,
  clone `nskb` stayed with parent, recycled skb did not merge packets. TX
  validated on `lcnd_traces_v2.log` (692 events) -> 222 packets: 33 RX-decap +
  30 TX-encap (all 9-event units, delivered) + 76 mgmt-fwd + 83 mgmt-match, 0
  unparsed, 0 orphans; encap mid-chain skb swap (`_multicast`) and the leading
  `lcnd_eth [Out]` both handled; v1 output unchanged (no regression).
- **notes**: `lcnd_skb_exit` and `lcnd_skb_clone_ctp` are DEFINED but never
  emitted (dead tracepoints, KSTACK-024) -- harmless to classify. Line numbers in
  perf dumps are the running image's, not source; anchor grouping on event NAMES
  (stable), never on the sample's skb/interface values (volatile).

### METHOD-016: Grab ASIC / card identity from a live switch, then classify SONE vs TOR
- **scope**: methodology (identify a switch's ASIC family + platform from switch details) (platform default: Silicon One)
- **status**: verified
- **date**: 2026-07-08
- **tags**: switch-access, asic, card-id, sw-card-id, silicon-one, sone, tor, identity, codename
- **method**: When the user provides switch access/details, resolve the ASIC and
  platform BEFORE reasoning about a datapath (the decap/encap function is
  platform-specific, KSTACK-003). Access is MCP-first / `sshpass -e` fallback
  (METHOD-008); all commands below are read-only / non-disruptive (rule 11).
  0. **Parallelize collection with subagents when feasible (handoff dispatch mode).**
     If more than one independent data pull is needed -- multiple switches, multiple
     slots/modules (`slot <n> quoted`, METHOD-009), or distinct data domains gathered
     at once (identity vs `lcnd hash-tables` vs perf `lcnd_traces` vs IPsec ladder) --
     fan out **parallel non-readonly** subagents (SKILL rule 12; readonly/Ask-mode
     subagents have no network/MCP and CANNOT reach the switch). Give EACH subagent a
     **handoff dispatch-mode prompt** (read `handoff` SKILL "Dispatch mode": include
     the template + the `Constraints (hard)` and `Return Contract` blocks). Per-agent:
     a SCOPED read-only command set + its own switch creds (creds don't auto-propagate)
     + a **fresh `mktemp` known_hosts** + "disconnect any MCP session you open."
     Constraints for switch collection: **propose/return raw output only, do NOT write
     the KB**; **read-only commands only** (no config/`clear`/reload); redact
     serials/secrets; stay in the assigned scope. **Single-actor rule:** never run
     config-churn in parallel on one box -- collection is read-only so parallel reads
     are safe, but if any step mutates the switch, pick ONE actor for that window. The
     PRIMARY re-verifies the returned data, synthesizes the identity, and owns the KB
     write. If subagents are unavailable, collect sequentially in the primary.
  1. **Identity commands** (paste output; redact serials/secrets):
     - `show module` -> per-slot Model (PID) + card type/state.
     - `show version` -> chassis string, CPU, running image.
     - `show inventory` -> PID + serial per chassis/module.
     - `show sprom module <mod> <idx> | include 'Mfg Bits'` -> ASIC variant bits
       (e.g. Eastlake Krypton-Lite: value `>4096` => E2 else E1).
     - `show hardware internal` (platform-specific) for ASIC instance detail when
       PID alone is ambiguous.
  2. **Map PID/chassis/codename -> ASIC family** using FLOW-006
     (`references/hw-codenames-sone.md`, the KSTACK-relevant SONE subset) or, for a
     non-SONE / unlisted card, the authoritative Confluence "Hardware codenames"
     page (Cisco Highly Confidential; re-fetch as it drifts).
     - **Cache-refresh protocol (do this on every Confluence access):** the full page
       is cached locally at `references/hw-codenames-confluence-cache.md`. Whenever you
       successfully fetch the live page (Atlassian MCP `getConfluencePage`, pageId
       561414869), REFRESH that cache: rewrite the body + bump the metadata
       (`page_version`, `cached_at`). If the returned `page_version` is unchanged, the
       cache is current -- no rewrite needed.
     - **Fallback when access is lost:** if the live page is unreachable (MCP down /
       auth lost), use the local cache; tell the user you are on the CACHED copy and
       cite its `page_version` + `cached_at` so staleness is explicit. Keep the cache
       contents local -- Cisco Highly Confidential.
  3. **Classify in code terms** (KSTACK-028): a SONE-family card =>
     `SW_CARD_ID_IS_WITH_SONE_FAMILY_ASIC(sw_card_id)` true => Silicon One datapath
     (`lcnd_sone_inband_decap` / `lcnd_sone_encap_fill_plat_hdr`, the KSTACK
     default, KSTACK-005). `SW_CARD_ID_IS_TOR(sw_card_id)` distinguishes ToR boxes.
     A non-SONE card selects a different `lcnd_<plat>_inband_decap` (Domain Map
     dispatch table) -- do NOT cross-cite (KSTACK-003).
  4. If the PID/codename is not in FLOW-006, the local cache, or the live Confluence
     page, STOP and report the unknown card rather than guessing its ASIC/platform.
- **evidence**: 2026-07-08 -- macros `SW_CARD_ID_IS_WITH_SONE_FAMILY_ASIC` /
  `SW_CARD_ID_IS_TOR` verified in `platform_cmn_intf.h` (KSTACK-028); codename ->
  model -> ASIC mapping cached from the Confluence "Hardware codenames" page
  (pageId 561414869, page_version 422) into `references/hw-codenames-sone.md` (SONE
  subset) and the FULL page into `references/hw-codenames-confluence-cache.md`; the
  page's own Eastlake note documents the `show sprom module ... | include 'Mfg Bits'`
  variant check. Parallel-subagent switch access verified viable per SKILL rule 12
  (non-readonly background subagent reached the lab switch via ssh + Nexus MCP).
- **notes**: PIDs/codenames/membership are VOLATILE (new cards ship) -- anchor on
  the ASIC family + the `SW_CARD_ID_IS_WITH_SONE_FAMILY_ASIC` macro, and re-fetch
  Confluence + re-read the macro when a card is unlisted. Keep Confluence content in
  the local skill brain only (Cisco Highly Confidential). Complements METHOD-008
  (switch access), METHOD-009 (module-level collection), METHOD-014 (subagent
  fan-out), the `handoff` skill (dispatch-mode prompts), KSTACK-023 (sw_card_id
  header), FLOW-006 (codename table + full-page cache).

### METHOD-017: Monthly incremental PR sweep for baselined kstack components
- **scope**: methodology (repeatable maintenance of `bug_reports/<comp>/` per-PR reports)
- **status**: verified
- **date**: 2026-07-10
- **tags**: pr-sweep, incremental, watermark, cron, cscid, idempotent, ghe, cdets, propose-only
- **method**:
  - Keep a per-component watermark in `bug_reports/_sweep_state.json`
    (`{path, last_sha, last_run, count, baseline_pending}`). Only components with
    `baseline_pending:false` are swept; a new component is onboarded with a FULL
    initial pass first, then flipped to `false` at the current `origin/nx_main` head.
  - **Delta = SHA-range first, date fallback.** `git log --format=%s
    <last_sha>..origin/nx_main -- <path>`; if `git merge-base --is-ancestor
    <last_sha> origin/nx_main` fails (history rewrite/force-push), fall back to
    `git log --format=%s --since=<last_run> ...`. Extract CSCIDs from the commit
    **subject** (`%s`, not the full body `%B`) with `CSC[a-z]{2}[0-9]{5}`
    (case-insensitive); the PR's own defect leads the subject, so this maps 1:1 to a
    report and avoids the hundreds of unrelated CSCIDs that rollup/code-drop commit
    BODIES enumerate. Normalize to the canonical on-disk form `CSC`+lowercase (e.g.
    `CSCwu19801`, matching the report filenames) so dedup and the files enrichment
    writes both agree, then `sort -u`.
  - **Idempotent by construction:** subtract any CSCID that already has a
    `bug_reports/<comp>/<CSCID>.md`; never overwrite a report, so re-runs are safe.
  - **Full-gated depth:** enrich each new CSCID (GHE PR + CDETS + slice diff) into a
    `<CSCID>.md`, prepend a `Summary.md` row, and draft KB proposals into
    `_kb_verification.md` — then PAUSE for human KB approval.
  - **Verify-before-advance:** advance a component's watermark to the swept head SHA
    ONLY after every expected `<CSCID>.md` is confirmed present on disk.
  - **Trigger = local cron on the workstation**, not a Cursor/cloud automation: the
    GHE + CDETS MCPs are user-local (`~/.cursor/mcp.json`; one at `devtools-mcp.cisco.com`)
    and the NXOS clone is a workstation-only `/nobackup/...` checkout.
  - **Repo path is a per-run INPUT, not hardcoded** (the `/nobackup/.../<IMG>` clone
    rotates per image build). Both scripts resolve it as `--repo PATH` > `KSTACK_REPO`
    env > interactive `/dev/tty` prompt (stored `.repo` as default) > stored `.repo`,
    then VALIDATE (dir + `git rev-parse --is-inside-work-tree` + `rev-parse --verify
    <.branch>`) and PERSIST the validated path back to `.repo`. A stale/rotated path
    ABORTS non-zero ("repo path '<X>' is not a valid git checkout of <branch> -- pass
    --repo <PATH> or set KSTACK_REPO") instead of a false `0 new`. cron has no TTY, so it
    MUST pass `--repo`/`KSTACK_REPO` explicitly; `monthly_sweep.sh` resolves once and
    threads the same `$REPO` into every `--list`/`--advance` + its HEAD_SHA rev-parse.
  - **KB stays propose-only:** the runner NEVER writes `~/.agents/skills/kstack/**`;
    proposals in `_kb_verification.md` are applied by a human (SKILL rule 12).
  - **Confluence mirror (publish stage).** After enrich+verify+advance,
    `monthly_sweep.sh` step 4 mirrors the reports of already-onboarded components
    (those present in `bug_reports/_confluence_map.json`) into Confluence via
    `tools/confluence_publish.py` (Markdown -> storage XHTML by `md_to_confluence.py`
    -> REST v2 create/update). Policy = new CSCID -> new page, `Summary` always
    refreshed, an existing bug page updated only when its `.md` `md_sha256` changed
    (tracked in the map). Every page gets a TOC macro + full-width tables; **true
    page-level wide width is NOT settable through the Atlassian MCP**, so it is set
    with a Confluence REST API token via the Cloud v2 page property
    `content-appearance-published=full-width` (and `-draft`) at
    `/wiki/api/v2/pages/{id}/properties`. Credentials come ONLY from
    `~/.config/kstack/confluence.env` (mode 600; env vars `CONFLUENCE_EMAIL` +
    `CONFLUENCE_API_TOKEN`), sourced at runtime — the token is NEVER printed, logged,
    or written into `_confluence_map.json` / `_sweep_state.json` / logs / any file
    (reference only the file path + var names). The stage skips with a warning if the
    token file, the map, or `cursor-agent` is absent (publish is deterministic, so the
    script can also be run directly). A component is mirrored only once it is in the
    map, so a not-yet-approved component is never auto-published.
  - Tooling lives in `bug_reports/tools/` (`kstack_pr_sweep.sh` delta engine +
    `monthly_sweep.sh` orchestrator + `enrich_prompt.tmpl` + `crontab.example`, plus
    the Confluence publish set `md_to_confluence.py` + `confluence_publish.py` +
    `publish_confluence_prompt.tmpl` and the page map `_confluence_map.json`); the
    stored `_sweep_state.json .repo` is only a default/last-known-good.
- **evidence**: 2026-07-10 — `kstack_pr_sweep.sh --dry-run` reported `0 new` for
  KLM_PS_INB and KLM_VDC at seeded `last_sha=9b61f1c546f` (== `origin/nx_main` head;
  `git merge-base --is-ancestor` = yes; `git log 9b61f1c546f..origin/nx_main -- <vdc
  path>` = 0 commits). Baselined counts: KLM_PS_INB 46, KLM_VDC 57. KIM/KVFIB/LCND
  left `baseline_pending:true` (excluded until a full pass exists).
- **notes**: Anchor CSCIDs and function/symbol names, not line numbers (rule 7). The
  delta engine touches only git + the local FS (no GHE/CDETS); enrichment (which does
  call the MCPs) runs as a separate, human- or cursor-agent-driven step. Complements
  METHOD-014 (cscope/subagent fan-out) and the `handoff` skill (dispatch-mode prompts).

### METHOD-018: Validate private raw-netlink hardening with least-mutating header-only ACK probes
- **scope**: methodology (LCND/private raw-netlink authorization and payload-bound validation)
- **status**: verified
- **date**: 2026-07-16
- **tags**: netlink, validation, cap-net-admin, payload-bounds, nxos, sudo, python
- **method**:
  - Split runtime validation into two intentionally small probes that do not
    carry a real payload and therefore should not add/delete table state.
  - **Unauthorized sender gate:** run a Python netlink sender from ordinary
    admin bash and first print `/proc/self/status` `CapEff`. If `CapEff` is zero,
    send a 16-byte `struct nlmsghdr` only (`nlmsg_len == sizeof(nlmsghdr)`) with
    `NLM_F_ACK` to the target protocol/type. Expected fixed behavior for a
    `netlink_capable(..., CAP_NET_ADMIN)` gate is `send_ok` followed by receive
    timeout/no ACK, because the handler returns before parsing/ACKing.
  - **Privileged malformed-payload gate:** confirm `feature bash-shell` and
    `run bash sudo -n id`, then run the same Python sender with
    `run bash sudo -n python3 <script>`. First verify effective caps are
    non-zero / include `CAP_NET_ADMIN`. Send the same 16-byte ACK-request
    header. Expected fixed behavior for payload-size hardening is an
    `NLMSG_ERROR` ACK with `err=-22` (`EINVAL`), proving the handler reached the
    payload-length check but rejected before `nlmsg_data()` fields were consumed.
  - Re-check relevant services after the run and remove any temporary script.
- **evidence**: CSCwv32090 on `des1infra` / `172.20.175.106` (fixed image
  `nxos64-s1-dpu.10.7.0.IMG9.0.231.F.bin`): admin bash sender showed
  `CapEff=0000000000000000` and `NETLINK_FDB(31)`, `NETLINK_MPLS(28)`,
  `NETLINK_VLAN_GID(26)` each returned `no_ack_timeout`. Sudo sender showed
  `CapEff=000001ffffffffff`; the same three protocols returned
  `ack type=2 err=-22 len=36`. Post-test `show system internal sysmgr service
  name ipfib` and `... kim` showed both services handshaked and never crashed
  since reboot.
- **notes**: NX-OS SSH command parsing does not reliably allow multiple
  `run bash ... ; run bash ...` segments inside one remote CLI command; prefer
  separate SSH invocations for each `run bash` command. `scp` to NX-OS may fail
  silently after the login banner; transferring a short script with
  `ssh 'run bash tee /tmp/<script>.py >/dev/null' < local.py` worked. Clean up
  the temporary script and do not persist credentials, runtime PIDs, or table
  contents in the KB.

### METHOD-019: Privileged NX-OS `run bash` one-liners via `sudo sh -c`
- **scope**: methodology (NX-OS Linux shell access from CLI, SSH, MCP)
- **status**: verified
- **date**: 2026-07-26
- **tags**: nxos, run-bash, sudo, dmesg, perf, cap-net-admin, mcp, lxc
- **method**:
  - Plain **`run bash <cmd>`** runs as an **unprivileged** user inside the sup/LXC
    namespace: no read of `/dev/kmsg` (`dmesg` -> permission denied), no
    `CAP_NET_RAW` (tcpdump fails — see METHOD-013), and typically `CapEff=0` for
    crafted netlink probes (METHOD-018 unauthorized gate).
  - For **any** Linux command that needs root — **`dmesg`**, **`perf`**, debug/proc
    writes, or `CAP_NET_ADMIN` senders — use a **single** privileged wrapper and put
    the **entire pipeline inside the quoted string**:
    - **Default kmsg read on sup LXC (MCP/SSH):**
      `run bash sudo sh -c "dmesg -F /dev/kmsg -P | grep cisco_nb"` — plain
      `dmesg`/`dmesg -P` can return empty even when `/dev/kmsg` has records
      (KSTACK-055).
    - **Raise console printk before chasing sparse `pr_info`:**
      `run bash sudo sh -c "echo '8 6 1 8' > /proc/sys/kernel/printk"` (optional
      `echo on > /proc/sys/kernel/printk_devkmsg`). Does **not** surface tracepoint
      hot path; does not fix plain `dmesg` on 107.
    - **Non-interactive single binary** (when `-n` works on-box): `run bash sudo -n
      python3 /tmp/script.py` (METHOD-018). **Kernel perf capture:** wrap full
      record+decode in `sudo sh -c "…"` per **METHOD-021** — not bare
      `run bash sudo timeout … perf record` without bootflash `-o` + `perf script -i`.
    - **Interactive shell:** `run bash sudo bash` (root `bash-#` prompt)
  - **Do NOT** rely on `run bash sudo dmesg | grep …` — the pipe may be parsed by
    the NX-OS CLI outside sudo. **Do NOT** chain `run bash … ; run bash …` in one
    CLI line (METHOD-018 notes); use separate invocations.
  - Require **`feature bash-shell`** before sudo paths. Verify elevation with
    `run bash sudo sh -c 'id -u'` (expect `0`) or `run bash sudo -n id` when `-n`
    is supported. On some images `sudo -n -c '…'` is rejected (prints sudo usage);
    fall back to `sudo sh -c`.
  - **Empty plain `dmesg` after sudo is not proof of no kernel activity** on sup LXC
    — re-read with **`dmesg -F /dev/kmsg -P`** (KSTACK-055). Netbroker RTNL trap
    still needs tracepoints/perf or nbproxy event-history for proof.
- **evidence**: 2026-07-26 on `172.20.175.107` (`10.7(0)IMG9(0.166)`, cgroup
  `lxc-*-vdc1sup1`): bare `run bash dmesg` permission denied; plain `run bash sudo
  sh -c "dmesg -P"` empty; injected `<6>probe` visible via `dmesg -F /dev/kmsg -P`
  and `dd if=/dev/kmsg`. `echo 8 > /proc/sys/kernel/printk` -> `8 6 1 1`; still no
  plain `dmesg` output; `ip route add … lo` in nbproxy event-history, zero
  `cisco_nb` in kmsg even after printk tune. `run bash sudo -n -c '…'` printed sudo
  usage; `sudo sh -c` worked.
- **notes**:   Complements METHOD-008 (switch access), METHOD-013 (unprivileged bash
  limits), METHOD-018 (sudo python3 probes). Persist technique only — no switch
  credentials in KB.

### METHOD-020: End-to-end netbroker validation (kernel perf + nbproxy event-history)
- **scope**: methodology (verify netbroker trap → nbproxy → completion on a live switch)
- **status**: verified
- **date**: 2026-07-26
- **tags**: netbroker, nbproxy, perf, cisco_nb_traces, validation, e2e, test
- **method**:
  - **Goal:** From one CLI `ip route add` (unprivileged bash `ip`, not whitelisted
    NXOS daemon), observe **both** kernel tracepoints **and** nbproxy NX-OS debug
    lines for the same transaction.
  - **Prerequisites:** `feature bash-shell`; `klm_cisco_nb` loaded; nbproxy
    `SRV_STATE_HANDSHAKED`; `/proc/net/cisco_nb_0` lists brokers with nbproxy pid;
    `disable_rtnl_hook=N`; `block_rib=N`; `perf list | grep cisco_nb` shows
    `cisco_nb_traces:*` (requires **`run bash sudo bash`** or `sudo sh -c` — METHOD-019).
  - **Step 0 — enable NX-OS side trace:**
    `debug nbproxy events`
  - **Step 1 — kernel capture + stimulus (METHOD-021 stimulus-bound pattern):**
    ```text
    run bash sudo sh -c "rm -f /bootflash/nb.perf /bootflash/nb_traces.txt; \
      perf record -a -e 'cisco_nb_traces:*' -o /bootflash/nb.perf -- \
      ip route add 192.0.2.88/32 via 127.0.0.1 dev lo; \
      perf script -i /bootflash/nb.perf > /bootflash/nb_traces.txt 2>&1"
    ```
    See **METHOD-021** for the general kernel perf recipe (timed vs stimulus-bound,
    decode rules, `perf list` probe). Interactive root bash: `run bash sudo bash`, then
    the same `perf record … -- …` / `perf script -i … > …` with shell redirect.
  - **Step 2 — NX-OS side trace:**
    `show nbproxy internal event-history events | include "IP Netbroker|operation 3|static route|Netbroker failed|Unknown interface"`
  - **Step 3 — outcome checks:**
    `run bash ip route show 192.0.2.88` (expect Linux FIB entry on `lo` test);
    `show ip route 192.0.2.88` (expect **not found** for `lo`/ENODEV path).
  - **Step 4 — cleanup:**
    `run bash ip route del 192.0.2.88/32 via 127.0.0.1 dev lo`
  - **Pass — kernel (`/bootflash/nb_traces.txt`, 7 lines on 107):**
    1. `ip` `nb_rtnl_doit` `family=0 type=18 group=0` — `RTM_GETLINK` probe, not trapped
    2. `ip` `nb_rtnl_doit` `family=2 type=24 group=4` — `RTM_NEWROUTE` → `NB_GRP_STATIC_ROUTE`
    3. `ip` `nb_send_request` `group=4 seq=N`
    4. `nbproxy` `nb_rtnl_doit` `type=18 group=0` — replay link probe on broker rtnl_sk
    5. `nbproxy` `nb_rtnl_doit` `type=24 group=4` — `libnb_update_kernel` replay
    6. `nbproxy` `nb_rcv_request` `group=4 seq=N`
    7. `nbproxy` `nb_rtnl_resp` `msg_type=24 status=0` — ACK to original `ip` socket
    Elapsed ~250µs trap→resp on 107 (`4502.049888` → `4502.050139`).
  - **Pass — NX-OS (same second, nbproxy pid e.g. 21580):**
    `IP Netbroker event for operation 3` → `IPv4 static route process op 3` →
    `Unknown interface type lo` → `Netbroker failed to process config: -19` (`ENODEV`).
    Operation **3** = `LIBNB_CFG_ROUTE_ADD`. `-19` on `lo` is **expected** for this
    probe; netbroker still proved end-to-end. For URIB/dynamic path use a real
    `Ethernet*` interface instead of `lo`.
  - **Fail hints:** empty perf file → events not exposed or hook disabled; no nbproxy
    lines → broker not registered or debug off; only `group=0` lines → message not
    mapped/trapped.
- **evidence**: Re-run 2026-07-26 on `172.20.175.107` (`10.7(0)IMG9(0.166)`): infra
  OK (nbproxy 21580 HANDSHAKED, all groups registered); perf 7 samples; nbproxy
  events at `18:58:34` UTC; Linux FIB `192.0.2.88 via 127.0.0.1 dev lo`. Matches
  user capture from interactive bash (`seq=11` vs agent re-run `seq=14`).
- **notes**: See FLOW-013 § E2E validation, KSTACK-054/055, switch-commands Netbroker
  block. Kernel capture/decode uses **METHOD-021** (stimulus-bound). Do not use plain
  `dmesg` for kernel hot path (KSTACK-055). Replace test prefix `192.0.2.88/32` if it
  collides. Session-local only — no credentials/PIDs in shared KB beyond illustrative
  examples.

### METHOD-021: Canonical NX-OS kernel perf trace capture (all tracepoint subsystems)
- **scope**: methodology (capture + decode kernel `TRACE_EVENT` subsystems on NX-OS sup/LC)
- **status**: verified
- **date**: 2026-07-26
- **tags**: perf, tracepoint, kernel, lcnd_traces, cisco_nb_traces, sudo, bootflash, capture
- **method**:
  - **Privilege (hard rule):** all on-switch perf work runs under **`run bash sudo sh -c
    '<pipeline>'`** or interactive **`run bash sudo bash`** (METHOD-019). Never bare
    `run bash perf …`.
  - **Step 0 — discover events on THIS image** (subsystems vary by build):
    ```text
    run bash sudo sh -c "perf list | grep -E 'lcnd_traces|cisco_nb'"
    ```
    If the subsystem is missing, stop — perf cannot prove that path on this box.
  - **Step 1 — record** to a **bootflash `.perf` data file** (tracepoints do not appear
    in plain `dmesg` — KSTACK-055). Two capture modes:
    - **Timed (background traffic / LCND datapath):** wrap `sleep <DUR>`. **ASK `<DUR>`;
      DEFAULT 10s.**
      ```text
      run bash sudo sh -c "rm -f /bootflash/<tag>.perf /bootflash/<tag>_traces.txt; \
        timeout <DUR> perf record -a -e '<SUBSYSTEM>:*' -o /bootflash/<tag>.perf -- sleep <DUR>; \
        perf script -i /bootflash/<tag>.perf > /bootflash/<tag>_traces.txt 2>&1"
      ```
    - **Stimulus-bound (single admin action / netbroker RTNL):** repro command after `--`.
      ```text
      run bash sudo sh -c "rm -f /bootflash/<tag>.perf /bootflash/<tag>_traces.txt; \
        perf record -a -e '<SUBSYSTEM>:*' -o /bootflash/<tag>.perf -- <stimulus>; \
        perf script -i /bootflash/<tag>.perf > /bootflash/<tag>_traces.txt 2>&1"
      ```
    Use **`-a`** (all CPUs). Quote event globs: `'lcnd_traces:*'`, `'cisco_nb_traces:*'`.
  - **Step 2 — inspect:**
    ```text
    run bash sudo cat /bootflash/<tag>_traces.txt
    ```
  - **Decode pitfalls (107, util-linux 2.39.3):**
    - **`perf script --no-pager` is INVALID** — use `> file` redirect or interactive
      `perf --no-pager script -i …`.
    - Keep pipes **inside** `sh -c "…"` (METHOD-019); do not `run bash sudo perf | grep`.
  - **Known subsystems:**
    | Subsystem | Event glob | Capture mode | Post-process |
    |-----------|------------|--------------|--------------|
    | LCND datapath | `lcnd_traces:*` | Timed `<DUR>` | `scripts/group_by_packet.py` (METHOD-015) |
    | Netbroker | `cisco_nb_traces:*` | Stimulus-bound | FLOW-013 § E2E (METHOD-020) |
  - **Remote decode stream (optional):**
    ```text
    sshpass -e ssh -F /dev/null admin@<switch> \
      'run bash sudo sh -c "timeout <DUR> perf record -a -e '"'"'lcnd_traces:*'"'"' -o /bootflash/lcnd.perf -- sleep <DUR>; perf script -i /bootflash/lcnd.perf"' \
      > /tmp/lcnd_traces_fresh.log
    ```
- **evidence**: 2026-07-26 `172.20.175.107`: netbroker stimulus capture 7 lines;
  `perf script -i /bootflash/nb.perf > file` OK; `--no-pager` failed. LCND timed
  variant aligned with METHOD-015 grouping workflow.
- **notes**: Complements METHOD-015/019/020. Use descriptive `<tag>` (`lcnd`, `nb`).
  Clean up bootflash when done. No credentials in KB templates (METHOD-008).

### METHOD-022: Load+run eBPF on NX-OS with no bcc/bpftool/libbpf — off-box compile + raw bpf() kprobe loader
- **scope**: running eBPF on a locked-down NX-OS switch (broken on-box clang/BCC, no bpftool)
- **status**: verified
- **date**: 2026-07-30
- **tags**: ebpf, bpf, kprobe, perf_event_open, ctypes, raw-syscall, clang, off-box, s1-dpu
- **method**: NX-OS SONE images ship a working BPF verifier + kprobe/BPF_EVENTS but
  broken userspace eBPF tooling (`libclang-cpp.so.*` missing → clang/BCC dead; no
  `bpftool`; `bpftrace` missing `libbpf.so.1`). To run eBPF anyway:
  1. **Compile OFF-box** (a host with working clang): `clang -O2 -target bpf -c prog.c
     -o prog.o`; write the program self-contained (declare helpers as
     `static long (*fn)(...) = (void*)<BPF_FUNC_id>` — e.g. trace_printk=6,
     skb_store_bytes=9, skb_load_bytes=26 — so there are NO map relocations and the
     raw section bytes are directly loadable). `llvm-objcopy --dump-section
     <sec>=prog.bin prog.o` to get raw insns.
  2. **Ship** via base64 over `run bash sudo sh -c 'echo <b64> | base64 -d > /bootflash/…'`
     (scp is awkward; base64 stays inside the CLI). Verify md5.
  3. **Load with a pure-Python raw-`bpf()` loader** (ctypes): `syscall(321,
     BPF_PROG_LOAD=5, &attr, size)` with a `bpf_attr` ctypes.Structure (let ctypes do
     `__aligned_u64` alignment) + a 64KB `log_buf` to capture verifier errors; set
     `prog_type` (KPROBE=2 works even though TC/XDP won't attach), `license="GPL"`.
     Attach a kprobe: write `p:NAME func` to `.../tracing/kprobe_events` (use plain
     `O_WRONLY`, NOT append — O_APPEND's nonzero offset → EINVAL), read the tracepoint
     `id`, `perf_event_open(type=PERF_TYPE_TRACEPOINT,config=id,pid=-1,cpu=0)`,
     `ioctl(pfd, PERF_EVENT_IOC_SET_BPF=0x40042408, prog_fd)`,
     `ioctl(pfd, PERF_EVENT_IOC_ENABLE=0x2400)`.
  4. **Set `tracing_on=1`** or `bpf_trace_printk` output is dropped; read
     `.../trace_pipe`. Distinguish "not firing" from "trace off" via
     `.../kprobe_profile` nhit.
  5. **Teardown order matters**: close the perf fd FIRST (else the kprobe is busy),
     then the prog fd, then write `-:NAME` to `kprobe_events` (append→EINVAL again;
     use O_WRONLY). Leftover `p:kprobes/NAME` means the perf fd was still open.
- **evidence**: 2026-07-30 switch 107 — `vdc_kprobe_poc.py` loaded a 23-insn kprobe
  prog (prog_fd), hooked `eth_type_trans_inb` (klm_vdc) and `finish_task_switch`,
  logged via bpf_trace_printk (kprobe_profile 42 / 53111 nhit). syscall#: x86_64
  bpf=321, perf_event_open=298. See session `files/vdc_kprobe_poc.py`.
- **notes**: For a *rewrite* (TC/XDP) prog the loader is the same but attach fails on
  this image (KSTACK-056). Reusable for any "eBPF on a switch with no bcc" task.
