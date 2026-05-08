import streamlit as st
import os, io, json, re
from datetime import datetime

st.set_page_config(page_title="EXD Insights Generator", page_icon="⚡", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; background-color: #0f0f0f !important; color: #d8d8d8 !important; }
#MainMenu, footer, header, .stDeployButton { visibility: hidden !important; }
.block-container { max-width: 800px !important; padding: 2rem 2rem 5rem !important; }
.section-hdr { display:flex; align-items:center; gap:12px; margin:2.5rem 0 1rem; }
.section-num { min-width:28px; height:28px; border-radius:50%; background:#2a2a2a; color:#fff; font-size:13px; font-weight:600; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.section-ttl { font-size:15px; font-weight:600; color:#fff; }
.section-sub { font-size:13px; color:#555; font-weight:400; }
.stTextInput > div > div > input, .stTextArea > div > div > textarea { background:#1a1a1a !important; border:1px solid #2a2a2a !important; border-radius:6px !important; color:#e0e0e0 !important; font-family:'Inter',sans-serif !important; font-size:14px !important; }
.stTextInput > div > div > input:focus, .stTextArea > div > div > textarea:focus { border-color:#ff6b2b !important; box-shadow:0 0 0 2px #ff6b2b18 !important; }
.stTextInput > label, .stTextArea > label, .stSelectbox > label { font-size:12px !important; font-weight:600 !important; letter-spacing:0.05em !important; color:#555 !important; text-transform:uppercase !important; }
.stSelectbox [data-baseweb="select"] > div { background:#1a1a1a !important; border:1px solid #2a2a2a !important; border-radius:6px !important; color:#e0e0e0 !important; font-family:'Inter',sans-serif !important; font-size:14px !important; }
div[data-testid="stButton"] > button { background:#1e1e1e !important; color:#ccc !important; border:1px solid #2a2a2a !important; border-radius:6px !important; font-family:'Inter',sans-serif !important; font-weight:600 !important; font-size:13px !important; padding:0.5rem 1rem !important; transition:all 0.15s !important; width:100% !important; }
div[data-testid="stButton"] > button:hover { border-color:#ff6b2b !important; color:#ff6b2b !important; background:#ff6b2b0f !important; }
div[data-testid="stButton"] > button:disabled { opacity:0.3 !important; cursor:not-allowed !important; }
.stDownloadButton > button { background:#1e1e1e !important; color:#ccc !important; border:1px solid #2a2a2a !important; border-radius:6px !important; font-family:'Inter',sans-serif !important; font-weight:600 !important; font-size:13px !important; padding:0.5rem 1rem !important; transition:all 0.15s !important; }
.stDownloadButton > button:hover { border-color:#ff6b2b !important; color:#ff6b2b !important; }
.stSpinner > div { border-top-color:#ff6b2b !important; }
hr { border-color:#1e1e1e !important; margin:1.5rem 0 !important; }
.streamlit-expanderHeader { background:#1a1a1a !important; border-radius:6px !important; font-size:13px !important; color:#777 !important; }
.vert-card { background:#1a1a1a; border:1px solid #2a2a2a; border-radius:8px; padding:0.9rem 0.75rem 0.5rem; text-align:center; margin-bottom:0.4rem; }
.vert-card.selected { border-color:#ff6b2b; background:#ff6b2b0d; }
.vert-icon { font-size:22px; display:block; margin-bottom:0.35rem; }
.vert-name { font-size:12px; font-weight:600; color:#ccc; line-height:1.3; display:block; }
.vert-card.selected .vert-name { color:#ff6b2b; }
.opt-card { background:#1a1a1a; border:1px solid #2a2a2a; border-radius:8px; padding:0.85rem 1rem; margin-bottom:0.5rem; display:flex; align-items:center; gap:0.75rem; }
.opt-card.selected { border-color:#ff6b2b; background:#ff6b2b0d; }
.opt-card-title { font-size:14px; font-weight:600; color:#e0e0e0; }
.opt-card-sub { font-size:12px; color:#555; margin-top:2px; }
.opt-dot { width:16px; height:16px; border-radius:50%; border:2px solid #333; flex-shrink:0; display:flex; align-items:center; justify-content:center; }
.opt-dot.on { border-color:#ff6b2b; background:#ff6b2b; }
.opt-dot.on::after { content:''; width:6px; height:6px; border-radius:50%; background:#fff; }
.stat-card { background:#141414; border:1px solid #202020; border-radius:8px; padding:1rem 1.2rem; margin-bottom:0.65rem; }
.stat-num { font-size:1rem; font-weight:700; color:#ff6b2b; line-height:1.3; margin-bottom:0.15rem; }
.stat-src { font-size:11px; color:#444; font-family:'Courier New',monospace; margin-bottom:0.35rem; }
.stat-ctx { font-size:12.5px; color:#888; line-height:1.55; margin-bottom:0.4rem; }
.stat-url a { font-size:10px; color:#3a3a3a; text-decoration:none; word-break:break-all; }
.stat-url a:hover { color:#ff6b2b; }
.rec-card { background:#ff6b2b0a; border:1px solid #ff6b2b22; border-radius:8px; padding:1rem 1.2rem; margin-top:0.65rem; }
.rec-label { font-size:10px; font-weight:700; letter-spacing:0.15em; text-transform:uppercase; color:#ff6b2b; margin-bottom:0.4rem; }
.rec-text { font-size:13px; color:#ccc; line-height:1.65; }
.headline-pill { font-size:14px; font-weight:600; color:#e8e8e8; border-left:3px solid #ff6b2b; padding:0.4rem 0 0.4rem 0.85rem; margin-bottom:1rem; line-height:1.45; }
.vert-badge { display:inline-flex; align-items:center; gap:0.4rem; font-size:11px; font-weight:700; letter-spacing:0.1em; text-transform:uppercase; color:#ff6b2b; background:#ff6b2b12; border:1px solid #ff6b2b30; border-radius:4px; padding:0.2rem 0.6rem; margin-bottom:0.9rem; }
.result-header { padding:1.25rem 0 0.5rem; border-bottom:1px solid #1e1e1e; margin-bottom:1.5rem; }
.result-header h2 { font-size:1.4rem !important; font-weight:700 !important; color:#f0f0f0 !important; margin:0.3rem 0 0.2rem !important; }
.result-header p { font-size:12px; color:#444; margin:0; }
.step-row { display:flex; align-items:center; gap:8px; font-size:12px; color:#444; font-family:'Courier New',monospace; padding:0.3rem 0; }
.step-dot { width:6px; height:6px; background:#ff6b2b; border-radius:50%; flex-shrink:0; }
</style>
""", unsafe_allow_html=True)

# ── Gemini ────────────────────────────────────────────────────────────────────
@st.cache_resource
def get_gemini_client():
    try:
        import google.genai as genai
    except ImportError:
        st.error("google-genai not installed."); st.stop()
    key = None
    try: key = st.secrets["GEMINI_KEY"]
    except Exception: key = os.environ.get("GEMINI_KEY")
    if not key: st.error("GEMINI_KEY not found in Streamlit secrets."); st.stop()
    return genai.Client(api_key=key)

def call_gemini(client, prompt, grounded=True):
    from google.genai import types
    MODELS = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
    def _call(model, use_grounding):
        kw = {"temperature": 0.4, "max_output_tokens": 4096}
        if use_grounding:
            kw["tools"] = [types.Tool(google_search=types.GoogleSearch())]
        r = client.models.generate_content(model=model, contents=prompt, config=types.GenerateContentConfig(**kw))
        if r.text: return r.text
        parts = [p.text for c in r.candidates for p in c.content.parts if hasattr(p,"text") and p.text]
        return "\n".join(parts)
    def _with_fallback(use_grounding):
        last = None
        for m in MODELS:
            try: return _call(m, use_grounding)
            except Exception as e:
                if any(x in str(e).lower() for x in ["not_found","404","not found","deprecated","no longer"]):
                    last = e; continue
                raise
        raise last
    if grounded:
        try: return _with_fallback(True)
        except Exception as e:
            if any(x in str(e).lower() for x in ["grounding","search","tool","400","403","permission"]):
                st.warning("Search grounding unavailable — generating without live web data.", icon="🔍")
                return _with_fallback(False)
            raise
    return _with_fallback(False)

def parse_json(text):
    if not text: return None
    m = re.search(r"```(?:json)?\s*([\[\{].*?)\s*```", text, re.DOTALL)
    raw = m.group(1) if m else text.strip()
    s = min((raw.find("[") if "[" in raw else len(raw)), (raw.find("{") if "{" in raw else len(raw)))
    e = max(raw.rfind("}"), raw.rfind("]"))
    if 0 <= s <= e: raw = raw[s:e+1]
    try: return json.loads(raw)
    except: return None

def clean(v):
    if not isinstance(v, str): v = str(v)
    v = re.sub(r'\*\*(.+?)\*\*', r'\1', v)
    v = re.sub(r'\*(.+?)\*', r'\1', v)
    return v.strip()

def extract_insight_text(ins):
    """Handle insight whether it's a plain string or a dict with fact/implication keys."""
    if isinstance(ins, str):
        return ins, "", ""
    if isinstance(ins, dict):
        # Preferred format
        if "text" in ins:
            return ins.get("text",""), ins.get("source",""), ins.get("source_url","")
        # Model returned {fact, implication} — merge them
        fact = ins.get("fact", ins.get("Fact",""))
        impl = ins.get("implication", ins.get("Implication",""))
        text = " ".join(filter(None, [fact, impl]))
        return text, ins.get("source",""), ins.get("source_url","")
    return str(ins), "", ""

# ── Data ──────────────────────────────────────────────────────────────────────
MARKETS = ["UAE","Saudi Arabia","Qatar","Kuwait","Bahrain","Oman","Egypt","Jordan","Lebanon","Morocco","South Africa","United Kingdom","United States","France","Germany","India","China","Japan","Australia"]

VERTICALS = {
    "SEO & AI Search":    {"icon":"🔍","focus":"organic search, AI search engines (Perplexity, ChatGPT Search, Google AI Overviews), GEO, content structure for AI citation, entity authority, E-E-A-T, zero-click trends, SGE/AIO impact"},
    "Customer Experience":{"icon":"💬","focus":"CX strategy, personalisation, loyalty programmes, omnichannel journeys, voice of customer, NPS/CSAT, digital-to-physical integration, conversational AI, CRM maturity"},
    "Tech & Creative":    {"icon":"⚙️","focus":"martech stack, AI-generated creative, personalisation engines, A/B testing, Core Web Vitals, accessibility, design systems, headless CMS, composable architecture"},
    "Strategy & Growth":  {"icon":"📈","focus":"paid media efficiency, attribution, growth loops, market share dynamics, competitive positioning, share of search, commercial strategy, media mix modelling"},
}

# ── Prompts ───────────────────────────────────────────────────────────────────
def market_stats_prompt(client_name, market, industry, website, fmt):
    if fmt == "headline":
        out = (
            'Return ONLY a valid JSON array with exactly 6 objects. No other text.\n'
            'Each object must have exactly these keys:\n'
            '  "stat": short punchy finding with a number, max 15 words\n'
            '  "source": organisation or publication name + year, e.g. "Euromonitor 2024"\n'
            '  "source_url": real URL where this data can be verified\n'
            '  "context": one plain English sentence explaining relevance, max 25 words\n'
            'Example: [{"stat":"UAE e-commerce grew 32% in 2024 to reach AED 42bn","source":"KPMG 2025","source_url":"https://kpmg.com/...","context":"Rapid digital commerce growth creates urgency for brands to capture organic and AI-driven discovery."}]\n'
            'Return the array only. No markdown, no preamble.'
        )
    else:
        out = (
            'Return ONLY this JSON object, no other text:\n'
            '{"narrative": "a 220-word paragraph weaving in at least 6 inline statistics with citations like (Euromonitor 2024)"}'
        )
    return f"You are a market intelligence analyst preparing a new business pitch.\nCLIENT: {client_name}\nMARKET: {market}\nINDUSTRY: {industry}\nWEBSITE: {website}\n\nSearch for current, specific statistics about this market and industry.\nRules:\n- Real data from credible sources, specific to {market}, 2023-2025 preferred\n- Cover: market size, digital adoption, consumer behaviour, AI/tech disruption, competitive dynamics\n- Do not fabricate. source_url must be a real URL.\n\n{out}"

def vertical_prompt(client_name, market, industry, website, vertical, focus, include_narrative):
    nar = '\n  "narrative": "120-word strategic paragraph connecting all insights into a pitch story",' if include_narrative else ""
    example_text = f'{client_name} receives 68% of traffic from branded keywords, leaving high-intent generic queries like "luxury apartments {market}" almost entirely to competitors. Emaar ranks top-3 for 14 of the top 20 such queries, capturing demand that {client_name} is invisible for.'
    return f"""You are EXD, the Experience Design practice inside Performics / Publicis Groupe, preparing a new business pitch.
CLIENT: {client_name} | MARKET: {market} | INDUSTRY: {industry} | WEBSITE: {website}
VERTICAL: {vertical} | FOCUS: {focus}

Search for real, current intelligence about this client and their competitive landscape.

Return ONLY the following JSON. No markdown, no preamble, no extra keys:

{{
  "headline": "punchy headline max 12 words, must name {client_name} or {market}",
  "insights": [{nar}
    {{
      "text": "Full insight as plain prose. Fact first, then implication. 2-3 sentences. Must include a real number, competitor name, or platform name. Example: {example_text}",
      "source": "Source name and year",
      "source_url": "https://real-url.com"
    }},
    {{ "text": "...", "source": "...", "source_url": "..." }},
    {{ "text": "...", "source": "...", "source_url": "..." }},
    {{ "text": "...", "source": "...", "source_url": "..." }},
    {{ "text": "...", "source": "...", "source_url": "..." }}
  ],
  "recommendation": "2-3 sentence recommendation starting with an action verb, specific to {vertical}."
}}

RULES:
- insights[i].text is always a plain string — never an object, never use sub-keys like 'fact' or 'implication'
- No markdown formatting (**bold**, *italic*) inside any string value
- source_url must be a real verifiable URL"""

# ── Word export ───────────────────────────────────────────────────────────────
def generate_docx(client_name, market, industry, results):
    try:
        from docx import Document
        from docx.shared import Pt, RGBColor, Cm
    except ImportError:
        return None
    doc = Document()
    for s in doc.sections:
        s.top_margin=Cm(2.2); s.bottom_margin=Cm(2.2); s.left_margin=Cm(2.5); s.right_margin=Cm(2.5)
    OR=RGBColor(255,107,43); WH=RGBColor(240,240,240); GR=RGBColor(140,140,140); DM=RGBColor(80,80,80)
    def add(text="",bold=False,size=10,color=None,italic=False,after=6):
        p=doc.add_paragraph(); p.paragraph_format.space_after=Pt(after)
        if text:
            r=p.add_run(text); r.font.name="Arial"; r.font.size=Pt(size)
            r.font.bold=bold; r.font.italic=italic; r.font.color.rgb=color or WH
        return p
    def rule():
        p=doc.add_paragraph(); p.paragraph_format.space_after=Pt(8)
        r=p.add_run("─"*88); r.font.name="Arial"; r.font.size=Pt(7); r.font.color.rgb=RGBColor(35,35,35)
    add("PERFORMICS · EXD PRACTICE",bold=True,size=7,color=OR,after=2)
    add("INSIGHTS BRIEF",bold=True,size=20,color=WH,after=4)
    add(f"{client_name}  ·  {market}  ·  {industry}",size=10,color=GR,after=2)
    add(f"Generated {datetime.now().strftime('%d %B %Y')}",size=8,color=DM,after=12); rule()
    if "stats" in results:
        add("MARKET INTELLIGENCE",bold=True,size=8,color=OR,after=6)
        stats=results["stats"]
        if isinstance(stats,list):
            for s in stats:
                if isinstance(s,dict):
                    p=doc.add_paragraph(); p.paragraph_format.space_after=Pt(3)
                    r1=p.add_run(f"{s.get('stat','')}  "); r1.font.name="Arial"; r1.font.size=Pt(10); r1.font.bold=True; r1.font.color.rgb=OR
                    r2=p.add_run(f"({s.get('source','')})"); r2.font.name="Arial"; r2.font.size=Pt(8); r2.font.color.rgb=DM
                    if s.get("context"): add(s["context"],size=9,color=GR,after=4)
                    if s.get("source_url"): add(s["source_url"],size=8,color=DM,after=7)
        elif isinstance(stats,dict) and "narrative" in stats:
            add(stats["narrative"],size=9,color=GR,after=8)
        rule()
    for vertical,data in results.get("verticals",{}).items():
        icon=VERTICALS.get(vertical,{}).get("icon","")
        add(f"{icon}  {vertical.upper()}",bold=True,size=8,color=OR,after=4)
        if data.get("headline"): add(data["headline"],bold=True,size=12,color=WH,after=8)
        for ins in data.get("insights",[]):
            t,src,url=extract_insight_text(ins)
            p=doc.add_paragraph(style="List Bullet"); p.paragraph_format.space_after=Pt(4)
            r=p.add_run(clean(t)); r.font.name="Arial"; r.font.size=Pt(9); r.font.color.rgb=RGBColor(200,200,200)
            if src or url: add(f"{src} — {url}" if src and url else src or url,size=8,color=DM,after=5)
        if data.get("narrative"): add(data["narrative"],size=9,color=GR,italic=True,after=6)
        if data.get("recommendation"):
            add("STRATEGIC RECOMMENDATION",bold=True,size=7,color=OR,after=3)
            add(data["recommendation"],size=9,color=RGBColor(210,210,210),after=10)
        rule()
    add("Confidential  ·  EXD @ Performics  ·  Publicis Groupe",size=7,color=DM)
    buf=io.BytesIO(); doc.save(buf); buf.seek(0); return buf.read()

# ── Auth ──────────────────────────────────────────────────────────────────────
def check_password():
    pwd = None
    try: pwd = st.secrets["APP_PASSWORD"]
    except Exception: pwd = os.environ.get("APP_PASSWORD","")
    if not pwd: return True
    if st.session_state.get("auth"): return True
    st.markdown("<div style='text-align:center;padding:4rem 0 2rem'><div style='font-size:11px;font-weight:700;letter-spacing:.2em;color:#ff6b2b;text-transform:uppercase;margin-bottom:.8rem'>Performics · EXD</div><div style='font-size:1.7rem;font-weight:700;color:#f0f0f0;margin-bottom:.25rem'>Insights Generator</div><div style='font-size:13px;color:#444;margin-bottom:2.5rem'>Internal tool — authorised access only</div></div>", unsafe_allow_html=True)
    c1,c2,c3=st.columns([1,1.6,1])
    with c2:
        entered=st.text_input("",type="password",key="pw",placeholder="Enter password")
        if st.button("Access →",use_container_width=True):
            if entered==pwd: st.session_state["auth"]=True; st.rerun()
            else: st.error("Incorrect password.")
    return False

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    if not check_password(): return

    st.markdown("# ⚡ EXD Insights Generator")
    st.markdown("AI-grounded pitch intelligence across all four verticals — in minutes.")
    st.divider()

    # Section 1 — Client Brief
    st.markdown('<div class="section-hdr"><div class="section-num">1</div><div><div class="section-ttl">Client Brief</div><div class="section-sub">Tell us about the pitch</div></div></div>', unsafe_allow_html=True)
    c1,c2=st.columns(2)
    with c1:
        client_name=st.text_input("Client / Brand",placeholder="e.g. Etihad Airways")
        industry=st.text_input("Industry",placeholder="e.g. Aviation, Retail Banking")
    with c2:
        market=st.selectbox("Market / Region",MARKETS,index=0)
        website=st.text_input("Client Website",placeholder="e.g. etihad.com")

    # Section 2 — Verticals
    st.markdown('<div class="section-hdr"><div class="section-num">2</div><div><div class="section-ttl">Verticals</div><div class="section-sub">Select which to generate insights for</div></div></div>', unsafe_allow_html=True)
    if "sel_v" not in st.session_state: st.session_state["sel_v"]=list(VERTICALS.keys())
    vcols=st.columns(4)
    for i,(vname,vmeta) in enumerate(VERTICALS.items()):
        with vcols[i]:
            is_sel=vname in st.session_state["sel_v"]
            st.markdown(f'<div class="vert-card {"selected" if is_sel else ""}"><span class="vert-icon">{vmeta["icon"]}</span><span class="vert-name">{vname}</span></div>', unsafe_allow_html=True)
            if st.button("✓ Selected" if is_sel else "Select", key=f"v_{vname}", use_container_width=True):
                if is_sel: st.session_state["sel_v"].remove(vname)
                else: st.session_state["sel_v"].append(vname)
                st.rerun()
    sel_v=st.session_state["sel_v"]
    if not sel_v: st.caption("⚠️ Select at least one vertical.")

    # Section 3 — Output Options
    st.markdown('<div class="section-hdr"><div class="section-num">3</div><div><div class="section-ttl">Output Options</div><div class="section-sub">Customise the report format</div></div></div>', unsafe_allow_html=True)
    if "stat_fmt" not in st.session_state: st.session_state["stat_fmt"]="headline"
    if "incl_nar" not in st.session_state: st.session_state["incl_nar"]=False
    opts=[("headline","Headline Stats","6 punchy data points with source citations"),("narrative","Narrative Paragraph","A flowing 220-word market story with embedded stats")]
    fc1,fc2=st.columns(2)
    for i,(val,title,sub) in enumerate(opts):
        with [fc1,fc2][i]:
            is_s=st.session_state["stat_fmt"]==val
            st.markdown(f'<div class="opt-card {"selected" if is_s else ""}"><div class="opt-dot {"on" if is_s else ""}"></div><div><div class="opt-card-title">{title}</div><div class="opt-card-sub">{sub}</div></div></div>', unsafe_allow_html=True)
            if st.button("✓ Selected" if is_s else "Select",key=f"fmt_{val}",use_container_width=True):
                st.session_state["stat_fmt"]=val; st.rerun()
    incl=st.session_state["incl_nar"]
    st.markdown(f'<div class="opt-card {"selected" if incl else ""}" style="margin-top:.5rem"><div class="opt-dot {"on" if incl else ""}"></div><div><div class="opt-card-title">Narrative paragraph per vertical</div><div class="opt-card-sub">Adds a 120-word strategic story to each vertical section</div></div></div>', unsafe_allow_html=True)
    if st.button("✓ Enabled" if incl else "Enable",key="nar_tog",use_container_width=True):
        st.session_state["incl_nar"]=not incl; st.rerun()

    # Generate
    st.divider()
    ready=all([client_name.strip(),market,industry.strip(),sel_v])
    if not ready: st.caption("Fill in all fields and select at least one vertical to continue.")
    gen=st.button("⚡  Generate Insights",disabled=not ready,use_container_width=True)

    if gen and ready:
        st.session_state.pop("results",None); st.session_state.pop("meta",None)
        client=get_gemini_client()
        results={"verticals":{}}
        total=1+len(sel_v)
        prog=st.progress(0); status=st.empty()

        status.markdown('<div class="step-row"><div class="step-dot"></div>Researching market data…</div>', unsafe_allow_html=True)
        try:
            raw=call_gemini(client,market_stats_prompt(client_name,market,industry,website,st.session_state["stat_fmt"]))
            parsed=parse_json(raw)
            results["stats"]=parsed if parsed else {"narrative":raw}
        except Exception as e:
            results["stats_err"]=str(e)
        prog.progress(1/total)

        for i,v in enumerate(sel_v):
            status.markdown(f'<div class="step-row"><div class="step-dot"></div>Generating {v} insights…</div>', unsafe_allow_html=True)
            try:
                raw=call_gemini(client,vertical_prompt(client_name,market,industry,website,v,VERTICALS[v]["focus"],st.session_state["incl_nar"]))
                parsed=parse_json(raw)
                results["verticals"][v]=parsed if parsed else {"raw":raw}
            except Exception as e:
                results["verticals"][v]={"error":str(e)}
            prog.progress((i+2)/total)

        prog.empty(); status.empty()
        st.session_state["results"]=results
        st.session_state["meta"]={"client_name":client_name,"market":market,"industry":industry,"website":website,"ts":datetime.now().strftime("%d %B %Y, %H:%M")}
        st.rerun()

    if "results" not in st.session_state: return

    results=st.session_state["results"]
    meta=st.session_state["meta"]
    st.divider()
    st.markdown(f'<div class="result-header"><div style="font-size:10px;font-weight:700;letter-spacing:.2em;text-transform:uppercase;color:#ff6b2b">Insights Brief</div><h2>{meta["client_name"]}</h2><p>{meta["market"]} &nbsp;·&nbsp; {meta["industry"]} &nbsp;·&nbsp; {meta["ts"]}</p></div>', unsafe_allow_html=True)

    # Market stats
    if "stats_err" in results:
        st.error(f"Market stats error: {results['stats_err']}")
    elif "stats" in results:
        st.markdown('<div class="section-hdr" style="margin-top:0"><div class="section-num" style="background:#1e1e1e;font-size:16px">📊</div><div class="section-ttl">Market Intelligence</div></div>', unsafe_allow_html=True)
        stats=results["stats"]
        if isinstance(stats,list):
            c1,c2=st.columns(2)
            for i,s in enumerate(stats):
                if isinstance(s,dict):
                    url=s.get("source_url","")
                    url_html=f'<div class="stat-url"><a href="{url}" target="_blank">↗ {url}</a></div>' if url else ""
                    with (c1 if i%2==0 else c2):
                        st.markdown(f'<div class="stat-card"><div class="stat-num">{clean(s.get("stat",""))}</div><div class="stat-src">{clean(s.get("source",""))}</div><div class="stat-ctx">{clean(s.get("context",""))}</div>{url_html}</div>', unsafe_allow_html=True)
        elif isinstance(stats,dict) and "narrative" in stats:
            st.markdown(f'<div class="stat-card"><div style="font-size:13.5px;color:#aaa;line-height:1.75">{clean(stats["narrative"])}</div></div>', unsafe_allow_html=True)

    # Verticals
    for vertical,data in results.get("verticals",{}).items():
        icon=VERTICALS.get(vertical,{}).get("icon","")
        st.markdown("<hr/>", unsafe_allow_html=True)
        st.markdown(f'<div class="vert-badge">{icon} {vertical}</div>', unsafe_allow_html=True)
        if "error" in data: st.error(f"Error: {data['error']}"); continue
        if "raw" in data:
            with st.expander("Raw output (JSON parse failed)"): st.code(data["raw"],language="text")
            continue
        if data.get("headline"):
            st.markdown(f'<div class="headline-pill">{clean(data["headline"])}</div>', unsafe_allow_html=True)
        insights=data.get("insights",[])
        if insights:
            c1,c2=st.columns(2)
            for i,ins in enumerate(insights):
                t,src,url=extract_insight_text(ins)
                url_html=f'<div class="stat-url"><a href="{url}" target="_blank">↗ {url}</a></div>' if url else ""
                with (c1 if i%2==0 else c2):
                    st.markdown(f'<div class="stat-card"><div class="stat-ctx" style="font-size:13px;color:#bbb;line-height:1.68;margin-bottom:.5rem">{clean(t)}</div><div class="stat-src">{clean(src)}</div>{url_html}</div>', unsafe_allow_html=True)
        if data.get("narrative"):
            st.markdown(f'<div class="stat-card" style="margin-top:.25rem"><div style="font-size:13px;color:#666;line-height:1.72;font-style:italic">{clean(data["narrative"])}</div></div>', unsafe_allow_html=True)
        if data.get("recommendation"):
            st.markdown(f'<div class="rec-card"><div class="rec-label">Strategic Recommendation</div><div class="rec-text">{clean(data["recommendation"])}</div></div>', unsafe_allow_html=True)

    # Export
    st.markdown("<hr/>", unsafe_allow_html=True)
    st.markdown('<div class="section-hdr" style="margin-top:0"><div class="section-num" style="background:#1e1e1e">↓</div><div class="section-ttl">Export</div></div>', unsafe_allow_html=True)
    c1,c2,_=st.columns([1.3,1.3,2])
    with c1:
        docx=generate_docx(meta["client_name"],meta["market"],meta["industry"],results)
        if docx:
            st.download_button("⬇ Word Doc",data=docx,file_name=f"EXD_Insights_{meta['client_name'].replace(' ','_')}.docx",mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",use_container_width=True)
        else: st.caption("Install python-docx for Word export")
    with c2:
        lines=[f"EXD INSIGHTS — {meta['client_name']} | {meta['market']} | {meta['industry']}",f"Generated: {meta['ts']}","="*60,""]
        if "stats" in results:
            lines+=["MARKET INTELLIGENCE","-"*40]
            s=results["stats"]
            if isinstance(s,list):
                for item in s:
                    if isinstance(item,dict): lines.append(f"• {item.get('stat','')} ({item.get('source','')})"); lines.append(f"  {item.get('source_url','')}"); lines.append(f"  {item.get('context','')}")
            elif isinstance(s,dict) and "narrative" in s: lines.append(s["narrative"])
            lines.append("")
        for v,d in results.get("verticals",{}).items():
            lines+=[f"\n{v.upper()}","-"*40]
            if d.get("headline"): lines.append(f"Headline: {d['headline']}")
            for ins in d.get("insights",[]):
                t,src,url=extract_insight_text(ins)
                lines.append(f"\n• {t}"); lines.append(f"  Source: {src}"); lines.append(f"  URL: {url}")
            if d.get("recommendation"): lines.append(f"\nRecommendation: {d['recommendation']}")
            lines.append("")
        st.download_button("⬇ Text File",data="\n".join(lines),file_name=f"EXD_Insights_{meta['client_name'].replace(' ','_')}.txt",mime="text/plain",use_container_width=True)

if __name__=="__main__": main()
