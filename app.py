import json
from typing import Any, Dict, List, Optional, Union

import pandas as pd
import streamlit as st

JsonType = Union[Dict[str, Any], List[Any]]


# -----------------------------
# Helpers (robust for n8n output)
# -----------------------------
def load_json_bytes(file_bytes: bytes) -> JsonType:
    return json.loads(file_bytes.decode("utf-8", errors="replace"))


def normalize_n8n_payload(raw: JsonType) -> Dict[str, Any]:
    """
    n8n output can be:
    - dict
    - list like [{"json": {...}}]
    - list like [{"output": [...]}]  <-- your case
    Normalize to a single dict (best-effort).
    """
    if isinstance(raw, dict):
        return raw

    if isinstance(raw, list) and raw:
        first = raw[0]
        if isinstance(first, dict):
            # Prefer {"json": {...}} if present, else use dict directly
            if "json" in first and isinstance(first["json"], dict):
                return first["json"]
            return first

    return {}


def deep_get(obj: Any, path: List[Union[str, int]]) -> Optional[Any]:
    cur = obj
    for p in path:
        if isinstance(p, int):
            if isinstance(cur, list) and 0 <= p < len(cur):
                cur = cur[p]
            else:
                return None
        else:
            if isinstance(cur, dict) and p in cur:
                cur = cur[p]
            else:
                return None
    return cur


def extract_metadata(payload: Dict[str, Any]) -> Dict[str, Any]:
    md = payload.get("metadata")
    if isinstance(md, dict):
        return md

    # Sometimes nested under "json"
    md2 = deep_get(payload, ["json", "metadata"])
    if isinstance(md2, dict):
        return md2

    return {}


def extract_prompt(payload: Dict[str, Any]) -> str:
    p = payload.get("prompt")
    if isinstance(p, str) and p.strip():
        return p.strip()

    # Sometimes nested under "json"
    p2 = deep_get(payload, ["json", "prompt"])
    if isinstance(p2, str) and p2.strip():
        return p2.strip()

    return ""


def extract_text(payload: Dict[str, Any]) -> str:
    """
    Extracts AI report text from common n8n / OpenAI / LangChain response shapes.

    Handles your specific n8n shape:
      {"output":[{"content":[{"type":"output_text","text":"..."}]}]}
    """
    # 1) Your n8n structure
    out = payload.get("output")
    if isinstance(out, list):
        texts: List[str] = []
        for msg in out:
            if isinstance(msg, dict):
                content = msg.get("content")
                if isinstance(content, list):
                    for c in content:
                        if (
                            isinstance(c, dict)
                            and c.get("type") == "output_text"
                            and isinstance(c.get("text"), str)
                            and c.get("text").strip()
                        ):
                            texts.append(c["text"].strip())
        if texts:
            return "\n\n".join(texts)

    # 2) Other common structures (string direct)
    candidates = [
        ["text"],
        ["content"],
        ["response"],
        ["result"],
        ["message", "content"],
        ["choices", 0, "message", "content"],  # OpenAI chat completions
        ["choices", 0, "text"],                # OpenAI completions
        ["data", "text"],
        ["data", "content"],
        ["data", "output"],
    ]

    for path in candidates:
        val = deep_get(payload, path)
        if isinstance(val, str) and val.strip():
            return val.strip()

    # 3) Fallback: choose longest long string field
    long_strings = [
        v.strip()
        for v in payload.values()
        if isinstance(v, str) and len(v.strip()) > 200
    ]
    if long_strings:
        return max(long_strings, key=len)

    return ""


# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(page_title="Madison Market Insight Engine", layout="wide")

st.title("Madison Market Insight Engine")
st.caption("Public interface wrapper for your Assignment 4 n8n market intelligence workflow (Assignment 5)")

with st.expander("About this tool", expanded=True):
    st.markdown(
        """
**One-sentence description:** AI-powered market + workforce intelligence from multi-source signals.

**What it does:** Ingests marketing content (HubSpot RSS + YouTube) and workforce demand (job roles + skills),
then produces executive-ready insights: trends, value props, in-demand roles/skills, alignment analysis, skill gaps,
and business recommendations.

**Who it’s for:** Non-technical stakeholders who want decision-ready insights without using n8n.

**Tech stack:** n8n (orchestration) + JavaScript (normalization/merge) + OpenAI model reasoning + Streamlit (UI)

**Built by:** Gunashree Rajakumar — Portfolio/Contact: https://www.linkedin.com/in/rajakumargunashree/
        """.strip()
    )

st.divider()
st.subheader("Inputs")

col1, col2 = st.columns(2)

with col1:
    uploaded = st.file_uploader(
        "Upload your A4 output JSON (madison_job_dataai.json)",
        type=["json"],
        help="Upload the JSON written by your final node output (Read/Write Files from Disk2).",
    )

with col2:
    pasted = st.text_area(
        "Or paste the JSON contents here",
        height=200,
        placeholder="Paste the contents of madison_job_dataai.json here",
    )

# Validation
if not uploaded and not pasted.strip():
    st.info("Upload your A4 output JSON file OR paste the JSON to view formatted insights.")
    st.stop()

# Load JSON
try:
    if uploaded:
        raw = load_json_bytes(uploaded.getvalue())
    else:
        raw = json.loads(pasted)
except Exception as e:
    st.error(f"Invalid JSON: {e}")
    st.stop()

payload = normalize_n8n_payload(raw)

# Detect workflow definition mistake
if "nodes" in payload and "connections" in payload:
    st.error(
        "You uploaded the n8n WORKFLOW JSON (nodes + connections), not the A4 OUTPUT JSON.\n\n"
        "For Assignment 5 Part 2, upload the AI output file produced by your workflow (e.g., madison_job_dataai.json)."
    )
    st.stop()

# Extract
metadata = extract_metadata(payload)
prompt = extract_prompt(payload)
report_text = extract_text(payload)

# Optional debug (professional toggle)
show_debug = st.checkbox("Show raw JSON (debug)", value=False)
if show_debug:
    st.json(payload)

st.divider()
st.subheader("Outputs (Formatted)")

left, right = st.columns([1, 2])

with left:
    st.markdown("### Run Metadata")
    if metadata:
        st.dataframe(pd.DataFrame([metadata]), use_container_width=True)

        numeric = {k: v for k, v in metadata.items() if isinstance(v, (int, float))}
        if numeric:
            chart_df = pd.DataFrame({"metric": list(numeric.keys()), "value": list(numeric.values())})
            st.bar_chart(chart_df.set_index("metric"))
    else:
        st.write("No metadata found in this output (okay).")

    st.markdown("### Prompt (from A4 Input Builder)")
    if prompt:
        st.code(prompt[:2500] + ("\n...\n" if len(prompt) > 2500 else ""), language="text")
    else:
        st.write("Prompt not found in this output (depends on what n8n saved).")

with right:
    st.markdown("### Executive Insight Report")
    if report_text:
        st.markdown(report_text)
    else:
        st.warning(
            "Could not detect the AI report text.\n\n"
            "This usually means the JSON structure is different than expected."
        )

st.success("✅ Your A4 workflow output is now accessible in a clean, non-technical interface.")
