'use strict';
'require form';
'require view';
'require uci';
'require ui';
'require poll';
'require tools.mihomo as mihomo';

function resolveProfileLabel() {
    const cfg = uci.get('mihomo', 'config', 'profile');

    if (!cfg)
        return _('No Profile Selected');

    if (cfg.startsWith('file:'))
        return _('File:') + cfg.substring(5);

    if (cfg.startsWith('subscription:')) {
        const sid = cfg.substring(13);
        const subscriptions = uci.sections('mihomo', 'subscription');
        const sub = subscriptions.find(s => s['.name'] === sid);

        return _('Subscription:') + (sub ? sub.name : sid);
    }

    return cfg;
}

function renderStatus(running) {
    return E('span', { class: 'mihomo-status' }, [
        E('span', { id: 'mihomo_status_dot', class: 'mihomo-dot ' + (running ? 'up' : 'down') }),
        E('span', { id: 'mihomo_status_text', class: running ? 'up-text' : 'down-text' },
            running ? _('Running') : _('Not Running'))
    ]);
}

function updateStatus(running) {
    const dot = document.getElementById('mihomo_status_dot');
    const text = document.getElementById('mihomo_status_text');

    if (dot)
        dot.className = 'mihomo-dot ' + (running ? 'up' : 'down');

    if (text) {
        text.className = running ? 'up-text' : 'down-text';
        text.textContent = running ? _('Running') : _('Not Running');
    }
}

function runAction(promise) {
    return L.resolveDefault(promise).catch(function (err) {
        ui.addNotification(null, E('p', _('An error occurred: %s').format(err)), 8000);
    });
}

function buildDashboard(data) {
    const appVersion = data[1]?.app ?? '';
    const coreVersion = data[1]?.core ?? '';
    const running = data[2];

    return E('div', { class: 'mihomo-dash' }, [
        E('div', { class: 'mihomo-dash-head' }, [
            E('span', { class: 'mihomo-logo' }, '🚀'),
            _('Status Overview')
        ]),
        E('div', { class: 'mihomo-dash-grid' }, [
            E('div', { class: 'mihomo-tile' }, [
                E('div', { class: 'mihomo-tile-label' }, _('Core Status')),
                E('div', { class: 'mihomo-tile-value' }, renderStatus(running))
            ]),
            E('div', { class: 'mihomo-tile' }, [
                E('div', { class: 'mihomo-tile-label' }, _('App Version')),
                E('div', { class: 'mihomo-tile-value' }, appVersion || '-')
            ]),
            E('div', { class: 'mihomo-tile' }, [
                E('div', { class: 'mihomo-tile-label' }, _('Core Version')),
                E('div', { class: 'mihomo-tile-value' }, coreVersion || '-')
            ]),
            E('div', { class: 'mihomo-tile' }, [
                E('div', { class: 'mihomo-tile-label' }, _('Current Profile')),
                E('div', { class: 'mihomo-tile-value' }, resolveProfileLabel())
            ])
        ]),
        E('div', { class: 'mihomo-dash-actions' }, [
            E('button', { type: 'button', class: 'cbi-button cbi-button-action', click: function () { return runAction(mihomo.reload()); } },
                '🔄 ' + _('Reload Service')),
            E('button', { type: 'button', class: 'cbi-button cbi-button-negative', click: function () { return runAction(mihomo.restart()); } },
                '⏹️ ' + _('Restart Service')),
            E('button', { type: 'button', class: 'cbi-button cbi-button-positive', click: function () { return runAction(mihomo.updateDashboard()); } },
                '⬆️ ' + _('Update Dashboard')),
            E('button', { type: 'button', class: 'cbi-button cbi-button-apply', click: function () { return runAction(mihomo.openDashboard()); } },
                '🌐 ' + _('Open Dashboard'))
        ])
    ]);
}

