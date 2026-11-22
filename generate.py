#!/usr/bin/env python3
"""Draw the 22 November 2026 one-image news poster.

make.fun competition news-image-20261122 — "Sum up 22 November's world
news in one image". Flat drawn illustration only: every picture element is
a shape, a panel, or typography drawn with Pillow. No external images.

Output: entry.png, 1024x1024, written next to this script.
"""

import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 16
CW = W - 2 * MARGIN  # content width: 992

# --- palette -----------------------------------------------------------------
PAPER = (250, 246, 238)
INK = (26, 26, 26)
MUTED = (96, 90, 80)
RED = (178, 34, 34)
DARKRED = (130, 22, 22)
BLUE = (28, 74, 120)
NAVY = (24, 42, 66)
SLATE = (52, 58, 64)
RULE = (198, 188, 170)
PANEL = (238, 231, 216)
PANEL2 = (232, 240, 246)
SEA = (205, 226, 241)
LAND = (233, 220, 194)
LAND_EDGE = (176, 160, 124)
FLAME = (228, 112, 28)
FLAME2 = (244, 178, 60)
GREEN = (70, 116, 70)
WHITE = (255, 255, 255)

FONT_DIR = "/usr/share/fonts/truetype"
SERIF_B = os.path.join(FONT_DIR, "dejavu", "DejaVuSerif-Bold.ttf")
SANS_B = os.path.join(FONT_DIR, "liberation", "LiberationSans-Bold.ttf")
SANS = os.path.join(FONT_DIR, "liberation", "LiberationSans-Regular.ttf")

_font_cache = {}


