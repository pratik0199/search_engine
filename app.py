"""
SHIFT REPORT SEARCH  —  Streamlit Web App
==========================================
Run:  streamlit run app.py
Then open browser at  http://localhost:8501
"""

import os, re, glob, sqlite3, io
from datetime import datetime
import streamlit as st
import pandas as pd
from docx import Document
from docx.oxml.ns import qn
from docx.table import Table
from docx.text.paragraph import Paragraph

# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────
DEFAULT_FOLDER = r"C:\Users\psonawane\Documents\shift_report"
DB_FILE        = "shift_reports.db"

# ─────────────────────────────────────────
# STEM TABLE
# ─────────────────────────────────────────
_STEMS = {
    "stoke":"strok","stokes":"strok","stroke":"strok","strokes":"strok","stroked":"strok",
    "trip":"trip","trips":"trip","tripped":"trip","tripping":"trip",
    "leak":"leak","leaks":"leak","leaked":"leak","leaking":"leak",
    "seal":"seal","seals":"seal","sealed":"seal","sealing":"seal",
    "fire":"fire","fires":"fire","fired":"fire","firing":"fire",
    "pump":"pump","pumps":"pump","pumped":"pump","pumping":"pump",
    "start":"start","starts":"start","started":"start","starting":"start",
    "stop":"stop","stops":"stop","stopped":"stop","stopping":"stop",
    "shutdown":"shutdown",
    "vibration":"vibrat","vibrations":"vibrat","vibrating":"vibrat","vibrate":"vibrat",
    "fail":"fail","fails":"fail","failed":"fail","failure":"fail","failures":"fail",
    "block":"block","blocks":"block","blocked":"block","blocking":"block",
    "bypass":"bypass","bypassed":"bypass","bypasses":"bypass",
    "replace":"replac","replaced":"replac","replacing":"replac","replacement":"replac",
    "repair":"repair","repairs":"repair","repaired":"repair","repairing":"repair",
    "clean":"clean","cleans":"clean","cleaned":"clean","cleaning":"clean",
    "install":"install","installs":"install","installed":"install","installing":"install",
    "swap":"swap","swaps":"swap","swapped":"swap","swapping":"swap",
    "drain":"drain","drains":"drain","drained":"drain","draining":"drain",
    "loto":"loto",
}

def _stem(w):
    w = w.lower().strip()
    if w in _STEMS: return _STEMS[w]
    for suf in ["ing","tion","tions","ment","ed","er","es","s","d"]:
        if w.endswith(suf) and len(w)-len(suf) >= 3:
            return w[:-len(suf)]
    return w

def _norm(text):
    if not text: return ""
    text = str(text).lower().strip()
    text = text.replace('\xa0',' ').replace('\u200b',' ')
    text = re.sub(r'\b([a-z]{1,3})-(\d{1,4})-?([a-z]?)\b',
                  lambda m: m.group(1)+m.group(2)+m.group(3), text)
    text = re.sub(r'[^a-z0-9\s]',' ', text)
    text = re.sub(r'\s+',' ', text).strip()
    return text

def _is_equip(w):
    return bool(re.match(r'^[a-z]{1,3}\d+[a-z]?$', w))

# ─────────────────────────────────────────
# DOCX PARSING
# ─────────────────────────────────────────
def _iter_blocks(doc):
    for child in doc.element.body.iterchildren():
        if   child.tag == qn('w:p'):   yield Paragraph(child, doc)
        elif child.tag == qn('w:tbl'): yield Table(child, doc)

def _is_header(table):
    for row in table.rows:
        for cell in row.cells:
            if re.match(r'Date:\s*\d', cell.text.strip(), re.I): return True
    return False

def _get_ds(table):
    d = s = ""
    for row in table.rows:
        for cell in row.cells:
            t = cell.text.strip()
            m = re.match(r'Date:\s*(.+)',  t, re.I)
            if m: d = m.group(1).strip()
            m = re.match(r'Shift:\s*(.+)', t, re.I)
            if m: s = m.group(1).strip()
    return d, s

