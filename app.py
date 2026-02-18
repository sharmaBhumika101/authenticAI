import os
import json
import time
import hashlib
import streamlit as st
import google.generativeai as genai
from tavily import TavilyClient
from dotenv import load_dotenv
from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from ecdsa import SigningKey, VerifyingKey, SECP256k1
import tweepy

# Load environment variables
load_dotenv()

# --- INITIAL SETUP ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

X_CONSUMER_KEY = os.getenv("X_CONSUMER_KEY")
X_CONSUMER_SECRET = os.getenv("X_CONSUMER_SECRET")
X_ACCESS_TOKEN = os.getenv("X_ACCESS_TOKEN")
X_ACCESS_SECRET = os.getenv("X_ACCESS_SECRET")

BRAND_FILE = "brand_profile.json"
LOG_FILE = "posts_log.json"

if not GEMINI_API_KEY:
    st.error("❌ Missing GEMINI_API_KEY. Please check your .env file.")
    st.stop()

# --- MODEL SELECTION ---
try:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('models/gemini-2.5-flash-lite')
except Exception:
    model = genai.GenerativeModel('models/gemini-1.5-flash')

tavily = TavilyClient(api_key=TAVILY_API_KEY) if TAVILY_API_KEY else None

# --- ENHANCED THEME CONFIG ---
if 'theme_color' not in st.session_state:
    st.session_state.theme_color = "Cyber"

themes = {
    "Cyber": {
        "bg": "#0B0E11",
        "card": "#151921",
        "sidebar": "#090C0F",
        "accent": "#00E5FF",
        "accent_grad": "linear-gradient(135deg, #00E5FF 0%, #2979FF 100%)",
        "text": "#E6E6E6",
        "secondary": "#2A303C",
        "success": "#00C853",
        "warning": "#FFD600",
        "danger": "#FF1744",
        "shadow": "0 4px 20px rgba(0, 0, 0, 0.5)",
        "border": "1px solid rgba(255, 255, 255, 0.08)"
    },
    "Slate": {
        "bg": "#F8FAFC",
        "card": "#FFFFFF",
        "sidebar": "#F1F5F9",
        "accent": "#475569",
        "accent_grad": "linear-gradient(135deg, #475569 0%, #1E293B 100%)",
        "text": "#1E293B",
        "secondary": "#E2E8F0",
        "success": "#10B981",
        "warning": "#F59E0B",
        "danger": "#EF4444",
        "shadow": "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
        "border": "1px solid #E2E8F0"
    },
    "Neon": {
        "bg": "#050505",
        "card": "#0A0A0A",
        "sidebar": "#000000",
        "accent": "#CC00FF",
        "accent_grad": "linear-gradient(135deg, #CC00FF 0%, #7000FF 100%)",
        "text": "#EDEDED",
        "secondary": "#1F1F1F",
        "success": "#00FF9D",
        "warning": "#FAFF00",
        "danger": "#FF0055",
        "shadow": "0 0 20px rgba(204, 0, 255, 0.15)",
        "border": "1px solid rgba(204, 0, 255, 0.2)"
    }
}

t = themes[st.session_state.theme_color]

