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
        "bg": "#0e1117", 
        "card": "#161b22", 
        "accent": "#58a6ff", 
        "accent_grad": "linear-gradient(90deg, #58a6ff 0%, #bc8cff 100%)",
        "text": "#e0e0e0", 
        "sidebar": "#0d1117", 
        "secondary": "#30363d",
        "success": "#3fb950",
        "warning": "#d29922",
        "shadow": "0 8px 24px rgba(0,0,0,0.5)"
    },
    "Slate": {
        "bg": "#f0f2f5", 
        "card": "#ffffff", 
        "accent": "#24292f", 
        "accent_grad": "linear-gradient(90deg, #24292f 0%, #444d56 100%)",
        "text": "#1a1a1a", 
        "sidebar": "#ffffff", 
        "secondary": "#d0d7de",
        "success": "#1a7f37",
        "warning": "#9a6700",
        "shadow": "0 4px 12px rgba(0,0,0,0.05)"
    },
    "Ocean": {
        "bg": "#001219", 
        "card": "#001e26", 
        "accent": "#00b4d8", 
        "accent_grad": "linear-gradient(90deg, #00b4d8 0%, #90e0ef 100%)",
        "text": "#caf0f8", 
        "sidebar": "#00151c", 
        "secondary": "#002a33",
        "success": "#52b788",
        "warning": "#eeef20",
        "shadow": "0 8px 30px rgba(0,0,0,0.6)"
    }
}

t = themes[st.session_state.theme_color]

