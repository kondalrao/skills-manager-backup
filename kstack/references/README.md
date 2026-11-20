# KSTACK flow references

End-to-end datapath flows and protocol command references for the `kstack` skill.
Use one flow per file when the material is direction-specific; use one
protocol-level file when command ladders or state correlation apply to both TX
and RX.

## Naming

- Direction-specific: `<protocol>-<direction>.md` -- e.g. `cdp-ingress.md`,
  `arp-punt.md`, `dhcp-relay.md`, `vxlan-decap.md`.
- Protocol-wide: `<protocol>.md` -- e.g. `ipsec.md` when shared SUP/module
  commands apply to TX and RX and direction-specific flows live as sections.
- No specific protocol: append the flow to `catch-all.md`.

## Each flow file contains

- A `FLOW-NNN` id, protocol, platform (default Silicon One), `status`
  (`verified | unverified | superseded`), and date.
- Ordered steps: `function -> function`, anchored on function/macro/snippet names
  (NOT `file:line` -- line numbers drift), with the field transformations at each
  step (what is read/written, e.g. `relay_id -> vlan -> l2ra_vni <-
  lc_if_info.lc_vlan`). Keep volatile values (line numbers, interface names,
  per-session hex) out of steps; put any observed values in a dated illustrative
  note. (See KNOWLEDGE.md "VOLATILE vs STABLE" banner / SKILL.md "Stable anchors
  only".)
- Known divergence points / branches (flag-gated paths).
- Shared protocol command ladders, when useful, with clear TX/RX scope and
  redaction notes for sensitive switch output.

## Keep the index in sync

After creating or updating a flow file, add/update its row in the
`## References` table of `../KNOWLEDGE.md` in the SAME edit. When a linked Entry is
`superseded`/`fixed`, update the affected flow step labels here too (e.g. mark a
step "was bug / now fixed") so the flow does not assert stale behavior.

## On reuse

When a live problem matches a recorded flow, walk the saved flow and report the
**differences between past and present** -- that delta is usually the bug.