def font(path, size):
    key = (path, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(path, size)
    return _font_cache[key]


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap by pixel width; returns a list of lines."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_lines(draw, x, y, lines, fnt, fill, leading):
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def fit_one_line(draw, text, fnt_path, start_size, max_w, min_size=8):
    """Shrink the font until the text fits on one line; returns (font, size)."""
    size = start_size
    while size > min_size:
        fnt = font(fnt_path, size)
        if draw.textlength(text, font=fnt) <= max_w:
            return fnt, size
        size -= 1
    return font(fnt_path, min_size), min_size


# --- content -----------------------------------------------------------------

FEATURES = [
    {
        "icon": "cop",
        "tag": "GLOBAL  ·  CLIMATE",
        "head": "COP31 COLLAPSES — FIRST SUMMIT WITH NO DEAL SINCE 2000",
        "body": (
            "The 10-page \u201cAntalya Accords\u201d draft \u2014 no mention of fossil fuels, "
            "oil, coal or phase-out \u2014 went to a vote early Sunday. The EU, UK and "
            "Panama objected; president Murat Kurum declared \u201cno consensus\u2026 "
            "these decisions have not been adopted\u201d. No new text will be drafted. "
            "The longest summit in 30+ years."
        ),
        "label": "CONFIRMED",
        "src": "Reuters · The Times · Sowetan",
    },
    {
        "icon": "drones",
        "tag": "EUROPE  ·  CONFLICT",
        "head": "UKRAINE: 186 DRONES OVERNIGHT, HOMES HIT",
        "body": (
            "Russia launched 186 drones overnight (72 jet-powered); Ukraine downed "
            "161, with impacts at 18 sites. A home was destroyed in Dymer, 12+ "
            "missing. Zaporizhzhia: 3 injured overnight incl. a child; a daytime "
            "strike killed 1. A FAB-250 on Sloviansk wounded 5. 131 clashes; "
            "Pokrovsk axis most intense."
        ),
        "label": "CONFIRMED",
        "src": "h.ua · Kyiv Post · 112.ua",
    },
    {
        "icon": "fire",
        "tag": "ASIA-PACIFIC  ·  DISASTER",
        "head": "INDONESIA: CANDY-FACTORY FIRE — 3 DEAD, DOZENS MISSING",
        "body": (
            "Search teams worked Sunday through the ruins of the PT Fonusa Agung "
            "Mulia (Milkita) candy factory in Cikande, Serang, after fire broke "
            "out Sat ~16:30 local. 3 dead, at least 36 missing \u2014 some reports "
            "say around 50 \u2014 7 body bags recovered, 15 survived. Cause unknown; "
            "ID may take 2\u20133 weeks."
        ),
        "label": "CONFIRMED",
        "src": "Reuters · AP",
    },
    {
        "icon": "car",
        "tag": "MIDDLE EAST  ·  CONFLICT",
        "head": "WEST BANK: SETTLERS TORCH CARS; \u201cJEWISH TERRORISM\u201d",
        "body": (
            "Overnight, settlers torched at least a dozen cars and vandalised "
            "homes in Deir al-Sudan, Deir Abu Mash\u2019al, Kafr Malik and At-Tuwani. "
            "Opposition leader Gadi Eisenkot condemned it Sunday as \u201cJewish "
            "terrorism\u201d, blamed Ben-Gvir and Smotrich, and demanded "
            "administrative detention plus Shin Bet operations. The IDF condemned "
            "the arson; Netanyahu stayed silent."
        ),
        "label": "CONFIRMED",
        "src": "CNN · AP · Petra",
    },
]

MINIS = [
    ("HORMUZ: IRGC CLAIMS 4TH DRONE DOWNED",
     "4th in 24h, 20th of the war \u2014 CLAIM, unconfirmed. Nakilat statement on hit LNG carrier Al Mayeda out Sunday."),
    ("HOUTHI MISSILE DOWNED OVER SAUDI",
     "Coalition intercepted a ballistic missile ~01:42 local; Mecca-region alert issued Sat 23:43."),
    ("EU\u2013INDONESIA CEPA: THE SUNDAY DETAIL",
     "90.4% of tariff lines to zero day one; ratification target 1 Jan 2027; EU to parliament Mon."),
    ("BITCOIN REBOUNDS ABOVE $60K",
     "$60,205\u201360,757, +2\u20133% in 24h, off Sat\u2019s $55,130 low; ETH >$1,700, SOL ~$70."),
    ("F1 LAS VEGAS: VERSTAPPEN WINS",
     "Norris 2nd, Piastri 3rd; 35 lead changes; Russell crashed lap 48, finished 9th."),
    ("NWSL FINAL: KANSAS CITY\u2019S FIRST TITLE",
     "Beat Washington Spirit 2\u20131: Olimpico 54\u2032, Debinha 90+7\u2032, Rodman 90+9\u2032."),
    ("NROL-136: FALCON 9 LAUNCHES SPY SATS",
     "12:23 UTC from Vandenberg; booster B1097 landed at LZ-4, 14th flight."),
    ("SOUTH KOREA: EDUCATION MINISTER QUITS",
     "Choi Kyo-jin resigned over AI-cheating chaos before Thursday\u2019s CSAT; Lee accepted within an hour."),
    ("SOUTH SUDAN: REBELS KILL 15 CIVILIANS",
     "Attack on Bol Bol Boma, Tonj East, late Sat; toll may rise; commissioner blames SPLA-IO."),
    ("JUVENTUS 4\u20130 VENEZIA",
     "Four second-half goals: Woltemade, Koopmeiners, Cabal, Kolo Muani (pen). Final score to confirm."),
    ("SPAIN: S\u00c1NCHEZ COMPARES FORM TO FRANCO\u2019S",
     "PM\u2019s X post: Franco-era reporting form \u201cto persecute and censor freedom of thought.\u201d"),
    ("SMR ALLIANCE: KOREA, US, JAPAN PUSH",
     "Joint SMR design standards, third-country markets; talks reported 22 Nov (SE Daily)."),
]

TIMELINE = [
    ("22:42 SAT", "Houthi missile intercepted"),
    ("OVERNIGHT", "186 drones hit Ukraine"),
    ("EARLY SUN", "COP31 collapses"),
    ("02:30", "Korean minister quits"),
    ("03:56", "Indonesia fire: 3 dead, 36 missing"),
    ("08:56", "SMR alliance reported"),
    ("12:23", "Falcon 9 launches NROL-136"),
    ("~13:20", "Juventus 4\u20130 Venezia"),
    ("14:00", "ANC visits Ngcuka family"),
    ("16:30", "Liverpool v Man Utd KO"),
]

ONE_LINERS = [
    "Kharkiv: strikes killed 1, injured 39 incl. 7 children. (h.ua)",
    "Sloviansk: FAB-250 bomb wounded 5, hit university + clinic. (Kyiv Post)",
    "Zaporizhzhia: overnight strike hurt 3 incl. child; daytime strike killed 1. (h.ua)",
    "Dymer: home destroyed in drone attack, 12+ missing \u2014 Zelensky. (h.ua)",
    "Kyiv: 131 clashes in 24h, Pokrovsk fiercest; 2,310 Russian casualties claimed. (Gen. Staff)",
    "Germany puts \u20ac30m into \u201cIndustrial Ramstein\u201d to rebuild Ukraine factories. (KSE)",
    "China slams \u201cmalicious\u201d US ban on telecom firms\u2019 phone-number access. (Brief)",
    "House Democrats split over risking lame-duck shutdown to defund Iran war. (sumi.news)",
    "Washington governor: ICE \u201cout of control\u201d after airport arrests. (ARY)",
    "Duk, South Sudan: 7 killed in fresh attack. (Juba Global)",
    "Drone strikes kill civilians in West and South Kordofan, Sudan. (Juba Global)",
    "Botswana\u2019s Boko pledges to scrap visas for Africans. (Juba Global)",
    "ANC\u2019s Mantashe visits Ngcuka family in Sandton at 16:00. (MyANC)",
    "Ghana unveils \u201cHeritage Series\u201d banknotes \u2014 Nkrumah, Annan, Makola traders. (C54)",
    "Am\u00e9rico Ramos reappointed PM of S\u00e3o Tom\u00e9 and Pr\u00edncipe. (C54)",
    "Kenya secures 293,600 job opportunities in Saudi Arabia. (C54)",
    "DRC: Tshisekedi enacts law for constitutional reform amid tensions. (C54)",
    "Cricket: Inglis and Carey put Australia in command of SA decider. (C54)",
    "Houthi media: 7 wounded in Hodeidah strikes \u2014 Ras Isa 4, Bajil 3. CLAIM. (Houthi media)",
    "Qatari LNG carrier Al Mayeda: Nakilat statement out Sunday after Fri hit. (Al Jazeera)",
    "Taiwan stocks fell 17% for the week, worst since 1990. (Invest News Week)",
    "India\u2019s Nifty 50 up 11%+ this month while AI-heavy markets fell. (Invest News Week)",
    "China: shares down 20%+ since summer; 10-yr yield at record lows. (Invest News Week)",
    "S\u00e1nchez: A-54 motorway to open \u201csoon\u201d; \u20ac19bn rail upkeep to 2030. (El Progreso)",
    "Lula: \u201cvery important\u201d S\u00e1nchez wins Spain\u2019s snap poll; will visit next week. (Breitbart)",
    "Vatican: Pope Leo XIV delivers Angelus; names Bonino papal theologian. (Catholic Intel.)",
    "F1: Russell hit barriers lap 48, 9th; Hamilton-Leclerc Ferrari collision. (F1)",
    "NWSL: Rodman\u2019s 90+9\u2032 goal came too late for Washington. (NWSL)",
    "CSAT: 111 suspected cheating cases; decisions before results 11 Dec. (JoongAng)",
    "NROL-136 booster B1097: 14th flight; first Vandenberg return since 10 Oct. (VC Star)",
    "Juventus scorers: Woltemade, Koopmeiners, Cabal, Kolo Muani (pen). (Football Italia)",
    "CEPA: EU submits deal to parliament Mon; Indonesia GSP ends 31 Dec 2026. (Cabinet Sec.)",
    "Crypto: ETH >$1,700, SOL ~$70, XRP ~$0.92\u20130.93; market cap ~$2.03T. (CoinLab)",
]

# (number, name, lon, lat, short label)
PINS = [
    (1, "Antalya, T\u00fcrkiye", 30.7, 36.9, "COP31 collapses"),
    (2, "Kyiv / Dymer, Ukraine", 30.5, 50.5, "overnight drone barrage"),
    (3, "Cikande, Indonesia", 106.3, -6.2, "factory fire"),
    (4, "West Bank", 35.2, 31.9, "settler arson"),
    (5, "Strait of Hormuz", 56.3, 26.5, "IRGC drone claim"),
    (6, "Mecca region, Saudi Arabia", 39.8, 21.4, "missile intercepted"),
    (7, "Tonj East, South Sudan", 28.7, 7.3, "rebels kill 15"),
    (8, "Seoul, South Korea", 127.0, 37.5, "minister resigns"),
    (9, "Vandenberg, California", -120.6, 34.7, "NROL-136 launch"),
    (10, "Turin, Italy", 7.7, 45.1, "Juventus 4\u20130"),
    (11, "Las Vegas, USA", -115.1, 36.2, "F1 Grand Prix"),
]

# Rough continent outlines in (lon, lat). Stylised, not surveyed.
CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 69), (-85, 70),
     (-80, 73), (-65, 60), (-55, 52), (-60, 46), (-70, 42), (-75, 35),
     (-80, 32), (-81, 25), (-90, 21), (-97, 26), (-105, 23), (-110, 24),
     (-114, 30), (-120, 34), (-125, 40), (-124, 48), (-130, 55),
     (-150, 60), (-165, 60)],
    # Greenland
    [(-45, 60), (-30, 68), (-22, 70), (-30, 76), (-55, 76), (-58, 70), (-52, 64)],
    # South America
    [(-78, 8), (-72, 11), (-62, 10), (-52, 5), (-50, 0), (-44, -3), (-35, -8),
     (-38, -15), (-40, -22), (-48, -28), (-52, -33), (-58, -38), (-62, -41),
     (-66, -47), (-69, -52), (-71, -54), (-73, -45), (-73, -37), (-71, -30),
     (-70, -20), (-75, -15), (-77, -8), (-80, 0), (-80, 6)],
    # Europe
    [(-10, 36), (-9, 43), (-2, 48), (0, 50), (3, 53), (8, 57), (10, 59),
     (18, 56), (21, 55), (24, 58), (28, 60), (30, 62), (32, 66), (40, 68),
     (45, 66), (40, 60), (35, 55), (30, 50), (28, 45), (30, 42), (28, 40),
     (23, 36), (19, 40), (15, 44), (12, 44), (10, 44), (8, 44), (3, 42),
     (-2, 37)],
    # Africa
    [(-17, 15), (-16, 21), (-10, 31), (-5, 35), (0, 36), (10, 37), (11, 34),
     (20, 32), (30, 31), (32, 31), (35, 28), (37, 22), (39, 18), (43, 12),
     (48, 11), (51, 10), (46, 5), (42, -2), (40, -8), (39, -15), (36, -20),
     (33, -26), (29, -31), (26, -34), (20, -35), (17, -32), (15, -27),
     (12, -18), (12, -12), (9, -1), (9, 4), (-8, 4), (-13, 8), (-17, 12)],
    # Asia
    [(28, 45), (35, 36), (44, 38), (50, 37), (57, 37), (63, 33), (68, 25),
     (72, 20), (77, 8), (80, 10), (88, 22), (92, 20), (97, 16), (100, 8),
     (103, 2), (105, 10), (109, 18), (114, 22), (120, 28), (122, 35),
     (126, 40), (132, 43), (140, 46), (142, 52), (155, 60), (170, 66),
     (178, 68), (170, 70), (150, 72), (130, 72), (110, 74), (90, 75),
     (70, 72), (55, 68), (45, 62), (35, 55), (30, 50)],
    # UK
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51)],
    # Japan
    [(130, 31), (132, 33), (135, 34), (138, 35), (140, 36), (141, 39),
     (142, 42), (144, 44), (142, 44), (140, 40), (139, 37), (136, 34), (132, 33)],
    # Indonesia
    [(95, 5), (100, 0), (105, -5), (110, -7), (115, -8), (120, -9), (125, -9),
     (130, -4), (135, -3), (140, -4), (141, -8), (135, -8), (130, -10),
     (125, -10), (120, -10), (115, -8), (110, -7), (105, -5), (100, -1), (95, 2)],
    # Australia
    [(114, -22), (114, -28), (116, -32), (118, -35), (124, -33), (129, -32),
     (132, -32), (135, -35), (138, -35), (140, -38), (145, -38), (147, -39),
     (150, -37), (153, -32), (153, -27), (151, -24), (146, -19), (143, -15),
     (142, -11), (140, -17), (136, -15), (132, -12), (130, -13), (126, -14),
     (122, -17), (118, -20)],
    # New Zealand
    [(167, -45), (172, -41), (174, -39), (177, -38), (178, -38), (176, -40),
     (173, -42), (170, -44), (168, -46)],
]