def _pd(raw):
    for fmt in ["%m-%d-%Y","%m/%d/%Y","%m/%d/%y","%m-%d-%y","%Y-%m-%d"]:
        try: return datetime.strptime(raw.strip(), fmt).strftime("%Y-%m-%d")
        except: pass
    return raw.strip()

def _ps(raw):
    r = raw.lower()
    if "day" in r:   return "Day"
    if "night" in r: return "Night"
    return "Unknown"

def _tlines(table):
    seen = set(); out = []
    for row in table.rows:
        for cell in row.cells:
            t = cell.text.strip()
            if t and len(t) > 3 and t not in seen:
                seen.add(t); out.append(t)
    return out

def extract_docx(fpath):
    try: doc = Document(fpath)
    except: return []
    fname = os.path.basename(fpath)
    recs = []; cd = cs = ""; buf = []
    def flush():
        if cd:
            for line in buf:
                line = line.strip()
                if len(line) > 3:
                    recs.append({"date":cd,"shift":cs,"sentence":line,
                                 "norm":_norm(line),"src":fname})
    for block in _iter_blocks(doc):
        if isinstance(block, Table):
            if _is_header(block):
                flush(); buf = []
                d, s = _get_ds(block)
                cd = _pd(d); cs = _ps(s)
            else: buf.extend(_tlines(block))
        elif isinstance(block, Paragraph):
            t = block.text.strip()
            if t and len(t) > 3: buf.append(t)
    flush(); return recs

# ─────────────────────────────────────────
# DATABASE
# ─────────────────────────────────────────
def build_db(folder):
    files = sorted(
        glob.glob(os.path.join(folder, "*.docx")) +
        glob.glob(os.path.join(folder, "*.DOCX"))
    )
    if not files: return 0, []
    all_rows = []; file_stats = []
    for fpath in files:
        recs = extract_docx(fpath)
        all_rows.extend(recs)
        file_stats.append(f"{os.path.basename(fpath)}  —  {len(recs):,} sentences")
    if not all_rows: return 0, []
    conn = sqlite3.connect(DB_FILE)
    conn.execute("DROP TABLE IF EXISTS sr")
    conn.execute("CREATE TABLE sr (date TEXT, shift TEXT, sentence TEXT, norm TEXT, src TEXT)")
    conn.executemany("INSERT INTO sr VALUES(?,?,?,?,?)",
        [(r["date"],r["shift"],r["sentence"],r["norm"],r["src"]) for r in all_rows])
    conn.execute("CREATE INDEX ix_d ON sr(date)")
    conn.commit(); conn.close()
    return len(all_rows), file_stats

def db_exists(): return os.path.exists(DB_FILE)

def db_count():
    if not db_exists(): return 0
    conn = sqlite3.connect(DB_FILE)
    n = conn.execute("SELECT COUNT(*) FROM sr").fetchone()[0]
    conn.close(); return n

# ─────────────────────────────────────────
# SEARCH
# ─────────────────────────────────────────
def _token_matches(qw, sw, ss):
    qn2 = _norm(qw); qs = _stem(qn2)
    if _is_equip(qn2):
        has_suffix = bool(re.match(r'^[a-z]{1,3}\d+[a-z]$', qn2))
        return qn2 in sw if has_suffix else any(w.startswith(qn2) for w in sw)
    return qs in ss

