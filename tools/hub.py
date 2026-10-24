"""Super-app content layer: Join hub, Follow page, Partner page, monthly digest, events calendar.
Called from build.py: build_hub(build_module). Data: content/join.json, content/events.json, theses.json, news.json."""
import html, json, os, re
from datetime import date, datetime
from collections import OrderedDict

def build_hub(B):
    bi, phero, layout, C, ROOT, SITE = B.bi, B.phero, B.layout, B.C, B.ROOT, B.SITE
    esc = html.escape
    news = B.news

    # ------------------------------------------------------------- JOIN
    J = json.load(open(os.path.join(C, 'join.json')))
    T = json.load(open(os.path.join(C, 'theses.json')))
    projects = T['projects']
    STATUS = {'open': ('Open', '招聘中', 'st-open'), 'rolling': ('Rolling', '常年招收', 'st-rolling'), 'closed': ('Closed', '已截止', 'st-closed')}

    pos = []
    for p in J['positions']:
        en, zh, cls = STATUS[p['status']]
        pos.append(f'''<div class="role hub-role">
      <div class="hub-role-h"><span class="mono">{p["id"]}</span><span class="st {cls}">{bi(en, zh)}</span></div>
      <h4>{bi(esc(p["en"]), esc(p["zh"]))}</h4>
      <p class="hub-topics">{bi(esc(p["topics_en"]), esc(p["topics_zh"]))}</p>
      <p>{bi(esc(p["note_en"]), esc(p["note_zh"]))}</p>
    </div>''')

    WHO = [('sjtu-ug', 'SJTU undergraduate', '交大本科生'), ('other-ug', 'Undergraduate elsewhere', '其他高校本科生'),
           ('highschool', 'High-school student', '高中生'), ('grad', "Master's / PhD applicant", '硕博申请者'),
           ('postdoc', 'Postdoc', '博士后'), ('intl', 'International student', '国际学生')]
    chips = ''.join(f'<button type="button" data-who="{k}">{bi(en, zh)}</button>' for k, en, zh in WHO)
    progs = []
    for g in J['programmes']:
        n = sum(1 for pr in projects if g.get('match') and g['match'].lower() in pr['program'].lower())
        # people hosted, counting names per project
        hosted = sum(len(pr.get('names', [])) for pr in projects if g.get('match') and g['match'].lower() in pr['program'].lower())
        tag = f'<span class="mono hub-count">{bi(f"{hosted} student{"s" if hosted != 1 else ""} so far", f"已接收{hosted}人")}</span>' if hosted else ''
        progs.append(f'''<li class="hub-prog" data-for="{" ".join(g["for"])}">
      <h4>{bi(esc(g["en"]), esc(g["zh"]))}</h4>
      <p>{bi(esc(g["desc_en"]), esc(g["desc_zh"]))}</p>{tag}
    </li>''')

    steps = ''.join(f'<li><span class="mono">0{i+1}</span><p>{bi(esc(s["en"]), esc(s["zh"]))}</p></li>' for i, s in enumerate(J['steps']))

    # alumni outcomes: 'now' from theses + "[Currently …]" on the People page
    outcomes = []
    for t in T['theses']:
        if t.get('now'):
            outcomes.append((t['name'], t.get('zh', ''), t['now'], t['year']))
    ppl = open(os.path.join(C, 'pages', 'people.html')).read()
    for m in re.finditer(r'<strong>(?:<a[^>]*>)?([^<【]+)(?:</a>)?【?([^】<]*)】?</strong>\(([^)]*)\)\s*\[Currently ([^\]]+)\]', ppl):
        name, zh, span, now = m.group(1).strip(), m.group(2).strip(), m.group(3), re.sub(r'<[^>]+>', '', m.group(4)).strip()
        yr = re.findall(r'(20\d\d)\.\d\d\s*–?\s*$', span) or re.findall(r'–\s*(20\d\d)', span)
        if not any(o[0] == name for o in outcomes):
            outcomes.append((name, zh, now, int(yr[0]) if yr else 0))
    outcomes.sort(key=lambda o: -o[3])
    alumni = ''.join(f'<li><strong>{esc(n)}{f"<span class=zh-name>{esc(z)}</span>" if z else ""}</strong><span>{esc(now)}</span><span class="mono">{y or ""}</span></li>' for n, z, now, y in outcomes)

    body = phero('JOIN', 'Opportunities hub', '加入我们', bi('Join the group', '加入缪子物理课题组'),
                 bi('Undergraduates, graduate students, postdocs and summer interns — find the route that fits you, see where our alumni went, and write to us.',
                    '本科生、研究生、博士后与暑期实习生——找到适合你的加入途径，看看校友的去向，然后联系我们。'), scene='module')
    body += f'''<section class="pbody hub">
<div class="wrap">
  <p class="label"><span class="idx">01</span>{bi('Positions', '岗位')}</p>
  <h2 class="h2">{bi('What we are looking for now', '当前招收')}</h2>
  <div class="roles hub-roles">{"".join(pos)}</div>

  <p class="label"><span class="idx">02</span>{bi('Programme finder', '项目查找')}</p>
  <h2 class="h2">{bi('Which route fits you?', '哪条路径适合你？')}</h2>
  <p class="lead">{bi('Tap who you are and we show the programmes that apply. Counts are students we have hosted through that route.', '点击你的身份，查看适用的项目。人数为该途径已接收的学生数。')}</p>
  <div class="chips hub-who" role="group" aria-label="I am a…"><button type="button" class="on" data-who="all">{bi('Everyone', '全部')}</button>{chips}</div>
  <ul class="hub-progs" id="hub-progs">{"".join(progs)}</ul>

  <p class="label"><span class="idx">03</span>{bi('How to apply', '如何申请')}</p>
  <h2 class="h2">{bi('Three steps', '三步走')}</h2>
  <ol class="hub-steps">{steps}</ol>
  <div class="cta-row"><a href="mailto:kimsiang84@sjtu.edu.cn?subject=Joining%20the%20TDLI%20Muon%20Physics%20Group" class="btn btn-primary">{bi('Email Kim', '给Kim发邮件')} <span class="arr">→</span></a><a href="{{ROOT}}research.html" class="btn btn-ghost">{bi('Read the research first', '先看研究方向')}</a></div>
  <p class="hub-note">{bi('We supervise in English, Chinese, Malay and Japanese (and a little German). Group culture: weekly muon-physics journal club, a textbook reading group, at least two conference talks a year, and an open, supportive lab.',
                        '我们可以用英语、中文、马来语和日语（以及少量德语）进行指导。课题组文化：每周缪子物理Journal Club、教材研读小组、每年至少两次会议报告，以及开放、支持性的实验室氛围。')}</p>

  <p class="label"><span class="idx">04</span>{bi('Alumni outcomes', '校友去向')}</p>
  <h2 class="h2">{bi('Where people go next', '他们去了哪里')}</h2>
  <ul class="hub-alumni">{alumni}</ul>
  <p class="src mono"><a href="{{ROOT}}people.html#former-members">{bi('All former members →', '全部往届成员 →')}</a> · <a href="{{ROOT}}theses.html">{bi('Theses archive →', '学位论文 →')}</a></p>
</div></section>'''
    layout('join.html', 'Join us', 'Open positions, undergraduate and graduate programmes, summer internships and alumni outcomes — how to join the TDLI Muon Physics Group.', body, 'join', title_zh='加入我们')

    # ------------------------------------------------------------- DIGEST + EVENTS + FOLLOW
    months = OrderedDict()
    for n in news:
        months.setdefault(n['date'][:7], []).append(n)
    MONTH_EN = ['', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    def mlabel(ym):
        y, m = ym.split('-')
        return bi(f'{MONTH_EN[int(m)]} {y}', f'{y}年{int(m)}月')
    digest = []
    for ym, items in list(months.items())[:24]:
        rows = ''.join(f'<li><a href="{{ROOT}}news/{n["slug"]}.html"><time>{n["date"][8:]}</time><span>{B.ntitle(n)}</span></a></li>' for n in items)
        digest.append(f'<section class="dg-month" id="m-{ym}"><h2>{mlabel(ym)} <span class="mono">{len(items)}</span></h2><ul>{rows}</ul></section>')
    body = phero('DIGEST', 'Monthly digest', '月度简报', bi('What happened, month by month', '每月回顾'),
                 bi('Every news item from the last two years, grouped by month. Subscribe to the feed to get the next one.', '过去两年的全部动态，按月汇总。订阅RSS即可获取下一期。'), scene='module')
    body += f'<section class="pbody hub"><div class="wrap">{"".join(digest)}<p class="src mono"><a href="{{ROOT}}news/index.html">{bi("Full news archive →", "完整新闻 →")}</a></p></div></section>'
    layout('digest.html', 'Monthly digest', 'Monthly digest of news from the TDLI Muon Physics Group.', body, 'news', title_zh='月度简报', lastmod=news[0]['date'])

    E = json.load(open(os.path.join(C, 'events.json')))['events']
    today = date.today().isoformat()
    upcoming = sorted([e for e in E if (e.get('end') or e['start'])[:10] >= today], key=lambda e: e['start'])
    def ics_dt(s):
        return s.replace('-', '').replace(':', '') + ('00' if 'T' in s else '')
    if upcoming:
        lines = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//TDLI Muon Physics Group//kimsiang.github.io//EN', 'X-WR-CALNAME:TDLI Muon Physics Group', 'X-WR-TIMEZONE:Asia/Shanghai']
        for e in upcoming:
            allday = 'T' not in e['start']
            lines += ['BEGIN:VEVENT', f'UID:{ics_dt(e["start"])}-{re.sub(r"[^a-z0-9]", "", e["title"].lower())[:24]}@kimsiang.github.io',
                      f'DTSTAMP:{datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")}',
                      f'DTSTART{";VALUE=DATE" if allday else ";TZID=Asia/Shanghai"}:{ics_dt(e["start"])}']
            if e.get('end'): lines.append(f'DTEND{";VALUE=DATE" if allday else ";TZID=Asia/Shanghai"}:{ics_dt(e["end"])}')
            lines.append(f'SUMMARY:{e["title"]}')
            if e.get('location'): lines.append(f'LOCATION:{e["location"]}')
            if e.get('url'): lines.append(f'URL:{e["url"]}')
            lines.append('END:VEVENT')
        lines.append('END:VCALENDAR')
        open(os.path.join(ROOT, 'events.ics'), 'w').write('\r\n'.join(lines) + '\r\n')
    ev_rows = ''.join(f'<li><time>{e["start"][:10]}</time><div><strong>{bi(esc(e["title"]), esc(e.get("title_zh", e["title"])))}</strong>{f"<span>{esc(e['location'])}</span>" if e.get("location") else ""}</div>{f"<a href=\"{esc(e['url'])}\" target=\"_blank\" rel=\"noopener\">↗</a>" if e.get("url") else ""}</li>' for e in upcoming)
    ev_block = (f'<ul class="hub-events">{ev_rows}</ul><p><a class="btn btn-ghost" href="{{ROOT}}events.ics" download>{bi("Add to my calendar (.ics)", "添加到我的日历 (.ics)")}</a></p>'
                if upcoming else f'<p class="hub-note">{bi("No upcoming public events are listed at the moment — the next NuFact-style workshop, open day or public talk will appear here with a calendar file to download.", "目前没有列出即将举行的公开活动——下一次研讨会、开放日或公开报告将在此公布，并提供日历文件下载。")}</p>')

    # latest WeChat articles (news posts that link to mp.weixin.qq.com)
    wx = []
    for n in news:
        src = B.news_src(n['slug'], 'en') + B.news_src(n['slug'], 'zh')
        m = re.search(r'href="(https://mp\.weixin\.qq\.com/s/[^"]+)"', src)
        if m: wx.append((n, m.group(1)))
        if len(wx) >= 6: break
    wx_rows = ''.join(f'<li><a href="{esc(u)}" target="_blank" rel="noopener"><time>{n["date"]}</time><span>{B.ntitle(n)}</span> <span class="arr">↗</span></a></li>' for n, u in wx)
    qr = os.path.exists(os.path.join(ROOT, 'assets', 'img', 'wechat-qr.webp'))
    qr_html = f'<img class="hub-qr" src="{{ROOT}}assets/img/wechat-qr.webp" alt="WeChat QR code" width="180" height="180" loading="lazy">' if qr else ''

    body = phero('FOLLOW', 'Stay in the loop', '关注我们', bi('Follow the group', '关注课题组'),
                 bi('A feed for your reader, the monthly digest, our WeChat articles and a calendar of public events.', 'RSS订阅、月度简报、微信公众号文章，以及公开活动日历。'), scene='module')
    body += f'''<section class="pbody hub"><div class="wrap">
  <div class="hub-grid">
    <div class="hub-card">
      <p class="label"><span class="idx">RSS</span>{bi('Feed', '订阅')}</p>
      <h3>{bi('Every news post, in your reader', '在阅读器中接收每条动态')}</h3>
      <p>{bi('An Atom feed with the latest 30 posts. Paste the address into Feedly, NetNewsWire, Inoreader or any RSS reader.', 'Atom格式，含最新30条动态。把地址粘贴到Feedly、NetNewsWire、Inoreader或任何RSS阅读器即可。')}</p>
      <p class="hub-copy"><code id="feed-url">{SITE}feed.xml</code><button type="button" class="btn btn-sm btn-ghost" data-copy="#feed-url">{bi('Copy', '复制')}</button></p>
    </div>
    <div class="hub-card">
      <p class="label"><span class="idx">WX</span>{bi('WeChat', '微信公众号')}</p>
      <h3>{bi('Our articles on WeChat', '微信公众号文章')}</h3>
      {qr_html}
      <ul class="hub-list">{wx_rows}</ul>
    </div>
    <div class="hub-card">
      <p class="label"><span class="idx">M</span>{bi('Digest', '简报')}</p>
      <h3>{bi('The monthly digest', '月度简报')}</h3>
      <p>{bi(f'{len(news)} posts since {news[-1]["date"][:4]}, grouped month by month — the quickest way to catch up.', f'自{news[-1]["date"][:4]}年以来的{len(news)}条动态按月汇总——最快的回顾方式。')}</p>
      <p><a class="btn btn-ghost" href="{{ROOT}}digest.html">{bi('Open the digest', '查看简报')} <span class="arr">→</span></a></p>
    </div>
    <div class="hub-card">
      <p class="label"><span class="idx">CAL</span>{bi('Events', '活动')}</p>
      <h3>{bi('Public events', '公开活动')}</h3>
      {ev_block}
    </div>
  </div>
  <p class="hub-note">{bi('Prefer email? Write to kimsiang84@sjtu.edu.cn and ask to be added to the group announcement list.', '更喜欢邮件？请写信至 kimsiang84@sjtu.edu.cn 申请加入课题组通知列表。')}</p>
</div></section>'''
    layout('follow.html', 'Follow us', 'Follow the TDLI Muon Physics Group: RSS feed, monthly digest, WeChat articles and public events calendar.', body, 'follow', title_zh='关注我们')

    # ------------------------------------------------------------- PARTNER
    offers = [
        ('01', 'Muography surveys', '缪子成像勘测',
         'Non-invasive imaging of what lies above or inside large structures: tunnels, river beds, foundations, karst and mine workings. Our pilot in the Shanghai Outer Ring Tunnel tracked the Huangpu tide through the muon rate; in 2026 we surveyed limestone and karst sites across Peninsular Malaysia.',
         '对大型结构上方或内部进行无损成像：隧道、河床、地基、岩溶与矿山巷道。在上海外环隧道的试验中，我们通过缪子计数率追踪到黄浦江潮汐；2026年又在马来西亚半岛的石灰岩与岩溶场地开展了勘测。',
         '{ROOT}research.html#muography'),
        ('02', 'Compact detector R&D', '便携探测器研发',
         'Portable scintillator–SiPM muon telescopes, readout electronics and DAQ, built in our own lab from design to deployment, with Geant4 simulation (musrSim-upgrade, CRY/EcoMug) to size a system before anything is built.',
         '便携式闪烁体–SiPM缪子望远镜、读出电子学与数据获取系统，在自有实验室从设计到部署一体完成；利用Geant4模拟（musrSim-upgrade、CRY/EcoMug）在动工前完成系统选型。',
         '{ROOT}research.html#muography'),
        ('03', 'Joint projects and training', '联合项目与人才培养',
         'Co-funded studies with city, infrastructure and geological partners, engineering internships for your staff or students, and access to the SHINE accelerator-based muography programme as it develops.',
         '与城市、基础设施及地质单位的联合研究，面向合作方员工或学生的工程实习，以及参与正在发展中的SHINE加速器缪子成像计划。',
         '{ROOT}research.html#shine-muon-source'),
    ]
    off_html = ''.join(f'''<div class="hub-card"><p class="label"><span class="idx">{c}</span>{bi('Service', '服务')}</p><h3>{bi(en, zh)}</h3><p>{bi(den, dzh)}</p><p><a href="{u}" class="mod-link">{bi('Related research', '相关研究')} <span class="arr">→</span></a></p></div>''' for c, en, zh, den, dzh, u in offers)
    how = [('Scoping call', '需求沟通', 'What you need to see, where, and at what resolution.', '你想看什么、在哪里、需要多高的分辨率。'),
           ('Feasibility study', '可行性模拟', 'A Geant4 simulation of your geometry gives expected contrast and exposure time before any hardware moves.', '对你的几何结构做Geant4模拟，在任何硬件进场前给出预期对比度与曝光时间。'),
           ('Pilot measurement', '现场试验', 'A portable telescope on site for weeks to months; data are analysed as they arrive.', '便携望远镜现场运行数周至数月，数据边采集边分析。'),
           ('Report and next steps', '报告与后续', 'Density maps, uncertainties and a recommendation on a longer campaign or a permanent monitor.', '密度图、不确定度，以及是否开展长期监测的建议。')]
    how_html = ''.join(f'<li><span class="mono">0{i+1}</span><div><h4>{bi(en, zh)}</h4><p>{bi(den, dzh)}</p></div></li>' for i, (en, zh, den, dzh) in enumerate(how))
    body = phero('PARTNER', 'Work with us', '合作洽谈', bi('Muography for cities, industry and geoscience', '面向城市、产业与地球科学的缪子成像'),
                 bi('Cosmic-ray muons arrive for free, pass through hundreds of metres of rock, and let us image the inside of large things without touching them. Here is how a project with our group works.',
                    '宇宙线缪子免费到达、可穿透数百米岩石，让我们无需接触即可对庞大目标内部成像。以下是与课题组合作的方式。'), scene='module')
    body += f'''<section class="pbody hub"><div class="wrap">
  <div class="hub-grid three">{off_html}</div>
  <p class="label"><span class="idx">HOW</span>{bi('How a project runs', '项目流程')}</p>
  <ol class="hub-steps how">{how_html}</ol>
  <div class="cta-row"><a href="mailto:kimsiang84@sjtu.edu.cn?subject=Partnership%20enquiry" class="btn btn-primary">{bi('Start a conversation', '开始洽谈')} <span class="arr">→</span></a><a href="{{ROOT}}index.html#collaborations" class="btn btn-ghost">{bi('Our partners', '合作伙伴')}</a><a href="https://kimsiang.github.io/scifi-mst-live/" class="btn btn-ghost" target="_blank" rel="noopener">{bi('Try the live demo', '在线演示')} ↗</a></div>
  <p class="hub-note">{bi('Our muography project won a First Prize at the 15th “Challenge Cup” Shanghai entrepreneurship competition. Academic collaborations on Muon g−2, muEDM and the SHINE muon source are described on the Research page.',
                        '课题组的缪子成像项目获第十五届“挑战杯”上海市创业计划竞赛一等奖。关于缪子g−2、缪子EDM与SHINE缪子源的学术合作，请见“研究”页面。')}</p>
</div></section>'''
    layout('partner.html', 'Work with us', 'Muography surveys, compact muon detector R&D and joint projects for city, industry and geoscience partners — work with the TDLI Muon Physics Group.', body, 'partner', title_zh='合作洽谈')
