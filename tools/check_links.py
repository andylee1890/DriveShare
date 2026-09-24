"""Check link reachability and save advisory health observations."""

from __future__ import annotations

import argparse
import json
import re
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def check(url: str, timeout: int) -> dict:
    state = "unknown"
    status = None
    final_url = None
    error = None
    request = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "DriveShare-LinkChecker/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            status = response.status
            final_url = response.geturl()
            state = "online" if 200 <= status < 300 else "redirected" if 300 <= status < 400 else "offline"
    except urllib.error.HTTPError as exc:
        status = exc.code
        final_url = exc.geturl()
        state = "requires_manual_check" if exc.code in {401, 403, 429} else "offline"
        error = str(exc)
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        error = str(exc)
        state = "requires_manual_check" if re.search(r"login|captcha|forbidden|unauthorized", error, re.I) else "unknown"
    return {
        "state": state,
        "checkedAt": utc_now(),
        "httpStatus": status,
        "finalUrl": final_url,
        "error": error,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--timeout", type=int, default=20)
    args = parser.parse_args()
    root = args.root.resolve()
    set_dir = root / "data" / "sets"
    status_path = root / "data" / "link-status.json"
    report_dir = root / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)

    results = {}
    for path in sorted(set_dir.glob("*.json")):
        source = json.loads(path.read_text(encoding="utf-8"))
        for link in sorted(source["links"], key=lambda item: item["position"]):
            result = check(link["url"], args.timeout)
            results[link["id"]] = result
            print(f"{result['state']}\t{link['id']}")

    payload = {"schemaVersion": 1, "checkedAt": utc_now(), "links": results}
    serialized = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    status_path.write_text(serialized, encoding="utf-8")
    report_path = report_dir / f"link-check-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    report_path.write_text(serialized, encoding="utf-8")
    print(f"Saved {status_path}")
    print(f"Saved {report_path}")


if __name__ == "__main__":
    main()