def search(raw_query, date_from=None, date_to=None, shift_filter=None):
    if not db_exists(): return pd.DataFrame()
    exact     = [p.strip().lower() for p in re.findall(r'"([^"]+)"', raw_query)]
    remainder = re.sub(r'"[^"]+"','', raw_query).strip()
    words     = [w for w in remainder.split() if w]
    if not exact and not words: return pd.DataFrame()
    conn   = sqlite3.connect(DB_FILE)
    q      = "SELECT date, shift, sentence, norm FROM sr WHERE 1=1"
    params = []
    if date_from: q += " AND date >= ?"; params.append(date_from)
    if date_to:   q += " AND date <= ?"; params.append(date_to)
    if shift_filter and shift_filter != "All":
        q += " AND shift = ?"; params.append(shift_filter)
    q += " ORDER BY date, shift"
    rows = conn.execute(q, params).fetchall()
    conn.close()
    results = []
    for date, shift, sentence, norm in rows:
        if not norm: continue
        sw = norm.split(); ss = [_stem(w) for w in sw]; sl = sentence.lower()
        ok = True
        for ph in exact:
            if ph not in sl: ok = False; break
        if not ok: continue
        for w in words:
            if not _token_matches(w, sw, ss): ok = False; break
        if ok: results.append({"Date":date,"Shift":shift,"Matched Sentence":sentence})
    return pd.DataFrame(results)

def highlight_html(text, raw_query):
    phrases = re.findall(r'"([^"]+)"', raw_query)
    remainder = re.sub(r'"[^"]+"','', raw_query)
    tokens = phrases + remainder.split()
    out = text
    for tok in tokens:
        tok = tok.strip()
        if tok:
            out = re.sub(f"(?i){re.escape(tok)}",
                         lambda m: f'<mark class="hl">{m.group()}</mark>', out)
    return out

# ═══════════════════════════════════════════
# STREAMLIT UI  —  Professional Redesign
# ═══════════════════════════════════════════
st.set_page_config(
    page_title="Shift Report Search",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
/* ── Fonts ─────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

:root {
    --bg:          #F5F6F8;
    --surface:     #FFFFFF;
    --surface2:    #EDEEF1;
    --border:      #D8DAE0;
    --border-dark: #B8BBCA;
    --text-primary:#1A1D27;
    --text-secondary:#5A5F7A;
    --text-muted:  #9096B0;
    --accent:      #1B4F8A;
    --accent-light:#EAF0FA;
    --accent-hover:#153D6E;
    --success:     #1A6640;
    --success-bg:  #EAF5EF;
    --warning:     #7A4A00;
    --warning-bg:  #FFF7EA;
    --error:       #7A1B1B;
    --error-bg:    #FFF0F0;
    --highlight:   #F0C33C;
    --day-color:   #1B4F8A;
    --night-color: #3D2D6E;
    --radius:      6px;
    --shadow:      0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.04);
    --shadow-md:   0 4px 12px rgba(0,0,0,0.08);
}

/* ── Base ───────────────────────────────────────────────── */
html, body, [class*="css"], .stApp {
    font-family: 'DM Sans', sans-serif !important;
    background-color: var(--bg) !important;
    color: var(--text-primary) !important;
}

/* ── Hide Streamlit chrome ──────────────────────────────── */
#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding-top: 0 !important;
    padding-bottom: 2rem !important;
    max-width: 100% !important;
}

/* ── Sidebar ────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background-color: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
    box-shadow: none !important;
}
section[data-testid="stSidebar"] .block-container {
    padding: 2rem 1.25rem !important;
}

/* ── Page header band ───────────────────────────────────── */
.page-header {
    background: var(--accent);
    padding: 22px 36px 22px 36px;
    margin-bottom: 28px;
    display: flex;
    align-items: baseline;
    gap: 16px;
}
.page-header-title {
    font-family: 'DM Sans', sans-serif;
    font-weight: 600;
    font-size: 1.35rem;
    color: #FFFFFF;
    letter-spacing: 0.01em;
    margin: 0;
}
.page-header-sub {
    font-size: 0.82rem;
    color: rgba(255,255,255,0.65);
    font-weight: 400;
    letter-spacing: 0.02em;
    text-transform: uppercase;
}

/* ── Sidebar section headings ───────────────────────────── */
.sidebar-heading {
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    font-weight: 500;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin: 0 0 10px 0;
    padding-bottom: 6px;
    border-bottom: 1px solid var(--border);
}

