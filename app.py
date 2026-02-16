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

# X API Keys (OAuth 1.0a)
X_CONSUMER_KEY = os.getenv("X_CONSUMER_KEY")
X_CONSUMER_SECRET = os.getenv("X_CONSUMER_SECRET")
X_ACCESS_TOKEN = os.getenv("X_ACCESS_TOKEN")
X_ACCESS_SECRET = os.getenv("X_ACCESS_SECRET")

# File Paths
BRAND_FILE = "brand_profile.json"
LOG_FILE = "posts_log.json"

# Safety Check
if not GEMINI_API_KEY:
    st.error("❌ Missing GEMINI_API_KEY. Please check your .env file.")
    st.stop()

# --- MODEL SELECTION ---
try:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('models/gemini-2.5-flash-lite')
except Exception:
    model = genai.GenerativeModel('models/gemini-1.5-flash')

# Configure Tavily
tavily = TavilyClient(api_key=TAVILY_API_KEY) if TAVILY_API_KEY else None

# --- UI STATE & THEME CONFIG ---
if 'theme_color' not in st.session_state:
    st.session_state.theme_color = "Cyber"

themes = {
    "Cyber": {"bg": "#0e1117", "card": "#1a1c24", "accent": "#58a6ff", "text": "#e0e0e0", "sidebar": "#161b22", "secondary": "#30363d"},
    "Slate": {"bg": "#f8f9fa", "card": "#ffffff", "accent": "#24292f", "text": "#1a1a1a", "sidebar": "#f1f3f5", "secondary": "#d0d7de"},
    "Ocean": {"bg": "#001219", "card": "#001e26", "accent": "#00b4d8", "text": "#caf0f8", "sidebar": "#00151c", "secondary": "#002a33"}
}

t = themes[st.session_state.theme_color]

# --- UI STYLING & THEME ---
# Use a cleaner HTML structure for styling to prevent Markdown misinterpretation
st.markdown(f"""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
<style>
    .stApp {{
        background-color: {t['bg']} !important;
        color: {t['text']} !important;
    }}
    
    /* Force background for sidebar */
    [data-testid="stSidebar"] {{
        background-color: {t['sidebar']} !important;
        border-right: 1px solid {t['secondary']};
    }}

    .agent-card {{
        background-color: {t['card']};
        padding: 24px;
        border-radius: 12px;
        border: 1px solid {t['secondary']};
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }}
    
    .badge {{
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        margin-bottom: 12px;
        border: 1px solid transparent;
    }}
    
    .badge-signed {{
        background-color: rgba(88, 166, 255, 0.1);
        color: #58a6ff;
        border-color: #58a6ff;
    }}
    
    .badge-verified {{
        background-color: rgba(63, 185, 80, 0.1);
        color: #3fb950;
        border-color: #3fb950;
    }}

    .stButton>button {{
        border-radius: 8px;
        font-weight: 600;
        border: 1px solid {t['secondary']};
    }}
    
    h1, h2, h3, h4, .section-header {{
        color: {t['accent']} !important;
        margin-bottom: 0.5rem;
        font-weight: 700;
    }}
    
    .header-container {{
        display: flex;
        align-items: center;
        gap: 20px;
        padding: 10px 0;
        border-bottom: 1px solid {t['secondary']};
        margin-bottom: 20px;
    }}
    
    .status-indicator {{
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 0.85rem;
        margin: 10px 0;
    }}
    
    .dot {{
        height: 10px;
        width: 10px;
        border-radius: 50%;
    }}

    /* Specific fixes for text inputs in dark mode */
    .stTextArea textarea, .stTextInput input {{
        background-color: {t['secondary']} !important;
        color: {t['text']} !important;
    }}
</style>
""", unsafe_allow_html=True)

# --- UTILITY FUNCTIONS ---
def safe_generate_content(prompt, retries=2, delay=2):
    for i in range(retries):
        try:
            return model.generate_content(prompt)
        except Exception as e:
            if "429" in str(e) and i < retries - 1:
                time.sleep(delay)
                continue
            raise e

