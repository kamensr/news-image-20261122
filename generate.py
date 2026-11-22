"""generate.py — flat illustrated news poster for news-image-20261122.

Written from scratch from the research brief
(~/workspace/makefun/news-image-20261122-brief.md).
Winner format: 49 stories (4 features + 12 minis + 33 one-liners),
UTC timeline strip, world map with 11 pins, DATE CHECK box,
CLAIM vs CONFIRMED labels, sources footer.
Flat drawn illustration only — no AI imagery, no photos, no collage.
PIL only. Deterministic output: same input always yields the same PNG.
"""

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = "entry.png"

FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# ---- palette -------------------------------------------------------------
PAPER = (247, 245, 239)
INK = (22, 30, 40)
MUTED = (96, 102, 112)
NAVY = (16, 35, 63)
NAVY2 = (28, 58, 96)
CARD = (255, 255, 255)
LINE = (208, 203, 192)
ACCENT = (196, 84, 32)      # burnt orange, section labels
GREEN = (21, 128, 61)       # CONFIRMED
GREEN_BG = (214, 240, 222)
AMBER = (176, 84, 8)        # CLAIM
AMBER_BG = (252, 234, 205)
OCEAN = (213, 230, 240)
LAND = (198, 215, 180)
LAND_EDGE = (150, 172, 134)
PIN_RED = (192, 38, 32)
STRIP_BG = (238, 240, 244)

REGION_COLORS = {
    "GLOBAL": (16, 35, 63),
    "EUROPE": (28, 78, 150),
    "ASIA-PACIFIC": (176, 84, 8),
    "MIDDLE EAST": (146, 44, 120),
}


def font(size, bold=False):
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REG, size)


# ---- text helpers --------------------------------------------------------
def wrap(draw, text, fnt, max_w):
    """Greedy word wrap to a list of lines that fit max_w."""
    lines = []
    for para in text.split("\n"):
        words = para.split()
        if not words:
            lines.append("")
            continue
        cur = words[0]
        for w in words[1:]:
            trial = cur + " " + w
            if draw.textlength(trial, font=fnt) <= max_w:
                cur = trial
            else:
                lines.append(cur)
                cur = w
        lines.append(cur)
    return lines


def fit(draw, text, fnt, max_w, max_lines):
    """Wrap and truncate to max_lines, adding an ellipsis if cut."""
    lines = wrap(draw, text, fnt, max_w)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        while lines and draw.textlength(lines[-1] + "\u2026", font=fnt) > max_w:
            lines[-1] = lines[-1][:-1]
        lines[-1] = lines[-1].rstrip() + "\u2026"
    return lines


def trunc(draw, text, fnt, max_w):
    """Single line, truncated with ellipsis to fit max_w."""
    if draw.textlength(text, font=fnt) <= max_w:
        return text
    t = text
    while t and draw.textlength(t + "\u2026", font=fnt) > max_w:
        t = t[:-1]
    return t.rstrip() + "\u2026"


def chip(draw, x, y, label, fg, bg):
    """Small rounded status chip; returns its right edge."""
    fnt = font(9, bold=True)
    w = draw.textlength(label, font=fnt) + 12
    h = 14
    draw.rounded_rectangle([x, y, x + w, y + h], radius=7, fill=bg)
    draw.text((x + 6, y + 2.5), label, font=fnt, fill=fg)
    return x + w


