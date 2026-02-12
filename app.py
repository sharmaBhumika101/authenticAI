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

# Import tweepy for Day 5 integration
try:
    import tweepy
except ImportError:
    st.error("Tweepy not found. Please run: pip install tweepy")
    tweepy = None

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

# --- UTILITY: RETRY LOGIC FOR RATE LIMITS ---
def safe_generate_content(prompt, retries=2, delay=2):
    for i in range(retries):
        try:
            return model.generate_content(prompt)
        except Exception as e:
            if "429" in str(e) and i < retries - 1:
                time.sleep(delay)
                continue
            raise e

# --- SOCIAL MEDIA LOGIC (X/TWITTER) ---

def post_to_x(content: str, signature: str = None):
    """
    Posts content to X with a more robust OAuth 1.0a handshake.
    """
    if not all([X_CONSUMER_KEY, X_CONSUMER_SECRET, X_ACCESS_TOKEN, X_ACCESS_SECRET]):
        return False, "Missing X API credentials in .env."
    
    try:
        # OAuth 1.0a Handshake (Force verification)
        auth = tweepy.OAuth1UserHandler(
            X_CONSUMER_KEY, X_CONSUMER_SECRET,
            X_ACCESS_TOKEN, X_ACCESS_SECRET
        )
        api = tweepy.API(auth)
        
        # Verify credentials first to pinpoint the error
        user = api.verify_credentials()
        if not user:
            return False, "401: X could not verify your credentials. Ensure your Access Token has 'Read/Write' and isn't expired."

        # Use Client for v2 API Posting
        client = tweepy.Client(
            consumer_key=X_CONSUMER_KEY,
            consumer_secret=X_CONSUMER_SECRET,
            access_token=X_ACCESS_TOKEN,
            access_token_secret=X_ACCESS_SECRET
        )
        
        final_text = content
        if signature:
            final_text += f"\n\n🛡️ Verified Human Signature: {signature[:12]}..."
            
        response = client.create_tweet(text=final_text)
        return True, response.data['id']
    
    except tweepy.TweepyException as e:
        error_str = str(e)
        if "401" in error_str:
            return False, "Error 401 (Unauthorized): This is a handshake failure. \n\n1. Go to 'User authentication settings' in X portal. \n2. Ensure permissions are 'Read and Write'. \n3. REGENERATE 'Access Token and Secret' and update .env. \n4. Check if your computer's clock is synced."
        elif "403" in error_str:
            return False, "Error 403 (Forbidden): You likely have the wrong permission level (Read-only)."
        return False, f"Tweepy Error: {error_str}"
    except Exception as e:
        return False, f"Unexpected Error: {str(e)}"

# --- CRYPTOGRAPHY LOGIC ---
def get_or_create_keys():
    if 'private_key' not in st.session_state:
        sk = SigningKey.generate(curve=SECP256k1)
        vk = sk.verifying_key
        st.session_state.private_key = sk
        st.session_state.public_key = vk
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
BRAND_FILE = "brand_profile.json"
def save_brand_profile(data):
    with open(BRAND_FILE, "w") as f:
        json.dump(data, f)
    st.success("✅ Brand identity saved!")

def load_brand_profile():
    if os.path.exists(BRAND_FILE):
        with open(BRAND_FILE, "r") as f:
            return json.load(f)
    return {"description": "A tech enthusiast persona focusing on AI security.", "sample_posts": []}

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
    st.write("🔍 Scout Agent is researching...")
    try:
        results = tavily.search(query=state["topic"], search_depth="basic")['results']
        state["raw_trends"] = [r['content'] for r in results[:3]]
    except:
        state["raw_trends"] = ["No live trends found."]
    return state

def architect_node(state: AgentState):
    st.write("📐 Architect Agent is strategizing...")
    prompt = f"Brand Persona: {state['brand_desc']}\nTrends: {state['raw_trends']}\nPick the best trend. Format: TREND: [text] REASON: [text]"
    response = safe_generate_content(prompt).text
    if "TREND:" in response and "REASON:" in response:
        state["selected_trend"] = response.split("TREND:")[1].split("REASON:")[0].strip()
        state["architect_reasoning"] = response.split("REASON:")[1].strip()
    return state

def creative_node(state: AgentState):
    st.write("🎨 Creative Agent is drafting...")
    prompt = f"Topic: {state['selected_trend']}\nReason: {state['architect_reasoning']}\nVoice: {state['brand_desc']}\nWrite 3 X posts separated by '---'."
    response = safe_generate_content(prompt).text
    state["final_posts"] = [p.strip() for p in response.split("---") if len(p.strip()) > 10]
    return state