def log_post(content: str, signature: str, tweet_id: str, public_key: str):
    new_entry = {
        "timestamp": int(time.time()),
        "content": content,
        "signature": signature,
        "tweet_id": tweet_id,
        "public_key": public_key
    }
    log_data = []
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r") as f:
                log_data = json.load(f)
        except:
            log_data = []
    log_data.append(new_entry)
    with open(LOG_FILE, "w") as f:
        json.dump(log_data, f, indent=4)

# --- SOCIAL MEDIA LOGIC ---
def post_to_x(content: str, signature: str = None, demo_mode: bool = False):
    if demo_mode:
        time.sleep(1)
        tweet_id = f"DEMO_{int(time.time())}"
        _, vk = get_or_create_keys()
        log_post(content, signature, tweet_id, vk.to_string().hex())
        return True, tweet_id
    if not all([X_CONSUMER_KEY, X_CONSUMER_SECRET, X_ACCESS_TOKEN, X_ACCESS_SECRET]):
        return False, "Missing X API credentials in .env."
    try:
        client = tweepy.Client(consumer_key=X_CONSUMER_KEY, consumer_secret=X_CONSUMER_SECRET, access_token=X_ACCESS_TOKEN, access_token_secret=X_ACCESS_SECRET)
        final_text = content
        if signature:
            final_text += f"\n\n🛡️ Verified: https://authentic-ai.vercel.app/verify/{signature[:16]}"
        response = client.create_tweet(text=final_text)
        tweet_id = response.data['id']
        _, vk = get_or_create_keys()
        log_post(content, signature, str(tweet_id), vk.to_string().hex())
        return True, tweet_id
    except Exception as e:
        error_msg = str(e)
        if "402" in error_msg:
            return False, "Error 402: X API requires a paid tier. Use 'Demo Mode' in the sidebar."
        return False, error_msg

# --- CRYPTOGRAPHY LOGIC ---
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
    except Exception:
        return False

# --- BRAND DATA MANAGEMENT ---
def save_brand_profile(data):
    with open(BRAND_FILE, "w") as f:
        json.dump(data, f)
    st.success("✅ Brand identity saved!")

def load_brand_profile():
    if os.path.exists(BRAND_FILE):
        with open(BRAND_FILE, "r") as f:
            return json.load(f)
    return {"description": "A cybersecurity researcher who likes to share tips in a witty way.", "sample_posts": []}

# --- LANGGRAPH AGENTS ---
class AgentState(TypedDict):
    topic: str
    brand_desc: str
    raw_trends: List[str]
    selected_trend: str
    architect_reasoning: str
    final_posts: List[str]
    critic_feedback: str

def scout_node(state: AgentState):
    with st.status("🔍 Scout researching live trends...", expanded=False):
        try:
            results = tavily.search(query=state["topic"], search_depth="basic")['results']
            state["raw_trends"] = [r['content'] for r in results[:3]]
        except:
            state["raw_trends"] = ["No live trends found."]
    return state

def architect_node(state: AgentState):
    with st.status("📐 Architect strategizing...", expanded=False):
        prompt = f"Brand Persona: {state['brand_desc']}\nTrends: {state['raw_trends']}\nPick the best trend. Format: TREND: [text] REASON: [text]"
        response = safe_generate_content(prompt).text
        if "TREND:" in response and "REASON:" in response:
            state["selected_trend"] = response.split("TREND:")[1].split("REASON:")[0].strip()
            state["architect_reasoning"] = response.split("REASON:")[1].strip()
    return state

def creative_node(state: AgentState):
    with st.status("🎨 Creative drafting posts...", expanded=False):
        prompt = f"Topic: {state['selected_trend']}\nReason: {state['architect_reasoning']}\nVoice: {state['brand_desc']}\nWrite 3 X posts separated by '---'."
        response = safe_generate_content(prompt).text
        state["final_posts"] = [p.strip() for p in response.split("---") if len(p.strip()) > 10]
    return state

def critic_node(state: AgentState):
    with st.status("⚖️ Critic final review...", expanded=False):
        prompt = f"Review these posts for brand consistency: {state['final_posts']}. Give short feedback."
        state["critic_feedback"] = safe_generate_content(prompt).text
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
<div class="header-container">
    <i class="fas fa-shield-halved" style="font-size: 3.5rem; color: {t['accent']};"></i>
    <div>
        <h1 style="margin: 0; padding: 0; line-height: 1; color: {t['accent']};">AuthentiPost</h1>
        <p style="margin: 5px 0 0 0; opacity: 0.7; font-size: 1.1rem;">The Human Verification Layer for Agentic Content</p>
    </div>