# ---- content (from the brief only) ---------------------------------------
FEATURES = [
    {
        "tag": "GLOBAL / CLIMATE",
        "color": REGION_COLORS["GLOBAL"],
        "status": "CONFIRMED",
        "headline": "COP31 COLLAPSES \u2014 first climate summit with no deal since 2000",
        "body": (
            "The 10-page \u201cAntalya Accords\u201d draft \u2014 no mention of fossil fuels, "
            "oil, coal or phase-out \u2014 went to a vote early Sunday in Antalya. The EU, "
            "UK and Panama objected; president Murat Kurum declared \u201cno consensus\u2026 "
            "these decisions have not been adopted.\u201d No new text will be drafted \u2014 "
            "the first COP to end with no deal since 2000, and the longest summit in 30+ years."
        ),
        "source": "Sources: Reuters, The Times, Sowetan, SE Daily, The Curtain, BelleNews",
    },
    {
        "tag": "EUROPE / CONFLICT",
        "color": REGION_COLORS["EUROPE"],
        "status": "CONFIRMED",
        "headline": "UKRAINE: Russia launches 186 drones overnight; homes hit",
        "body": (
            "Overnight 21\u219222 Nov, Russia launched 186 drones (72 jet-powered); Ukraine "
            "downed 161, with impacts at 18 sites. A home was destroyed in Dymer, Kyiv region "
            "\u2014 12+ missing, Zelensky said. Zaporizhzhia: 3 injured overnight incl. a child; "
            "a daytime strike killed 1. A FAB-250 bomb on Sloviansk wounded 5. Kharkiv region: "
            "1 killed, 39 injured (7 children). 131 clashes; Pokrovsk axis most intense."
        ),
        "source": "Sources: h.ua, 112.ua, Kyiv Post / EuropeSays",
    },
    {
        "tag": "ASIA-PACIFIC / DISASTER",
        "color": REGION_COLORS["ASIA-PACIFIC"],
        "status": "CONFIRMED",
        "headline": "INDONESIA: Candy-factory fire \u2014 3 dead, dozens missing in Cikande",
        "body": (
            "Search teams worked Sunday through the ruins of the PT Fonusa Agung Mulia candy "
            "factory (Milkita) in Cikande, Serang, Banten, after fire broke out Sat ~16:30 local. "
            "Sunday: 3 dead, at least 36 missing (latest rescue update 39; police and the owner "
            "say ~50), 7 body bags recovered, 15 survived. Cause unknown; victim identification "
            "may take 2\u20133 weeks."
        ),
        "source": "Sources: Reuters (22 Nov 03:56 UTC), AP, political.org",
    },
    {
        "tag": "MIDDLE EAST / CONFLICT",
        "color": REGION_COLORS["MIDDLE EAST"],
        "status": "CONFIRMED",
        "headline": "WEST BANK: Settlers torch cars; Eisenkot calls it \u201cJewish terrorism\u201d",
        "body": (
            "Overnight Sat\u2192Sun, settlers torched at least a dozen cars and vandalised homes "
            "in Deir al-Sudan, Deir Abu Mash\u2019al, Kafr Malik and At-Tuwani. Opposition leader "
            "Gadi Eisenkot (PM-designate) condemned it Sunday as \u201cJewish terrorism\u201d, "
            "blamed Ben-Gvir and Smotrich, and demanded administrative detention and Shin Bet "
            "operations. The IDF condemned the arson; Netanyahu stayed silent."
        ),
        "source": "Sources: CNN, AP, Petra, Azernews",
    },
]

MINIS = [
    ("HORMUZ: IRGC CLAIMS 4TH DRONE DOWNED",
     "IRGC says it downed another MQ-1 east of the strait Sunday \u2014 4th in 24h, 20th of the war. CLAIM, no outside confirmation.",
     "CLAIM"),
    ("HOUTHI MISSILE INTERCEPTED OVER SAUDI",
     "Saudi-led coalition intercepted a Houthi ballistic missile toward western Saudi Arabia early Sunday (~01:42 local).",
     "CLAIM*"),
    ("EU\u2013INDONESIA CEPA: THE SUNDAY DETAIL",
     "Deal signed Sat in Brussels; Sunday, Airlangga Hartarto detailed it: 90.4% of tariff lines to zero from day one.",
     None),
    ("BITCOIN REBOUNDS ABOVE $60K",
     "~$60,205\u201360,757 Sunday, +2.2\u20133% in 24h, up from Saturday\u2019s low of $55,130 (lowest since Sept 2024). ETH above $1,700.",
     None),
    ("F1 LAS VEGAS: VERSTAPPEN WINS",
     "Verstappen won the Las Vegas GP (Norris 2nd, Piastri 3rd); 35 lead changes. Race ended early Sunday UTC.",
     None),
    ("NWSL FINAL: KANSAS CITY\u2019S FIRST TITLE",
     "Kansas City Current beat Washington Spirit 2\u20131: DiBernardo Olimpico 54\u2019, Debinha 90+7\u2019, Rodman 90+9\u2019. First NWSL title.",
     None),
    ("NROL-136: FALCON 9 LAUNCHES SPY SATELLITES",
     "SpaceX Falcon 9 launched NROL-136 from Vandenberg at 12:23 UTC Sunday; booster B1097 (14th flight) landed back at LZ-4.",
     None),
    ("SOUTH KOREA: EDUCATION MINISTER QUITS",
     "Choi Kyo-jin resigned Sunday over anti-cheating confusion ahead of Thursday\u2019s CSAT exam; Lee accepted within ~1 hour.",
     None),
    ("SOUTH SUDAN: REBELS KILL 15 CIVILIANS",
     "Attack on Bol Bol Boma, Tonj East, began late Saturday: at least 15 civilians killed, toll likely to rise; 4 attackers also killed.",
     None),
    ("JUVENTUS 4\u20130 VENEZIA",
     "Serie A, Allianz Stadium: four second-half goals \u2014 Woltemade 53\u2019, Koopmeiners 59\u2019, Cabal 65\u2019, Kolo Muani 71\u2019 (pen).",
     None),
    ("SPAIN: S\u00c1NCHEZ COMPARES MADRID FORM TO FRANCO\u2019S",
     "PM Pedro S\u00e1nchez posted on X Sunday comparing a Madrid reporting form to one from the Franco regime. Snap election 29 Nov.",
     None),
    ("SMR ALLIANCE: KOREA, US, JAPAN IN JOINT NUCLEAR PUSH",
     "Working-level SMR talks on the IAEA ministerial sidelines in Songdo \u2014 first reported 22 Nov. Joint design standards planned.",
     None),
]

