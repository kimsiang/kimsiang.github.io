"""PI profile page (kim.html). Called from build.py: build_kim(build_module).

Facts come from content/members.json (education, awards, IDs) and
content/publications.json (stats, selected papers); prose lives here.
"""
import json, os, html


def build_kim(B):
    bi = B.bi
    m = next(x for x in B.MEMBERS if x['slug'] == 'kim-siang-khaw')
    pubs = json.load(open(os.path.join(B.C, 'publications.json')))
    cites = sum(p['cites'] for p in pubs)
    cs = sorted((p['cites'] for p in pubs), reverse=True)
    h = sum(1 for i, c in enumerate(cs, 1) if c >= i)

    def two(en, zh):            # block-level bilingual
        return f'<div class="en">{en}</div><div class="zh">{zh}</div>'

    def H(id_, en, zh):
        return f'<h2 id="{id_}">{bi(en, zh)}</h2>'

    def fig(src, en, zh, cls=''):
        return (f'<figure class="kfig {cls}"><a class="zoom" href="{{ROOT}}{src}"><img src="{{ROOT}}{src}" alt="{html.escape(en)}" loading="lazy" decoding="async"></a>'
                f'<figcaption>{bi(en, zh)}</figcaption></figure>')

    # ---------------------------------------------------------------- side
    links = [('ORCID', m['orcid'], f'https://orcid.org/{m["orcid"]}'),
             ('INSPIRE-HEP', m['inspire'], f'https://inspirehep.net/authors/{m["inspire"]}'),
             ('Google Scholar', m['scholar'], f'https://scholar.google.com/citations?user={m["scholar"]}')]
    side = (f'<figure class="mphoto"><a class="zoom" href="{{ROOT}}{m["photo"]}"><img src="{{ROOT}}{m["photo"]}" alt="Kim Siang Khaw" loading="lazy" decoding="async"></a></figure>'
            '<div class="kstats">'
            f'<div><b>{len(pubs)}</b>{bi("papers", "论文")}</div>'
            f'<div><b>{cites:,}</b>{bi("citations", "引用")}</div>'
            f'<div><b>{h}</b>{bi("h-index", "h指数")}</div></div>'
            '<p class="mono mlabel">' + bi('Contact', '联系方式') + '</p>'
            '<div class="mlinks">'
            '<a href="mailto:kimsiang84@sjtu.edu.cn"><b>Email</b><span>kimsiang84@sjtu.edu.cn</span></a>'
            '<span class="kaddr"><b>' + bi('Lab', '实验室') + '</b><span>' + bi('Lab S243, Tsung-Dao Lee Institute, 1 Lisuo Road, Pudong, Shanghai', '上海市浦东新区李所路1号 李政道研究所 S243') + '</span></span></div>'
            '<p class="mono mlabel">' + bi('Profiles', '学术主页') + '</p>'
            '<div class="mlinks">' + ''.join(f'<a href="{u}" target="_blank" rel="noopener"><b>{n}</b><span>{i}</span></a>' for n, i, u in links)
            + '<a href="{ROOT}people/kim-siang-khaw.html"><b>' + bi('Full publication list', '完整论文列表') + '</b><span>' + bi('Synced from INSPIRE-HEP →', '同步自INSPIRE-HEP →') + '</span></a></div>'
            '<nav class="toc" aria-label="On this page"><p class="mono">' + bi('On this page', '本页目录') + '</p><ol>'
            + ''.join(f'<li><a href="#{i}">{bi(e, z)}</a></li>' for i, e, z in [
                ('bio', 'Biography', '个人简介'), ('research', 'Research', '研究方向'), ('career', 'Career', '教育与经历'),
                ('honours', 'Honours', '荣誉奖励'), ('service', 'Service', '学术服务'), ('papers', 'Selected papers', '代表性论文'),
                ('group', 'Working with me', '加入团队'), ('outside', 'Outside the lab', '工作之余')])
            + '</ol></nav>')

    # ---------------------------------------------------------------- body
    bio = two(
        '<p class="klead">I lead the Muon Physics Group at the Tsung-Dao Lee Institute (TDLI), Shanghai Jiao Tong University, where I am a Tenured Fellow and a Tenured Associate Professor in the School of Physics and Astronomy.</p>'
        '<p>My work uses the muon to test the Standard Model of particle physics. I measure its magnetic anomaly in the Muon g-2 Experiment at Fermilab and search for its electric dipole moment with the muEDM experiment at PSI. Closer to home, my group is designing a high-repetition-rate muon source at Shanghai’s SHINE facility and using cosmic-ray muons to image the city’s underground spaces. I like to think of this as working across the full chain: from making muons, to measuring them, to putting them to use.</p>'
        '<p>I grew up in Penang, Malaysia, and spent sixteen years studying and working abroad before coming to Shanghai: in Japan (Osaka University of Foreign Studies, Kyoto University, University of Tokyo), Switzerland (ETH Zurich, PhD 2015) and the USA (University of Washington, postdoc 2015–2019). Along the way I learned to do physics in five languages — Malay, Japanese, German, English and Chinese. I joined TDLI in 2019 and received tenure in 2025.</p>',
        '<p class="klead">我是上海交通大学李政道研究所长聘学者、物理与天文学院长聘副教授，领导李政道研究所缪子物理课题组。</p>'
        '<p>我的研究以缪子为探针检验粒子物理标准模型：在美国费米实验室缪子g-2实验中精确测量其反常磁矩，在瑞士保罗谢勒研究所（PSI）的muEDM实验中寻找其电偶极矩。在上海，课题组正在基于SHINE装置设计高重频缪子源，并利用宇宙线缪子对城市地下空间进行成像。从“产生缪子”到“测量缪子”再到“应用缪子”，我们希望打通这一完整链条。</p>'
        '<p>我来自马来西亚槟城，来上海之前在海外学习和工作了16年：日本（大阪外国语大学、京都大学、东京大学）、瑞士（苏黎世联邦理工学院，2015年获博士学位）和美国（华盛顿大学，2015–2019年博士后）。这段经历让我能够用马来语、日语、德语、英语和汉语五种语言学习和开展物理研究。2019年加入李政道研究所，2025年获得长聘。</p>')
    bio += fig('assets/media/1921.webp', 'Speaking at the Pujiang Innovation Forum 2024', '在2024浦江创新论坛上发言')

    pillars = [
        ('Muon g-2', '缪子反常磁矩', 'Fermilab', 'research.html#muon-g-2',
         'Final result at 127 ppb (2025); our group works on the anomalous precession frequency and beam-dynamics corrections.',
         '2025年最终结果精度达127 ppb；课题组负责反常进动频率测量与束流动力学修正。'),
        ('Muon EDM', '缪子电偶极矩', 'PSI', 'research.html#muon-edm',
         'A frozen-spin search aiming at 6 × 10⁻²³ e·cm; we build the muon entrance trigger.',
         '冻结自旋方法，目标灵敏度 6 × 10⁻²³ e·cm；课题组负责缪子入射触发探测器。'),
        ('SHINE muon source', 'SHINE缪子源', 'Shanghai', 'research.html#shine-muon-source',
         'A 50 kHz pulsed muon beam driven by an X-ray laser’s electron linac.',
         '利用X射线自由电子激光电子直线加速器产生50 kHz脉冲缪子束。'),
        ('Muography', '缪子成像', 'Shanghai', 'research.html#muography',
         'Imaging tunnels and underground spaces with cosmic-ray muons, since 2024.',
         '自2024年起，利用宇宙线缪子对隧道等城市地下空间成像。'),
    ]
    research = '<div class="kpill">' + ''.join(
        f'<a href="{{ROOT}}{u}"><span class="mono">{w}</span><b>{bi(e, z)}</b><span>{bi(de, dz)}</span></a>'
        for e, z, w, u, de, dz in pillars) + '</div>'
    research += '<p class="kmore mono"><a href="{ROOT}results.html">' + bi('Headline results →', '代表性成果 →') + '</a> · <a href="{ROOT}research.html">' + bi('Research in detail →', '研究方向详情 →') + '</a></p>'

    career = '<ul class="mtl">' + ''.join(f'<li><b>{html.escape(y)}</b><span>{bi(html.escape(e), html.escape(z))}</span></li>' for y, e, z in m['education']) + '</ul>'
    honours = '<ul class="mtl">' + ''.join(f'<li><b>{html.escape(y)}</b><span>{bi(html.escape(e), html.escape(z))}</span></li>' for y, e, z in m['awards']) + '</ul>'
    service = ('<ul class="mtl">'
               '<li><b>2026</b><span>' + bi('Chair, NuFact 2026 — 27th International Workshop on Neutrinos from Accelerators, hosted at TDLI, Shanghai (31 Aug – 5 Sep)',
                                             '主席，NuFact 2026第27届加速器中微子国际研讨会，李政道研究所主办（8月31日–9月5日）') + '</span></li>'
               '<li><b>2026</b><span>' + bi('Member, Muon EDM Task Force, Fermilab Muon g-2 Collaboration (new direct muon EDM limit)',
                                             '费米实验室缪子g-2合作组缪子电偶极矩专项组成员（缪子电偶极矩新直接上限）') + '</span></li>'
               '</ul>')

    pick = {2928642: 'g-2', 3190062: 'EDM', 2874447: 'muEDM', 2896777: 'SHINE', 2906901: 'Muography', 1754786: 'PhD thesis'}
    sel = sorted([p for p in pubs if p['id'] in pick], key=lambda p: p['date'], reverse=True)
    papers = '<ol class="pubs">' + ''.join(B.pub_rows(sel)) + '</ol>'
    papers += '<p class="kmore mono"><a href="{ROOT}people/kim-siang-khaw.html">' + bi(f'All {len(pubs)} papers →', f'全部 {len(pubs)} 篇论文 →') + '</a> · <a href="{ROOT}talks.html">' + bi('Talks →', '学术报告 →') + '</a></p>'

    group = two(
        '<p>We are a small, international team, and I try to keep the atmosphere open and curious. Each week we run a study group on introductory particle-physics textbooks, a journal club, and dedicated meetings for the Muon g-2 and muEDM collaborations. Students present their work at a national or international conference about twice a year, and strong graduate students can spend extended research periods at Fermilab and PSI.</p>'
        '<p>Each year I take several undergraduates (PRP, Zhiyuan Scholars, Physics Research Practice and other programmes), two to five graduate students including international students, and postdocs. If you enjoy precision experiments, building detectors or turning data into physics, please write to me.</p>'
        '<p class="kmore mono"><a href="{ROOT}index.html#joinus">Join us →</a> · <a href="{ROOT}people.html">Meet the team →</a> · <a href="{ROOT}theses.html">Theses →</a></p>',
        '<p>我们是一个规模不大、高度国际化的团队，我希望营造开放、自由、充满好奇心的学术氛围。课题组每周举办粒子物理入门教材研读会（Study Group）、文献阅读会（Journal Club），以及缪子g-2与muEDM国际合作项目专项组会。成员平均每年至少参加两次国内外学术会议并报告进展，优秀研究生还有机会赴美国费米实验室、瑞士PSI开展长期科研训练。</p>'
        '<p>课题组每年招收多名本科生（PRP、致远学者研究计划、物理研究实践等项目）、2–5名研究生（含国际研究生）以及优秀博士后。如果你喜欢精密测量实验、动手搭建探测器或从数据中挖掘物理，欢迎与我联系。</p>'
        '<p class="kmore mono"><a href="{ROOT}index.html#joinus">加入我们 →</a> · <a href="{ROOT}people.html">团队成员 →</a> · <a href="{ROOT}theses.html">学位论文 →</a></p>')
    group += ('<div class="kgrid">'
              + fig('assets/media/1871.webp', 'Weekly group meeting', '每周组会')
              + fig('assets/media/1936.webp', 'Graduation day', '毕业典礼')
              + fig('assets/media/1934.webp', 'Team-building day', '团建活动') + '</div>')

    outside = two(
        '<p>Outside physics I play badminton, the guitar, and enjoy cooking and good food — as a Penangite, durian comes first. I have travelled to more than 25 countries and 50 cities. I also share physics with the public, in Chinese, as “从槟城出发的粒子” (Particles from Penang).</p>',
        '<p>工作之余，我喜欢打羽毛球、弹吉他、下厨和品尝美食——身为槟城人，对榴莲情有独钟。至今已踏足超过25个国家、50余座城市。我也以“从槟城出发的粒子”为名，用中文开展物理科普。</p>')

    body = (H('bio', 'Biography', '个人简介') + bio
            + H('research', 'Research', '研究方向') + research
            + H('career', 'Career', '教育与经历') + career
            + H('honours', 'Honours', '荣誉奖励') + honours
            + H('service', 'Service &amp; leadership', '学术服务') + service
            + H('papers', 'Selected papers', '代表性论文') + papers
            + H('group', 'Working with me', '加入团队') + group
            + H('outside', 'Outside the lab', '工作之余') + outside)

    hero = B.phero('PI', 'People', '团队成员', 'Kim Siang Khaw <span class="zh-name">许金祥</span>', bi(
        'Tenured Fellow, Tsung-Dao Lee Institute · Tenured Associate Professor, School of Physics and Astronomy, Shanghai Jiao Tong University',
        '上海交通大学李政道研究所长聘学者 · 物理与天文学院长聘副教授'),
        crumbs='<p class="crumbs mono"><a href="{ROOT}people.html">' + bi('People', '团队成员') + '</a> / ' + bi('Principal Investigator', '课题组长') + '</p>')
    out = (hero + '<section class="pbody"><div class="wrap with-side">'
           + f'<aside class="side mside">{side}</aside><div class="prose doc member kim">{body}</div></div></section>')
    # keep content/pages/kim.html in sync so the Ask-the-group index sees the current text
    open(os.path.join(B.C, 'pages', 'kim.html'), 'w').write(body)
    B.layout('kim.html', 'Kim Siang Khaw', 'Kim Siang Khaw (许金祥) — Tenured Associate Professor at TDLI, Shanghai Jiao Tong University; leader of the Muon Physics Group (Muon g-2, muEDM, SHINE muon source, muography).', out, 'people')
