"""Build the website-facing DriveShare index from data/sets/*.json."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()
    set_dir = root / "data" / "sets"
    status_path = root / "data" / "link-status.json"
    index_path = root / "data" / "index.json"

    sets = [read_json(path) for path in sorted(set_dir.glob("*.json"))]
    set_ids: set[str] = set()
    link_ids: set[str] = set()
    for item in sets:
        if item["id"] in set_ids:
            raise ValueError(f"Duplicate set id: {item['id']}")
        set_ids.add(item["id"])
        links = sorted(item["links"], key=lambda link: link["position"])
        positions = [link["position"] for link in links]
        if positions != list(range(1, len(positions) + 1)):
            raise ValueError(f"Positions for set {item['id']} must be continuous from 1")
        for link in links:
            if link["id"] in link_ids:
                raise ValueError(f"Duplicate link id: {link['id']}")
            link_ids.add(link["id"])

    status = read_json(status_path) if status_path.exists() else {"links": {}}
    health_by_id = status.get("links", {})
    index = {
        "schemaVersion": 1,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "repository": "andylee1890/DriveShare",
        "repositoryUrl": "https://github.com/andylee1890/DriveShare",
        "website": "https://englishanchor.online",
        "purpose": "English Anchor 网盘分享套索引，供网站展示和检索。",
        "indexPath": "/DriveShare/data/index.json",
        "statusValues": {
            "published": "公开展示中的分享套。",
            "archived": "历史记录，不作为默认推荐。",
            "draft": "尚未完成核验，不应作为稳定资源推荐。",
        },
        "linkHealthValues": {
            "unchecked": "尚未检查。",
            "online": "HTTP 请求可达；不代表网盘内容完整。",
            "redirected": "发生跳转，需要人工确认最终页面。",
            "requires_manual_check": "需要登录、Cookie、口令或反爬验证。",
            "offline": "请求失败或明确不可达。",
            "unknown": "无法可靠判断。",
        },
        "providers": sorted({item["provider"] for item in sets}),
        "setCount": len(sets),
        "sets": [],
    }
    for source in sets:
        item = dict(source)
        item["links"] = []
        for source_link in sorted(source["links"], key=lambda link: link["position"]):
            link = dict(source_link)
            if source_link["id"] in health_by_id:
                link["health"] = health_by_id[source_link["id"]]
            item["links"].append(link)
        index["sets"].append(item)

    index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Generated {index_path} ({len(sets)} sets, {len(link_ids)} links)")


if __name__ == "__main__":
    main()