ONELINERS = [
    "Kharkiv region: strikes killed 1, injured 39 incl. 7 children over the past day.",
    "Sloviansk: FAB-250 glide bomb wounded 5; damaged a university, medical facility, apartment block.",
    "Zaporizhzhia: overnight strike injured 3 incl. a child; daytime strike killed 1 man.",
    "Dymer, Kyiv region: home destroyed in overnight drone attack; 12+ missing, Zelensky said.",
    "Ukraine General Staff: 131 clashes in 24h, Pokrovsk most intense; 2,310 Russian casualties claimed. [CLAIM]",
    "Germany to put \u20ac30m into \u201cIndustrial Ramstein\u201d to rebuild Ukraine\u2019s war-hit factories.",
    "China slams \u201cmalicious\u201d US ban on telecom firms\u2019 phone-number access.",
    "House Democrats split over risking a lame-duck shutdown to defund the Iran war.",
    "Sea-Tac: DHS and Washington Democrats clash Sunday over Saturday\u2019s ICE jetway arrests of 2 travellers.",
    "Duk, South Sudan: 7 killed in a fresh attack.",
    "Drone strikes kill civilians in West and South Kordofan, Sudan.",
    "Botswana\u2019s President Boko pledges to scrap visas for Africans.",
    "ANC officials visit the Ngcuka family in Sandton at 16:00 after Mlambo-Ngcuka\u2019s death.",
    "Liverpool 4\u20130 Man Utd: Pochettino\u2019s debut ends in a rout at Anfield; United 19th, 1 win in 11.",
    "Atalanta 4\u20134 Inter: Esposito hat-trick, Kessi\u00e9\u2019s 90+1\u2019 penalty completes the comeback.",
    "Milan 5\u20131 Frosinone: Ramos ends his goal drought as Milan return to the top four.",
    "Manipur hooch toll rises to 18 on Sunday: 1,130 screened, 228 still in hospital, 6 arrested.",
    "Trump to meet Putin in Anchorage on Monday; warns of \u201cvery severe consequences\u201d if no deal.",
    "Houthi media: 7 wounded in Hodeidah strikes \u2014 4 at Ras Isa dock, 3 at Bajil oil site. [CLAIM]",
    "Qatari LNG carrier Al Mayeda: operator Nakilat\u2019s statement published Sunday after Friday hit.",
    "Taiwan stocks fell 17% for the week, worst since 1990. (week-in-review)",
    "India\u2019s Nifty 50 up 11%+ this month while AI-heavy markets fell. (week-in-review)",
    "China: shares down 20%+ since summer; 10-year bond yield at record lows. (week-in-review)",
    "S\u00e1nchez: A-54 motorway to open \u201csoon\u201d; \u20ac19bn for rail maintenance to 2030.",
    "COP31 reaction: Guterres \u201cdeeply disappointed\u201d \u2014 \u201cThere is no ambiguity in the science.\u201d COP32 in Addis Ababa.",
    "Vatican: Pope Leo XIV delivers the Sunday Angelus; names Fr Bonino Theologian of the Papal Household.",
    "F1: Russell hit the barriers on lap 48, finished 9th; Hamilton and Leclerc collided.",
    "NWSL: Rodman\u2019s 90+9\u2019 goal came too late for Washington Spirit.",
    "CSAT: 111 suspected cheating cases; final decisions before results on 11 Dec.",
    "NROL-136 booster B1097 flew its 14th mission; first Vandenberg return since 10 Oct.",
    "Hull 2\u20130 Brighton: Oli McBurnie scores a late brace as Hull stun Brighton.",
    "CEPA: EU submits the deal to parliament Mon 23 Nov; Indonesia\u2019s GSP expires 31 Dec 2026.",
    "Crypto: ETH above $1,700, SOL ~$70, XRP ~$0.92\u20130.93; total market cap ~$2.03T.",
]