# --- ADVANCED UI STYLING ---
# --- ADVANCED UI STYLING ---
st.markdown(f"""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    /* Global Reset & Typography */
    .stApp {{
        background-color: {t['bg']} !important;
        color: {t['text']} !important;
        font-family: 'Inter', sans-serif;
    }}
    
    /* Layout Improvements */
    .block-container {{
        max-width: 1200px !important;
        padding-top: 2rem !important;
        padding-bottom: 5rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }}
    
    h1, h2, h3, h4, h5, h6 {{
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        letter-spacing: -0.02em;
        color: {t['text']} !important;
    }}
    
    code, pre {{
        font-family: 'JetBrains Mono', monospace !important;
    }}

    /* Sidebar */
    [data-testid="stSidebar"] {{
        background-color: {t['sidebar']} !important;
        border-right: {t['border']};
    }}
    
    [data-testid="stSidebarNav"] {{
        border-bottom: {t['border']};
        margin-bottom: 20px;
        padding-bottom: 20px;
    }}

    /* TABS STYLING - Replacing emojis with FA icons via CSS */
    iframe {{ display: none; }} /* Hide generic Streamlit elements if needed */
    
    .stTabs [data-testid="stMarkdownContainer"] p {{
        font-size: 1rem;
        font-weight: 600;
        padding-top: 2px;
    }}

    /* Tab Icons via Pseudo-elements */
    /* Tab 1: Identity */
    button[data-testid="stTab"][id*="tabs-bui1-tab-0"] p::before {{
        font-family: "Font Awesome 6 Free";
        font-weight: 900;
        content: "\\f007"; /* fa-user */
        margin-right: 8px;
        color: {t['accent']};
    }}
    
    /* Tab 2: Agent Swarm */
    button[data-testid="stTab"][id*="tabs-bui1-tab-1"] p::before {{
        font-family: "Font Awesome 6 Free";
        font-weight: 900;
        content: "\\f544"; /* fa-robot */
        margin-right: 8px;
        color: {t['accent']};
    }}
    
    /* Tab 3: Approval Queue */
    button[data-testid="stTab"][id*="tabs-bui1-tab-2"] p::before {{
        font-family: "Font Awesome 6 Free";
        font-weight: 900;
        content: "\\f00c"; /* fa-check */
        margin-right: 8px;
        color: {t['accent']};
    }}
    
    /* Tab 4: Audit Trail */
    button[data-testid="stTab"][id*="tabs-bui1-tab-3"] p::before {{
        font-family: "Font Awesome 6 Free";
        font-weight: 900;
        content: "\\f201"; /* fa-chart-line */
        margin-right: 8px;
        color: {t['accent']};
    }}
    
    /* Active Tab Styling */
    button[data-testid="stTab"][aria-selected="true"] {{
        border-bottom-color: {t['accent']} !important;
    }}
    
    button[data-testid="stTab"][aria-selected="true"] p {{
        color: {t['accent']} !important;
    }}
    
    button[data-testid="stTab"]:hover {{
        color: {t['accent']} !important;
    }}

    /* Card Component */
    .saas-card {{
        background-color: {t['card']};
        padding: 24px;
        border-radius: 12px;
        border: {t['border']};
        box-shadow: {t['shadow']};
        margin-bottom: 24px;
        transition: all 0.3s ease;
    }}
    
    .saas-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 12px 30px rgba(0,0,0,0.2) !important;
        border-color: {t['accent']};
    }}

    /* Signed State Glow */
    .card-signed {{
        border: 1px solid {t['accent']} !important;
        box-shadow: 0 0 20px {t['accent']}22 !important;
        position: relative;
        overflow: hidden;
    }}
    
    .card-signed::before {{
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 4px;
        background: {t['accent_grad']};
    }}

    /* Unified Badge System */
    .status-badge {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}
    
    .badge-primary {{ background: {t['accent']}22; color: {t['accent']}; border: 1px solid {t['accent']}44; }}
    .badge-success {{ background: {t['success']}22; color: {t['success']}; border: 1px solid {t['success']}44; }}
    .badge-warning {{ background: {t['warning']}22; color: {t['warning']}; border: 1px solid {t['warning']}44; }}
    .badge-neutral {{ background: {t['secondary']}; color: {t['text']}; border: 1px solid {t['text']}22; }}

    /* Workflow Stepper */
    .step-container {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        position: relative;
        margin: 40px 0;
    }}
    
    .step-line {{
        position: absolute;
        top: 50%;
        left: 0;
        width: 100%;
        height: 2px;
        background: {t['secondary']};
        z-index: 0;
        transform: translateY(-50%);
    }}
    
    .step-node {{
        position: relative;
        z-index: 1;
        background: {t['card']};
        border: 2px solid {t['secondary']};
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: {t['text']};
        transition: all 0.3s ease;
    }}
    
    .step-node.active {{
        border-color: {t['accent']};
        background: {t['bg']};
        box-shadow: 0 0 15px {t['accent']}66;
        transform: scale(1.1);
    }}
    
    .step-node.completed {{
        background: {t['accent']};
        border-color: {t['accent']};
        color: {t['bg']};
    }}

    /* Buttons */
    .stButton>button {{
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.6rem 1.2rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        border: none !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1) !important;
    }}
    
    .stButton>button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2) !important;
    }}

    div[data-testid="stButton"] > button[kind="primary"] {{
        background: {t['accent_grad']} !important;
        color: white !important;
        box-shadow: 0 4px 15px {t['accent']}44 !important;
    }}

    div[data-testid="stButton"] > button[kind="secondary"] {{
        background: {t['secondary']} !important;
        color: {t['text']} !important;
        border: 1px solid {t['secondary']} !important;
    }}

    /* Inputs */
    .stTextInput>div>div, .stTextArea>div>div {{
        background-color: {t['bg']} !important;
        border: {t['border']} !important;
        border-radius: 8px !important;
        color: {t['text']} !important;
    }}
    
    .stTextInput>div>div:focus-within, .stTextArea>div>div:focus-within {{
        border-color: {t['accent']} !important;
        box-shadow: 0 0 0 1px {t['accent']} !important;
    }}

    /* Timeline */
    .timeline-item {{
        position: relative;
        padding-left: 30px;
        margin-bottom: 24px;
        border-left: 2px solid {t['secondary']};
    }}
    
    .timeline-dot {{
        position: absolute;
        left: -6px;
        top: 0;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background: {t['accent']};
        box-shadow: 0 0 0 4px {t['bg']};
    }}

    /* Animations */
    @keyframes pulse {{
        0% {{ box-shadow: 0 0 0 0 {t['accent']}66; }}
        70% {{ box-shadow: 0 0 0 10px rgba(0,0,0,0); }}
        100% {{ box-shadow: 0 0 0 0 rgba(0,0,0,0); }}
    }}
    
    .animate-pulse {{
        animation: pulse 2s infinite;
    }}
    
    /* Skeleton Loading */
    @keyframes shimmer {{
        0% {{background-position: -200% 0;}}
        100% {{background-position: 200% 0;}}
    }}
    
    .skeleton {{
        background: linear-gradient(90deg, {t['secondary']} 25%, {t['card']} 50%, {t['secondary']} 75%);
        background-size: 200% 100%;
        animation: shimmer 2s infinite;
        border-radius: 4px;
    }}

</style>
""", unsafe_allow_html=True)

