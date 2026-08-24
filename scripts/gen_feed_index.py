#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 Mihomo Feed 首页 index.html (替代 tree 命令的简陋输出)。

用法: python gen_feed_index.py [public_dir]
遍历 public/<branch>/<arch>/mihomo/ 下的包, 生成暗色高端风格的单文件页面。
"""
import json
import os
import re
import sys
from html import escape

ROOT = sys.argv[1] if len(sys.argv) > 1 else "public"
OUT = os.path.join(ROOT, "index.html")

BRANCH_LABELS = {
    "openwrt-24.10": ("24.10", "ipk / opkg"),
    "openwrt-25.12": ("25.12", "apk"),
}


def fmt_size(n):
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def parse_pkg(fname, arch_dir):
    """从 OpenWrt 包文件名解析。架构名(如 aarch64_cortex-a53)含下划线, 用目录名反查剥离, 避免正则歧义。
    例: luci-app-mihomo_1.0.2-r1_all.ipk / mihomo_1.19.30-r1_aarch64_cortex-a53.ipk / mihomo-1.19.30-r1.apk"""
    fmt = "apk" if fname.endswith(".apk") else "ipk"
    base = fname[: -(len(fmt) + 1)]
    if fmt == "ipk":
        if base.endswith("_all"):
            name, _, ver = base[: -4].rpartition("_")
            return {"name": name, "version": ver, "arch": "all", "fmt": fmt}
        if base.endswith("_" + arch_dir):
            core = base[: -(len(arch_dir) + 1)]
            name, _, ver = core.rpartition("_")
            return {"name": name, "version": ver, "arch": arch_dir, "fmt": fmt}
        return {"name": base, "version": "", "arch": "", "fmt": fmt}
    m = None
    if fmt == "apk":
        # 版本可能含 -rN (如 1.0.2-r1): 从右往左找第一个 "-<数字>" 作为 name/version 分界
        for i in range(len(base) - 1, 0, -1):
            if base[i] == "-" and base[i + 1].isdigit():
                return {"name": base[:i], "version": base[i + 1:], "arch": "", "fmt": fmt}
        return {"name": base, "version": "", "arch": "", "fmt": fmt}
    return {"name": base, "version": "", "arch": "", "fmt": fmt}


def collect(public):
    """返回 {branch: {arch: {pkgname: {version, size, fmt, url}}}}"""
    data = {}
    if not os.path.isdir(public):
        return data
    for branch in sorted(os.listdir(public)):
        bpath = os.path.join(public, branch)
        if not os.path.isdir(bpath):
            continue
        archs = {}
        for arch in sorted(os.listdir(bpath)):
            apath = os.path.join(bpath, arch, "mihomo")
            if not os.path.isdir(apath):
                continue
            pkgs = {}
            for fname in sorted(os.listdir(apath)):
                if not (fname.endswith(".ipk") or fname.endswith(".apk")):
                    continue
                full = os.path.join(apath, fname)
                p = parse_pkg(fname, arch)
                p["size"] = os.path.getsize(full)
                p["url"] = f"/{branch}/{arch}/mihomo/{fname}"
                pkgs[fname] = p
            if pkgs:
                archs[arch] = pkgs
        if archs:
            data[branch] = archs
    return data


def build_html(data):
    branches = sorted(data.keys())
    total_archs = sum(len(a) for a in data.values())
    total_pkgs = sum(len(p) for a in data.values() for p in a.values())
    data_json = json.dumps(data, ensure_ascii=False)

    branch_tabs = ""
    for i, b in enumerate(branches):
        short, fmt = BRANCH_LABELS.get(b, (b, ""))
        active = " active" if i == 0 else ""
        branch_tabs += (
            f'<button class="tab{active}" data-branch="{escape(b)}">'
            f'<span class="tab-name">{escape(short)}</span>'
            f'<span class="tab-fmt">{escape(fmt)}</span></button>'
        )

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mihomo Feed — OpenWrt 软件源</title>
<meta name="description" content="Mihomo 核心与 LuCI 插件 OpenWrt 软件源, 支持 openwrt-24.10 (ipk) 与 openwrt-25.12 (apk), usign/APK 签名校验">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='8' fill='%23ec4899'/%3E%3Ctext x='16' y='23' font-size='18' font-family='Arial' font-weight='bold' fill='white' text-anchor='middle'%3EM%3C/text%3E%3C/svg%3E">
<style>
:root {{
  --bg: #0b0b10;
  --bg2: #12121a;
  --card: #171722;
  --card2: #1d1d2b;
  --border: #262636;
  --text: #e8e8f0;
  --muted: #8b8ba3;
  --pink: #ec4899;
  --pink2: #f472b6;
  --pink-dim: rgba(236,72,153,.12);
  --green: #34d399;
  --mono: ui-monospace, "SF Mono", "Cascadia Code", Consolas, monospace;
}}
* {{ margin:0; padding:0; box-sizing:border-box; }}
html {{ scroll-behavior:smooth; }}
body {{
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
  background:
    radial-gradient(1000px 500px at 85% -10%, rgba(236,72,153,.10), transparent 60%),
    radial-gradient(800px 400px at -10% 20%, rgba(168,85,247,.07), transparent 55%),
    var(--bg);
  color: var(--text);
  min-height: 100vh;
  line-height: 1.6;
}}
::selection {{ background: var(--pink); color:#fff; }}
a {{ color: var(--pink2); text-decoration:none; }}
a:hover {{ text-decoration:underline; }}
.container {{ max-width: 1080px; margin: 0 auto; padding: 0 24px; }}

/* ---------- nav ---------- */
nav {{
  position: sticky; top:0; z-index: 50;
  backdrop-filter: blur(14px);
  background: rgba(11,11,16,.72);
  border-bottom: 1px solid var(--border);
}}
nav .container {{ display:flex; align-items:center; justify-content:space-between; height:60px; }}
.logo {{ display:flex; align-items:center; gap:10px; font-weight:700; font-size:17px; }}
.logo-badge {{
  width:30px; height:30px; border-radius:8px; display:grid; place-items:center;
  background: linear-gradient(135deg, var(--pink), #a855f7);
  color:#fff; font-weight:800; font-size:15px; box-shadow: 0 4px 16px rgba(236,72,153,.35);
}}
.nav-links {{ display:flex; gap:22px; font-size:14px; color:var(--muted); }}
.nav-links a {{ color:var(--muted); transition:color .15s; }}
.nav-links a:hover {{ color:var(--text); text-decoration:none; }}

/* ---------- hero ---------- */
.hero {{ padding: 72px 0 40px; text-align:center; }}
.hero h1 {{
  font-size: clamp(34px, 6vw, 56px);
  font-weight: 800; letter-spacing: -1.5px;
  background: linear-gradient(120deg, #fff 20%, var(--pink) 55%, #a855f7 90%);
  -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent;
}}
.hero p {{ color:var(--muted); max-width:640px; margin:14px auto 0; font-size:16px; }}
.badges {{ display:flex; justify-content:center; gap:10px; margin-top:22px; flex-wrap:wrap; }}
.badge {{
  display:inline-flex; align-items:center; gap:7px; font-size:13px;
  padding:6px 14px; border-radius:999px; border:1px solid var(--border);
  background: var(--card); color:var(--muted);
}}
.badge b {{ color:var(--text); font-weight:600; }}
.dot {{ width:7px; height:7px; border-radius:50%; background:var(--green); box-shadow:0 0 8px var(--green); }}

/* ---------- stats ---------- */
.stats {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(160px,1fr)); gap:14px; margin:34px 0; }}
.stat {{
  background: linear-gradient(180deg, var(--card), var(--bg2));
  border:1px solid var(--border); border-radius:16px; padding:18px 20px; text-align:center;
}}
.stat b {{ display:block; font-size:28px; font-weight:800; letter-spacing:-.5px; }}
.stat b em {{ font-style:normal; color:var(--pink); }}
.stat span {{ color:var(--muted); font-size:13px; }}

/* ---------- panel ---------- */
.panel {{
  background: var(--card); border:1px solid var(--border); border-radius:20px;
  overflow:hidden; margin-bottom:28px; box-shadow: 0 20px 60px rgba(0,0,0,.35);
}}
.tabs {{ display:flex; border-bottom:1px solid var(--border); background: var(--bg2); }}
.tab {{
  flex:1; padding:14px 16px; border:none; cursor:pointer; font:inherit; font-size:14px;
  background:transparent; color:var(--muted); display:flex; flex-direction:column; align-items:center; gap:2px;
  border-bottom:2px solid transparent; transition:all .15s;
}}
.tab-name {{ font-weight:700; font-size:15px; }}
.tab-fmt {{ font-size:11.5px; color:var(--muted); opacity:.75; }}
.tab:hover {{ color:var(--text); background:rgba(255,255,255,.03); }}
.tab.active {{ color:var(--text); border-bottom-color:var(--pink); background:linear-gradient(180deg, var(--pink-dim), transparent); }}
.tab.active .tab-fmt {{ color:var(--pink2); }}

/* arch picker */
.picker {{ padding:20px 22px 8px; }}
.picker label {{ display:block; font-size:12px; text-transform:uppercase; letter-spacing:.08em; color:var(--muted); margin-bottom:10px; }}
.arch-grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(150px,1fr)); gap:8px; max-height:210px; overflow-y:auto; padding-right:6px; }}
.arch-btn {{
  text-align:left; padding:9px 12px; border-radius:10px; border:1px solid var(--border);
  background:var(--bg2); color:var(--muted); font:inherit; font-size:12.5px; cursor:pointer;
  transition:all .12s; font-family:var(--mono);
}}
.arch-btn:hover {{ border-color:var(--pink); color:var(--text); }}
.arch-btn.active {{ border-color:var(--pink); color:#fff; background:var(--pink-dim); }}
.arch-btn .cnt {{ float:right; opacity:.6; font-size:11px; }}
.arch-grid::-webkit-scrollbar {{ width:6px; }}
.arch-grid::-webkit-scrollbar-thumb {{ background:var(--border); border-radius:3px; }}

/* command card */
.cmd {{ margin:14px 22px 20px; border-radius:14px; overflow:hidden; border:1px solid var(--border); }}
.cmd-head {{
  display:flex; align-items:center; justify-content:space-between; padding:10px 16px;
  background:var(--bg2); border-bottom:1px solid var(--border); font-size:12.5px; color:var(--muted);
}}
.cmd-head .lbl {{ display:flex; align-items:center; gap:8px; }}
.cmd-body {{ position:relative; }}
.cmd-body pre {{
  padding:16px; font-family:var(--mono); font-size:13px; line-height:1.75; overflow-x:auto;
  background:#0e0e16; color:#c9d1d9;
}}
.cmd-body pre .cmt {{ color:#565673; }}
.copy {{
  position:absolute; top:10px; right:10px; border:none; cursor:pointer; font:inherit; font-size:12px;
  padding:5px 12px; border-radius:8px; background:var(--pink); color:#fff; font-weight:600;
  transition:all .15s; box-shadow:0 4px 14px rgba(236,72,153,.3);
}}
.copy:hover {{ background:var(--pink2); }}
.copy.done {{ background:var(--green); }}

/* package list */
.pkgs {{ padding: 4px 22px 22px; }}
.pkg-table {{ width:100%; border-collapse:collapse; font-size:13.5px; }}
.pkg-table th {{
  text-align:left; font-size:11.5px; text-transform:uppercase; letter-spacing:.07em;
  color:var(--muted); padding:10px 12px; border-bottom:1px solid var(--border); font-weight:600;
}}
.pkg-table td {{ padding:10px 12px; border-bottom:1px solid rgba(38,38,54,.6); vertical-align:middle; }}
.pkg-table tr:last-child td {{ border-bottom:none; }}
.pkg-table tr:hover td {{ background:rgba(255,255,255,.02); }}
.pkg-name {{ font-family:var(--mono); font-weight:600; font-size:13px; }}
.pkg-name .tag {{
  display:inline-block; margin-left:8px; font-size:10.5px; font-weight:700; letter-spacing:.04em;
  padding:2px 8px; border-radius:6px; vertical-align:1px;
}}
.tag-ipk {{ background:rgba(236,72,153,.14); color:var(--pink2); border:1px solid rgba(236,72,153,.3); }}
.tag-apk {{ background:rgba(168,85,247,.14); color:#c4b5fd; border:1px solid rgba(168,85,247,.3); }}
.pkg-ver {{ color:var(--muted); font-family:var(--mono); font-size:12.5px; }}
.pkg-size {{ color:var(--muted); font-family:var(--mono); font-size:12.5px; }}
.dl {{
  display:inline-flex; align-items:center; gap:5px; font-size:12.5px; font-weight:600;
  padding:5px 14px; border-radius:8px; border:1px solid var(--border); color:var(--text);
  transition:all .12s; background:var(--bg2);
}}
.dl:hover {{ border-color:var(--pink); color:var(--pink2); text-decoration:none; box-shadow:0 0 18px rgba(236,72,153,.15); }}
.empty {{ padding:40px; text-align:center; color:var(--muted); }}

/* keys */
.keys {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); gap:14px; padding:0 22px 22px; }}
.key-card {{
  border:1px solid var(--border); border-radius:14px; padding:16px; background:var(--bg2);
  display:flex; align-items:center; justify-content:space-between; gap:12px;
}}
.key-card .k-info {{ display:flex; align-items:center; gap:12px; min-width:0; }}
.key-icon {{
  width:38px; height:38px; border-radius:10px; display:grid; place-items:center; flex-shrink:0;
  background:var(--pink-dim); border:1px solid rgba(236,72,153,.25);
}}
.key-icon svg {{ width:20px; height:20px; }}
.key-card b {{ display:block; font-size:13.5px; }}
.key-card span {{ font-size:12px; color:var(--muted); font-family:var(--mono); word-break:break-all; }}

/* footer */
footer {{ text-align:center; padding: 40px 0 60px; color:var(--muted); font-size:13px; }}
footer a {{ color:var(--muted); }}
footer a:hover {{ color:var(--pink2); }}
footer .sep {{ margin:0 10px; opacity:.4; }}

@media (max-width: 640px) {{
  .hero {{ padding-top:48px; }}
  .pkg-table th:nth-child(3), .pkg-table td:nth-child(3) {{ display:none; }}
  .nav-links {{ display:none; }}
}}
</style>
</head>
<body>
<nav>
  <div class="container">
    <div class="logo"><span class="logo-badge">M</span> Mihomo Feed</div>
    <div class="nav-links">
      <a href="https://github.com/MinimaxFlora/luci-app-mihomo" target="_blank" rel="noopener">GitHub</a>
      <a href="https://doc.kejizero.xyz" target="_blank" rel="noopener">文档</a>
      <a href="https://github.com/MinimaxFlora/luci-app-mihomo/releases" target="_blank" rel="noopener">Releases</a>
    </div>
  </div>
</nav>

<header class="hero container">
  <h1>Mihomo Feed</h1>
  <p>Mihomo 核心与 LuCI 插件的一站式 OpenWrt 软件源。双分支覆盖 24 种架构, 包索引全程签名校验, 支持 opkg 与 apk。</p>
  <div class="badges">
    <span class="badge"><span class="dot"></span><b>{total_archs}</b> 架构</span>
    <span class="badge"><b>{total_pkgs}</b> 个包</span>
    <span class="badge">usign / APK <b>签名</b></span>
    <span class="badge">Cloudflare <b>全球加速</b></span>
  </div>
</header>

<main class="container">
  <div class="stats">
    <div class="stat"><b><em id="stat-arch">0</em></b><span>可用架构</span></div>
    <div class="stat"><b id="stat-pkg">0</b><span>软件包</span></div>
    <div class="stat"><b>24.10 + 25.12</b><span>双版本分支</span></div>
    <div class="stat"><b><em>100%</em></b><span>签名覆盖</span></div>
  </div>

  <section class="panel">
    <div class="tabs">{branch_tabs}</div>

    <div class="picker">
      <label>选择架构</label>
      <div class="arch-grid" id="archGrid"></div>
    </div>

    <div class="cmd" id="cmdCard" style="display:none">
      <div class="cmd-head">
        <span class="lbl"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 17l6-6-6-6M12 19h8"/></svg> 一键添加软件源</span>
        <span id="cmdDesc"></span>
      </div>
      <div class="cmd-body">
        <pre id="cmdText"></pre>
        <button class="copy" id="copyBtn" onclick="copyCmd()">复制</button>
      </div>
    </div>

    <div class="pkgs">
      <div class="empty" id="empty">请选择架构查看可用软件包</div>
      <table class="pkg-table" id="pkgTable" style="display:none">
        <thead><tr><th>软件包</th><th>版本</th><th>大小</th><th></th></tr></thead>
        <tbody id="pkgBody"></tbody>
      </table>
    </div>

    <div class="keys">
      <div class="key-card">
        <div class="k-info">
          <div class="key-icon"><svg viewBox="0 0 24 24" fill="none" stroke="#ec4899" stroke-width="2"><path d="M21 2l-2 2m-7.61 7.61a5.5 5.5 0 1 1-7.778 7.778 5.5 5.5 0 0 1 7.777-7.777zm0 0L15.5 7.5m0 0l3 3L22 7l-3-3m-3.5 3.5L19 4"/></svg></div>
          <div><b>opkg 签名公钥</b><span>key-build.pub</span></div>
        </div>
        <a class="dl" href="/key-build.pub" download>下载</a>
      </div>
      <div class="key-card">
        <div class="k-info">
          <div class="key-icon"><svg viewBox="0 0 24 24" fill="none" stroke="#c4b5fd" stroke-width="2"><path d="M21 2l-2 2m-7.61 7.61a5.5 5.5 0 1 1-7.778 7.778 5.5 5.5 0 0 1 7.777-7.777zm0 0L15.5 7.5m0 0l3 3L22 7l-3-3m-3.5 3.5L19 4"/></svg></div>
          <div><b>apk 签名公钥</b><span>public-key.pem</span></div>
        </div>
        <a class="dl" href="/public-key.pem" download>下载</a>
      </div>
    </div>
  </section>
</main>

<footer>
  <a href="https://github.com/MinimaxFlora/luci-app-mihomo" target="_blank" rel="noopener">luci-app-mihomo</a>
  <span class="sep">·</span> Powered by Cloudflare Pages
  <span class="sep">·</span> 建议搭配 <a href="https://doc.kejizero.xyz" target="_blank" rel="noopener">Mihomo Docs</a> 使用
</footer>

<script>
const DATA = {data_json};
const $ = s => document.querySelector(s);
let curBranch = null, curArch = null;

const ARCH_LABEL = {{
  "x86_64":"x86-64", "i386_pentium4":"i386", "aarch64_cortex-a53":"ARM64-A53",
  "aarch64_cortex-a72":"ARM64-A72", "aarch64_cortex-a76":"ARM64-A76", "aarch64_generic":"ARM64",
  "arm_cortex-a5_vfpv4":"ARM A5", "arm_cortex-a7_neon-vfpv4":"ARM A7", "arm_cortex-a8_vfpv3":"ARM A8",
  "arm_cortex-a9":"ARM A9", "arm_cortex-a9_vfpv3-d16":"ARM A9-d16", "arm_cortex-a9_neon":"ARM A9-NEON",
  "arm_cortex-a15_neon-vfpv4":"ARM A15", "mips_24kc":"MIPS 24Kc", "mips_4kec":"MIPS 4KEc",
  "mips_mips32":"MIPS32", "mipsel_24kc":"MIPSEL 24Kc", "mipsel_24kc_24kf":"MIPSEL 24Kf",
  "mipsel_74kc":"MIPSEL 74Kc", "mipsel_mips32":"MIPSEL32", "mips64_octeonplus":"MIPS64 Octeon",
  "riscv64_riscv64":"RISC-V64", "riscv64_generic":"RISC-V64", "loongarch64_generic":"LoongArch64",
}};
const shortArch = a => ARCH_LABEL[a] || a;

function renderArchs(branch) {{
  const archs = Object.keys(DATA[branch] || {{}}).sort();
  const grid = $("#archGrid");
  grid.innerHTML = archs.map(a =>
    `<button class="arch-btn" data-arch="${{a}}" onclick="pickArch('${{a}}')">${{shortArch(a)}} <span class="cnt">${{Object.keys(DATA[branch][a]).length}}</span></button>`
  ).join("");
  // 恢复记忆
  const saved = localStorage.getItem("mihomo-arch");
  if (archs.includes(saved)) pickArch(saved);
  else if (archs.length) pickArch(archs[0]);
}}

function pickArch(arch) {{
  curArch = arch;
  localStorage.setItem("mihomo-arch", arch);
  document.querySelectorAll(".arch-btn").forEach(b => b.classList.toggle("active", b.dataset.arch === arch));
  renderPkgs();
}}

function renderPkgs() {{
  const branch = curBranch, arch = curArch;
  const pkgs = DATA[branch]?.[arch] || {{}};
  const table = $("#pkgTable"), empty = $("#empty"), cmd = $("#cmdCard");
  const names = Object.keys(pkgs).sort();
  if (!names.length) {{
    table.style.display = "none"; cmd.style.display = "none"; empty.style.display = "block";
    return;
  }}
  empty.style.display = "none"; table.style.display = "table"; cmd.style.display = "block";
  $("#pkgBody").innerHTML = names.map(n => {{
    const p = pkgs[n];
    const tag = p.fmt === "apk" ? "tag-apk" : "tag-ipk";
    return `<tr>
      <td><span class="pkg-name">${{p.name}}<span class="tag ${{tag}}">${{p.fmt.toUpperCase()}}</span></span></td>
      <td class="pkg-ver">${{p.version}}</td>
      <td class="pkg-size">${{p.size}}</td>
      <td style="text-align:right"><a class="dl" href="${{p.url}}" download>下载 ↓</a></td>
    </tr>`;
  }}).join("");
  // 命令
  const feedUrl = `https://feed.kejizero.xyz/${{branch}}/${{arch}}/mihomo`;
  const isApk = branch.includes("25.12");
  const cmdText = isApk
    ? `# 添加 Mihomo 软件源 (apk / 25.12)\nwget -O /etc/apk/keys/mihomo.pem https://feed.kejizero.xyz/public-key.pem\necho "${{feedUrl}}/packages.adb" >> /etc/apk/repositories.d/customfeeds.list\napk update`
    : `# 添加 Mihomo 软件源 (opkg / 24.10)\nwget -O key-build.pub https://feed.kejizero.xyz/key-build.pub\nopkg-key add key-build.pub\necho "src/gz mihomo ${{feedUrl}}" >> /etc/opkg/customfeeds.conf\nopkg update`;
  $("#cmdText").textContent = cmdText;
  $("#cmdDesc").textContent = `${{shortArch(arch)}} · ${{branch}}`;
}}

function copyCmd() {{
  const txt = $("#cmdText").textContent;
  navigator.clipboard.writeText(txt).then(() => {{
    const b = $("#copyBtn");
    b.textContent = "已复制 ✓"; b.classList.add("done");
    setTimeout(() => {{ b.textContent = "复制"; b.classList.remove("done"); }}, 1600);
  }});
}}

document.querySelectorAll(".tab").forEach(t => t.addEventListener("click", () => {{
  document.querySelectorAll(".tab").forEach(x => x.classList.remove("active"));
  t.classList.add("active");
  curBranch = t.dataset.branch;
  renderArchs(curBranch);
  $("#stat-arch").textContent = Object.keys(DATA[curBranch]).length;
  let total = 0; for (const a in DATA[curBranch]) total += Object.keys(DATA[curBranch][a]).length;
  $("#stat-pkg").textContent = total;
}}));

// init
document.querySelectorAll(".tab")[0]?.click();
</script>
</body>
</html>
"""


def main():
    data = collect(ROOT)
    if not data:
        print("未找到包数据, 检查目录:", ROOT)
        sys.exit(1)
    html = build_html(data)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)
    archs = sum(len(a) for a in data.values())
    pkgs = sum(len(p) for a in data.values() for p in a.values())
    print(f"已生成 {OUT}: {len(data)} 分支 / {archs} 架构 / {pkgs} 包")


if __name__ == "__main__":
    main()