TIMELINE = [
    ("22:42 Sat", "Houthi missile intercepted"),
    ("Overnight", "Russia launches 186 drones"),
    ("Early Sun", "COP31 collapses: no consensus"),
    ("02:30 UTC", "Korea minister offers to resign"),
    ("03:56 UTC", "Reuters: Indonesia fire, 3 dead"),
    ("08:56 UTC", "Korea\u2013US\u2013Japan SMR reported"),
    ("12:23 UTC", "Falcon 9 launches NROL-136"),
    ("~13:20 UTC", "Juventus 4\u20130 Venezia FT"),
    ("14:00 UTC", "ANC visits Ngcuka family"),
    ("16:30 UTC", "Liverpool 4\u20130 Man Utd KO"),
    ("18:07 UTC", "Germany \u20ac30m Ramstein"),
    ("19:45 UTC", "Atalanta 4\u20134 Inter KO"),
    ("Sunday", "Manipur hooch toll rises to 18"),
    ("Sunday", "Guterres \u201cdeeply disappointed\u201d"),
]

# (lon, lat, number, badge dx, badge dy)
PINS = [
    (30.7, 36.9, 1, 0, 11),      # Antalya
    (30.5, 50.4, 2, -2, -11),    # Kyiv / Dymer
    (106.3, -6.2, 3, 0, -10),    # Cikande
    (35.2, 31.9, 4, 13, 7),      # West Bank
    (56.3, 26.6, 5, 8, -8),      # Hormuz
    (39.8, 21.4, 6, -10, 6),     # Mecca region
    (28.7, 7.8, 7, 8, 8),        # Tonj East
    (127.0, 37.5, 8, 0, -10),    # Seoul
    (-120.6, 34.7, 9, -9, -7),   # Vandenberg
    (7.7, 45.1, 10, -11, -4),    # Turin
    (-115.1, 36.2, 11, 9, 7),    # Las Vegas
]

PIN_LEGEND = [
    "1 Antalya \u00b7 2 Kyiv/Dymer \u00b7 3 Cikande \u00b7 4 West Bank \u00b7 5 Hormuz \u00b7 6 Mecca",
    "7 Tonj East \u00b7 8 Seoul \u00b7 9 Vandenberg \u00b7 10 Turin \u00b7 11 Las Vegas",
]

DATECHECK = [
    "Ghana banknotes \u2014 unveiled 12 Nov",
    "S\u00e3o Tom\u00e9 PM reappointed \u2014 12 Nov",
    "Kenya Saudi jobs \u2014 announced 12 Nov",
    "DRC referendum law \u2014 signed 9 Nov",
    "Lula\u2013S\u00e1nchez Madrid visit \u2014 16 Nov",
    "Cape Town Test \u2014 27\u201331 Oct",
    "Cairns T20 decider \u2014 Aug 2025",
    "ICE Sea-Tac arrests \u2014 Sat 21 Nov",
    "Manipur \u201c21 dead\u201d \u2014 date unverified",
    "Jeffries pledge \u2014 Sat 21 Nov",
    "Norway oil ruling \u2014 13 Nov",
    "DRC Ebola toll \u2014 11 Nov",
    "US House AI report \u2014 20 Nov",
    "Pope LatAm tour \u2014 ended 16 Nov",
    "Peru quake M6.7 \u2014 20 Nov",
    "GTA 6 $3.79B \u2014 20 Nov",
]

