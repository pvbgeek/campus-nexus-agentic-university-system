# Contributing

Use synthetic data only. Do not commit API keys, passwords, sessions, operational databases, model caches or local source backups. Review `git status` and the staged diff before every commit.

Pull team changes before editing shared files. The team's current workflow uses normal commits to main; do not force push or replace history.

The primary app is `app.main:app`. Reproduce the current build with `requirements-agents.lock.txt` and the User Guide. Use `scripts/check_progress.py` for current verification; the old course walkthrough targets the preserved starter only.

For a code change, run the checks affected by it and record failures honestly. Do not repeatedly consume model quota when a change only affects documentation. Never relabel a provider test double as a live model result.

Red Team work is restricted to this authorized local synthetic application. Preserve case/run IDs, expected/observed outcome, logs and retest links. Report model recommendation separately from independent authorization and actual execution.

Update individual contributions with completed work and current status. An assigned role is not proof of authorship. Keep known limitations and unresolved findings visible in the progress and final reports.