return view.extend({
    load: function () {
        return Promise.all([
            uci.load('mihomo'),
            mihomo.version(),
            mihomo.status(),
            mihomo.listProfiles()
        ]);
    },
    render: function (data) {
        mihomo.injectCSS();

        const subscriptions = uci.sections('mihomo', 'subscription');
        const profiles = data[3];

        let m, s, o;

        m = new form.Map('mihomo', _('Mihomo'), `${_('Transparent Proxy with Mihomo on OpenWrt.')} <a href="https://github.com/MinimaxFlora/luci-app-mihomo" target="_blank">${_('How To Use')}</a>`);

        s = m.section(form.NamedSection, 'config', 'config', _('App Config'));

        o = s.option(form.Flag, 'enabled', _('Enable'));
        o.rmempty = false;

        o = s.option(form.ListValue, 'profile', _('Choose Profile'));
        o.optional = true;

        for (const profile of profiles) {
            o.value('file:' + profile.name, _('File:') + profile.name);
        };

        for (const subscription of subscriptions) {
            o.value('subscription:' + subscription['.name'], _('Subscription:') + subscription.name);
        };

        o = s.option(form.Value, 'start_delay', _('Start Delay'));
        o.datatype = 'uinteger';
        o.placeholder = _('Start Immidiately');

        o = s.option(form.Flag, 'scheduled_restart', _('Scheduled Restart'));
        o.rmempty = false;

        o = s.option(form.Value, 'scheduled_restart_cron', _('Scheduled Restart Cron'));
        o.retain = true;
        o.rmempty = false;
        o.depends('scheduled_restart', '1');

        o = s.option(form.Flag, 'test_profile', _('Test Profile'));
        o.rmempty = false;

        o = s.option(form.Flag, 'core_only', _('Core Only'));
        o.rmempty = false;

        s = m.section(form.NamedSection, 'procd', 'procd', _('procd Config'));

        s.tab('general', '⚙️ ' + _('General Config'));

        o = s.taboption('general', form.Flag, 'fast_reload', _('Fast Reload'));
        o.rmempty = false;

        s.tab('rlimit', '🛠️ ' + _('RLIMIT Config'));

        o = s.taboption('rlimit', form.Value, 'rlimit_nproc_soft', _('Number of Processes Soft Limit'));
        o.datatype = 'uinteger';

        o = s.taboption('rlimit', form.Value, 'rlimit_nproc_hard', _('Number of Processes Hard Limit'));
        o.datatype = 'uinteger';

        o = s.taboption('rlimit', form.Value, 'rlimit_address_space_soft', _('Address Space Size Soft Limit'));
        o.datatype = 'uinteger';
        o.placeholder = _('Unlimited');

        o = s.taboption('rlimit', form.Value, 'rlimit_address_space_hard', _('Address Space Size Hard Limit'));
        o.datatype = 'uinteger';
        o.placeholder = _('Unlimited');

        o = s.taboption('rlimit', form.Value, 'rlimit_data_soft', _('Heap Size Soft Limit'));
        o.datatype = 'uinteger';
        o.placeholder = _('Unlimited');

        o = s.taboption('rlimit', form.Value, 'rlimit_data_hard', _('Heap Size Hard Limit'));
        o.datatype = 'uinteger';
        o.placeholder = _('Unlimited');

        o = s.taboption('rlimit', form.Value, 'rlimit_stack_soft', _('Stack Size Soft Limit'));
        o.datatype = 'uinteger';
        o.placeholder = _('Unlimited');

        o = s.taboption('rlimit', form.Value, 'rlimit_stack_hard', _('Stack Size Hard Limit'));
        o.datatype = 'uinteger';
        o.placeholder = _('Unlimited');

        o = s.taboption('rlimit', form.Value, 'rlimit_nofile_soft', _('Number of Open Files Soft Limit'));
        o.datatype = 'uinteger';

        o = s.taboption('rlimit', form.Value, 'rlimit_nofile_hard', _('Number of Open Files Hard Limit'));
        o.datatype = 'uinteger';

        s.tab('environment_variable', '🌱 ' + _('Environment Variable Config'));

        o = s.taboption('environment_variable', form.Value, 'env_go_max_procs', 'GOMAXPROCS');
        o.datatype = 'uinteger';
        o.placeholder = _('Unlimited');

        o = s.taboption('environment_variable', form.Value, 'env_go_mem_limit', 'GOMEMLIMIT');
        o.datatype = 'uinteger';
        o.placeholder = _('Unlimited');

        o = s.taboption('environment_variable', form.DynamicList, 'env_safe_paths', _('Safe Paths'));
        o.load = function (section_id) {
            return this.super('load', section_id)?.split(':');
        };
        o.write = function (section_id, formvalue) {
            this.super('write', section_id, formvalue?.join(':'));
        };

        o = s.taboption('environment_variable', form.Flag, 'env_disable_loopback_detector', _('Disable Loopback Detector'));
        o.rmempty = false;

        o = s.taboption('environment_variable', form.Flag, 'env_disable_quic_go_gso', _('Disable GSO of quic-go'));
        o.rmempty = false;

        o = s.taboption('environment_variable', form.Flag, 'env_disable_quic_go_ecn', _('Disable ECN of quic-go'));
        o.rmempty = false;

        o = s.taboption('environment_variable', form.Flag, 'env_skip_system_ipv6_check', _('Skip System IPv6 Check'));
        o.rmempty = false;

        return m.render().then(function (node) {
            poll.add(function () {
                return L.resolveDefault(mihomo.status()).then(updateStatus);
            });

            return E([buildDashboard(data), node]);
        });
    }
});