</div>
""", unsafe_allow_html=True)

brand_data = load_brand_profile()
sk, vk = get_or_create_keys()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown(f"<div class='section-header'><i class='fas fa-sliders'></i> Dashboard Settings</div>", unsafe_allow_html=True)
    
    # Theme Switcher
    theme_choice = st.selectbox(
        "Application Theme", 
        options=list(themes.keys()), 
        index=list(themes.keys()).index(st.session_state.theme_color),
        key="theme_picker"
    )
    if theme_choice != st.session_state.theme_color:
        st.session_state.theme_color = theme_choice
        st.rerun()
    
    st.divider()
    
    # Connection Management
    demo_mode = st.toggle("🛠️ Demo Mode", value=True)
    x_keys_ready = all([X_CONSUMER_KEY, X_CONSUMER_SECRET, X_ACCESS_TOKEN, X_ACCESS_SECRET])
    
    status_color = "#3fb950" if demo_mode or x_keys_ready else "#f85149"
    st.markdown(f"""
    <div class="status-indicator">
        <div class="dot" style="background-color: {status_color}"></div>
        <span>System Status: <b>{'Online (Demo)' if demo_mode else ('Online (Live)' if x_keys_ready else 'Offline')}</b></span>
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    
    st.markdown(f"<div class='section-header'><i class='fas fa-id-badge'></i> Identity Profile</div>", unsafe_allow_html=True)
    st.caption("Human Public Key (ECDSA)")
    st.code(vk.to_string().hex()[:24] + "...", language="text")
    
    if st.button("🔄 Test API Connection", use_container_width=True):
        try:
            auth = tweepy.OAuth1UserHandler(X_CONSUMER_KEY, X_CONSUMER_SECRET, X_ACCESS_TOKEN, X_ACCESS_SECRET)
            api = tweepy.API(auth)
            api.verify_credentials()
            st.success("API Handshake Verified")
        except:
            st.error("Connection Failed")

# --- MAIN TABS ---
tab_identity, tab_swarm, tab_approval, tab_audit = st.tabs([
    "👤 Identity", 
    "🐝 Agent Swarm", 
    "✅ Approval Queue", 
    "📊 Audit Trail"
])

