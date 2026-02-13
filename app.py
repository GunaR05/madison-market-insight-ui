import streamlit as st

# MUST BE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="Madison Market Insight",
    layout="wide",
)

import os
import requests
from typing import Any, Dict, List, Optional, Union

JsonType = Union[Dict[str, Any], List[Any]]

# =====================================================
# CONFIG (Railway / Render / Docker friendly)
# =====================================================
def get_config(key: str, default: Optional[str] = None) -> Optional[str]:
    return os.getenv(key, default)


N8N_WEBHOOK_URL = get_config("N8N_WEBHOOK_URL")
N8N_HEADER_NAME = get_config("N8N_HEADER_NAME", "X-API-KEY")
N8N_HEADER_VALUE = get_config("N8N_HEADER_VALUE")


# =====================================================
# HELPERS
# =====================================================
def normalize_response(raw: JsonType) -> Dict[str, Any]:
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, list) and raw and isinstance(raw[0], dict):
        return raw[0]
    return {}


def safe_str(x: Any) -> str:
    return x.strip() if isinstance(x, str) else ""


# =====================================================
# CALL N8N WORKFLOW
# =====================================================
def call_n8n(brand: str, goal: str) -> Dict[str, Any]:
    if not N8N_WEBHOOK_URL:
        raise RuntimeError("Missing N8N_WEBHOOK_URL environment variable.")

    if not N8N_HEADER_VALUE:
        raise RuntimeError("Missing N8N_HEADER_VALUE environment variable.")

    headers = {
        "Content-Type": "application/json",
        N8N_HEADER_NAME: N8N_HEADER_VALUE,
    }

    payload = {
        "brand": brand,
        "goal": goal,
    }

    resp = requests.post(
        N8N_WEBHOOK_URL,
        headers=headers,
        json=payload,
        timeout=120,
    )

    resp.raise_for_status()
    return normalize_response(resp.json())


# =====================================================
# UI HEADER
# =====================================================
st.title("Madison Market Insight Engine")
st.caption("Public interface for my Assignment 4 AI workflow")

# =====================================================
# ABOUT SECTION
# =====================================================
with st.expander("About this tool", expanded=True):
    st.markdown(
        """
**One-sentence description**  
Transforms marketing + workforce signals into executive-ready insights.

**What it does**
- Fetches real market data
- Analyzes hiring demand
- Detects trends + skill gaps
- Generates decision-ready recommendations

**Who it's for**
- Founders  
- Marketers  
- Product teams  
- Analysts  

**Tech Stack**
n8n · APIs · Data Processing · LLM · Streamlit

**Author**  
Gunashree Rajakumar  
https://www.linkedin.com/in/rajakumargunashree/
"""
    )

st.divider()
st.subheader("Inputs")

col1, col2 = st.columns(2)

with col1:
    brand = st.text_input(
        "Brand / Company",
        placeholder="Example: OpenAI",
    )

with col2:
    goal = st.text_input(
        "Analysis Goal",
        placeholder="Example: Generate market + workforce insights",
    )

brand_clean = safe_str(brand)
goal_clean = safe_str(goal)

run = st.button("Run Analysis", type="primary")

st.divider()
st.subheader("Results")

# =====================================================
# EXECUTION
# =====================================================
if run:

    if not brand_clean or not goal_clean:
        st.error("Please fill both inputs before running.")
        st.stop()

    with st.spinner("Fetching data → analyzing → generating insights..."):

        try:
            result = call_n8n(brand_clean, goal_clean)

        except requests.HTTPError as e:
            st.error("Workflow returned HTTP error")
            st.code(str(e))
            st.stop()

        except Exception as e:
            st.error("Workflow failed. Check webhook + variables.")
            st.code(str(e))
            st.stop()

    # =====================================================
    # OUTPUT DISPLAY
    # =====================================================
    tool_name = safe_str(result.get("tool_name")) or "Madison Market Insight"
    one_liner = safe_str(result.get("one_liner"))
    report_text = safe_str(result.get("report_text"))

    st.markdown(f"## {tool_name}")

    if one_liner:
        st.info(one_liner)

    if report_text:
        st.markdown("### Executive Insight Report")
        st.markdown(report_text)
    else:
        st.warning("No report_text returned from workflow.")

    # Insights
    if isinstance(result.get("top_insights"), list):
        st.markdown("### Key Insights")
        for i, x in enumerate(result["top_insights"][:10], 1):
            st.markdown(f"{i}. {x}")

    # Metadata Table
    if isinstance(result.get("metadata"), dict):
        st.markdown("### Analysis Summary")
        st.table(result["metadata"])

    # Raw Items
    if isinstance(result.get("items"), list):
        st.markdown("### Supporting Items")
        st.json(result["items"][:25])

    # Debug toggle
    with st.expander("Debug Response"):
        st.json(result)

    st.success("Workflow executed successfully.")

else:
    st.info("Enter inputs and click Run Analysis.")
