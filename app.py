import json
import os
from typing import Any, Dict, List, Optional, Union

import requests
import streamlit as st

JsonType = Union[Dict[str, Any], List[Any]]


# -----------------------------
# Config (env vars / secrets)
# -----------------------------
def get_config(key: str, default: Optional[str] = None) -> Optional[str]:
    # Works on Streamlit Cloud (st.secrets) + local (env vars)
    if key in st.secrets:
        return str(st.secrets[key])
    return os.getenv(key, default)


N8N_WEBHOOK_URL = get_config("N8N_WEBHOOK_URL")
N8N_HEADER_NAME = get_config("N8N_HEADER_NAME", "X-API-KEY")
N8N_HEADER_VALUE = get_config("N8N_HEADER_VALUE")


# -----------------------------
# Helpers
# -----------------------------
def normalize_response(raw: JsonType) -> Dict[str, Any]:
    """
    Normalize n8n response into a dict:
    - dict -> dict
    - list -> first dict item
    """
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, list) and raw and isinstance(raw[0], dict):
        return raw[0]
    return {}


def safe_str(x: Any) -> str:
    return x.strip() if isinstance(x, str) else ""


def call_n8n(brand: str, goal: str) -> Dict[str, Any]:
    if not N8N_WEBHOOK_URL:
        raise RuntimeError("Missing N8N_WEBHOOK_URL. Set it in Streamlit secrets or environment variables.")
    if not N8N_HEADER_VALUE:
        raise RuntimeError("Missing N8N_HEADER_VALUE. Set it in Streamlit secrets or environment variables.")

    headers = {
        "Content-Type": "application/json",
        N8N_HEADER_NAME: N8N_HEADER_VALUE,
    }

    payload = {"brand": brand, "goal": goal}

    resp = requests.post(N8N_WEBHOOK_URL, headers=headers, json=payload, timeout=120)
    # If n8n returns HTML or empty body, this will raise — which is good for debugging
    resp.raise_for_status()
    return normalize_response(resp.json())


# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(page_title="Madison Market Insight", layout="wide")

st.title("Madison Market Insight")
st.caption("A public UI wrapper for my Assignment 4 n8n Madison workflow (Assignment 5).")

with st.expander("About this tool", expanded=True):
    st.markdown(
        """
**One-sentence description:** Turns marketing + talent signals into executive-ready insights for non-technical users.

**What it does:** Sends your inputs to an n8n workflow that pulls market signals (ex: RSS + YouTube) and generates
a structured insight report (trends, value props, role/skill implications, gaps, recommendations).

**Who it’s for:** Marketing managers, brand managers, and stakeholders who need insights without using n8n.

**Tech stack:** n8n + JavaScript + LLM + Streamlit

**Built by:** Gunashree Rajakumar — https://www.linkedin.com/in/rajakumargunashree/
        """.strip()
    )

st.divider()
st.subheader("Inputs")

col1, col2 = st.columns([1, 2])

with col1:
    brand = st.text_input(
        "Brand / Company",
        placeholder="Example: OpenAI",
        help="Required. The brand you want insights about.",
    )

with col2:
    goal = st.text_input(
        "Goal",
        placeholder="Example: Generate market + workforce insights",
        help="Required. Tell the agent what you want the report to focus on.",
    )

# Basic validation
brand_clean = safe_str(brand)
goal_clean = safe_str(goal)

run = st.button("Run analysis", type="primary")

st.divider()
st.subheader("Outputs (Formatted)")

if run:
    if not brand_clean or not goal_clean:
        st.error("Please fill in both **Brand** and **Goal** before running.")
        st.stop()

    with st.spinner("Running n8n workflow…"):
        try:
            result = call_n8n(brand_clean, goal_clean)
        except requests.HTTPError as e:
            st.error("n8n returned an HTTP error.")
            st.code(str(e), language="text")
            st.stop()
        except Exception as e:
            st.error("Could not run the workflow. Check webhook URL, auth header, and that the workflow is Active.")
            st.code(str(e), language="text")
            st.stop()

    # Expected fields from your workflow
    tool_name = safe_str(result.get("tool_name")) or "Madison Market Insight"
    one_liner = safe_str(result.get("one_liner"))
    report_text = safe_str(result.get("report_text"))

    top_insights = result.get("top_insights")
    items = result.get("items")

    st.markdown(f"### {tool_name}")
    if one_liner:
        st.info(one_liner)

    # Main report
    if report_text:
        st.markdown("### Executive Insight Report")
        st.markdown(report_text)
    else:
        st.warning("No `report_text` found in the response. Make sure your final n8n node returns `report_text`.")

    # Optional extras (only if present)
    if isinstance(top_insights, list) and top_insights:
        st.markdown("### Top Insights")
        for i, x in enumerate(top_insights[:10], start=1):
            st.markdown(f"{i}. {x}")

    if isinstance(items, list) and items:
        st.markdown("### Items")
        st.json(items[:25])

    # Debug toggle
    with st.expander("Debug (raw response)"):
        st.json(result)

    st.success("✅ Your A4 workflow is now accessible to non-technical users through this UI.")
else:
    st.info("Enter inputs and click **Run analysis** to generate insights.")
