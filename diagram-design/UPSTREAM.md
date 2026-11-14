# Upstream provenance

- Source: https://github.com/cathrynlavery/diagram-design
- Source commit: `d1376371965f513d99cc9ec388835d255c5c88d5`
- Plugin version at that commit: `2.6.64`
- Skill version at that commit: `2.6`
- License: MIT; see `LICENSE` and bundled notices in `THIRD_PARTY_LICENSES.md`.

This skill is installed as a standalone Agent Skill under `~/.agents/skills/diagram-design` on the local and remote Codex hosts. Refresh from the reviewed upstream commit or a later reviewed release; preserve the routing section in `SKILL.md` when updating.

The repository description says 42 diagram types, while the skill and plugin manifest at this commit say 44. Use the skill's type guide as the operational list.

The default HTML templates may load Google Fonts. For offline or privacy-sensitive output, remove the external font link and use the documented system-font fallback.

Local compatibility note: on the remote Codex host, `python3` resolves to 3.5; `/bin/python3.11` is available and should be used for this skill's scripts.
