# 网盘支持范围

DriveShare 的提供商目录参考了两个成熟项目：

- [AList](https://github.com/AlistGo/alist)：更偏向网盘聚合和分享场景。当前源码包含 115、123 云盘、阿里云盘、百度网盘、夸克/UC、天翼、腾讯微云、PikPak、迅雷、蓝奏、OneDrive、Google Drive、Dropbox、Mega、PikPak、WebDAV、S3 等驱动，以及 Cloudreve、Seafile 等自建存储。
- [rclone](https://github.com/rclone/rclone)：更偏向同步和对象存储。当前后端包含 Google Drive、OneDrive、Dropbox、Box、MEGA、pCloud、Proton Drive、Yandex Disk、iCloud Drive、S3、Cloudflare R2、Azure Blob、Backblaze B2、WebDAV、SFTP、SMB 等。

这两个项目的“支持”含义不同：AList 的驱动可能直接处理分享链接，rclone 的 backend 通常需要账户授权或配置，不能直接当作公开分享链接。DriveShare 只在实际出现分享链接时录入对应提供商。

## 图标规则

图标保存在 `assets/providers/`，目录和网页索引由 `data/providers.json` 维护。优先使用提供商公开 favicon；没有合适 favicon 时使用 [Simple Icons](https://github.com/simple-icons/simple-icons) 的 SVG。未确认来源的图标不提交，网页使用通用回退图标。

当前已经准备常用图标：阿里云盘、百度网盘、115、夸克网盘、UC 网盘、腾讯微云、PikPak、360 云盘、Google Drive、Dropbox、MEGA、Proton Drive、Yandex Disk、iCloud Drive、Seafile、Box、Cloudflare R2。