/* ── Stat cards ─────────────────────────────────────────── */
.stat-row { display: flex; gap: 14px; margin-bottom: 24px; }
.stat-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 16px 20px;
    flex: 1;
    box-shadow: var(--shadow);
}
.stat-value {
    font-family: 'DM Mono', monospace;
    font-size: 1.6rem;
    font-weight: 500;
    color: var(--accent);
    line-height: 1;
    margin-bottom: 6px;
}
.stat-label {
    font-size: 0.72rem;
    font-weight: 500;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--text-muted);
}
.stat-ready .stat-value   { color: var(--success); }
.stat-ready .stat-label   { color: var(--text-muted); }

/* ── Search input ───────────────────────────────────────── */
.search-label {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--text-secondary);
    margin-bottom: 6px;
}
div[data-testid="stTextInput"] input {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.97rem !important;
    background: var(--surface) !important;
    color: var(--text-primary) !important;
    border: 1.5px solid var(--border-dark) !important;
    border-radius: var(--radius) !important;
    padding: 11px 14px !important;
    box-shadow: var(--shadow) !important;
    transition: border-color 0.15s, box-shadow 0.15s !important;
}
div[data-testid="stTextInput"] input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(27,79,138,0.12) !important;
    outline: none !important;
}
div[data-testid="stTextInput"] input::placeholder { color: var(--text-muted) !important; }

/* ── Buttons ────────────────────────────────────────────── */
div[data-testid="stButton"] > button {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.83rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.03em !important;
    background: var(--accent) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: var(--radius) !important;
    padding: 9px 18px !important;
    width: 100% !important;
    transition: background 0.15s !important;
    box-shadow: var(--shadow) !important;
}
div[data-testid="stButton"] > button:hover {
    background: var(--accent-hover) !important;
}

/* ── Download button ────────────────────────────────────── */
div[data-testid="stDownloadButton"] > button {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.83rem !important;
    font-weight: 500 !important;
    background: var(--surface) !important;
    color: var(--accent) !important;
    border: 1.5px solid var(--accent) !important;
    border-radius: var(--radius) !important;
    padding: 8px 18px !important;
    transition: background 0.15s !important;
}
div[data-testid="stDownloadButton"] > button:hover {
    background: var(--accent-light) !important;
}

/* ── Select / Date inputs ───────────────────────────────── */
div[data-baseweb="select"] > div {
    background: var(--surface) !important;
    border: 1.5px solid var(--border-dark) !important;
    border-radius: var(--radius) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.88rem !important;
}
div[data-baseweb="select"] span { color: var(--text-primary) !important; }
div[data-testid="stDateInput"] input {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.85rem !important;
    background: var(--surface) !important;
    border: 1.5px solid var(--border-dark) !important;
    border-radius: var(--radius) !important;
    color: var(--text-primary) !important;
}

/* ── Sidebar text inputs ────────────────────────────────── */
section[data-testid="stSidebar"] div[data-testid="stTextInput"] input {
    font-size: 0.83rem !important;
}

/* ── Alerts ─────────────────────────────────────────────── */
div[data-testid="stAlert"] {
    border-radius: var(--radius) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.88rem !important;
}

/* ── Result counter header ──────────────────────────────── */
.results-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 0 12px 0;
    margin-bottom: 16px;
    border-bottom: 1px solid var(--border);
}
.results-count {
    font-size: 0.85rem;
    font-weight: 600;
    color: var(--text-secondary);
    letter-spacing: 0.02em;
}
.results-count span {
    font-family: 'DM Mono', monospace;
    font-size: 1.1rem;
    color: var(--accent);
    font-weight: 500;
}

