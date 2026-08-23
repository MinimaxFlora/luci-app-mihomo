# luci-app-mihomo

在 OpenWrt 上使用 Mihomo 进行透明代理的 LuCI 插件(基于 [nikkinikki-org/OpenWrt-nikki](https://github.com/nikkinikki-org/OpenWrt-nikki) 移植)。

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

## 环境要求

- OpenWrt / ImmortalWrt >= 24.10
- Linux Kernel >= 5.13
- firewall4

## 编译

```shell
# 将本仓库加入 feeds(二选一)
echo "src-git mihomo https://github.com/MinimaxFlora/luci-app-mihomo.git;main" >> "feeds.conf.default"
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

## 安装

```shell
# opkg
opkg install mihomo luci-app-mihomo luci-i18n-mihomo-zh-cn
# apk
apk add mihomo luci-app-mihomo luci-i18n-mihomo-zh-cn
```

也可以在 LuCI「系统 → 软件包」中安装。安装后到「服务 → Mihomo」中上传/订阅配置并启用。

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

打 tag(如 `v1.0.0`)自动触发 GitHub Actions 构建,使用 ImmortalWrt SDK 24.10.5(ipk)与 25.12.0(apk)产出全部三个包并发布到 Releases。

## 致谢

- [nikkinikki-org/OpenWrt-nikki](https://github.com/nikkinikki-org/OpenWrt-nikki) —— 本项目的前身
- [MetaCubeX/mihomo](https://github.com/MetaCubeX/mihomo) —— mihomo 核心
