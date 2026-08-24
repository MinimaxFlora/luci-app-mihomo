#!/bin/sh

# Mihomo's uninstaller

# uninstall
if [ -x "/bin/opkg" ]; then
	opkg list-installed luci-i18n-mihomo-* | cut -d ' ' -f 1 | xargs opkg remove
	opkg remove luci-app-mihomo
	opkg remove mihomo
elif [ -x "/usr/bin/apk" ]; then
	apk list --installed --manifest luci-i18n-mihomo-* | cut -d ' ' -f 1 | xargs apk del
	apk del luci-app-mihomo
	apk del mihomo
fi
# remove config
rm -f /etc/config/mihomo
# remove files
rm -rf /etc/mihomo
# remove log
rm -rf /var/log/mihomo
# remove temp
rm -rf /var/run/mihomo
# remove feed
if [ -x "/bin/opkg" ]; then
	if grep -q mihomo /etc/opkg/customfeeds.conf; then
		sed -i '/mihomo/d' /etc/opkg/customfeeds.conf
	fi
	wget -O "mihomo.pub" "https://feed.kejizero.xyz/key-build.pub"
	opkg-key remove mihomo.pub
	rm -f mihomo.pub
elif [ -x "/usr/bin/apk" ]; then
	if grep -q mihomo /etc/apk/repositories.d/customfeeds.list; then
		sed -i '/mihomo/d' /etc/apk/repositories.d/customfeeds.list
	fi
	rm -f /etc/apk/keys/mihomo.pem
fi