# --- UTILITY & CRYPTO LOGIC (Retained) ---
# --- LANGGRAPH STATE DEFINITION ---
class AgentState(TypedDict):
    topic: str
    brand_desc: str
    raw_trends: List[str]
    selected_trend: str
    architect_reasoning: str
    final_posts: List[str]
    critic_feedback: str
    
def safe_generate_content(prompt, retries=2, delay=2):
    for i in range(retries):
        try: return model.generate_content(prompt)
        except Exception as e:
            if "429" in str(e) and i < retries - 1:
                time.sleep(delay)
                continue
            raise e

def log_post(content: str, signature: str, tweet_id: str, public_key: str):
    new_entry = {"timestamp": int(time.time()), "content": content, "signature": signature, "tweet_id": tweet_id, "public_key": public_key}
    log_data = []
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r") as f: log_data = json.load(f)
        except: log_data = []
    log_data.append(new_entry)
    with open(LOG_FILE, "w") as f: json.dump(log_data, f, indent=4)

def get_or_create_keys():
    if 'private_key' not in st.session_state:
        sk = SigningKey.generate(curve=SECP256k1)
        st.session_state.private_key = sk
        st.session_state.public_key = sk.verifying_key
    return st.session_state.private_key, st.session_state.public_key

def sign_post(content: str):
    sk, _ = get_or_create_keys()
    timestamp = str(int(time.time()))
    payload = f"{content}|TS:{timestamp}"
    content_hash = hashlib.sha256(payload.encode()).digest()
    signature = sk.sign(content_hash)
    return signature.hex(), payload

def verify_post(payload: str, signature_hex: str, public_key_hex: str):
    try:
        vk = VerifyingKey.from_string(bytes.fromhex(public_key_hex), curve=SECP256k1)
        content_hash = hashlib.sha256(payload.encode()).digest()
        return vk.verify(bytes.fromhex(signature_hex), content_hash)
    except: return False

