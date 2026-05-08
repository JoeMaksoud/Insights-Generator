import streamlit as st
import os
import io
import json
import re
from datetime import datetime

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="EXD Insights Generator",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Brand CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

  html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0d0d0d;
    color: #e8e8e8;
  }

  /* Hide Streamlit chrome */
  #MainMenu, footer, header { visibility: hidden; }
  .block-container { padding-top: 2rem; padding-bottom: 4rem; max-width: 960px; }

  /* Headings */
  h1, h2, h3 { font-family: 'DM Sans', sans-serif; font-weight: 700; }

  /* Inputs */
  .stTextInput > div > div > input,
  .stTextArea > div > div > textarea,
  .stSelectbox > div > div > div {
    background-color: #1a1a1a !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 6px !important;
    color: #e8e8e8 !important;
    font-family: 'DM Sans', sans-serif !important;
  }
  .stTextInput > div > div > input:focus,
  .stTextArea > div > div > textarea:focus {
    border-color: #b8ff57 !important;
    box-shadow: 0 0 0 1px #b8ff57 !important;
  }

  /* Labels */
  .stTextInput label, .stTextArea label, .stSelectbox label,
  .stMultiSelect label, .stRadio label { color: #888 !important; font-size: 0.78rem !important; letter-spacing: 0.08em; text-transform: uppercase; }

  /* Buttons */
  .stButton > button {
    background-color: #b8ff57 !important;
    color: #0d0d0d !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 6px !important;
    padding: 0.6rem 1.8rem !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.04em;
    transition: opacity 0.15s ease !important;
  }
  .stButton > button:hover { opacity: 0.85 !important; }
  .stButton > button:disabled { opacity: 0.4 !important; }

  /* Secondary button style via key trick */
  .stDownloadButton > button {
    background-color: #1a1a1a !important;
    color: #b8ff57 !important;
    border: 1px solid #b8ff57 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    border-radius: 6px !important;
  }

  /* Multiselect tags */
  .stMultiSelect [data-baseweb="tag"] {
    background-color: #b8ff5720 !important;
    border: 1px solid #b8ff57 !important;
    color: #b8ff57 !important;
  }

  /* Checkboxes */
  .stCheckbox > label { color: #e8e8e8 !important; }

  /* Divider */
  hr { border-color: #2a2a2a !important; }

  /* Expander */
  .streamlit-expanderHeader { background-color: #1a1a1a !important; border-radius: 6px !important; }

  /* Spinner */
  .stSpinner > div { border-top-color: #b8ff57 !important; }

  /* Cards */
  .insight-card {
    background: #141414;
    border: 1px solid #2a2a2a;
    border-left: 3px solid #b8ff57;
    border-radius: 8px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
  }
  .stat-card {
    background: #141414;
    border: 1px solid #2a2a2a;
    border-radius: 8px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 0.75rem;
  }
  .vertical-header {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin-bottom: 1rem;
  }
  .badge {
    display: inline-block;
    background: #b8ff5720;
    border: 1px solid #b8ff57;
    color: #b8ff57;
    font-size: 0.7rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 0.2rem 0.6rem;
    border-radius: 4px;
    font-weight: 600;
  }
  .rec-box {
    background: #b8ff570d;
    border: 1px solid #b8ff5740;
    border-radius: 6px;
    padding: 1rem 1.2rem;
    margin-top: 0.75rem;
  }
</style>
""", unsafe_allow_html=True)

# ── Helpers ───────────────────────────────────────────────────────────────────
def get_gemini_client():
    try:
        import google.genai as genai
        api_key = st.secrets.get("GEMINI_KEY") or os.environ.get("GEMINI_KEY")
        if not api_key:
            st.error("⚠️  GEMINI_KEY secret not found. Add it in Streamlit secrets.")
            st.stop()
        client = genai.Client(api_key=api_key)
        return client
    except ImportError:
        st.error("google-genai not installed. Check requirements.txt.")
        st.stop()

def call_gemini(client, prompt: str, grounded: bool = True) -> str:
    """Call Gemini 2.0 Flash with optional Google Search grounding."""
    from google.genai import types

    tools = []
    if grounded:
        tools = [types.Tool(google_search=types.GoogleSearch())]

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=tools,
            temperature=0.7,
            max_output_tokens=4096,
        ),
    )
    return response.text

def parse_json_block(text: str) -> dict | list | None:
    """Extract and parse a JSON block from model output."""
    match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
    if match:
        raw = match.group(1)
    else:
        # Try to find bare JSON object/array
        raw = text.strip()
    try:
        return json.loads(raw)
    except Exception:
        return None

# ── Vertical metadata ─────────────────────────────────────────────────────────
VERTICALS = {
    "SEO & AI Search": {
        "icon": "🔍",
        "focus": "organic search, AI search engines (Perplexity, ChatGPT, Gemini), GEO (Generative Engine Optimization), content structure, crawlability, entity authority, zero-click trends, SGE/AIO impact",
    },
    "Customer Experience": {
        "icon": "💬",
        "focus": "CX strategy, personalisation, loyalty, omnichannel journeys, voice of customer, NPS/CSAT benchmarks, digital-physical integration, conversational AI, CRM maturity",
    },
    "Tech & Creative": {
        "icon": "⚙️",
        "focus": "martech stack, creative production at scale, AI-generated content, personalisation engines, A/B testing, web performance, accessibility, design systems, headless CMS, composable architecture",
    },
    "Strategy & Growth": {
        "icon": "📈",
        "focus": "performance marketing, paid media efficiency, attribution, growth loops, market share dynamics, competitive positioning, category trends, commercial strategy",
    },
}

# ── Prompts ───────────────────────────────────────────────────────────────────
def market_stats_prompt(client_name, market, industry, website, format_choice):
    fmt = (
        "Return 6 headline statistics, each with: stat (the number/finding), source (publication + year), and one sentence of context. Format as JSON array."
        if format_choice == "Headline stats with sources"
        else "Return a 250-word narrative paragraph weaving in at least 6 specific market statistics with inline citations (e.g. '...according to Euromonitor 2024...'). Return as JSON with key 'narrative'."
    )
    return f"""
You are a senior market intelligence analyst preparing a pitch brief.
Client: {client_name}
Market: {market}
Industry: {industry}
Website: {website}

Search for the most current, specific, and surprising statistics about this market and industry.
Do NOT use recycled generic stats. Find real data from credible sources (industry reports, analyst firms, government data, news).
Focus on: market size & growth, digital adoption trends, consumer behaviour shifts, AI/tech disruption, competitive dynamics in {market}.

{fmt}

Be specific to {market} and {industry}. Avoid generic global stats unless directly relevant.
Return ONLY the JSON. No preamble, no markdown outside the JSON block.
"""

def vertical_insights_prompt(client_name, market, industry, website, vertical, focus, include_narrative):
    narrative_instruction = (
        "Also include a 'narrative' key with a 150-word strategic paragraph."
        if include_narrative
        else "Do not include a narrative paragraph."
    )
    return f"""
You are EXD, an experience design practice inside Publicis Groupe, preparing a new business pitch.
Client: {client_name} | Market: {market} | Industry: {industry} | Website: {website}
Vertical: {vertical}
Focus areas: {focus}

Search for real, current intelligence about this client and market through the lens of {vertical}.

Return a JSON object with these keys:
- "headline": one punchy, specific insight headline (max 12 words). Should name the client or market specifically.
- "insights": array of exactly 5 insight bullets. Each must be:
  * Specific to {market} and {industry} — not generic
  * Include a real data point, competitor name, or platform reference
  * Written as a provocative, pitch-ready observation
  * 2-3 sentences each
- "recommendation": one bold strategic recommendation for how EXD should position for this client on {vertical} (2-3 sentences, starts with an action verb)
{narrative_instruction}

Example of the specificity level required:
BAD: "74% of users expect personalised experiences."
GOOD: "In UAE retail banking, Emirates NBD's mobile app processes 78% of all transactions yet its search experience returns zero results for 'savings goal' — a gap Al Hilal Bank is actively closing through conversational UX."

Return ONLY the JSON. No preamble.
"""

# ── Word doc generation ───────────────────────────────────────────────────────
def generate_word_doc(client_name, market, industry, results: dict) -> bytes:
    """Generate a branded Word doc from results dict."""
    try:
        from docx import Document
        from docx.shared import Pt, RGBColor, Inches, Cm
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        from docx.oxml.ns import qn
        from docx.oxml import OxmlElement
        import copy

        doc = Document()

        # Page margins
        for section in doc.sections:
            section.top_margin = Cm(2)
            section.bottom_margin = Cm(2)
            section.left_margin = Cm(2.5)
            section.right_margin = Cm(2.5)

        # Helpers
        def set_font(run, bold=False, size=11, color=None):
            run.font.name = "Arial"
            run.font.size = Pt(size)
            run.font.bold = bold
            if color:
                run.font.color.rgb = RGBColor(*color)

        def add_heading(text, level=1):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            run = p.add_run(text)
            if level == 1:
                set_font(run, bold=True, size=20, color=(184, 255, 87))
            elif level == 2:
                set_font(run, bold=True, size=14, color=(184, 255, 87))
            else:
                set_font(run, bold=True, size=11, color=(200, 200, 200))
            return p

        def add_body(text, italic=False, color=None):
            p = doc.add_paragraph()
            run = p.add_run(text)
            set_font(run, size=10, color=color or (220, 220, 220))
            run.font.italic = italic
            return p

        def add_bullet(text):
            p = doc.add_paragraph(style="List Bullet")
            run = p.add_run(text)
            set_font(run, size=10, color=(220, 220, 220))
            return p

        def add_spacer():
            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(4)

        # Title block
        p = doc.add_paragraph()
        r = p.add_run("EXD INSIGHTS BRIEF")
        set_font(r, bold=True, size=9, color=(184, 255, 87))
        p.paragraph_format.space_after = Pt(2)

        add_heading(f"{client_name} — {market}", level=1)

        p = doc.add_paragraph()
        r = p.add_run(f"{industry}  ·  Generated {datetime.now().strftime('%d %B %Y')}")
        set_font(r, size=9, color=(120, 120, 120))
        add_spacer()

        doc.add_paragraph("─" * 80)
        add_spacer()

        # Market stats
        if "stats" in results:
            add_heading("MARKET INTELLIGENCE", level=2)
            add_spacer()
            stats = results["stats"]
            if isinstance(stats, list):
                for s in stats:
                    if isinstance(s, dict):
                        p = doc.add_paragraph()
                        r1 = p.add_run(f"{s.get('stat', '')}  ")
                        set_font(r1, bold=True, size=11, color=(184, 255, 87))
                        r2 = p.add_run(f"({s.get('source', '')})")
                        set_font(r2, size=9, color=(140, 140, 140))
                        if s.get("context"):
                            add_body(s["context"])
                    add_spacer()
            elif isinstance(stats, dict) and "narrative" in stats:
                add_body(stats["narrative"])
            add_spacer()
            doc.add_paragraph("─" * 80)
            add_spacer()

        # Verticals
        for vertical, data in results.get("verticals", {}).items():
            add_heading(vertical.upper(), level=2)
            if data.get("headline"):
                add_heading(data["headline"], level=3)
            add_spacer()

            if data.get("insights"):
                for ins in data["insights"]:
                    add_bullet(ins)
            add_spacer()

            if data.get("narrative"):
                add_body(data["narrative"], italic=True, color=(180, 180, 180))
                add_spacer()

            if data.get("recommendation"):
                p = doc.add_paragraph()
                r = p.add_run("STRATEGIC RECOMMENDATION  ")
                set_font(r, bold=True, size=9, color=(184, 255, 87))
                add_body(data["recommendation"])

            add_spacer()
            doc.add_paragraph("─" * 80)
            add_spacer()

        # Footer
        p = doc.add_paragraph()
        r = p.add_run("Confidential · EXD @ Performics · Publicis Groupe")
        set_font(r, size=8, color=(80, 80, 80))

        buf = io.BytesIO()
        doc.save(buf)
        buf.seek(0)
        return buf.read()

    except ImportError:
        return None

# ── Auth gate ─────────────────────────────────────────────────────────────────
def check_password():
    pwd = st.secrets.get("APP_PASSWORD") or os.environ.get("APP_PASSWORD", "")
    if not pwd:
        return True  # No password set — allow through (dev mode)

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        return True

    st.markdown("""
    <div style='text-align:center; padding: 4rem 0 2rem 0;'>
      <div style='font-size:0.75rem; letter-spacing:0.15em; color:#b8ff57; text-transform:uppercase; margin-bottom:0.5rem;'>Performics EXD</div>
      <h1 style='font-size:2rem; font-weight:700; color:#e8e8e8; margin:0;'>Insights Generator</h1>
      <p style='color:#555; margin-top:0.5rem; font-size:0.9rem;'>Internal tool — restricted access</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        entered = st.text_input("Password", type="password", key="pw_input", label_visibility="collapsed", placeholder="Enter password")
        if st.button("Enter", use_container_width=True):
            if entered == pwd:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Incorrect password.")
    return False

# ── Main app ──────────────────────────────────────────────────────────────────
def main():
    if not check_password():
        return

    # Header
    st.markdown("""
    <div style='margin-bottom:2rem;'>
      <div style='font-size:0.7rem; letter-spacing:0.2em; color:#b8ff57; text-transform:uppercase; margin-bottom:0.3rem;'>Performics · EXD Practice</div>
      <h1 style='font-size:2.2rem; font-weight:700; color:#e8e8e8; margin:0; line-height:1.1;'>Insights Generator</h1>
      <p style='color:#555; margin-top:0.4rem; font-size:0.9rem;'>AI-powered pitch intelligence grounded in real market data.</p>
    </div>
    <hr/>
    """, unsafe_allow_html=True)

    # ── Input form ────────────────────────────────────────────────────────────
    with st.container():
        st.markdown("#### Client Brief")
        col1, col2 = st.columns(2)
        with col1:
            client_name = st.text_input("Client / Brand Name", placeholder="e.g. Etihad Airways")
            market = st.text_input("Market / Region", placeholder="e.g. UAE, Saudi Arabia, MENA")
        with col2:
            industry = st.text_input("Industry / Category", placeholder="e.g. Aviation, Retail Banking, QSR")
            website = st.text_input("Client Website", placeholder="e.g. etihad.com")

    st.markdown("---")

    # ── Options ───────────────────────────────────────────────────────────────
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("#### Verticals to Generate")
        selected_verticals = st.multiselect(
            "Select one or more",
            options=list(VERTICALS.keys()),
            default=list(VERTICALS.keys()),
            label_visibility="collapsed",
        )
    with col_b:
        st.markdown("#### Output Options")
        stat_format = st.radio(
            "Market stats format",
            ["Headline stats with sources", "Narrative paragraph"],
            horizontal=True,
        )
        include_narrative = st.checkbox("Include narrative paragraph per vertical", value=False)

    st.markdown("---")

    # ── Generate ──────────────────────────────────────────────────────────────
    ready = all([client_name, market, industry, selected_verticals])
    generate_btn = st.button("⚡ Generate Insights", disabled=not ready, use_container_width=False)

    if not ready and not generate_btn:
        st.caption("Fill in all fields and select at least one vertical to generate insights.")

    if generate_btn and ready:
        client = get_gemini_client()
        results = {}

        # Step 1: Market stats
        with st.spinner(f"Researching {industry} market data in {market}…"):
            stats_raw = call_gemini(client, market_stats_prompt(client_name, market, industry, website, stat_format))
            parsed_stats = parse_json_block(stats_raw)
            if parsed_stats:
                results["stats"] = parsed_stats
            else:
                results["stats_raw"] = stats_raw

        # Step 2: Verticals
        results["verticals"] = {}
        for vertical in selected_verticals:
            focus = VERTICALS[vertical]["focus"]
            with st.spinner(f"Generating {vertical} insights…"):
                v_raw = call_gemini(client, vertical_insights_prompt(
                    client_name, market, industry, website, vertical, focus, include_narrative
                ))
                parsed_v = parse_json_block(v_raw)
                if parsed_v:
                    results["verticals"][vertical] = parsed_v
                else:
                    results["verticals"][vertical] = {"raw": v_raw}

        st.session_state["results"] = results
        st.session_state["meta"] = {
            "client_name": client_name,
            "market": market,
            "industry": industry,
            "website": website,
        }

    # ── Display results ───────────────────────────────────────────────────────
    if "results" in st.session_state:
        results = st.session_state["results"]
        meta = st.session_state["meta"]
        client_name = meta["client_name"]
        market = meta["market"]
        industry = meta["industry"]

        st.markdown("---")
        st.markdown(f"""
        <div style='margin-bottom:1.5rem;'>
          <span class='badge'>Generated</span>
          <h2 style='font-size:1.6rem; font-weight:700; margin:0.5rem 0 0.2rem 0;'>{client_name} — {market}</h2>
          <p style='color:#555; font-size:0.85rem; margin:0;'>{industry} · {datetime.now().strftime('%d %B %Y, %H:%M')}</p>
        </div>
        """, unsafe_allow_html=True)

        # Market stats
        if "stats" in results:
            st.markdown("### 📊 Market Intelligence")
            stats = results["stats"]
            if isinstance(stats, list):
                cols = st.columns(2)
                for i, s in enumerate(stats):
                    if isinstance(s, dict):
                        with cols[i % 2]:
                            st.markdown(f"""
                            <div class='stat-card'>
                              <div style='font-size:1.1rem; font-weight:700; color:#b8ff57; margin-bottom:0.3rem;'>{s.get('stat','')}</div>
                              <div style='font-size:0.75rem; color:#555; margin-bottom:0.4rem;'>{s.get('source','')}</div>
                              <div style='font-size:0.85rem; color:#aaa;'>{s.get('context','')}</div>
                            </div>
                            """, unsafe_allow_html=True)
            elif isinstance(stats, dict) and "narrative" in stats:
                st.markdown(f"""
                <div class='stat-card'>
                  <div style='font-size:0.9rem; color:#ccc; line-height:1.7;'>{stats['narrative']}</div>
                </div>
                """, unsafe_allow_html=True)
        elif "stats_raw" in results:
            with st.expander("Raw market stats output"):
                st.text(results["stats_raw"])

        # Verticals
        for vertical, data in results.get("verticals", {}).items():
            icon = VERTICALS.get(vertical, {}).get("icon", "")
            st.markdown(f"### {icon} {vertical}")

            if "raw" in data:
                with st.expander("Raw output"):
                    st.text(data["raw"])
                continue

            if data.get("headline"):
                st.markdown(f"""
                <div style='font-size:1.15rem; font-weight:700; color:#e8e8e8; border-left:3px solid #b8ff57; padding-left:0.8rem; margin-bottom:1rem;'>
                  {data['headline']}
                </div>
                """, unsafe_allow_html=True)

            if data.get("insights"):
                for ins in data["insights"]:
                    st.markdown(f"""
                    <div class='insight-card'>
                      <div style='font-size:0.9rem; color:#ccc; line-height:1.65;'>{ins}</div>
                    </div>
                    """, unsafe_allow_html=True)

            if data.get("narrative"):
                st.markdown(f"""
                <div class='stat-card' style='margin-top:0.5rem;'>
                  <div style='font-size:0.85rem; color:#888; font-style:italic; line-height:1.7;'>{data['narrative']}</div>
                </div>
                """, unsafe_allow_html=True)

            if data.get("recommendation"):
                st.markdown(f"""
                <div class='rec-box'>
                  <div style='font-size:0.7rem; letter-spacing:0.12em; color:#b8ff57; text-transform:uppercase; font-weight:700; margin-bottom:0.4rem;'>Strategic Recommendation</div>
                  <div style='font-size:0.9rem; color:#ddd; line-height:1.65;'>{data['recommendation']}</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("---")

        # ── Export ────────────────────────────────────────────────────────────
        st.markdown("### Export")
        col_dl1, col_dl2 = st.columns(2)

        with col_dl1:
            docx_bytes = generate_word_doc(client_name, market, industry, results)
            if docx_bytes:
                fname = f"EXD_Insights_{client_name.replace(' ','_')}_{market.replace(' ','_')}.docx"
                st.download_button(
                    label="⬇ Download Word Doc",
                    data=docx_bytes,
                    file_name=fname,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            else:
                st.caption("Word export unavailable — python-docx not installed.")

        with col_dl2:
            # Plain text fallback
            txt_lines = [f"EXD INSIGHTS — {client_name} | {market} | {industry}", "=" * 60, ""]
            if "stats" in results:
                txt_lines.append("MARKET INTELLIGENCE")
                txt_lines.append("-" * 40)
                stats = results["stats"]
                if isinstance(stats, list):
                    for s in stats:
                        if isinstance(s, dict):
                            txt_lines.append(f"• {s.get('stat','')} ({s.get('source','')})")
                            txt_lines.append(f"  {s.get('context','')}")
                elif isinstance(stats, dict) and "narrative" in stats:
                    txt_lines.append(stats["narrative"])
                txt_lines.append("")

            for vertical, data in results.get("verticals", {}).items():
                txt_lines.append(f"\n{vertical.upper()}")
                txt_lines.append("-" * 40)
                if data.get("headline"):
                    txt_lines.append(f"Headline: {data['headline']}")
                if data.get("insights"):
                    for ins in data["insights"]:
                        txt_lines.append(f"\n• {ins}")
                if data.get("recommendation"):
                    txt_lines.append(f"\nRecommendation: {data['recommendation']}")
                txt_lines.append("")

            txt_content = "\n".join(txt_lines)
            st.download_button(
                label="⬇ Download Text File",
                data=txt_content,
                file_name=f"EXD_Insights_{client_name.replace(' ','_')}.txt",
                mime="text/plain",
            )

if __name__ == "__main__":
    main()