with tab_identity:
    col1, col2 = st.columns([3, 2])
    with col1:
        st.markdown(f"<div class='section-header'><i class='fas fa-pen-nib'></i> System Persona</div>", unsafe_allow_html=True)
        with st.form("identity_form", border=False):
            new_desc = st.text_area("Global System Prompt", value=brand_data["description"], height=200, help="Define the voice and constraints for your AI agents.")
            if st.form_submit_button("Update System Prompt", use_container_width=True):
                save_brand_profile({"description": new_desc, "sample_posts": []})
                st.rerun()
    with col2:
        st.markdown(f"<div class='section-header'><i class='fas fa-circle-info'></i> Configuration</div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="agent-card">
            <p><b>Active Persona:</b><br>{brand_data['description'][:150]}...</p>
            <hr style="border-color: {t['secondary']}">
            <p><small><i class="fas fa-microchip"></i> <b>Model:</b> Gemini 2.5 Flash Lite</small><br>
            <small><i class="fas fa-fingerprint"></i> <b>Security:</b> SECP256k1</small></p>
        </div>
        """, unsafe_allow_html=True)

with tab_swarm:
    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown(f"<div class='section-header'><i class='fas fa-magnifying-glass'></i> Initiate Research</div>", unsafe_allow_html=True)
        topic = st.text_input("Define mission objective:", value="Latest social engineering tactics in 2024")
        if st.button("🚀 Deploy Agents", type="primary", use_container_width=True):
            graph = build_workflow()
            initial_state = {"topic": topic, "brand_desc": brand_data["description"], "raw_trends": [], "selected_trend": "", "architect_reasoning": "", "final_posts": [], "critic_feedback": ""}
            try:
                final_state = graph.invoke(initial_state)
                st.session_state.last_run = final_state
                st.balloons()
            except Exception as e:
                st.error(f"Mission Failed: {e}")
    with c2:
        st.markdown(f"<div class='section-header'><i class='fas fa-chart-simple'></i> Telemetry</div>", unsafe_allow_html=True)
        if "last_run" in st.session_state:
            run = st.session_state.last_run
            m1, m2 = st.columns(2)
            m1.metric("Drafts", len(run['final_posts']))
            m2.metric("Sources", len(run['raw_trends']))
        else:
            st.info("No active mission telemetry.")

with tab_approval:
    if "last_run" in st.session_state:
        state = st.session_state.last_run
        st.markdown(f"""
        <div class="agent-card">
            <h4 style="color: {t['accent']};"><i class="fas fa-brain"></i> Strategic Reasoning</h4>
            <p>{state['architect_reasoning']}</p>
            <p style="font-size: 0.85rem; opacity: 0.8; margin-top: 10px;">
                <i class="fas fa-shield"></i> <b>Critic Feedback:</b> {state['critic_feedback']}
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.divider()
        cols = st.columns(3)
        for i, post in enumerate(state["final_posts"]):
            with cols[i % 3]:
                st.markdown('<div class="agent-card">', unsafe_allow_html=True)
                if f"signed_{i}" in st.session_state:
                    st.markdown('<span class="badge badge-signed"><i class="fas fa-lock"></i> Digitally Signed</span>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<span class="badge" style="background: {t["secondary"]}; border: 1px solid {t["accent"]}; color: {t["accent"]};"><i class="fas fa-robot"></i> AI Draft</span>', unsafe_allow_html=True)
                
                edited = st.text_area("Edit Content:", value=post, key=f"edit_{i}", height=150)
                
                btn_col1, btn_col2 = st.columns(2)
                if btn_col1.button(f"🔒 Sign", key=f"btn_sign_{i}", use_container_width=True):
                    sig, payload = sign_post(edited)
                    st.session_state[f"signed_{i}"] = {"sig": sig, "payload": payload}
                    st.rerun()
                
                if f"signed_{i}" in st.session_state:
                    if btn_col2.button(f"🚀 Post", key=f"btn_post_{i}", type="primary", use_container_width=True):
                        success, result = post_to_x(edited, st.session_state[f"signed_{i}"]['sig'], demo_mode=demo_mode)
                        if success: st.toast("Post successfully broadcasted!")
                        else: st.error(result)
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Approval queue is empty. Deploy agents in the 'Agent Swarm' tab.")

with tab_audit:
    st.markdown(f"<div class='section-header'><i class='fas fa-list-check'></i> Historical Verification</div>", unsafe_allow_html=True)
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            try: logs = json.load(f)
            except: logs = []
        
        for entry in reversed(logs[-10:]):
            with st.container():
                st.markdown(f"""
                <div class="agent-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span class="badge badge-verified"><i class="fas fa-check-double"></i> Verified Human Origin</span>
                        <small style="opacity: 0.6;"><i class="fas fa-clock"></i> {time.ctime(entry['timestamp'])}</small>
                    </div>
                    <p style="margin-top: 10px; font-weight: 500;">{entry['content']}</p>
                    <hr style="border-color: {t['secondary']}">
                    <p style="font-size: 0.75rem; opacity: 0.7; overflow-wrap: break-word;">
                        <i class="fas fa-signature"></i> <b>Signature:</b> {entry['signature']}<br>
                        <i class="fas fa-hashtag"></i> <b>Network ID:</b> {entry['tweet_id']}
                    </p>
                </div>
                """, unsafe_allow_html=True)

    st.divider()
    with st.expander("🛠️ Manual Cryptographic Audit Tool"):
        v_col1, v_col2 = st.columns(2)
        with v_col1:
            v_payload = st.text_area("Signed Payload (Content|TS)")
            v_sig = st.text_input("Signature Hex")
        with v_col2:
            v_pk = st.text_input("Public Key Hex")
            if st.button("🛡️ Execute Integrity Check", use_container_width=True):
                if verify_post(v_payload, v_sig, v_pk): st.success("✅ INTEGRITY CONFIRMED")
                else: st.error("❌ INTEGRITY BREACH")