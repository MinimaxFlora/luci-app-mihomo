#!/bin/sh
#==========================================
#  Mihomo LuCI 一键安装脚本 (OpenWrt)
#  https://github.com/MinimaxFlora/luci-app-mihomo
#
#  用法:
#    sh install.sh                            # 自动检测架构与固件版本
#    sh install.sh <架构> <版本>               # 手动指定,如: sh install.sh x86_64 24.10
#    sh install.sh <架构> <版本> <下载源>      # 指定下载源: github | kejizero | ghfast
#
#  示例:
#    sh install.sh
#    sh install.sh x86_64 24.10
#    sh install.sh aarch64_generic 25.12 kejizero
#==========================================

set -e

REPO="MinimaxFlora/luci-app-mihomo"
VERSION="v1.0.1"

ARCH="${1:-}"
BRANCH="${2:-}"
MIRROR="${3:-github}"

#---- 架构检测 ----
detect_arch() {
    case "$(uname -m)" in
        x86_64|amd64) echo "x86_64" ;;
        i386|i486|i586|i686) echo "i386_pentium4" ;;
        aarch64|arm64) echo "aarch64_generic" ;;
        armv8l) echo "aarch64_generic" ;;
        armv7l|armv6l) echo "arm_cortex-a7_neon-vfpv4" ;;
        mips) echo "mips_24kc" ;;
        mipsel) echo "mipsel_24kc" ;;
        riscv64) echo "riscv64_generic" ;;
        loongarch64) echo "loongarch64_generic" ;;
        *) echo "" ;;
    esac
}

#---- 固件版本检测 (存在 apk 包管理器则为 25.12) ----
detect_branch() {
    if command -v apk >/dev/null 2>&1; then
        echo "25.12"
    else
        echo "24.10"
    fi
}

#---- 下载前缀 ----
get_base() {
    case "$MIRROR" in
        kejizero) echo "https://gh-proxy.kejizero.xyz/https://github.com/$REPO" ;;
        ghfast) echo "https://ghfast.top/https://github.com/$REPO" ;;
        *) echo "https://github.com/$REPO" ;;
    esac
}

#---- 下载文件 ----
download() {
    if command -v curl >/dev/null 2>&1; then
        curl -fsSL "$1" -o "$2"
    elif command -v wget >/dev/null 2>&1; then
        wget -q "$1" -O "$2"
    else
        return 1
    fi
}

#---- 解压/下载工具检测 (部分精简固件未内置 tar/gzip) ----
ensure_tools() {
    missing=""
    for tool in tar gzip; do
        command -v "$tool" >/dev/null 2>&1 || missing="$missing $tool"
    done
    command -v curl >/dev/null 2>&1 || command -v wget >/dev/null 2>&1 || missing="$missing curl"
    if [ -n "$missing" ]; then
        echo "[Mihomo] 检测到缺少工具:$missing,正在尝试自动安装..."
        if command -v opkg >/dev/null 2>&1; then
            opkg update || true
            opkg install $missing
        elif command -v apk >/dev/null 2>&1; then
            apk update || true
            apk add --allow-untrusted $missing
        else
            echo "[Mihomo] 错误:未找到 opkg/apk 包管理器,请手动安装:$missing 后重试"
            exit 1
        fi
        # 重新校验
        for tool in tar gzip; do
            command -v "$tool" >/dev/null 2>&1 || {
                echo "[Mihomo] 错误:工具 $tool 安装失败,请手动安装后重试"
                exit 1
            }
        done
    fi
    echo "[Mihomo] 解压/下载工具就绪 ✓"
}

#---- 下载并安装 ----
install_pkg() {
    BASE="$(get_base)"
    FILE="mihomo_${ARCH}-openwrt-${BRANCH}.tar.gz"
    URL="${BASE}/releases/download/${VERSION}/${FILE}"

    echo "[Mihomo] 下载: $URL"
    if ! download "$URL" "$FILE"; then
        echo "[Mihomo] 错误:下载失败,请确认架构/版本正确或更换下载源"
        echo "[Mihomo] 支持架构: x86_64 aarch64_generic arm_cortex-a7_neon-vfpv4 arm_cortex-a9 mipsel_24kc mips_24kc riscv64_generic loongarch64_generic ..."
        exit 1
    fi

    echo "[Mihomo] 解压: $FILE"
    tar -xzf "$FILE"

    PKGDIR="bin/packages/${ARCH}/mihomo"
    [ -d "$PKGDIR" ] || PKGDIR="."

    echo "[Mihomo] 安装软件包..."
    if [ "$BRANCH" = "25.12" ]; then
        apk add --allow-untrusted "$PKGDIR"/mihomo-*.apk "$PKGDIR"/luci-app-mihomo-*.apk
        # 汉化包 (部分旧版本发布未包含,存在才安装)
        I18N_APKS="$(ls "$PKGDIR"/luci-i18n-mihomo-zh-cn-*.apk 2>/dev/null || true)"
        if [ -n "$I18N_APKS" ]; then
            apk add --allow-untrusted $I18N_APKS
        fi
    else
        opkg install --force-reinstall "$PKGDIR"/mihomo_*.ipk "$PKGDIR"/luci-app-mihomo_*.ipk
        # 汉化包 (部分旧版本发布未包含,存在才安装)
        I18N_IPKS="$(ls "$PKGDIR"/luci-i18n-mihomo-zh-cn_*.ipk 2>/dev/null || true)"
        if [ -n "$I18N_IPKS" ]; then
            opkg install --force-reinstall $I18N_IPKS
        fi
    fi

    rm -rf bin "$FILE"
    echo ""
    echo "[Mihomo] ✔ 安装完成!"
    echo "[Mihomo] 请进入 LuCI 界面 -> 服务 -> Mihomo 进行配置"
}

#---- 主流程 ----
main() {
    [ -z "$ARCH" ] && ARCH="$(detect_arch)"
    [ -z "$BRANCH" ] && BRANCH="$(detect_branch)"

    if [ -z "$ARCH" ]; then
        echo "[Mihomo] 无法自动检测架构 (uname -m: $(uname -m))"
        echo "[Mihomo] 请手动指定: sh install.sh <架构> <版本>"
        echo "[Mihomo] 例如: sh install.sh x86_64 24.10"
        echo "[Mihomo] 常见架构: x86_64 aarch64_generic arm_cortex-a7_neon-vfpv4 mipsel_24kc mips_24kc riscv64_generic loongarch64_generic"
        exit 1
    fi

    echo "[Mihomo] 架构: $ARCH | 固件: OpenWrt $BRANCH | 下载源: $MIRROR"
    ensure_tools
    install_pkg
}

main "$@"