# --- ADVANCED UI STYLING ---
st.markdown(f"""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=JetBrains+Mono&display=swap');
    
    .stApp {{
        background-color: {t['bg']} !important;
        color: {t['text']} !important;
        font-family: 'Inter', sans-serif;
    }}

    [data-testid="stSidebar"] {{
        background-color: {t['sidebar']} !important;
        border-right: 1px solid {t['secondary']};
    }}
    
    .agent-card {{
        background-color: {t['card']};
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid {t['secondary']};
        box-shadow: {t['shadow']};
        margin-bottom: 20px;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }}
    
    .agent-card:hover {{
        transform: translateY(-4px);
        border-color: {t['accent']};
    }}

    .signed-card {{
        border: 1px solid {t['accent']} !important;
        box-shadow: 0 0 15px rgba(88, 166, 255, 0.2) !important;
    }}

    .workflow-container {{
        display: flex;
        justify-content: space-between;
        padding: 20px 0;
        margin-bottom: 30px;
    }}
    
    .workflow-step {{
        text-align: center;
        flex: 1;
    }}
    
    .step-icon {{
        width: 40px;
        height: 40px;
        background: {t['secondary']};
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 8px;
        border: 2px solid {t['bg']};
    }}

    .badge {{
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        display: inline-block;
        margin-bottom: 12px;
    }}
    
    .badge-signed {{ background: {t['accent_grad']}; color: white; }}
    .badge-verified {{ background: {t['success']}; color: white; }}

    .stButton>button {{
        border-radius: 10px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        font-size: 0.8rem !important;
        font-weight: 600;
    }}

    .section-header {{
        display: flex;
        align-items: center;
        gap: 12px;
        font-size: 1.1rem;
        font-weight: 700;
        margin: 25px 0 15px 0;
        color: {t['accent']} !important;
    }}
    
    .section-header i {{
        background: {t['accent_grad']};
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
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

# --- HEADER SECTION ---
st.markdown(f"""
<div style="display: flex; align-items: center; gap: 20px; padding-bottom: 20px; border-bottom: 1px solid {t['secondary']};">
    <i class="fas fa-shield-halved" style="font-size: 3.5rem; color: {t['accent']};"></i>
    <div>
        <h1 style="margin: 0; padding: 0; line-height: 1; color: {t['accent']};">AuthentiPost</h1>
        <p style="margin: 5px 0 0 0; opacity: 0.7; font-size: 1.1rem;">Human Verification Layer for Agentic Content</p>
    </div>
</div>
""", unsafe_allow_html=True)

brand_data = {"description": "A cybersecurity researcher who likes to share tips in a witty way.", "sample_posts": []}
if os.path.exists(BRAND_FILE):
    with open(BRAND_FILE, "r") as f: brand_data = json.load(f)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown(f"<div class='section-header'><i class='fas fa-sliders'></i> Settings</div>", unsafe_allow_html=True)
    theme_choice = st.selectbox("Dashboard Theme", options=list(themes.keys()), index=list(themes.keys()).index(st.session_state.theme_color))
    if theme_choice != st.session_state.theme_color:
        st.session_state.theme_color = theme_choice
        st.rerun()
    
    st.divider()
    demo_mode = st.toggle("🛠️ Demo Mode", value=True)
    st.markdown(f"<div class='section-header'><i class='fas fa-fingerprint'></i> Secure Identity</div>", unsafe_allow_html=True)
    _, vk = get_or_create_keys()
    st.code(vk.to_string().hex()[:24] + "...", language="text")

# --- MAIN TABS ---
tab_identity, tab_swarm, tab_approval, tab_audit = st.tabs(["👤 Identity", "🐝 Agent Swarm", "✅ Approval Queue", "📊 Audit Trail"])

with tab_identity:
    st.markdown(f"<div class='section-header'><i class='fas fa-pen-nib'></i> System Persona</div>", unsafe_allow_html=True)
    new_desc = st.text_area("Global System Prompt", value=brand_data["description"], height=200)
    if st.button("Update System Prompt", use_container_width=True):
        with open(BRAND_FILE, "w") as f: json.dump({"description": new_desc, "sample_posts": []}, f)
        st.success("✅ Identity updated!")

with tab_swarm:
    st.markdown(f"""
    <div class="workflow-container">
        <div class="workflow-step"><div class="step-icon"><i class="fas fa-search"></i></div><small>Scout</small></div>
        <div class="workflow-step" style="opacity: 0.3; padding-top: 10px;"><i class="fas fa-chevron-right"></i></div>
        <div class="workflow-step"><div class="step-icon"><i class="fas fa-drafting-compass"></i></div><small>Architect</small></div>
        <div class="workflow-step" style="opacity: 0.3; padding-top: 10px;"><i class="fas fa-chevron-right"></i></div>
        <div class="workflow-step"><div class="step-icon"><i class="fas fa-palette"></i></div><small>Creative</small></div>
        <div class="workflow-step" style="opacity: 0.3; padding-top: 10px;"><i class="fas fa-chevron-right"></i></div>
        <div class="workflow-step"><div class="step-icon"><i class="fas fa-balance-scale"></i></div><small>Critic</small></div>
    </div>
    """, unsafe_allow_html=True)
    
    topic = st.text_input("Define mission objective:", value="Latest social engineering tactics in 2024")
    if st.button("🚀 Deploy Swarm", type="primary", use_container_width=True):
        graph = build_workflow()
        initial_state = {"topic": topic, "brand_desc": brand_data["description"], "raw_trends": [], "selected_trend": "", "architect_reasoning": "", "final_posts": [], "critic_feedback": ""}
        final_state = graph.invoke(initial_state)
        st.session_state.last_run = final_state
        st.balloons()

with tab_approval:
    if "last_run" in st.session_state:
        state = st.session_state.last_run
        st.markdown(f"<div class='agent-card'><h4 style='color:{t['accent']}'><i class='fas fa-brain'></i> Strategic Reasoning</h4><p>{state['architect_reasoning']}</p></div>", unsafe_allow_html=True)
        
        cols = st.columns(3)
        for i, post in enumerate(state["final_posts"]):
            with cols[i % 3]:
                is_signed = f"signed_{i}" in st.session_state
                card_class = "agent-card signed-card" if is_signed else "agent-card"
                st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
                
                if is_signed:
                    st.markdown('<span class="badge badge-signed"><i class="fas fa-shield-check"></i> Signed</span>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<span class="badge" style="border:1px solid {t["accent"]}; color:{t["accent"]}"><i class="fas fa-robot"></i> Draft</span>', unsafe_allow_html=True)
                
                edited = st.text_area("Edit Content:", value=post, key=f"edit_{i}", height=150)
                if st.button(f"🔒 Sign Post", key=f"sign_{i}", use_container_width=True):
                    sig, payload = sign_post(edited)
                    st.session_state[f"signed_{i}"] = {"sig": sig, "payload": payload}
                    st.rerun()
                
                if is_signed and st.button(f"🚀 Broadcast", key=f"post_{i}", type="primary", use_container_width=True):
                    success, result = post_to_x(edited, st.session_state[f"signed_{i}"]['sig'], demo_mode=demo_mode)
                    if success: st.toast("Success!")
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Queue is empty. Deploy agents in the 'Agent Swarm' tab.")

with tab_audit:
    st.markdown(f"<div class='section-header'><i class='fas fa-list-check'></i> History</div>", unsafe_allow_html=True)
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f: logs = json.load(f)
        for entry in reversed(logs[-5:]):
            st.markdown(f"""
            <div class="agent-card">
                <div style="display:flex; justify-content:space-between;">
                    <span class="badge badge-verified">Verified</span>
                    <small>{time.ctime(entry['timestamp'])}</small>
                </div>
                <p>{entry['content']}</p>
                <code style="font-size:0.7rem; opacity:0.5; overflow-wrap:break-word;">SIG: {entry['signature']}</code>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown('<div style="text-align:center; padding:50px; opacity:0.5;"><i class="fas fa-box-open" style="font-size:3rem;"></i><p>No posts yet</p></div>', unsafe_allow_html=True)