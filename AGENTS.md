# DriveShare Maintenance Instructions

## Purpose

DriveShare is a public index of external cloud-drive share sets. It is not a file mirror, downloader, release repository, or credential store. Never copy shared-drive contents into this repository.

## Data model

- A **set** is the unit users see and select. One set may contain one root share and any number of related folder/file links.
- A **link** belongs to exactly one set and has a stable `id`, display `title`, `position`, `kind`, `provider`, and `url`.
- `kind` is one of `root`, `folder`, `file`, or `other`.
- `provider` is the normalized Chinese provider name, such as `阿里云盘`.
- Keep URLs exactly as supplied by the owner. Do not shorten, rewrite, or append tracking parameters.
- `data/sets/*.json` is the editable source. `data/index.json` is the website-facing aggregate generated from those files.
- `data/providers.json` is the provider catalog. Provider icons live in `assets/providers/`; use its stable provider ID and relative icon path in generated website data.
- Link health is separate from content: `data/link-status.json` records the latest automated observation keyed by link ID. A failed check must not silently delete or rewrite a link.

## Stable identifiers

- Set IDs use lowercase kebab-case and never change after publication.
- Link IDs are `<set-id>-<short-name>` and never change after publication.
- Rename display text without changing IDs. A moved folder remains the same link if its URL is unchanged.

## Status values

Set status: `published`, `archived`, `draft`.

Link health state: `unchecked`, `online`, `redirected`, `requires_manual_check`, `offline`, `unknown`.

Automated HTTP checks are advisory. Aliyun and other providers may reject `HEAD`, require cookies, return anti-bot pages, or return a login page with HTTP 200. Mark these as `requires_manual_check`, not `online`.

## Index workflow

1. Edit or add one file in `data/sets/`.
2. Validate JSON and run `python tools/build_index.py`.
3. Run `python tools/check_links.py`; inspect the generated report and `data/link-status.json`.
4. Review changes to title, URLs, ordering, and status manually.
5. Commit source files, the regenerated `data/index.json`, and link status only when the status change is useful to consumers.

When adding a provider, first check the AList and rclone source inventories. Do not claim support merely because a backend exists: rclone backends often require account authorization and are not public-share providers. Do not copy third-party repositories into the project; keep research clones under the workspace `tmp/` directory.

The index must retain `schemaVersion`, `generatedAt`, `repository`, `website`, `statusValues`, `providers`, and the complete `sets` array. Do not make the website reconstruct sets by scanning a GitHub repository.

## R2 publication

R2 is a deployment target, not the source of truth. Sync only the public DriveShare data, for example:

`rclone sync DriveShare/data r2-english-anchor:english-anchor-public-prod/DriveShare/data`

Do not sync `.git`, `reports`, `temp`, local credentials, or arbitrary workspace files. Verify the remote index after synchronization.