# Simplified continent outlines (lon, lat), equirectangular.
CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80), (-85, 70),
     (-75, 72), (-60, 60), (-55, 47), (-65, 45), (-75, 35), (-80, 25),
     (-85, 30), (-90, 21), (-97, 16), (-105, 20), (-115, 28), (-125, 40),
     (-125, 49), (-140, 60), (-158, 58), (-168, 66)],
    # Greenland
    [(-45, 60), (-40, 65), (-30, 68), (-22, 70), (-25, 76), (-40, 80),
     (-55, 76), (-58, 70), (-52, 64), (-45, 60)],
    # South America
    [(-80, 10), (-75, 11), (-60, 8), (-50, 0), (-35, -8), (-40, -20),
     (-48, -28), (-58, -38), (-65, -45), (-70, -54), (-73, -40), (-72, -20),
     (-78, -5), (-80, 10)],
    # Africa
    [(-17, 15), (-10, 30), (0, 35), (10, 37), (20, 32), (30, 31), (35, 28),
     (43, 12), (51, 11), (48, 0), (40, -10), (35, -20), (32, -29), (20, -35),
     (12, -18), (9, -1), (-8, 4), (-17, 15)],
    # Eurasia (Asia + Europe as one landmass, drawn first)
    [(30, 70), (45, 68), (60, 70), (75, 73), (90, 75), (110, 76), (130, 72),
     (160, 70), (178, 66), (162, 60), (158, 52), (142, 50), (140, 40),
     (135, 35), (127, 38), (122, 32), (120, 25), (110, 20), (105, 10),
     (100, 8), (95, 15), (90, 22), (80, 10), (75, 8), (70, 20), (60, 25),
     (55, 26), (50, 30), (45, 30), (40, 35), (35, 36), (30, 40), (28, 40),
     (23, 36), (19, 40), (12, 44), (3, 42), (-2, 37), (-9, 37), (-10, 36),
     (-9, 43), (-2, 48), (0, 51), (5, 53), (8, 57), (10, 59), (18, 56),
     (21, 55), (28, 60), (30, 70)],
    # Australia
    [(113, -22), (114, -30), (115, -35), (125, -33), (130, -32), (137, -35),
     (140, -38), (145, -38), (150, -37), (153, -27), (146, -19), (142, -11),
     (135, -12), (130, -13), (126, -14), (122, -17), (118, -20), (113, -22)],
]


# ---- sections ----------------------------------------------------------------
def draw_header(draw):
    draw.rectangle([0, 0, W, 62], fill=NAVY)
    draw.rectangle([0, 62, W, 64], fill=ACCENT)
    draw.text((14, 8), "SUNDAY 22 NOVEMBER 2026",
              font=font(25, bold=True), fill=(255, 255, 255))
    draw.text((14, 38),
              "THE WORLD IN ONE IMAGE  \u00b7  49 stories  \u00b7  7 regions  \u00b7  "
              "Every story first reported on 22 Nov 2026 (any time zone)",
              font=font(11), fill=(205, 216, 228))
    # legend, right aligned
    fnt = font(10, bold=True)
    draw.ellipse([W - 252, 42, W - 242, 52], fill=GREEN)
    draw.text((W - 238, 40), "CONFIRMED", font=fnt, fill=(255, 255, 255))
    draw.ellipse([W - 148, 42, W - 138, 52], fill=(232, 164, 42))
    draw.text((W - 134, 40), "CLAIM = unverified", font=fnt, fill=(255, 255, 255))


def draw_timeline(draw):
    y0, y1 = 68, 112
    draw.rounded_rectangle([12, y0, 1012, y1], radius=6, fill=CARD, outline=LINE)
    draw.text((22, y0 + 14), "SUNDAY\nIN UTC", font=font(10, bold=True), fill=NAVY)
    x0 = 92
    cw = (1000 - x0) // 7
    for i, (t, txt) in enumerate(TIMELINE):
        col, row = i % 7, i // 7
        x = x0 + col * cw + 2
        y = y0 + 3 + row * 21
        draw.text((x, y), t, font=font(8, bold=True), fill=NAVY2)
        draw.text((x, y + 10), trunc(draw, txt, font(8), cw - 6),
                  font=font(8), fill=INK)