def critic_node(state: AgentState):
    st.write("⚖️ Critic Agent is reviewing...")
    prompt = f"Review these posts for brand consistency: {state['final_posts']}. Give feedback."
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

# --- STREAMLIT UI ---
st.set_page_config(page_title="AgenticVoice Dashboard", layout="wide", page_icon="🤖")
st.title("🛡️ AgenticVoice: Trust-Layered Content")

brand_data = load_brand_profile()
sk, vk = get_or_create_keys()

with st.sidebar:
    st.header("🔌 Connection Status")
    
    # Check computer time
    local_time = int(time.time())
    st.write(f"System Epoch: `{local_time}`")
    st.caption("If this time is wrong, OAuth will fail with 401.")
    
    x_keys_ready = all([X_CONSUMER_KEY, X_CONSUMER_SECRET, X_ACCESS_TOKEN, X_ACCESS_SECRET])
    if x_keys_ready:
        st.success("X API: Keys Loaded")
    else:
        st.warning("X API: Keys Incomplete")
    
    st.divider()
    if st.button("🛠️ Test Handshake"):
        if x_keys_ready:
            try:
                auth = tweepy.OAuth1UserHandler(X_CONSUMER_KEY, X_CONSUMER_SECRET, X_ACCESS_TOKEN, X_ACCESS_SECRET)
                api = tweepy.API(auth)
                user = api.verify_credentials()
                st.success(f"Connected as: @{user.screen_name}")
            except Exception as e:
                st.error(f"Handshake Failed: {e}")
        else:
            st.error("Missing keys")

    st.divider()
    st.header("🗝️ Identity Key")
    st.code(vk.to_string().hex()[:16] + "...", language="text")

tab_setup, tab_generate, tab_review, tab_verify = st.tabs(["⚙️ Brand Setup", "🚀 Generate Posts", "👀 Review & Post", "🛡️ Verify Authenticity"])

with tab_setup:
    st.header("1. Configure Your Identity")
    with st.form("brand_setup_form"):
        new_desc = st.text_area("Brand Persona", value=brand_data["description"])
        if st.form_submit_button("Save Identity"):
            save_brand_profile({"description": new_desc, "sample_posts": []})
            st.rerun()

with tab_generate:
    st.header("2. Research and Draft")
    topic_input = st.text_input("Scout topic:", value="AI Security")
    if st.button("🚀 Trigger Agents"):
        graph = build_workflow()
        initial_state = {"topic": topic_input, "brand_desc": brand_data["description"], "raw_trends": [], "selected_trend": "", "architect_reasoning": "", "final_posts": [], "critic_feedback": ""}
        with st.status("Agents collaborating...") as status:
            try:
                final_state = graph.invoke(initial_state)
                st.session_state.last_run = final_state
                status.update(label="Complete!", state="complete")
            except Exception as e:
                st.error(f"Error: {e}")

with tab_review:
    st.header("3. Human Approval & Posting")
    if "last_run" in st.session_state:
        state = st.session_state.last_run
        col_feedback, col_posts = st.columns([1, 2])
        with col_feedback:
            st.subheader("💡 Strategic Intent")
            st.write(state['architect_reasoning'])
            st.info(state["critic_feedback"])
        with col_posts:
            st.subheader("📝 Draft Content")
            for i, post in enumerate(state["final_posts"]):
                with st.expander(f"Post {i+1}", expanded=True):
                    edited_post = st.text_area("Final Polish:", value=post, key=f"edit_{i}")
                    c1, c2 = st.columns(2)
                    if c1.button(f"🔒 Sign Locally", key=f"app_{i}"):
                        sig, payload = sign_post(edited_post)
                        st.session_state[f"signed_{i}"] = {"sig": sig, "payload": payload, "pk": vk.to_string().hex()}
                        st.success("ECC Signature Generated!")
                    if f"signed_{i}" in st.session_state:
                        if c2.button(f"🚀 Push to X", key=f"post_{i}"):
                            with st.status("Posting verified content...") as status:
                                success, result = post_to_x(edited_post, st.session_state[f"signed_{i}"]['sig'])
                                if success:
                                    status.update(label="Live!", state="complete")
                                    st.success(f"Tweet ID: {result}")
                                else:
                                    status.update(label="Posting Failed", state="error")
                                    st.error(result)
    else:
        st.info("Run agents in Step 2 first.")

with tab_verify:
    st.header("4. Verify Trust Layer")
    test_payload = st.text_area("Payload")
    test_sig = st.text_input("Signature")
    test_pk = st.text_input("Public Key")
    if st.button("🛡️ Verify"):
        if verify_post(test_payload, test_sig, test_pk):
            st.success("🔒 SIGNATURE VERIFIED")
        else:
            st.error("❌ VERIFICATION FAILED")