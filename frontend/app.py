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
    .arabic-text {
        font-family: 'Amiri', 'Traditional Arabic', 'Scheherazade', serif;
        font-size: 1.4rem;
        direction: rtl;
        text-align: right;
        line-height: 2.0;
        color: #1b5e20;
        padding: 10px;
        background-color: #f1f8e9;
        border-radius: 8px;
        border-right: 4px solid #4caf50;
        margin-bottom: 8px;
    }
    .verified-badge {
        display: inline-block;
        background-color: #e8f5e9;
        color: #2e7d32;
        padding: 4px 12px;
        border-radius: 16px;
        font-weight: bold;
        font-size: 0.9rem;
        border: 1px solid #a5d6a7;
    }
    .warning-badge {
        display: inline-block;
        background-color: #fff3e0;
        color: #e65100;
        padding: 4px 12px;
        border-radius: 16px;
        font-weight: bold;
        font-size: 0.9rem;
        border: 1px solid #ffcc80;
    }
    .source-card {
        padding: 12px;
        margin-bottom: 12px;
        border-radius: 8px;
        background-color: #fafafa;
        border: 1px solid #e0e0e0;
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
