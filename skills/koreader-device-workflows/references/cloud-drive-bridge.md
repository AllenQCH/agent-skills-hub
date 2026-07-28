# KOReader 与夸克/百度网盘的云盘桥接

## 本次验证结果

KOReader 当前仓库的 `plugins/cloudstorage.koplugin` provider 目录只包含：

- `dropbox.lua`
- `webdav.lua`
- `ftp.lua`

因此 KOReader 的 Cloud storage+ 不是一个通用网盘登录器，不能直接填写夸克网盘或百度网盘账号。

KOReader 官方文档支持：

- Cloud storage：Dropbox / FTP / WebDAV；
- OPDS：自定义 OPDS catalog，浏览并下载电子书；
- Kindle/Kobo/PocketBook 上的 SSH/SFTP 文件传输。

## 推荐架构

```text
Quark / Baidu Netdisk
        ↓ provider/driver
OpenList 或 AList
        ↓ WebDAV
KOReader Cloud storage+
        ↓
/mnt/us/books/ 或 /mnt/us/books/inbox/
```

OpenList 文档的 storage driver 列表包含 `Baidu Netdisk` 和 `Quark / TV`，同时提供 WebDAV endpoint。WebDAV 地址的通用形式是：

```text
http[s]://<host>:<port>/dav/
```

本地 Mac 示例（端口以实际部署配置为准）：

```text
http://192.168.1.20:5244/dav/
```

## KOReader 配置要点

```text
工具 → Cloud storage+ → 添加 → WebDAV
```

建议使用 OpenList 专用低权限账号：

- 只给目标书籍目录的读取/下载权限；
- 不授予删除、重命名、移动、复制、上传，除非确实需要；
- 下载目录设置为 `/mnt/us/books/inbox/`；
- 用一个小 EPUB 先验证，再批量下载。

## 部署建议

### Mac 本地桥接

- Kindle 与 Mac 连接同一可信 Wi-Fi；
- OpenList 运行在 Mac 上；
- Mac 关闭或服务停止时，Kindle 无法访问网盘；
- 适合家庭局域网，避免公网暴露。

### NAS/VPS/远程桥接

- OpenList 运行在 NAS、家庭服务器或 VPS；
- 远程访问优先使用 Tailscale/VPN；
- 不要直接把 WebDAV 端口裸露到公网；
- 使用 HTTPS、专用账号和最小权限。

## 不推荐的路径

直接把夸克/百度分享链接粘到 KOReader 浏览器或下载器中，通常不稳定，因为分享页可能依赖登录 Cookie、JavaScript、验证码、临时下载链接和防盗链。它适合临时测试，不适合作为日常书库入口。

第三方 rclone/AList/OpenList driver 可能随云盘接口变化而失效；部署后要用一个小文件验证列目录、下载和断线重连。不要把夸克/百度 Cookie、refresh token 或密码写入聊天、笔记或公开配置。

## 替代方案：Mac 网盘客户端 + Calibre

```text
百度/夸克客户端下载到 Mac
        ↓
导入 Calibre
        ↓ Wi-Fi
KOReader Calibre wireless / OPDS
        ↓
/mnt/us/books/
```

这是依赖最少、批量管理最稳的方案，但不能让 Kindle 直接浏览云盘。

## 权威来源

- KOReader Cloud storage 源码：`plugins/cloudstorage.koplugin/providers/`
- KOReader User Guide：`https://koreader.rocks/user_guide/`
- KOReader OPDS：`https://github.com/koreader/koreader/wiki/OPDS-support`
- KOReader SSH：`https://github.com/koreader/koreader/wiki/SSH`
- OpenList Quark driver：`https://doc.oplist.org/guide/drivers/quark.html`
- OpenList WebDAV：`https://doc.oplist.org/guide/webdav.html`
- AList Baidu/Quark driver docs：`https://alistgo.com/guide/drivers/quark.html`