/* ── Result cards ───────────────────────────────────────── */
.result-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 14px 18px;
    margin-bottom: 8px;
    box-shadow: var(--shadow);
    transition: box-shadow 0.15s;
}
.result-card:hover { box-shadow: var(--shadow-md); }
.result-meta {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 8px;
}
.meta-date {
    font-family: 'DM Mono', monospace;
    font-size: 0.77rem;
    color: var(--text-secondary);
    font-weight: 500;
    letter-spacing: 0.04em;
}
.meta-divider {
    width: 1px;
    height: 12px;
    background: var(--border);
}
.badge {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    padding: 2px 8px;
    border-radius: 3px;
}
.badge-day {
    background: var(--accent-light);
    color: var(--day-color);
}
.badge-night {
    background: #EEEBF8;
    color: var(--night-color);
}
.badge-unknown {
    background: var(--surface2);
    color: var(--text-muted);
}
.result-text {
    font-size: 0.9rem;
    line-height: 1.6;
    color: var(--text-primary);
}
.result-text mark.hl {
    background: #FFF3C4;
    color: #5C3D00;
    border-radius: 2px;
    padding: 1px 3px;
    font-weight: 600;
}

/* ── Tip table ──────────────────────────────────────────── */
.tip-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.8rem;
    margin-top: 4px;
}
.tip-table tr { border-bottom: 1px solid var(--border); }
.tip-table tr:last-child { border-bottom: none; }
.tip-table td { padding: 6px 4px; color: var(--text-secondary); vertical-align: top; }
.tip-table td:first-child {
    font-family: 'DM Mono', monospace;
    font-size: 0.77rem;
    color: var(--accent);
    font-weight: 500;
    white-space: nowrap;
    padding-right: 10px;
    width: 110px;
}

/* ── No result / status messages ────────────────────────── */
.status-msg {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 20px 24px;
    text-align: center;
    color: var(--text-secondary);
    font-size: 0.9rem;
}
.status-msg strong { color: var(--text-primary); }

