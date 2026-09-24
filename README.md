# DriveShare

English Anchor 网盘分享索引。项目按“套”维护分享资源；一套可以包含一个或多个网盘链接，例如一个总分享链接和若干指向具体课程目录的子链接。

DriveShare 不发布 Release，也不保存网盘文件本身。仓库只维护分享链接、面向网页的主索引，以及链接有效性检查记录。网站应直接消费 `data/index.json`，部署时同步到 R2 的 `DriveShare/data/index.json`。

## 目录

- `data/sets/`：每套分享的源数据，一个 JSON 文件对应一套分享。
- `data/index.json`：由源数据聚合生成的网页主索引，包含套、链接、排序和最新检查状态。
- `schemas/`：数据结构说明和校验约束。
- `tools/`：构建索引和检查链接的本地脚本。
- `reports/`、`temp/`：本地生成的报告和临时文件，不提交 Git。

## 维护流程

1. 在 `data/sets/` 新增或修改一套分享文件，保持 `links[].position` 连续且稳定。
2. 运行 `pwsh -File tools/build-index.ps1`，重新生成 `data/index.json`。
3. 运行 `pwsh -File tools/check-links.ps1` 检查链接。检查结果写入 `data/link-status.json`，不会覆盖套的标题、说明或 URL。
4. 人工复核失效或需要登录的链接，再提交源数据和索引。
5. 使用 R2 的差异同步命令，把 `data/index.json` 和需要公开的 `data/sets/` 同步到 `english-anchor-public-prod/DriveShare/`。

链接检查只能说明当前 HTTP 响应是否可达，不能证明网盘内文件仍完整；需要登录、需要口令或被反爬拦截的链接应标记为 `requires_manual_check`。

## 索引地址

生产网站使用相对资源路径，不在前端代码中写死 R2 域名。R2 对外映射后，主索引路径固定为：

`/DriveShare/data/index.json`