DATE_CHECK = (
    "DATE CHECK \u2014 these are NOT 22 Nov: Jeffries settler-sanctions pledge \u2014 Sat 21 Nov  ·  "
    "Norway oil ruling \u2014 13 Nov  ·  Peru quake \u2014 Fri 20 Nov  ·  Trump FBI-hack remarks \u2014 Sat 21 Nov  ·  "
    "Iran tanker strikes \u2014 Sat 21 Nov  ·  CEPA signing \u2014 Sat 21 Nov  ·  GTA 6 $3.79B \u2014 Fri 20 Nov  ·  "
    "Amazon\u2013Decart \u2014 Sat 21 Nov  ·  Flamengo title \u2014 Sat 21 Nov  ·  Manipur toll \u201c21 dead\u201d \u2014 date unverified"
)

SOURCES = (
    "SOURCES: Reuters · AP · CNN · The Times · Sowetan · SE Daily · h.ua · 112.ua · Kyiv Post · "
    "Petra · Al Jazeera · SPA · Finnhub · CoinLab · SpaceX · VC Star · Korea JoongAng Daily · KBS · "
    "AFP · Football Italia · ANI · Dem\u00f3crata · ARY News · Juba Global News · MyANC · C54 · "
    "Catholic Intelligence · Breitbart · Invest News Week"
)