/* ── Section divider ────────────────────────────────────── */
.divider {
    border: none;
    border-top: 1px solid var(--border);
    margin: 20px 0;
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════
with st.sidebar:

    # Brand
    st.markdown("""
    <div style="margin-bottom:28px;">
        <div style="font-family:'DM Mono',monospace; font-size:0.68rem;
                    letter-spacing:0.14em; text-transform:uppercase;
                    color:#9096B0; margin-bottom:4px;">
            Petrochemical Operations
        </div>
        <div style="font-family:'DM Sans',sans-serif; font-size:1.05rem;
                    font-weight:600; color:#1A1D27; letter-spacing:0.01em;">
            Shift Report Search
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Setup
    st.markdown('<div class="sidebar-heading">Data Source</div>', unsafe_allow_html=True)
    folder = st.text_input(
        "Reports folder path",
        value=DEFAULT_FOLDER,
        label_visibility="collapsed",
        placeholder="Folder path..."
    )
    st.caption(f"Folder path: {folder}")

    if st.button("Build / Rebuild Database"):
        with st.spinner("Indexing shift reports..."):
            n, stats = build_db(folder)
        if n:
            st.success(f"{n:,} sentences indexed across {len(stats)} file(s)")
            for s in stats: st.caption(s)
            st.cache_data.clear()
        else:
            st.error("No .docx files found in the specified folder.")

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # Filters
    st.markdown('<div class="sidebar-heading">Search Filters</div>', unsafe_allow_html=True)
    shift_f  = st.selectbox("Shift", ["All", "Day", "Night"], label_visibility="visible")
    col1, col2 = st.columns(2)
    with col1:  date_from = st.date_input("From", value=None)
    with col2:  date_to   = st.date_input("To",   value=None)

    df_str = str(date_from) if date_from else None
    dt_str = str(date_to)   if date_to   else None
    sh_str = None if shift_f == "All" else shift_f

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # Search tips
    st.markdown('<div class="sidebar-heading">Search Syntax</div>', unsafe_allow_html=True)
    st.markdown("""
<table class="tip-table">
  <tr><td>fire</td><td>Single keyword</td></tr>
  <tr><td>trip</td><td>Matches trip, tripped, tripping</td></tr>
  <tr><td>stroke</td><td>Matches stroke, strokes, stokes</td></tr>
  <tr><td>P-24</td><td>Same as P24, p-24, P 24</td></tr>
  <tr><td>P-23</td><td>All variants: P-23A, P-23B...</td></tr>
  <tr><td>P-23A strokes</td><td>Multi-word (all must match)</td></tr>
  <tr><td>"seal leak"</td><td>Exact phrase match</td></tr>
</table>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# MAIN CONTENT
# ══════════════════════════════════════════════════════════════

# Page header
st.markdown("""
<div class="page-header">
    <div class="page-header-title">Shift Report Search</div>
    <div class="page-header-sub">Full-text keyword search across all shift records</div>
</div>
""", unsafe_allow_html=True)

# ── Stat cards ──────────────────────────────────────────────
n_db    = db_count()
n_files = len(glob.glob(os.path.join(folder, "*.docx"))) if os.path.exists(folder) else 0
db_ok   = db_exists()

st.markdown(f"""
<div class="stat-row">
    <div class="stat-card">
        <div class="stat-value">{n_db:,}</div>
        <div class="stat-label">Sentences Indexed</div>
    </div>
    <div class="stat-card">
        <div class="stat-value">{n_files}</div>
        <div class="stat-label">Report Files Available</div>
    </div>
    <div class="stat-card {'stat-ready' if db_ok else ''}">
        <div class="stat-value">{'Ready' if db_ok else 'Not Built'}</div>
        <div class="stat-label">Database Status</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Database warning ─────────────────────────────────────────
if not db_ok:
    st.warning("Database not initialised. Set the folder path in the sidebar and click Build / Rebuild Database.")

# ── Search bar ───────────────────────────────────────────────
st.markdown('<div class="search-label">Search Query</div>', unsafe_allow_html=True)
query = st.text_input(
    "query",
    placeholder='Enter keyword, equipment ID, or phrase  —  e.g.   P-23A strokes   /   "seal leak"   /   trip',
    label_visibility="collapsed"
)

# ── Results ──────────────────────────────────────────────────
if query and query.strip():
    with st.spinner("Searching..."):
        results = search(query.strip(), date_from=df_str, date_to=dt_str, shift_filter=sh_str)

    if results.empty:
        st.markdown("""
<div class="status-msg">
    <strong>No results found</strong><br>
    Try a different keyword or check the search syntax in the sidebar.
</div>""", unsafe_allow_html=True)

    else:
        total = len(results)

        # Results header + download
        csv_buf = io.StringIO()
        results.to_csv(csv_buf, index=False)
        ts     = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_q = re.sub(r'[^a-z0-9]+','_', query.lower())[:25].strip('_')

        col_count, col_dl = st.columns([3, 1])
        with col_count:
            st.markdown(f"""
<div class="results-count">
    <span>{total:,}</span> result{'s' if total!=1 else ''} for
    <span style="color:#1A1D27; font-family:'DM Mono',monospace;
                 font-size:0.88rem;">"{query}"</span>
    {f' &nbsp;—&nbsp; showing first 200' if total > 200 else ''}
</div>""", unsafe_allow_html=True)
        with col_dl:
            st.download_button(
                label=f"Export CSV  ({total:,} rows)",
                data=csv_buf.getvalue(),
                file_name=f"search_{safe_q}_{ts}.csv",
                mime="text/csv"
            )

        st.markdown('<hr class="divider">', unsafe_allow_html=True)

        # Result cards
        for _, row in results.head(200).iterrows():
            hl     = highlight_html(row["Matched Sentence"], query)
            shift  = row["Shift"]
            badge_cls = ("badge-day"   if shift == "Day"   else
                         "badge-night" if shift == "Night" else "badge-unknown")
            st.markdown(f"""
<div class="result-card">
    <div class="result-meta">
        <span class="meta-date">{row['Date']}</span>
        <div class="meta-divider"></div>
        <span class="badge {badge_cls}">{shift}</span>
    </div>
    <div class="result-text">{hl}</div>
</div>""", unsafe_allow_html=True)

        if total > 200:
            st.markdown(f"""
<div class="status-msg" style="margin-top:12px;">
    Displaying 200 of <strong>{total:,}</strong> results.
    Export the CSV to view all matches.
</div>""", unsafe_allow_html=True)