"""Publish a reviewed policy to the local retrieval index as a deployment operator."""
import argparse
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.storage import audit, database


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("draft_id", nargs="?", help="Approved draft ID; omit to list approved drafts")
    args = parser.parse_args()
    with database() as db:
        if not args.draft_id:
            rows = db.execute(
                "SELECT id,title,reviewed FROM policy_drafts WHERE status=? ORDER BY reviewed DESC",
                ("approved",),
            ).fetchall()
            for row in rows:
                print(row["id"], row["reviewed"], repr(row["title"]))
            if not rows:
                print("No approved drafts.")
            return

        draft = db.execute(
            "SELECT content,status FROM policy_drafts WHERE id=?", (args.draft_id,)
        ).fetchone()
    if draft is None or draft["status"] != "approved":
        parser.exit(2, "Only approved policy drafts can be published.\n")

    from app.policy_index import build_policy_index

    with tempfile.TemporaryDirectory(prefix="campus-policy-") as folder:
        source = Path(folder) / "reviewed-policy.md"
        source.write_text(draft["content"], encoding="utf-8")
        manifest = build_policy_index(source)

    with database(write=True) as db:
        audit(db, args.draft_id, "policy_draft_published",
              actor="deployment_operator", collection=manifest["collection"])
    print("Published reviewed draft:", args.draft_id)
    print("Active retrieval collection:", manifest["collection"])


if __name__ == "__main__":
    main()
