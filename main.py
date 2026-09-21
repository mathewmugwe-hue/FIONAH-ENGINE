"""
================================================================================
FIONAH ENGINE v2.0 — Football Intelligence & Odds Normalization Heuristic Arch.
Strict Entity Taxonomy · State-Machine Parser Support · Zero Hallucination
Dixon-Coles Bivariate Poisson · Shin De-vigging · Fractional Kelly Acca Builder
================================================================================
"""
import os, re, math, time, json, difflib, urllib.request, urllib.parse, datetime as dt
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

app = FastAPI(title="FIONAH ENGINE", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

DEFAULT_LAMBDA_HOME, DEFAULT_LAMBDA_AWAY, DEFAULT_RHO = 1.38, 1.12, -0.055

INTL_ELO_SEEDS: Dict[str, float] = {
    "argentina": 2150, "france": 2120, "spain": 2115, "england": 2045, "brazil": 2040, "belgium": 1980,
    "netherlands": 1975, "portugal": 1970, "colombia": 1960, "italy": 1950, "uruguay": 1940, "germany": 1935,
    "croatia": 1910, "morocco": 1895, "japan": 1885, "senegal": 1855, "usa": 1845, "united states": 1845,
    "mexico": 1840, "switzerland": 1835, "denmark": 1820, "austria": 1815, "korea republic": 1805,
    "south korea": 1805, "iran": 1795, "australia": 1785, "turkey": 1775, "ukraine": 1770,
    "nigeria": 1760, "egypt": 1750, "ivory coast": 1745, "cameroon": 1730, "algeria": 1725,
    "ghana": 1710, "ecuador": 1830, "chile": 1790, "paraguay": 1765, "peru": 1760,
    "venezuela": 1740, "bolivia": 1610, "kenya": 1395, "uganda": 1410, "tanzania": 1365, "south africa": 1690,
    "saudi arabia": 1720, "qatar": 1680, "tunisia": 1710, "costa rica": 1690, "panama": 1650,
    "honduras": 1620, "jamaica": 1600, "el salvador": 1580, "guatemala": 1560,
}

CLUB_ELO_SEEDS: Dict[str, float] = {
    "manchester city": 2060, "real madrid": 2050, "arsenal": 2005, "liverpool": 1990, "bayern munich": 1985,
    "inter": 1975, "inter milan": 1975, "barcelona": 1975, "bayer leverkusen": 1965, "paris saint-germain": 1955,
    "paris saint germain": 1955, "paris st germain": 1955, "psg": 1955, "atletico madrid": 1930,
    "borussia dortmund": 1910, "dortmund": 1910, "juventus": 1895, "chelsea": 1890, "aston villa": 1880,
    "tottenham": 1870, "tottenham hotspur": 1870, "ac milan": 1865, "newcastle": 1860, "sporting cp": 1860,
    "sporting lisbon": 1860, "manchester united": 1850, "atalanta": 1845, "crvena zvezda": 1770,
    "red star belgrade": 1770, "rb leipzig": 1840, "benfica": 1835, "sl benfica": 1835, "roma": 1830,
    "as roma": 1830, "real sociedad": 1825, "villarreal": 1820, "fc porto": 1820, "porto": 1820,
    "brighton": 1815, "west ham": 1800, "marseille": 1795, "olympique marseille": 1795, "feyenoord": 1785,
    "psv": 1780, "psv eindhoven": 1780, "celtic": 1750, "rangers": 1740, "bournemouth": 1735,
    "afc bournemouth": 1735, "bologna": 1765, "lazio": 1770, "fiorentina": 1765, "acf fiorentina": 1765,
    "napoli": 1860, "torino": 1720, "monaco": 1820, "as monaco": 1820, "lille": 1805, "lyon": 1770,
    "olympique lyon": 1770, "olympique lyonnais": 1770, "rennes": 1730, "stade rennais": 1730,
    "lens": 1775, "sevilla": 1760, "athletic bilbao": 1815, "athletic club": 1815, "real betis": 1765,
    "betis": 1765, "valencia": 1660, "girona": 1805, "eintracht frankfurt": 1785, "eintracht fr": 1785,
    "stuttgart": 1800, "vfb stuttgart": 1800, "wolfsburg": 1735, "freiburg": 1740, "sc freiburg": 1740,
    "werder bremen": 1655, "augsburg": 1650, "hamburg": 1620, "1. fc cologne": 1635, "1. fc koln": 1635,
    "cologne": 1635, "koln": 1635, "borussia (mg)": 1650, "borussia mg": 1650, "borussia monchengladbach": 1650,
    "mainz": 1640, "mainz 05": 1640, "brest": 1735, "stade brestois": 1735, "parma": 1630, "genoa": 1640,
    "auxerre": 1610, "lorient": 1610, "venezia": 1590, "deportivo a coruna": 1570, "deportivo la coruna": 1570,
    "le mans": 1480, "ferencvaros": 1690, "viktoria plzen": 1680, "sparta prague": 1720, "slavia prague": 1735,
    "union saint-gilloise": 1740, "club brugge": 1755, "anderlecht": 1715, "nec nijmegen": 1600,
    "vasco da gama": 1710, "flamengo": 1780, "palmeiras": 1790, "fluminense": 1740, "sao paulo": 1735,
    "corinthians": 1720, "river plate": 1775, "boca juniors": 1760, "wimbledon": 1450, "mk dons": 1460,
    "bastia": 1580, "cannes": 1450, "elana torun": 1420, "lech ii poznan": 1470, "lech poznan": 1690,
    "lecce": 1540, "sassuolo": 1610, "empoli": 1560, "salernitana": 1490,
    # Extended seeds for broader coverage
    "manta": 1520, "manta fc": 1520, "orense": 1510, "orense sc": 1510,
    "chievo": 1580, "ac chievo verona": 1580, "chievo verona": 1580,
    "palmeiras sp": 1790, "se palmeiras sp": 1790, "ituano": 1530, "ituano fc sp": 1530,
    "redditch": 1450, "redditch united": 1450, "warwick": 1420, "rc warwick": 1420,
    "lumezzane": 1480, "ac lumezzane": 1480, "dolomiti bellunesi": 1470,
    "trento": 1490, "ac trento": 1490, "pro vercelli": 1500, "pro vercelli 1892": 1500,
    "treviso": 1460, "treviso fbc 1993": 1460, "desenzano": 1440, "calcio desenzano": 1440,
    "livorno": 1530, "us livorno 1915": 1530, "guidonia": 1450, "guidonia montecelio 1937 fc": 1450,
    "pianese": 1460, "us pianese": 1460, "sambenedettese": 1470, "us sambenedettese": 1470,
    "spezia": 1560, "spezia calcio": 1560, "vis pesaro": 1480, "vis pesaro 1898": 1480,
    "hull": 1680, "hull city": 1680, "leeds": 1700, "leeds united": 1700,
    "sunderland": 1680, "ipswich": 1660, "ipswich town": 1660,
    "everton": 1720, "brentford": 1705, "fulham": 1770, "nottingham forest": 1810,
    "crystal palace": 1755, "coventry": 1620, "coventry city": 1620,
    "malaga": 1640, "alaves": 1660, "deportivo la coruna": 1570, "deportivo": 1570,
    "espanyol": 1680, "getafe": 1660, "rayo vallecano": 1680,
    "real madrid": 2050, "valencia": 1660, "real betis": 1765,
    "newcastle utd": 1860, "newcastle united": 1860,
    "man city": 2060, "man united": 1850, "man utd": 1850,
    "notts county": 1580, "grimsby": 1560, "walsall": 1570, "stevenage": 1590,
    "oldham": 1550, "fleetwood": 1570, "fleetwood town": 1570,
    "tranmere": 1560, "shrewsbury": 1580, "rochdale": 1540,
    "peterborough": 1620, "colchester": 1570, "swindon": 1560, "swindon town": 1560,
    "newport": 1540, "wigan": 1600, "blackpool": 1590,
    "salford city": 1570, "salford": 1570, "sheffield wed": 1600, "sheffield wednesday": 1600,
    "york city": 1530, "york": 1530, "rotherham": 1610,
    "plymouth": 1630, "luton": 1580, "luton town": 1580, "crawley": 1560, "crawley town": 1560,
    "leicester": 1740, "milton keynes dons": 1460,
    "lanus": 1680, "estudiantes": 1700, "estudiantes lp": 1700,
    "cuiaba": 1620, "cuiaba mt": 1620, "nautico": 1600, "nautico pe": 1600,
    "barracas central": 1560, "independiente rivadavia": 1570,
    "nueva chicago": 1550, "patronato": 1560, "patronato parana": 1560,
    "guabira": 1520, "guabira montero": 1520, "san antonio bulo bulo": 1510,
    "criciuma": 1600, "criciuma sc": 1600, "operario": 1580, "operario ferroviario": 1580,
    "central espanol": 1520, "central espanol fc": 1520, "torque": 1530,
    "leon": 1680, "leon w": 1680, "juarez": 1640, "fc juarez": 1640, "fc juarez w": 1640,
    "toluca": 1700, "toluca w": 1700, "uanl": 1720, "uanl w": 1720,
    "atlante": 1580, "atlante fc": 1580, "queretaro": 1620, "queretaro w": 1620,
    "bogota": 1560, "bogota fc": 1560, "barranquilla": 1550, "barranquilla fc": 1550,
    "real cartagena": 1540, "envigado": 1560, "envigado fc": 1560,
    "real soacha": 1520, "real soacha cundinamarca": 1520, "deportes quindio": 1540,
    "nacional ac muriae": 1480, "santarritense": 1460, "santarritense fc mg": 1460,
    "juventus sp": 1500, "uniao sao joao": 1480, "uniao sao joao ec sp": 1480,
    "corinthians w": 1720, "ec bahia": 1640, "ec bahia ba w": 1640,
    "umecit": 1480, "cocle": 1470, "cocle fc": 1470,
    "hb koege": 1520, "hb koege w": 1520, "arsenal w": 2005,
    "juventus w": 1895, "sl benfica w": 1835, "bayern munich w": 1985,
    "manchester city w": 2060, "inter milan w": 1975, "kopparbergs go": 1580, "kopparbergs go w": 1580,
    "real madrid w": 2050, "paris saint germain w": 1955,
    "south korea u23": 1805, "saudi arabia u23": 1720,
    "santa clara u23": 1520, "portimonense u23": 1510,
    "charlton athletic u21": 1560, "sheffield united u21": 1570,
    "wigan athletic u21": 1600, "coventry city u21": 1620,
    "leicester u21": 1740, "fulham u21": 1770, "liverpool u21": 1990,
    "luton town u21": 1580, "ipswich town u21": 1660, "crystal palace u21": 1755,
    "academico viseu u23": 1520, "estoril praia u23": 1530,
    "fardu ferghana": 1480, "bukhoro davlat universiteti": 1460,
    "pfc terdu": 1440, "fk gazalkent": 1430,
    "sanat mes kerman": 1520, "sanat mes kerman fc": 1520, "saipa karadj": 1510,
    "csc dumbravita": 1460, "scolar resita": 1450,
    "dc power": 1480, "dc power fc": 1480, "fort lauderdale": 1470, "fort lauderdale united fc": 1470,
    "havadar": 1500, "besat kermanshah": 1490,
    "skjetten": 1440, "skjervoy": 1430,
    "naft masjed soleyman": 1510, "naft masjed soleyman fc": 1510, "palayesh naft bandar abbas": 1500, "palayesh naft bandar abbas fc": 1500,
    "naft gachsaran": 1490, "ario eslamshahr": 1480,
    "club dr benjamin aceval": 1500, "ca tembetary ypane": 1490,
    "virtus ciseranobergamo": 1460, "s.s.d. virtus ciseranobergamo 1909": 1460,
}

# ─── STRICT ENTITY VALIDATION ────────────────────────────────────────────────
# These patterns identify lines that are DEFINITELY NOT team names
NOT_A_TEAM_PATTERNS = [
    re.compile(r"^\d+(st|nd|rd|th)?\s*half", re.I),           # 1ST HALF, 2ND HALF
    re.compile(r"^live\s*[•·]", re.I),                          # LIVE• 02'
    re.compile(r"^#\d+"),                                        # #6817
    re.compile(r"^\+\d+\s*more", re.I),                         # +183 more
    re.compile(r"^\d+$"),                                        # Pure integers (scores)
    re.compile(r"^\d+\.\d+$"),                                   # Pure decimals (odds)
    re.compile(r"^(1|2|x)$", re.I),                             # Market labels
    re.compile(r"^(1\s*or\s*x|x\s*or\s*2|1\s*or\s*2)$", re.I), # Double chance labels
    re.compile(r"^bet\s*now", re.I),                             # Bet now button
    re.compile(r"^load\s*all", re.I),                            # Load all button
    re.compile(r"^\(\d+\)$"),                                    # (1), (10) match counts
    re.compile(r"/\s*$"),                                        # Country/ separator
    re.compile(r"^(over|under)\s*\d", re.I),                     # Over/Under markets
    re.compile(r"^(draw\s*no\s*bet|double\s*chance|handicap|asian|corner|cards|total|goals|boosted)", re.I),
    re.compile(r"^(home|away|draw)$", re.I),                     # Home/Away/Draw labels
    re.compile(r"^\d{2}/\d{2}/\d{2}"),                          # Date headers
    re.compile(r"^(1x2|x-up)$", re.I),                          # Market type labels
    re.compile(r"^full\s*time", re.I),                           # Full Time
    re.compile(r"^[•\-\*]\s"),                                   # Bullet points
]

# Country and league names that should not be treated as teams
GEOGRAPHIC_NAMES = {
    "ecuador", "paraguay", "italy", "brazil", "england", "internationals",
    "spain", "france", "germany", "argentina", "portugal", "netherlands",
    "colombia", "mexico", "usa", "japan", "korea", "australia", "turkey",
    "nigeria", "egypt", "morocco", "senegal", "ghana", "cameroon",
    "serie a", "serie b", "serie c", "serie d", "segunda division",
    "premier league", "championship", "league one", "league two",
    "la liga", "bundesliga", "ligue 1", "eredivisie", "primeira liga",
    "group a", "group b", "group c", "girone b", "girone a",
    "u20 paulista", "u20", "u21", "u23",
    "southern football league", "premier division central",
    "premier-zoom", "liga-zoom", "premier-zoom turbo",
}

def looks_like_real_team_name(s: str) -> bool:
    """Strict validation: does this string look like a real football team?"""
    if not s or len(s.strip()) < 3:
        return False
    s = s.strip()
    
    # Reject all known non-team patterns
    for p in NOT_A_TEAM_PATTERNS:
        if p.match(s):
            return False
    
    # Reject geographic/league names
    if s.lower() in GEOGRAPHIC_NAMES:
        return False
    
    # Must contain at least one letter
    if not re.search(r"[a-zA-Z]", s):
        return False
    
    # Reject strings that are mostly numbers/symbols
    letters = sum(1 for c in s if c.isalpha())
    if letters < 2:
        return False
    
    # Reject strings with bullet/special chars that indicate UI chrome
    if "•" in s and any(kw in s.lower() for kw in ["half", "live", "min"]):
        return False
    
    return True

def clean_team_name(s: str) -> str:
    """Strip virtual match prefixes and clean up."""
    s = s.strip()
    # Strip Z. and ZTurbo. prefixes (virtual/simulated matches)
    s = re.sub(r"^zturbo\.", "", s, flags=re.I)
    s = re.sub(r"^z\.", "", s, flags=re.I)
    return s.strip()

def normalize_name(s: str) -> str:
    clean = s.strip().lower()
    clean = re.sub(r"\bst\b", "saint", clean)
    clean = re.sub(r"\butd\b", "united", clean)
    clean = re.sub(r"\s+fc\b", "", clean)
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean

def verify_team_entity(team_name: str, domain: str = "domestic") -> Dict[str, Any]:
    """Strict entity verification. No silent faking."""
    cleaned = clean_team_name(team_name)
    
    if not looks_like_real_team_name(cleaned):
        return {"verified": False, "source": "invalid_name", "canonical": team_name, "elo": 0.0,
                "reason": f"'{team_name}' does not look like a real team name"}
    
    clean = normalize_name(cleaned)
    seeds = INTL_ELO_SEEDS if domain == "international" else CLUB_ELO_SEEDS
    canonical_list = list(seeds.keys())
    
    # 1. Exact match
    if clean in canonical_list:
        return {"verified": True, "source": "exact_match", "canonical": clean.title(), "elo": seeds[clean]}
    
    # 2. Fuzzy match
    matches = difflib.get_close_matches(clean, canonical_list, n=1, cutoff=0.70)
    if matches:
        return {"verified": True, "source": "difflib_fuzzy", "canonical": matches[0].title(), "elo": seeds[matches[0]]}
    
    # 3. Substring match
    for k, v in seeds.items():
        if k in clean or clean in k:
            return {"verified": True, "source": "substring", "canonical": k.title(), "elo": v}
    
    # 4. HARD REJECTION - No provisional baseline for unknown names
    # This prevents hallucination. Real models don't invent data.
    return {"verified": False, "source": "no_canonical_match", "canonical": cleaned, "elo": 0.0,
            "reason": f"'{cleaned}' not in team database. Add to CLUB_ELO_SEEDS for coverage."}

def apply_fatigue_and_rest(lambda_base: float, rest_days: int, opponent_rest_days: int) -> float:
    if rest_days <= 3 and opponent_rest_days >= 6: return round(lambda_base * 0.88, 3)
    if rest_days <= 3 and opponent_rest_days <= 3: return round(lambda_base * 0.94, 3)
    return lambda_base

def apply_vaep_injury_adjustment(lambda_base: float, vaep_delta: float) -> float:
    return round(lambda_base * (1.0 + vaep_delta), 3)

def de_vig_odds_shin(odds_h: float, odds_d: float, odds_a: float) -> Tuple[Dict[str, float], float, float]:
    oh, od, oa = max(1.01, odds_h), max(1.01, odds_d), max(1.01, odds_a)
    inv_h, inv_d, inv_a = 1.0 / oh, 1.0 / od, 1.0 / oa
    overround = inv_h + inv_d + inv_a
    z = 0.0
    for _ in range(40):
        def f(zv):
            def q(inv):
                det = max(0.0, zv**2 + 4.0 * (1.0 - zv) * (inv**2 / overround))
                return (math.sqrt(det) - zv) / (2.0 * (1.0 - zv)) if zv < 0.999 else inv / overround
            return q(inv_h) + q(inv_d) + q(inv_a) - 1.0
        fz = f(z)
        if abs(fz) < 1e-6: break
        dfz = (f(z + 1e-5) - fz) / 1e-5
        if abs(dfz) < 1e-12: break
        z = max(0.0, min(0.40, z - fz / dfz))
    def final_p(inv):
        det = max(0.0, z**2 + 4.0 * (1.0 - z) * (inv**2 / overround))
        return (math.sqrt(det) - z) / (2.0 * (1.0 - z)) if z < 0.999 else inv / overround
    ph = max(0.01, final_p(inv_h))
    pd = max(0.01, final_p(inv_d))
    pa = max(0.01, final_p(inv_a))
    tot = ph + pd + pa
    return {"1": ph / tot, "X": pd / tot, "2": pa / tot}, overround - 1.0, z

def dixon_coles_tau(x: int, y: int, lambda_h: float, mu_a: float, rho: float) -> float:
    if x == 0 and y == 0: return max(0.0, 1.0 - lambda_h * mu_a * rho)
    if x == 0 and y == 1: return 1.0 + lambda_h * rho
    if x == 1 and y == 0: return 1.0 + mu_a * rho
    if x == 1 and y == 1: return 1.0 - rho
    return 1.0

def poisson_prob(k: int, lambd: float) -> float:
    if lambd <= 0: return 1.0 if k == 0 else 0.0
    return (math.exp(-lambd) * (lambd ** k)) / math.factorial(k)

def calculate_dixon_coles_grid(lambda_h: float, mu_a: float, rho: float = -0.055, max_goals: int = 8) -> Dict[str, Any]:
    prob_matrix = [[0.0 for _ in range(max_goals + 1)] for _ in range(max_goals + 1)]
    p_home, p_draw, p_away, p_btts, p_over15, p_over25 = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
    for x in range(max_goals + 1):
        px = poisson_prob(x, lambda_h)
        for y in range(max_goals + 1):
            py = poisson_prob(y, mu_a)
            tau = dixon_coles_tau(x, y, lambda_h, mu_a, rho)
            p = max(0.0, px * py * tau)
            prob_matrix[x][y] = p
            if x > y: p_home += p
            elif x == y: p_draw += p
            else: p_away += p
            if x > 0 and y > 0: p_btts += p
            if (x + y) > 1: p_over15 += p
            if (x + y) > 2: p_over25 += p
    total = sum(sum(row) for row in prob_matrix)
    if total > 0:
        p_home /= total; p_draw /= total; p_away /= total
        p_btts /= total; p_over15 /= total; p_over25 /= total
    return {"p_home": p_home, "p_draw": p_draw, "p_away": p_away, "p_btts": p_btts,
            "p_over15": p_over15, "p_over25": p_over25, "p_1X": p_home + p_draw,
            "p_X2": p_away + p_draw, "lambda_home": lambda_h, "lambda_away": mu_a}

def evaluate_1x2_value(p_h, p_d, p_a, fair_h, fair_d, fair_a, market_h, market_d, market_a, total_xg, home, away):
    eff_h = market_h if (market_h and market_h > 1.05) else fair_h
    eff_d = market_d if (market_d and market_d > 1.05) else fair_d
    eff_a = market_a if (market_a and market_a > 1.05) else fair_a
    ev_h, ev_d, ev_a = (p_h * eff_h) - 1.0, (p_d * eff_d) - 1.0, (p_a * eff_a) - 1.0
    is_stalemate = (total_xg <= 2.40 and abs(p_h - p_a) <= 0.16)
    is_tactical_draw = (p_d >= 0.275 and eff_d >= 2.90 and (ev_d >= -0.04 or is_stalemate))
    if is_tactical_draw and (ev_d >= 0.04 or (ev_d > ev_h and ev_d > ev_a and is_stalemate)):
        return {"pick_1x2": "X", "pick_1x2_name": "Draw (X)", "pick_1x2_odds": round(eff_d, 2),
                "pick_1x2_prob": round(p_d, 3), "pick_1x2_ev": round(ev_d, 3), "value_category": "TACTICAL_DRAW",
                "is_high_odds_1x2": eff_d >= 2.50, "high_odds_reason": f"Tactical Draw: {p_d*100:.1f}% density."}
    if p_a >= 0.27 and eff_a >= 2.65 and ev_a >= max(ev_h, ev_d):
        return {"pick_1x2": "2", "pick_1x2_name": f"{away} (2)", "pick_1x2_odds": round(eff_a, 2),
                "pick_1x2_prob": round(p_a, 3), "pick_1x2_ev": round(ev_a, 3), "value_category": "VALUE_UNDERDOG",
                "is_high_odds_1x2": True, "high_odds_reason": f"Value Away: {p_a*100:.1f}% at {eff_a:.2f}."}
    if p_h >= 0.28 and eff_h >= 2.50 and ev_h >= max(ev_d, ev_a):
        return {"pick_1x2": "1", "pick_1x2_name": f"{home} (1)", "pick_1x2_odds": round(eff_h, 2),
                "pick_1x2_prob": round(p_h, 3), "pick_1x2_ev": round(ev_h, 3), "value_category": "VALUE_UNDERDOG",
                "is_high_odds_1x2": True, "high_odds_reason": f"Value Home: {p_h*100:.1f}% at {eff_h:.2f}."}
    if p_h >= p_d and p_h >= p_a:
        return {"pick_1x2": "1", "pick_1x2_name": f"{home} (1)", "pick_1x2_odds": round(eff_h, 2),
                "pick_1x2_prob": round(p_h, 3), "pick_1x2_ev": round(ev_h, 3),
                "value_category": "VALUE_FAVORITE" if p_h >= 0.50 else "BALANCED",
                "is_high_odds_1x2": eff_h >= 2.50, "high_odds_reason": None}
    if p_a >= p_h and p_a >= p_d:
        return {"pick_1x2": "2", "pick_1x2_name": f"{away} (2)", "pick_1x2_odds": round(eff_a, 2),
                "pick_1x2_prob": round(p_a, 3), "pick_1x2_ev": round(ev_a, 3),
                "value_category": "VALUE_FAVORITE" if p_a >= 0.48 else "BALANCED",
                "is_high_odds_1x2": eff_a >= 2.50, "high_odds_reason": None}
    return {"pick_1x2": "X", "pick_1x2_name": "Draw (X)", "pick_1x2_odds": round(eff_d, 2),
            "pick_1x2_prob": round(p_d, 3), "pick_1x2_ev": round(ev_d, 3), "value_category": "TACTICAL_DRAW",
            "is_high_odds_1x2": eff_d >= 2.50, "high_odds_reason": f"Symmetrical → {p_d*100:.1f}% draw."}

class FixtureInput(BaseModel):
    id: Optional[str] = None
    home: str
    away: str
    league: Optional[str] = None
    odds_home: Optional[float] = None
    odds_draw: Optional[float] = None
    odds_away: Optional[float] = None
    rest_days_home: int = 5
    rest_days_away: int = 5
    vaep_delta_home: float = 0.0
    vaep_delta_away: float = 0.0

class BatchPredictionRequest(BaseModel):
    fixtures: List[FixtureInput]

def predict_fixture(f: FixtureInput) -> Dict[str, Any]:
    try:
        domain = "international" if any(k in (f.league or "").lower() for k in ["world cup", "euro", "copa", "nations"]) else "domestic"
        v_home = verify_team_entity(f.home, domain)
        v_away = verify_team_entity(f.away, domain)
        
        if not (v_home["verified"] and v_away["verified"]):
            return {"id": f.id or f"{f.home}-{f.away}", "home": f.home, "away": f.away, "verified": False,
                    "verification": {"home": v_home, "away": v_away},
                    "reject_reason": f"Home: {v_home.get('reason', 'Unverified')}. Away: {v_away.get('reason', 'Unverified')}",
                    "primary_pick": "NO BET", "confidence_tier": "REJECTED", "acca_eligible": False}
        
        elo_h, elo_a = v_home["elo"], v_away["elo"]
        elo_diff = (elo_h + 60.0) - elo_a
        lambda_h = DEFAULT_LAMBDA_HOME * (10.0 ** (elo_diff / 1000.0))
        lambda_a = DEFAULT_LAMBDA_AWAY * (10.0 ** (-elo_diff / 1000.0))
        lambda_h = apply_fatigue_and_rest(lambda_h, f.rest_days_home, f.rest_days_away)
        lambda_a = apply_fatigue_and_rest(lambda_a, f.rest_days_away, f.rest_days_home)
        lambda_h = apply_vaep_injury_adjustment(lambda_h, f.vaep_delta_home)
        lambda_a = apply_vaep_injury_adjustment(lambda_a, f.vaep_delta_away)
        
        has_odds = (f.odds_home and f.odds_draw and f.odds_away and f.odds_home > 1.05)
        fair_market, margin, z_shin = de_vig_odds_shin(f.odds_home, f.odds_draw, f.odds_away) if has_odds else (None, 0.05, 0.02)
        dc = calculate_dixon_coles_grid(lambda_h, lambda_a, rho=DEFAULT_RHO)
        
        if fair_market:
            p_home = (dc["p_home"] * 0.35) + (fair_market["1"] * 0.65)
            p_draw = (dc["p_draw"] * 0.35) + (fair_market["X"] * 0.65)
            p_away = (dc["p_away"] * 0.35) + (fair_market["2"] * 0.65)
            tot = p_home + p_draw + p_away
            p_home /= tot; p_draw /= tot; p_away /= tot
        else:
            p_home, p_draw, p_away = dc["p_home"], dc["p_draw"], dc["p_away"]
        
        fair_odds_h = round(1.0 / max(0.01, p_home), 2)
        fair_odds_d = round(1.0 / max(0.01, p_draw), 2)
        fair_odds_a = round(1.0 / max(0.01, p_away), 2)
        val_1x2 = evaluate_1x2_value(p_home, p_draw, p_away, fair_odds_h, fair_odds_d, fair_odds_a,
                                     f.odds_home, f.odds_draw, f.odds_away, lambda_h + lambda_a, f.home, f.away)
        
        primary_pick, pick_odds, primary_prob, tier = "NO BET", 1.35, 0.0, "CANDIDATE"
        if p_home >= 0.64:
            primary_pick, pick_odds, primary_prob = f"{f.home} (1)", f.odds_home or fair_odds_h, p_home
            tier = "ELITE" if p_home >= 0.72 else "STRONG"
        elif p_away >= 0.60:
            primary_pick, pick_odds, primary_prob = f"{f.away} (2)", f.odds_away or fair_odds_a, p_away
            tier = "ELITE" if p_away >= 0.68 else "STRONG"
        else:
            p_1x, p_x2 = p_home + p_draw, p_away + p_draw
            if p_1x >= 0.72 and p_home >= p_away:
                primary_pick, pick_odds, primary_prob = f"{f.home} or Draw (1X)", max(1.20, min(1.80, round(1.0/p_1x, 2))), p_1x
                tier = "STRONG" if p_1x >= 0.78 else "CANDIDATE"
            elif p_x2 >= 0.70 and p_away >= p_home:
                primary_pick, pick_odds, primary_prob = f"{f.away} or Draw (X2)", max(1.20, min(1.80, round(1.0/p_x2, 2))), p_x2
                tier = "STRONG" if p_x2 >= 0.76 else "CANDIDATE"
            else:
                primary_pick, pick_odds, primary_prob = (f"{f.home} or Draw (1X)", 1.38, p_1x) if p_1x >= p_x2 else (f"{f.away} or Draw (X2)", 1.40, p_x2)

        return {
            "id": f.id or f"{f.home}-{f.away}", "home": f.home, "away": f.away, "league": f.league or "Universal",
            "verified": True, "verification": {"home": v_home, "away": v_away},
            "elo_home": elo_h, "elo_away": elo_a, "elo_gap": round(elo_diff - 60.0, 1),
            "lambda_home": round(lambda_h, 2), "lambda_away": round(lambda_a, 2),
            "p_home": round(p_home, 3), "p_draw": round(p_draw, 3), "p_away": round(p_away, 3),
            "p_1X": round(p_home + p_draw, 3), "p_X2": round(p_away + p_draw, 3),
            "p_over15": round(dc["p_over15"], 3), "p_over25": round(dc["p_over25"], 3), "p_btts": round(dc["p_btts"], 3),
            "fair_odds_home": fair_odds_h, "fair_odds_draw": fair_odds_d, "fair_odds_away": fair_odds_a,
            "pick_1x2": val_1x2["pick_1x2"], "pick_1x2_name": val_1x2["pick_1x2_name"],
            "pick_1x2_odds": val_1x2["pick_1x2_odds"], "pick_1x2_ev": val_1x2["pick_1x2_ev"],
            "value_category": val_1x2["value_category"], "is_high_odds_1x2": val_1x2["is_high_odds_1x2"],
            "high_odds_reason": val_1x2["high_odds_reason"],
            "primary_pick": primary_pick, "pick_odds": pick_odds, "primary_win_prob": primary_prob,
            "confidence_tier": tier, "adj_edge": round(max(0.0, (primary_prob * pick_odds) - 1.0), 3),
            "acca_eligible": primary_prob >= 0.58,
            "reason": f"DC xG: {lambda_h:.2f} vs {lambda_a:.2f}. Elo: {elo_h:.0f} vs {elo_a:.0f}."
        }
    except Exception as e:
        return {"id": f.id or f"{f.home}-{f.away}", "home": f.home, "away": f.away, "verified": False,
                "verification": {"home": {"source": "error"}, "away": {"source": "error"}},
                "reject_reason": f"Error: {str(e)[:100]}", "primary_pick": "NO BET", "confidence_tier": "REJECTED", "acca_eligible": False}

def build_accumulators(predictions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    actionable = [p for p in predictions if p.get("verified") and p.get("acca_eligible")]
    sorted_cands = sorted(actionable, key=lambda x: x.get("primary_win_prob", 0.0), reverse=True)
    def create_acca(name, target_min_odds, max_legs=8):
        legs, used_teams, comb_odds, comb_prob = [], set(), 1.0, 1.0
        for cand in sorted_cands:
            h, a = cand["home"].lower(), cand["away"].lower()
            if h in used_teams or a in used_teams: continue
            legs.append(cand); used_teams.add(h); used_teams.add(a)
            comb_odds *= cand["pick_odds"]; comb_prob *= cand["primary_win_prob"]
            if comb_odds >= target_min_odds and len(legs) >= 2: break
            if len(legs) >= max_legs: break
        if comb_odds < 3.00 or len(legs) < 2: return None
        ev = (comb_prob * comb_odds) - 1.0
        b = comb_odds - 1.0; q = 1.0 - comb_prob
        kelly_stake = max(0.0, ((b * comb_prob) - q) / b * 0.25)
        return {"name": f"{name} (≥{target_min_odds:.2f})", "combined_odds": round(comb_odds, 2),
                "combined_model_prob": round(comb_prob * 100, 1), "expected_value": round(ev * 100, 1),
                "fractional_kelly_stake_pct": round(kelly_stake * 100, 2), "n_legs": len(legs),
                "legs": [{"home": l["home"], "away": l["away"], "pick": l["primary_pick"],
                          "odds": l["pick_odds"], "prob": l["primary_win_prob"]} for l in legs]}
    accas = []
    for name, target, max_l in [("Banker", 3.00, 4), ("Growth", 6.00, 5), ("Power", 10.00, 6)]:
        a = create_acca(name, target, max_l)
        if a: accas.append(a)
    return accas

@app.get("/")
def serve_frontend():
    html_path = Path(__file__).parent / "index.html"
    if html_path.exists(): return FileResponse(html_path, media_type="text/html")
    return JSONResponse({"engine": "FIONAH ENGINE v2.0", "status": "online"})

@app.get("/api/health")
def health(): return {"status": "ok", "version": "2.0.0", "timestamp": dt.datetime.utcnow().isoformat()}

@app.post("/api/predict")
def predict_endpoint(fixture: FixtureInput):
    try: return predict_fixture(fixture)
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/batch-predict")
def batch_predict(req: BatchPredictionRequest):
    try:
        predictions = [predict_fixture(f) for f in req.fixtures]
        verified = [p for p in predictions if p.get("verified")]
        unverified = [p for p in predictions if not p.get("verified")]
        return {"engine": "FIONAH-v2.0", "count": len(predictions), "verified_count": len(verified),
                "rejected_count": len(unverified), "predictions": verified, "unverified_fixtures": unverified,
                "accumulators": build_accumulators(predictions),
                "guardrails": ["no_llm_math", "no_provisional_baseline", "strict_entity_check"]}
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
