# luci-app-mihomo

[![Docs](https://img.shields.io/badge/docs-doc.kejizero.xyz-ec4899)](https://doc.kejizero.xyz/)
[![latest version](https://img.shields.io/github/release/MinimaxFlora/luci-app-mihomo)](https://github.com/MinimaxFlora/luci-app-mihomo/releases)
[![license](https://img.shields.io/github/license/MinimaxFlora/luci-app-mihomo)](LICENSE)

在 OpenWrt 上使用 Mihomo 进行透明代理的 LuCI 插件(基于 [nikkinikki-org/OpenWrt-nikki](https://github.com/nikkinikki-org/OpenWrt-nikki) 移植)。

**📚 文档站:[https://doc.kejizero.xyz/](https://doc.kejizero.xyz/)**(用户指南 / 安装教程 / 配置指南 / FAQ / 更新日志,中英双语,源码见 [MinimaxFlora/Mihomo-Docs](https://github.com/MinimaxFlora/Mihomo-Docs))

本仓库包含两个包:

| 包 | 说明 |
|---|---|
| `mihomo` | 核心包:内置 mihomo 核心(Go 源码编译)+ procd 服务脚本 + ucode 配置混入 + nftables 透明代理规则 |
| `luci-app-mihomo` | LuCI 前端:6 个页面,卡片化界面,与 LuCI 主题联动(明/暗色) |

## 功能

- 透明代理(Redirect / TPROXY / TUN,IPv4 和/或 IPv6)
- 访问控制(路由器本机 / LAN 设备,支持用户、组、cgroup、IP、MAC)
- 配置文件混入(Mixin,含 9 类配置:常规 / 外部控制 / 入站 / TUN / DNS / 嗅探 / 规则 / GeoX / 自定义文件)
- 配置文件编辑器(配置文件 / 订阅 / 规则集 / 代理集 / mixin)
- 订阅管理(URL / UA / 用量 / 到期时间 / 手动更新)
- 定时重启、日志轮转清理、调试日志下载
- 状态仪表盘(运行状态 / 版本 / 当前配置 / 快捷操作)
- 插件/核心一键在线更新

## 安装

### 一键脚本

```shell
# 自动检测架构与固件版本,下载解压安装(自动安装缺失的 tar/gzip/curl)
curl -fsSL https://raw.githubusercontent.com/MinimaxFlora/luci-app-mihomo/master/install.sh > install-mihomo.sh && sh install-mihomo.sh
```

### 软件源(opkg/apk)

```shell
# 添加官方软件源(自动检测固件版本与架构,安装签名公钥)
curl -fsSL https://raw.githubusercontent.com/MinimaxFlora/luci-app-mihomo/master/feed.sh > feed-mihomo.sh && sh feed-mihomo.sh

# 安装
opkg install luci-app-mihomo        # OpenWrt 24.10
apk add --allow-untrusted luci-app-mihomo   # OpenWrt 25.12
```

软件源地址:`https://feed.kejizero.xyz/<分支>/<架构>/mihomo`

### 手动安装

从 [GitHub Releases](https://github.com/MinimaxFlora/luci-app-mihomo/releases) 或[文档站下载页](https://doc.kejizero.xyz/guide/installation/download.html)下载对应架构的压缩包,解压后安装:

```shell
tar -xzf mihomo_<架构>-openwrt-<版本>.tar.gz
# OpenWrt 24.10
opkg install --force-reinstall bin/packages/*/mihomo/mihomo_*.ipk bin/packages/*/mihomo/luci-app-mihomo_*.ipk
# OpenWrt 25.12
apk add --allow-untrusted bin/packages/*/mihomo/mihomo-*.apk bin/packages/*/mihomo/luci-app-mihomo-*.apk
```

### 卸载

```shell
curl -fsSL https://raw.githubusercontent.com/MinimaxFlora/luci-app-mihomo/master/uninstall.sh > uninstall-mihomo.sh && sh uninstall-mihomo.sh
```

## 环境要求

- OpenWrt / ImmortalWrt >= 24.10
- Linux Kernel >= 5.13
- firewall4

## 编译

```shell
# 将本仓库加入 feeds(二选一)
echo "src-git mihomo https://github.com/MinimaxFlora/luci-app-mihomo.git;master" >> "feeds.conf.default"
./scripts/feeds update -a
./scripts/feeds install -a

# 编译
make package/mihomo/compile
make package/luci-app-mihomo/compile
```

编译产物位于 `bin/packages/<架构>/` 下:

- `mihomo`(核心)
- `luci-app-mihomo`(前端)
- `luci-i18n-mihomo-zh-cn`(简体中文翻译)

## 依赖

- ca-bundle
- curl
- yq
- firewall4
- ip-full
- kmod-inet-diag
- kmod-nft-socket
- kmod-nft-tproxy
- kmod-tun
- kmod-dummy

## 发布

打 tag(如 `v1.0.2`)自动触发 GitHub Actions:

1. **release**:openwrt/gh-action-sdk 多架构构建(24 架构 × openwrt-24.10/25.12),产物发布到 Releases
2. **feed**:构建完成后自动将 opkg/apk 软件源部署到 Cloudflare Pages([https://feed.kejizero.xyz](https://feed.kejizero.xyz),含签名公钥)

## 致谢

- [nikkinikki-org/OpenWrt-nikki](https://github.com/nikkinikki-org/OpenWrt-nikki) —— 本项目的前身
- [MetaCubeX/mihomo](https://github.com/MetaCubeX/mihomo) —— mihomo 核心
