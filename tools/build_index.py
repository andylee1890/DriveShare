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
    providers_path = root / "data" / "providers.json"
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
    provider_catalog = read_json(providers_path).get("providers", []) if providers_path.exists() else []
    provider_by_name = {item["name"]: item for item in provider_catalog}
    provider_aliases = {
        "阿里云盘": "aliyun-drive", "百度网盘": "baidu-netdisk", "115生活": "115",
        "夸克网盘": "quark", "UC网盘": "uc-drive", "天翼云盘": "tianyi",
        "腾讯微云": "weiyun", "PikPak": "pikpak", "360云盘": "360-yunpan",
        "Google Drive": "google-drive", "OneDrive": "onedrive", "Dropbox": "dropbox",
        "MEGA": "mega", "pCloud": "pcloud", "Proton Drive": "proton-drive",
        "Yandex Disk": "yandex-disk", "iCloud Drive": "icloud-drive", "Seafile": "seafile",
        "Box": "box", "Cloudflare R2": "cloudflare-r2",
    }
    provider_by_id = {item["id"]: item for item in provider_catalog}
    provider_catalog_public = []
    for item in provider_catalog:
        public_item = dict(item)
        if item.get("icon"):
            public_item["iconUrl"] = f"/DriveShare/assets/providers/{item['icon']}"
        provider_catalog_public.append(public_item)

    def provider_info(name: str) -> dict:
        provider_id = provider_aliases.get(name)
        item = provider_by_id.get(provider_id) if provider_id else provider_by_name.get(name)
        if not item:
            return {"name": name, "providerId": provider_id}
        result = {"name": item["name"], "providerId": item["id"]}
        if item.get("icon"):
            result["icon"] = f"/DriveShare/assets/providers/{item['icon']}"
        return result
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
        "providers": provider_catalog_public or sorted({item["provider"] for item in sets}),
        "setCount": len(sets),
        "sets": [],
    }
    for source in sets:
        item = dict(source)
        item["providerInfo"] = provider_info(source["provider"])
        item["links"] = []
        for source_link in sorted(source["links"], key=lambda link: link["position"]):
            link = dict(source_link)
            link["providerInfo"] = provider_info(source_link["provider"])
            if source_link["id"] in health_by_id:
                link["health"] = health_by_id[source_link["id"]]
            item["links"].append(link)
        index["sets"].append(item)

    index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Generated {index_path} ({len(sets)} sets, {len(link_ids)} links)")


if __name__ == "__main__":
    main()