def draw_features(draw):
    xs = [12, 514]
    ys = [116, 262]
    cw, ch = 498, 142
    for idx, f in enumerate(FEATURES):
        x = xs[idx % 2]
        y = ys[idx // 2]
        draw.rounded_rectangle([x, y, x + cw, y + ch], radius=6, fill=CARD, outline=LINE)
        draw.rectangle([x + 6, y, x + cw - 6, y + 4], fill=f["color"])
        # tag + status chip
        draw.text((x + 10, y + 10), f["tag"], font=font(9, bold=True), fill=f["color"])
        chip(draw, x + cw - 78, y + 9,
             f["status"], (255, 255, 255), GREEN)
        # headline (max 2 lines)
        hf = font(14, bold=True)
        lines = fit(draw, f["headline"], hf, cw - 20, 2)
        hy = y + 28
        for ln in lines:
            draw.text((x + 10, hy), ln, font=hf, fill=INK)
            hy += 17
        # body (max 5 lines)
        bf = font(10)
        blines = fit(draw, f["body"], bf, cw - 20, 5)
        by = hy + 2
        for ln in blines:
            draw.text((x + 10, by), ln, font=bf, fill=(40, 46, 54))
            by += 12.5
        # source line
        draw.text((x + 10, y + ch - 15),
                  trunc(draw, f["source"], font(8), cw - 20),
                  font=font(8), fill=MUTED)


def draw_minis(draw):
    draw.text((12, 408), "12 MORE STORIES", font=font(12, bold=True), fill=NAVY)
    draw.line([150, 415, 1012, 415], fill=LINE, width=1)
    xs = [12, 346, 680]
    ys = [424, 476, 528, 580]
    cw, ch = 330, 48
    for i, (head, body, claim) in enumerate(MINIS):
        x = xs[i % 3]
        y = ys[i // 3]
        draw.rounded_rectangle([x, y, x + cw, y + ch], radius=5, fill=CARD, outline=LINE)
        draw.rectangle([x, y + 5, x + 3, y + ch - 5], fill=ACCENT)
        chip_w = 56 if claim else 0
        if claim:
            chip(draw, x + cw - 52, y + 4, claim,
                 (255, 255, 255), AMBER if claim == "CLAIM" else (120, 60, 10))
        hf = font(9, bold=True)
        hlines = fit(draw, head, hf, cw - 16 - chip_w, 2)
        hy = y + 4
        for ln in hlines:
            draw.text((x + 9, hy), ln, font=hf, fill=INK)
            hy += 12
        # body: 2 lines if headline took 1, else 1
        max_body = 2 if len(hlines) == 1 else 1
        bf = font(9)
        blines = fit(draw, body, bf, cw - 16, max_body)
        by = hy + 1
        for ln in blines:
            draw.text((x + 9, by), ln, font=bf, fill=(40, 46, 54))
            by += 11


def draw_oneliners(draw):
    draw.text((12, 630), "THE REST \u2014 33 STORIES IN ONE LINE",
              font=font(12, bold=True), fill=NAVY)
    draw.line([330, 637, 1012, 637], fill=LINE, width=1)
    xs = [12, 346, 680]
    nf = font(9, bold=True)
    tf = font(9)
    for i, txt in enumerate(ONELINERS):
        x = xs[i % 3]
        y = 646 + (i // 3) * 19
        num = "%d." % (i + 1)
        draw.text((x, y), num, font=nf, fill=NAVY2)
        nw = draw.textlength(num, font=nf) + 5
        lines = fit(draw, txt, tf, 330 - nw - 2, 2)
        ly = y
        for ln in lines:
            draw.text((x + nw, ly), ln, font=tf, fill=INK)
            ly += 9.5


def project(lon, lat, x0, y0, mw, mh):
    x = x0 + (lon + 180.0) / 360.0 * mw
    y = y0 + (75.0 - lat) / 130.0 * mh
    return x, y


def draw_map_datecheck(draw):
    # ---- world map box (left)
    draw.rounded_rectangle([12, 856, 506, 972], radius=6, fill=CARD, outline=LINE)
    draw.text((22, 861), "WORLD MAP \u2014 11 PINS",
              font=font(10, bold=True), fill=NAVY)
    mx0, my0, mw, mh = 18, 874, 482, 70
    draw.rectangle([mx0, my0, mx0 + mw, my0 + mh], fill=OCEAN, outline=LINE)
    # graticule
    for lon in range(-150, 181, 30):
        gx, _ = project(lon, 0, mx0, my0, mw, mh)
        draw.line([gx, my0, gx, my0 + mh], fill=(196, 214, 226), width=1)
    for lat in (60, 30, 0, -30):
        _, gy = project(0, lat, mx0, my0, mw, mh)
        draw.line([mx0, gy, mx0 + mw, gy], fill=(196, 214, 226), width=1)
    # continents
    for poly in CONTINENTS:
        pts = [project(lon, lat, mx0, my0, mw, mh) for lon, lat in poly]
        draw.polygon(pts, fill=LAND, outline=LAND_EDGE)
    # pins
    for lon, lat, n, dx, dy in PINS:
        px, py = project(lon, lat, mx0, my0, mw, mh)
        bx, by = px + dx, py + dy
        draw.ellipse([px - 2.5, py - 2.5, px + 2.5, py + 2.5], fill=PIN_RED)
        if dx or dy:
            draw.line([px, py, bx, by], fill=PIN_RED, width=1)
        draw.ellipse([bx - 6, by - 6, bx + 6, by + 6], fill=PIN_RED, outline=(255, 255, 255))
        nf = font(8, bold=True)
        label = str(n)
        tw = draw.textlength(label, font=nf)
        draw.text((bx - tw / 2, by - 4.5), label, font=nf, fill=(255, 255, 255))
    lf = font(8)
    draw.text((22, 948), PIN_LEGEND[0], font=lf, fill=MUTED)
    draw.text((22, 959), PIN_LEGEND[1], font=lf, fill=MUTED)

    # ---- date check box (right)
    draw.rounded_rectangle([510, 856, 1012, 972], radius=6, fill=CARD, outline=LINE)
    draw.text((520, 861), "DATE CHECK \u2014 STALE STORIES EXCLUDED",
              font=font(10, bold=True), fill=(146, 30, 24))
    df = font(8)
    col_x = [520, 768]
    for i, item in enumerate(DATECHECK):
        x = col_x[i % 2]
        y = 878 + (i // 2) * 11.5
        draw.text((x, y), "\u2715", font=font(8, bold=True), fill=(192, 38, 32))
        draw.text((x + 11, y), trunc(draw, item, df, 226), font=df, fill=(70, 60, 58))


def draw_footer(draw):
    draw.line([12, 980, 1012, 980], fill=LINE, width=1)
    f1 = font(8)
    draw.text((12, 985),
              trunc(draw,
                    "Sources: Reuters, AP, CNN, The Times, Kyiv Post, h.ua, 112.ua, "
                    "SE Daily, Al Jazeera, SPA, SpaceX, Korea JoongAng Daily, AFP, "
                    "Football Italia, Sportradar, PTI, Politico, UN News, Fox News, "
                    "USA Today \u2014 and 40+ more outlets (full list in the brief).",
                    f1, 1000),
              font=f1, fill=MUTED)
    draw.text((12, 997),
              "All 49 stories were first reported on Sunday 22 November 2026 (any time zone). "
              "CLAIM = single-source / unverified. Flat drawn illustration \u2014 no AI imagery, no photos.",
              font=f1, fill=MUTED)
    draw.text((12, 1009),
              "news-image-20261122  \u00b7  $100 USDC escrowed pool  \u00b7  "
              "Result Tue 8 Dec 2026, 15:00 WIB  \u00b7  Poster built from the research brief, 22 Nov 2026.",
              font=font(7), fill=MUTED)


def build():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    draw_header(draw)
    draw_timeline(draw)
    draw_features(draw)
    draw_minis(draw)
    draw_oneliners(draw)
    draw_map_datecheck(draw)
    draw_footer(draw)
    img.save(OUT, format="PNG")
    return OUT