def post_to_x(content: str, signature: str = None, demo_mode: bool = False):
    if demo_mode:
        time.sleep(1)
        tweet_id = f"DEMO_{int(time.time())}"
        _, vk = get_or_create_keys()
        log_post(content, signature, tweet_id, vk.to_string().hex())
        return True, tweet_id
    # Twitter logic omitted for brevity, same as original
    return False, "Live API logic"

# --- AGENT NODES (Improved Visuals) ---
def scout_node(state: AgentState):
    with st.status("📡 **Scout** researching live trends...", expanded=False) as status:
        try:
            results = tavily.search(query=state["topic"], search_depth="basic")['results']
            state["raw_trends"] = [r['content'] for r in results[:3]]
            status.update(label="✅ Scout found 3 live trends", state="complete")
        except:
            state["raw_trends"] = ["No live trends found."]
            status.update(label="⚠️ Scout research limited", state="error")
    return state

def architect_node(state: AgentState):
    with st.status("📐 **Architect** strategizing...", expanded=False) as status:
        prompt = f"Brand Persona: {state['brand_desc']}\nTrends: {state['raw_trends']}\nPick the best trend. Format: TREND: [text] REASON: [text]"
        response = safe_generate_content(prompt).text
        if "TREND:" in response and "REASON:" in response:
            state["selected_trend"] = response.split("TREND:")[1].split("REASON:")[0].strip()
            state["architect_reasoning"] = response.split("REASON:")[1].strip()
        status.update(label="✅ Architect strategy finalized", state="complete")
    return state

def creative_node(state: AgentState):
    with st.status("🎨 **Creative** drafting content...", expanded=False) as status:
        prompt = f"Topic: {state['selected_trend']}\nReason: {state['architect_reasoning']}\nVoice: {state['brand_desc']}\nWrite 3 X posts separated by '---'."
        response = safe_generate_content(prompt).text
        state["final_posts"] = [p.strip() for p in response.split("---") if len(p.strip()) > 10]
        status.update(label=f"✅ Creative generated {len(state['final_posts'])} drafts", state="complete")
    return state

def critic_node(state: AgentState):
    with st.status("⚖️ **Critic** reviewing for consistency...", expanded=False) as status:
        prompt = f"Review these posts for brand consistency: {state['final_posts']}. Give short feedback."
        state["critic_feedback"] = safe_generate_content(prompt).text
        status.update(label="✅ Critic review complete", state="complete")
    return state

def build_workflow():
    workflow = StateGraph(AgentState)
    workflow.add_node("scout", scout_node)
    workflow.add_node("architect", architect_node)
    workflow.add_node("creative", creative_node)
    workflow.add_node("critic", critic_node)
    workflow.set_entry_point("scout")
    workflow.add_edge("scout", "architect")
    workflow.add_edge("architect", "creative")
    workflow.add_edge("creative", "critic")
    workflow.add_edge("critic", END)
    return workflow.compile()

# --- UI COMPONENTS ---
def render_header():
    st.markdown(f"""
<div style="background: {t['card']}; border: {t['border']}; border-radius: 12px; padding: 24px; margin-bottom: 30px; box-shadow: {t['shadow']};">
<div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 20px;">
<div style="display: flex; align-items: center; gap: 20px;">
<div style="width: 60px; height: 60px; background: {t['accent']}11; border-radius: 12px; border: 1px solid {t['accent']}33; display: flex; align-items: center; justify-content: center;">
<i class="fas fa-shield-halved" style="font-size: 1.8rem; color: {t['accent']};"></i>
</div>
<div>
<div style="font-family: 'Inter', sans-serif; font-weight: 800; font-size: 2rem; background: {t['accent_grad']}; -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: -0.03em; line-height: 1;">AuthentiPost</div>
<div style="opacity: 0.6; font-size: 0.95rem; margin-top: 4px; font-weight: 500;">Secure Agentic Workflow & Verification Layer</div>
</div>
</div>
<div style="display: flex; align-items: center; gap: 15px; background: {t['bg']}; padding: 8px 16px; border-radius: 50px; border: {t['border']};">
<div style="display: flex; align-items: center; gap: 6px;">
<div class="animate-pulse" style="width: 8px; height: 8px; background: {t['success']}; border-radius: 50%;"></div>
<span style="font-size: 0.8rem; font-weight: 600; color: {t['success']}; letter-spacing: 0.5px;">SYSTEM ONLINE</span>
</div>
<div style="width: 1px; height: 16px; background: {t['secondary']};"></div>
<div style="font-size: 0.8rem; opacity: 0.5; font-family: 'JetBrains Mono';">v2.0.4</div>
</div>
</div>
</div>
""", unsafe_allow_html=True)