# --- illustration panels -------------------------------------------------------

def icon_cop(draw, x0, y0, w, h):
    """Globe with a red slash: no deal."""
    draw.rectangle([x0, y0, x0 + w, y0 + h], fill=NAVY)
    cx, cy, r = x0 + w // 2, y0 + h // 2 - 4, 30
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(150, 200, 228),
                 outline=WHITE, width=2)
    draw.ellipse([cx - r // 2, cy - r, cx + r // 2, cy + r], outline=BLUE, width=1)
    draw.line([cx - r, cy, cx + r, cy], fill=BLUE, width=1)
    draw.line([cx, cy - r, cx, cy + r], fill=BLUE, width=1)
    draw.line([cx - r - 6, cy + r + 6, cx + r + 6, cy - r - 6], fill=RED, width=6)
    draw.text((x0 + 8, y0 + h - 20), "NO DEAL", font=font(SANS_B, 12), fill=WHITE)


def icon_drones(draw, x0, y0, w, h):
    """Skyline under three drone silhouettes."""
    draw.rectangle([x0, y0, x0 + w, y0 + h], fill=SLATE)
    base = y0 + h - 26
    for bx, bw, bh in [(6, 16, 18), (26, 20, 30), (50, 14, 22), (66, 16, 34)]:
        draw.rectangle([x0 + bx, base - bh, x0 + bx + bw, base],
                       fill=(30, 33, 38))
    draw.rectangle([x0, 0 + base, x0 + w, y0 + h], fill=(30, 33, 38))
    for dx, dy in [(18, 14), (46, 30), (66, 12)]:
        cx, cy = x0 + dx, y0 + dy
        draw.rectangle([cx - 7, cy - 3, cx + 7, cy + 3], fill=WHITE)
        draw.line([cx - 12, cy - 5, cx + 12, cy - 5], fill=WHITE, width=2)
        draw.ellipse([cx - 13, cy - 7, cx - 9, cy - 3], fill=WHITE)
        draw.ellipse([cx + 9, cy - 7, cx + 13, cy - 3], fill=WHITE)
    draw.text((x0 + 8, y0 + h - 20), "186 DRONES", font=font(SANS_B, 11),
              fill=WHITE)


def icon_fire(draw, x0, y0, w, h):
    """Factory with flames."""
    draw.rectangle([x0, y0, x0 + w, y0 + h], fill=(74, 44, 32))
    base = y0 + h - 24
    draw.rectangle([x0 + 10, base - 34, x0 + 74, base], fill=(120, 84, 60))
    draw.polygon([(x0 + 10, base - 34), (x0 + 26, base - 46),
                  (x0 + 42, base - 34), (x0 + 58, base - 46),
                  (x0 + 74, base - 34)], fill=(150, 108, 74))
    draw.rectangle([x0 + 60, base - 62, x0 + 68, base - 34], fill=(150, 108, 74))
    cx = x0 + 30
    draw.polygon([(cx - 16, base - 44), (cx - 8, base - 66), (cx - 2, base - 52),
                  (cx + 6, base - 72), (cx + 12, base - 54), (cx + 18, base - 64),
                  (cx + 16, base - 44)], fill=FLAME)
    draw.polygon([(cx - 7, base - 44), (cx - 2, base - 58), (cx + 4, base - 48),
                  (cx + 8, base - 56), (cx + 8, base - 44)], fill=FLAME2)
    draw.text((x0 + 8, y0 + h - 20), "CIKANDE", font=font(SANS_B, 11),
              fill=WHITE)


def icon_car(draw, x0, y0, w, h):
    """Burning car silhouette."""
    draw.rectangle([x0, y0, x0 + w, y0 + h], fill=(56, 36, 36))
    base = y0 + h - 30
    draw.polygon([(x0 + 8, base), (x0 + 12, base - 14), (x0 + 26, base - 24),
                  (x0 + 54, base - 24), (x0 + 68, base - 12), (x0 + 76, base)],
                 fill=(20, 20, 22))
    draw.ellipse([x0 + 18, base - 4, x0 + 30, base + 8], fill=(20, 20, 22))
    draw.ellipse([x0 + 54, base - 4, x0 + 66, base + 8], fill=(20, 20, 22))
    cx = x0 + 42
    draw.polygon([(cx - 14, base - 24), (cx - 6, base - 44), (cx, base - 32),
                  (cx + 8, base - 48), (cx + 12, base - 32), (cx + 16, base - 40),
                  (cx + 14, base - 24)], fill=FLAME)
    draw.text((x0 + 8, y0 + h - 20), "WEST BANK", font=font(SANS_B, 11),
              fill=WHITE)


ICONS = {"cop": icon_cop, "drones": icon_drones, "fire": icon_fire,
         "car": icon_car}


# --- sections ------------------------------------------------------------------

def section_head(draw, x, y, text):
    """Section header: red square + bold caps + rule."""
    draw.rectangle([x, y + 1, x + 10, y + 11], fill=RED)
    draw.text((x + 15, y - 1), text, font=font(SANS_B, 13), fill=INK)
    draw.line([x, y + 15, x + CW, y + 15], fill=RULE, width=1)
    return y + 18


def draw_masthead(draw):
    y = 10
    draw.text((MARGIN, y), "ONE DAY  ·  49 STORIES  ·  7 REGIONS",
              font=font(SANS_B, 12), fill=RED)
    right = "SUNDAY EDITION"
    draw.text((W - MARGIN - draw.textlength(right, font=font(SANS_B, 12)), y),
              right, font=font(SANS_B, 12), fill=MUTED)
    y += 16
    date = "22 NOVEMBER 2026"
    fnt = font(SERIF_B, 50)
    draw.text(((W - draw.textlength(date, font=fnt)) / 2, y), date,
              font=fnt, fill=INK)
    y += 56
    sub = "THE WORLD IN ONE IMAGE  —  EVERY STORY HAPPENED, OR WAS FIRST REPORTED, ON 22 NOVEMBER 2026"
    fnt2 = font(SANS_B, 11)
    draw.text(((W - draw.textlength(sub, font=fnt2)) / 2, y), sub,
              font=fnt2, fill=MUTED)
    y += 16
    draw.line([MARGIN, y, W - MARGIN, y], fill=INK, width=3)
    draw.line([MARGIN, y + 4, W - MARGIN, y + 4], fill=INK, width=1)
    return y + 8


def draw_timeline(draw, y):
    y = section_head(draw, MARGIN, y, "UTC TIMELINE  —  SUNDAY 22 NOVEMBER")
    col_w = CW / 5
    f_time = font(SANS_B, 10)
    f_txt = font(SANS, 10)
    for row in range(2):
        for col in range(5):
            idx = row * 5 + col
            t, txt = TIMELINE[idx]
            x = MARGIN + col * col_w
            draw.text((x, y), t, font=f_time, fill=RED)
            tw = draw.textlength(t + "  ", font=f_time)
            draw.text((x + tw, y), txt, font=f_txt, fill=INK)
        y += 13
    draw.line([MARGIN, y + 2, W - MARGIN, y + 2], fill=RULE, width=1)
    return y + 6


def draw_features(draw, y):
    y = section_head(draw, MARGIN, y, "TOP STORIES")
    cell_w = (CW - 12) // 2
    cell_h = 134
    icon_w = 84
    for i, feat in enumerate(FEATURES):
        row, col = divmod(i, 2)
        x0 = MARGIN + col * (cell_w + 12)
        y0 = y + row * (cell_h + 8)
        draw.rectangle([x0, y0, x0 + cell_w, y0 + cell_h], fill=PANEL,
                       outline=RULE, width=1)
        ICONS[feat["icon"]](draw, x0 + 1, y0 + 1, icon_w, cell_h - 2)
        tx = x0 + icon_w + 10
        tw = cell_w - icon_w - 18
        ty = y0 + 7
        tag = feat["tag"]
        draw.text((tx, ty), tag, font=font(SANS_B, 9), fill=BLUE)
        lw = draw.textlength(feat["label"] + "  ", font=font(SANS_B, 9))
        draw.rectangle([tx + tw - lw - 8, ty - 1,
                        tx + tw + 2, ty + 11], fill=GREEN)
        draw.text((tx + tw - lw - 4, ty), feat["label"],
                  font=font(SANS_B, 9), fill=WHITE)
        ty += 14
        head_lines = wrap(draw, feat["head"], font(SANS_B, 15), tw)
        ty = draw_lines(draw, tx, ty, head_lines, font(SANS_B, 15), INK, 16)
        ty += 2
        body_lines = wrap(draw, feat["body"], font(SANS, 11), tw)
        ty = draw_lines(draw, tx, ty, body_lines, font(SANS, 11), INK, 12.5)
        draw.text((tx, y0 + cell_h - 14), "Sources: " + feat["src"],
                  font=font(SANS, 9), fill=MUTED)
    return y + 2 * cell_h + 8 + 6


def draw_minis(draw, y):
    y = section_head(draw, MARGIN, y, "THE DAY IN BRIEF  —  12 MORE STORIES")
    cols, rows = 3, 4
    cell_w = CW // cols
    cell_h = 41
    for i, (head, body) in enumerate(MINIS):
        row, col = divmod(i, cols)
        x0 = MARGIN + col * cell_w
        y0 = y + row * cell_h
        draw.rectangle([x0, y0 + 1, x0 + 16, y0 + 15], fill=RED)
        num = "M%d" % (i + 1)
        nw = draw.textlength(num, font=font(SANS_B, 9))
        draw.text((x0 + (16 - nw) / 2, y0 + 2), num, font=font(SANS_B, 9),
                  fill=WHITE)
        tx = x0 + 21
        tw = cell_w - 26
        head_lines = wrap(draw, head, font(SANS_B, 11), tw)
        ty = draw_lines(draw, tx, y0, head_lines, font(SANS_B, 11), INK, 12)
        body_lines = wrap(draw, body, font(SANS, 10), tw)
        draw_lines(draw, tx, ty, body_lines, font(SANS, 10), MUTED, 12)
        if col < cols - 1:
            draw.line([x0 + cell_w - 5, y0 + 2, x0 + cell_w - 5,
                       y0 + cell_h - 4], fill=RULE, width=1)
    return y + rows * cell_h + 4


def draw_map(draw, y):
    y = section_head(draw, MARGIN, y, "WHERE IT HAPPENED  —  11 PLACES ON THE MAP")
    map_x, map_w = MARGIN, 616
    map_h = 142
    leg_x = MARGIN + map_w + 14
    leg_w = W - MARGIN - leg_x
    draw.rectangle([map_x, y, map_x + map_w, y + map_h], fill=SEA,
                   outline=RULE, width=1)

    def project(lon, lat):
        px = map_x + (lon + 180.0) / 360.0 * map_w
        py = y + (75.0 - lat) / 130.0 * map_h
        return px, py

    for poly in CONTINENTS:
        pts = [project(lon, lat) for lon, lat in poly]
        draw.polygon(pts, fill=LAND, outline=LAND_EDGE)

    # pins with a small de-collision pass (Europe/Middle East cluster)
    pts = []
    for num, name, lon, lat, label in PINS:
        pts.append([num, name, label, *project(lon, lat)])
    for _ in range(3):
        for i in range(len(pts)):
            for j in range(i + 1, len(pts)):
                dx = pts[j][3] - pts[i][3]
                dy = pts[j][4] - pts[i][4]
                d2 = dx * dx + dy * dy
                if d2 < 20 * 20 and d2 > 0:
                    d = d2 ** 0.5
                    push = (20 - d) / 2
                    ux, uy = dx / d, dy / d
                    pts[i][3] -= ux * push
                    pts[i][4] -= uy * push
                    pts[j][3] += ux * push
                    pts[j][4] += uy * push
    f_pin = font(SANS_B, 9)
    for num, name, label, px, py in pts:
        draw.ellipse([px - 8, py - 8, px + 8, py + 8], fill=RED,
                     outline=WHITE, width=1)
        s = str(num)
        sw = draw.textlength(s, font=f_pin)
        draw.text((px - sw / 2, py - 6), s, font=f_pin, fill=WHITE)

    # legend
    ly = y + 2
    f_leg = font(SANS, 10)
    f_legb = font(SANS_B, 10)
    for num, name, label, px, py in pts:
        draw.ellipse([leg_x, ly, leg_x + 12, ly + 12], fill=RED)
        s = str(num)
        sw = draw.textlength(s, font=f_pin)
        draw.text((leg_x + (12 - sw) / 2, ly + 1), s, font=f_pin, fill=WHITE)
        draw.text((leg_x + 17, ly), name, font=f_legb, fill=INK)
        nw = draw.textlength(name + "  ", font=f_legb)
        draw.text((leg_x + 17 + nw, ly), "\u2014 " + label, font=f_leg,
                  fill=MUTED)
        ly += 12.5
    return y + map_h + 6


def draw_one_liners(draw, y):
    y = section_head(draw, MARGIN, y, "ALSO ON 22 NOVEMBER  —  33 MORE STORIES")
    cols, rows = 3, 11
    cell_w = CW // cols
    row_h = 11.5
    for i, text in enumerate(ONE_LINERS):
        row, col = divmod(i, cols)
        x0 = MARGIN + col * cell_w
        y0 = y + row * row_h
        num = "%d." % (i + 1)
        draw.text((x0, y0), num, font=font(SANS_B, 10), fill=RED)
        nw = draw.textlength(num + " ", font=font(SANS_B, 10))
        fnt, _ = fit_one_line(draw, text, SANS, 10, cell_w - nw - 6)
        draw.text((x0 + nw, y0), text, font=fnt, fill=INK)
    return y + rows * row_h + 4


def draw_datecheck(draw, y):
    fnt = font(SANS, 10)
    lines = wrap(draw, DATE_CHECK, fnt, CW - 16)
    box_h = len(lines) * 13 + 12
    draw.rectangle([MARGIN, y, W - MARGIN, y + box_h], fill=PANEL2,
                   outline=BLUE, width=1)
    draw_lines(draw, MARGIN + 8, y + 6, lines, fnt, INK, 13)
    return y + box_h + 6


def draw_footer(draw, y):
    fnt = font(SANS, 8)
    lines = wrap(draw, SOURCES, fnt, CW)
    y = draw_lines(draw, MARGIN, y, lines, fnt, MUTED, 10)
    return y


def main():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    y = draw_masthead(draw)
    y = draw_timeline(draw, y)
    y = draw_features(draw, y)
    y = draw_minis(draw, y)
    y = draw_map(draw, y)
    y = draw_one_liners(draw, y)
    y = draw_datecheck(draw, y)
    y = draw_footer(draw, y)
    draw.rectangle([0, 0, W - 1, H - 1], outline=INK, width=2)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, "PNG", optimize=True)
    print("wrote", out, "final y:", y)


if __name__ == "__main__":
    main()
