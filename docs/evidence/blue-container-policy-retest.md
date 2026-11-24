# Blue Team retest: container policy initialization

Verified locally on November 24, 2026. Fix commit: 87c47da.

Before: policy indexing and retrieval succeeded, but evidence export failed because the non-root process could not create /srv/app/redteam/results.

Change: container policy build evidence now goes to /srv/data/evidence on the mounted volume.

Retest: a fresh release container reopened the volume, found the identities, policy index and build evidence, and successfully retrieved policy passages. This run did not call Groq or test a hosted deployment.