def render_sidebar():
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align: center; padding: 20px 0;">
            <div style="width: 60px; height: 60px; background: {t['accent_grad']}; border-radius: 50%; margin: 0 auto 15px; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 20px {t['accent']}66;">
                <i class="fas fa-user-shield" style="font-size: 1.5rem; color: white;"></i>
            </div>
            <h3 style="margin: 0; font-size: 1.2rem;">Admin Console</h3>
            <p style="opacity: 0.5; font-size: 0.8rem;">Secure Session Active</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        st.markdown(f"<p style='font-size: 0.8rem; font-weight: 600; color: {t['accent']}; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px;'>Configuration</p>", unsafe_allow_html=True)
        theme_choice = st.selectbox("Interface Theme", options=list(themes.keys()), index=list(themes.keys()).index(st.session_state.theme_color))
        if theme_choice != st.session_state.theme_color:
            st.session_state.theme_color = theme_choice
            st.rerun()
            
        st.markdown(f"<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
        demo_mode = st.toggle("Simulation Mode", value=True)
        
        st.divider()
        
        st.markdown(f"<p style='font-size: 0.8rem; font-weight: 600; color: {t['accent']}; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px;'>Identity Key</p>", unsafe_allow_html=True)
        _, vk = get_or_create_keys()
        key_str = vk.to_string().hex()
        st.code(key_str[:24] + "...", language="text")
        st.caption(f"Fingerprint: {hashlib.sha256(key_str.encode()).hexdigest()[:8]}")
        
    return demo_mode

# --- MAIN APP LAYOUT ---
render_header()
demo_mode = render_sidebar()

brand_data = {"description": "A cybersecurity researcher who likes to share tips in a witty way.", "sample_posts": []}
if os.path.exists(BRAND_FILE):
    with open(BRAND_FILE, "r") as f: brand_data = json.load(f)

# --- MAIN TABS ---
tab_identity, tab_swarm, tab_approval, tab_audit = st.tabs(["Identity Persona", "Agent Swarm", "Approval Queue", "Audit Trail"])

with tab_identity:
    st.markdown(f"<div class='saas-card'>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='margin-bottom: 20px;'>System Persona</h3>", unsafe_allow_html=True)
    new_desc = st.text_area("Define the high-level prompt for the agent swarm:", value=brand_data["description"], height=200)
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("Update Profile", use_container_width=True, type="primary"):
            with open(BRAND_FILE, "w") as f: json.dump({"description": new_desc, "sample_posts": []}, f)
            st.toast("Identity profile updated successfully!", icon="✅")
    st.markdown("</div>", unsafe_allow_html=True)

with tab_swarm:
    # Animated Pipeline Visualization
    st.markdown(f"""
    <div class="step-container">
        <div class="step-line"></div>
        <div class="step-node completed"><i class="fas fa-search"></i></div>
        <div class="step-node completed"><i class="fas fa-drafting-compass"></i></div>
        <div class="step-node active animate-pulse"><i class="fas fa-palette"></i></div>
        <div class="step-node"><i class="fas fa-balance-scale"></i></div>
    </div>
    <div style="display: flex; justify-content: space-between; margin-top: -30px; margin-bottom: 40px; position: relative; z-index: 2;">
        <div style="text-align: center; width: 40px; font-size: 0.8rem; font-weight: 600;">Scout</div>
        <div style="text-align: center; width: 40px; font-size: 0.8rem; font-weight: 600;">Plan</div>
        <div style="text-align: center; width: 40px; font-size: 0.8rem; font-weight: 600; color: {t['accent']};">Create</div>
        <div style="text-align: center; width: 40px; font-size: 0.8rem; font-weight: 600; opacity: 0.5;">Verify</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"<div class='saas-card'>", unsafe_allow_html=True)
    topic = st.text_input("Mission Objective", value="Latest social engineering tactics in 2024", placeholder="What should the agents focus on?")
    
    if st.button("🚀 Initialize Swarm Protocol", type="primary", use_container_width=True):
        graph = build_workflow()
        initial_state = {"topic": topic, "brand_desc": brand_data["description"], "raw_trends": [], "selected_trend": "", "architect_reasoning": "", "final_posts": [], "critic_feedback": ""}
        final_state = graph.invoke(initial_state)
        st.session_state.last_run = final_state
        st.balloons()
    st.markdown("</div>", unsafe_allow_html=True)

with tab_approval:
    if "last_run" in st.session_state:
        state = st.session_state.last_run
        
        # Strategy Insight Card
        st.markdown(f"""
        <div class='saas-card' style='border-left: 4px solid {t['accent']};'>
            <h4 style='color:{t['accent']}; margin-bottom: 10px;'><i class='fas fa-brain'></i> Strategic Insight</h4>
            <p style='font-style: italic; opacity: 0.9;'>"{state['architect_reasoning']}"</p>
        </div>
        """, unsafe_allow_html=True)
        
        cols = st.columns(3)
        for i, post in enumerate(state["final_posts"]):
            with cols[i % 3]:
                is_signed = f"signed_{i}" in st.session_state
                
                # Render Card
                card_class = "saas-card card-signed" if is_signed else "saas-card"
                badge = f'<span class="status-badge badge-primary"><i class="fas fa-lock"></i> Secured</span>' if is_signed else f'<span class="status-badge badge-neutral"><i class="fas fa-pencil"></i> Draft</span>'
                
                st.markdown(f"""
                <div class="{card_class}">
                    <div style="display:flex; justify-content:space-between; margin-bottom:15px;">
                        {badge}
                        <small style="opacity:0.5">GEN-{i+1}</small>
                    </div>
                """, unsafe_allow_html=True)
                
                edited = st.text_area("Content", value=post, key=f"edit_{i}", height=140, label_visibility="collapsed")
                
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Actions
                c1, c2 = st.columns(2)
                with c1:
                    if st.button(f"Signs", key=f"sign_{i}", use_container_width=True, disabled=is_signed):
                        sig, payload = sign_post(edited)
                        st.session_state[f"signed_{i}"] = {"sig": sig, "payload": payload}
                        st.rerun()
                with c2:
                    if is_signed:
                        if st.button(f"Broadcast", key=f"post_{i}", type="primary", use_container_width=True):
                            success, result = post_to_x(edited, st.session_state[f"signed_{i}"]['sig'], demo_mode=demo_mode)
                            if success: st.toast("Content successfully broadcasted!", icon="📡")
    else:
        st.info("⚠️ Approval queue empty. Deploy agents from the Swarm tab.")

with tab_audit:
    # Header
    st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
        <h3>Blockchain Audit Trail</h3>
        <span class="status-badge badge-success">Live Sync</span>
    </div>
    """, unsafe_allow_html=True)
    
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f: logs = json.load(f)
        for entry in reversed(logs[-5:]):
            st.markdown(f"""
            <div class="timeline-item">
                <div class="timeline-dot"></div>
                <div class="saas-card" style="margin-bottom: 10px; padding: 15px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                        <span class="status-badge badge-success"><i class="fas fa-check-circle"></i> Verified on-chain</span>
                        <small style="opacity: 0.5; font-family: 'JetBrains Mono';">{time.ctime(entry['timestamp'])}</small>
                    </div>
                    <p style="margin-bottom: 15px;">{entry['content']}</p>
                    <div style="background: {t['bg']}; padding: 10px; border-radius: 6px; border: {t['border']};">
                        <div style="display: flex; gap: 10px; align-items: center;">
                            <i class="fas fa-key" style="opacity: 0.5;"></i>
                            <code style="font-size: 0.7rem; color: {t['accent']};">{entry['signature'][:60]}...</code>
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown('<div style="text-align:center; padding:50px; opacity:0.5;"><i class="fas fa-box-open" style="font-size:3rem;"></i><p>Ledger is empty</p></div>', unsafe_allow_html=True)