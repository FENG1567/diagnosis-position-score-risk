"""Retrieve pinned AmsterdamUMCdb SQL used to identify score and diagnosis fields."""

import hashlib
import json
from pathlib import Path
import urllib.request


ROOT = Path(__file__).resolve().parents[3]
WORK = ROOT / "work" / "v2" / "amsterdam"
OUT = ROOT / "outputs" / "v2" / "amsterdam"
REPOSITORY = "AmsterdamUMC/AmsterdamUMCdb"
COMMIT = "5422b94dbaba6c1d9b7c301f059c425ca1fc13ce"
FILES = (
    "amsterdamumcdb/sql/common/legacy/gcs.sql",
    "amsterdamumcdb/sql/diagnosis/legacy/reason_for_admission.sql",
)


def main() -> None:
    (WORK / "references").mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    records = []
    for relative_path in FILES:
        url = (
            f"https://raw.githubusercontent.com/{REPOSITORY}/"
            f"{COMMIT}/{relative_path}"
        )
        request = urllib.request.Request(
            url, headers={"User-Agent": "PaperB-Amsterdam-supplementary-audit"}
        )
        with urllib.request.urlopen(request, timeout=40) as response:
            blob = response.read()
        target = WORK / "references" / Path(relative_path).name
        target.write_bytes(blob)
        records.append(
            {
                "repository": REPOSITORY,
                "commit": COMMIT,
                "relative_path": relative_path,
                "url": url,
                "local_path": str(target.relative_to(ROOT)),
                "bytes": len(blob),
                "sha256": hashlib.sha256(blob).hexdigest(),
            }
        )
    (OUT / "official_sql_provenance.json").write_text(
        json.dumps(records, indent=2), encoding="utf-8"
    )
    print(json.dumps(records, indent=2))


if __name__ == "__main__":
    main()
