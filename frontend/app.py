import os
import requests
import streamlit as st

# Set page config
st.set_page_config(
    page_title="aain.ai",
    page_icon="📖",
    layout="wide"
)

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Custom CSS for rich aesthetics
st.markdown("""
<style>
    /* Background for the whole app */
    .stApp {
        background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
        background-attachment: fixed;
    }

    /* Glass effect for main blocks */
    .stApp > header {
        background-color: transparent;
    }
    .block-container {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 3rem !important;
        margin-top: 2rem;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        color: white;
    }
    
    /* General text adjustments for dark glass theme */
    h1, h2, h3, h4, h5, h6, p, label, span {
        color: #ffffff !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: rgba(0, 0, 0, 0.2);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Input fields */
    .stTextInput>div>div>input {
        background: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 10px !important;
    }
    .stTextInput>div>div>input::placeholder {
        color: rgba(255, 255, 255, 0.5) !important;
    }
    
    /* Buttons */
    .stButton>button {
        background: rgba(255, 255, 255, 0.15) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 12px !important;
        backdrop-filter: blur(5px);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: rgba(255, 255, 255, 0.25) !important;
        border: 1px solid rgba(255, 255, 255, 0.5) !important;
        transform: translateY(-2px);
    }

    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    div[data-testid="stExpanderDetails"] {
        background: rgba(0, 0, 0, 0.15);
        border-radius: 0 0 10px 10px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }

    /* Custom classes */
    .arabic-text {
        font-family: 'Amiri', 'Traditional Arabic', 'Scheherazade', serif;
        font-size: 1.5rem;
        direction: rtl;
        text-align: right;
        line-height: 2.2;
        color: #e0f2f1;
        padding: 15px;
        background-color: rgba(0, 0, 0, 0.25);
        border-radius: 12px;
        border-right: 4px solid #80cbc4;
        margin-bottom: 12px;
    }
    .verified-badge {
        display: inline-block;
        background: rgba(76, 175, 80, 0.15);
        backdrop-filter: blur(5px);
        color: #aed581;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.9rem;
        border: 1px solid rgba(76, 175, 80, 0.4);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .warning-badge {
        display: inline-block;
        background: rgba(255, 152, 0, 0.15);
        backdrop-filter: blur(5px);
        color: #ffcc80;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.9rem;
        border: 1px solid rgba(255, 152, 0, 0.4);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .source-card {
        padding: 15px;
        margin-bottom: 15px;
        border-radius: 12px;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(10px);
    }
</style>
""", unsafe_allow_html=True)

# Title and header
st.title("📖 aain.ai")
st.markdown("*A faithful, citation-verified AI assistant grounded strictly in the Holy Quran and authentic Hadiths.*")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    top_k = st.slider("Top Documents to Retrieve", min_value=1, max_value=10, value=5)
    verify_citations = st.checkbox("Enable LLM-as-a-Judge Citation Verification", value=True)
    
    st.divider()
    st.markdown("### 📌 Example Questions")
    example_prompts = [
        "What does the Quran say about patience (Sabr)?",
        "What are the five pillars of Islam according to Hadith?",
        "What is the virtue of Ayat al-Kursi?",
        "What does Islam say about justice and fair trade?",
        "What is said about honoring one's parents?"
    ]
    for prompt in example_prompts:
        if st.button(prompt, use_container_width=True):
            st.session_state["query_input"] = prompt

# Query input
query = st.text_input(
    "Ask a question based on Quran & Hadith:",
    value=st.session_state.get("query_input", ""),
    placeholder="e.g., What does the Quran teach about charity and spending in the cause of God?"
)

if st.button("Search & Answer", type="primary") and query.strip():
    with st.spinner("Searching sacred texts, reranking context, and generating verified answer..."):
        try:
            payload = {
                "query": query.strip(),
                "top_k": top_k,
                "verify_citations": verify_citations
            }
            response = requests.post(f"{API_URL}/ask", json=payload, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get("answer", "")
                sources = data.get("sources", [])
                is_faithful = data.get("is_faithful", True)
                reasoning = data.get("verification_reasoning", "")
                
                # Display verification status badge
                st.subheader("Answer")
                if is_faithful:
                    st.markdown('<span class="verified-badge">✓ Grounded & Citation Verified</span>', unsafe_allow_html=True)
                else:
                    st.markdown('<span class="warning-badge">⚠️ Potential Hallucination / Unsupported Claim</span>', unsafe_allow_html=True)
                
                if reasoning and reasoning != "Verification skipped.":
                    with st.expander("🔍 Verification Analysis"):
                        st.write(reasoning)
                
                # Display answer text
                st.markdown(answer)
                
                # Display sources
                st.divider()
                st.subheader(f"📚 Cited Sources ({len(sources)})")
                
                for idx, src in enumerate(sources, 1):
                    source_label = src.get("source", f"Source #{idx}")
                    score = src.get("rerank_score", src.get("score", 0.0))
                    text_ar = src.get("text_ar", "")
                    text_en = src.get("text_en", "")
                    
                    with st.expander(f"[{idx}] {source_label} (Relevance Score: {score:.3f})"):
                        if text_ar:
                            st.markdown(f'<div class="arabic-text">{text_ar}</div>', unsafe_allow_html=True)
                        st.markdown(f"**Translation:** {text_en}")
                        st.caption(f"Document ID: {src.get('doc_id')}")
            else:
                st.error(f"API Error {response.status_code}: {response.text}")
                
        except requests.exceptions.ConnectionError:
            st.error(f"Could not connect to API at `{API_URL}`. Make sure the FastAPI server is running.")
        except Exception as e:
            st.error(f"Unexpected error: {e}")
