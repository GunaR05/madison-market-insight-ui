# Madison Market Insight — Public AI Interface

## Overview
Madison Market Insight is a public web interface that converts real marketing signals and workforce data into executive-ready insights for non-technical users.

It wraps an intelligent n8n automation workflow inside a simple interface so anyone can generate structured market analysis without needing technical knowledge.

---

## One-Sentence Description
Turns marketing + workforce signals into executive-ready insights for decision-makers.

---

## Who This Tool Is For
- Founders  
- Marketing teams  
- Product managers  
- Business analysts  
- Job seekers exploring industry demand  

---

## What It Does
Given a brand and an analysis goal, the system:

1. Collects market content signals  
2. Aggregates job market data  
3. Detects trends and positioning patterns  
4. Identifies in-demand roles and skills  
5. Finds skill gaps  
6. Generates strategic recommendations  

All results are formatted into a structured executive report.


---

## Architecture Flow
User Input  
→ Streamlit Interface  
→ Webhook Request  
→ n8n Workflow  
→ Data Processing + AI Analysis  
→ Structured Response  
→ Formatted Report Display

---

## Tech Stack
Frontend  
Streamlit  

Automation + Orchestration  
n8n  

Processing + Integration  
APIs  
JavaScript logic nodes  
Data transformation  

AI Layer  
LLM analysis node  

Deployment  
Railway — UI hosting  
ngrok — temporary public webhook tunnel

---

## Interface Features

### Clear Inputs
- Simple text fields
- Example placeholders
- Input validation before execution

### Readable Outputs
- Structured executive report
- Highlighted insights
- Tables and sections
- Clean formatting (no raw JSON)

### Basic Info Section
Includes
- Tool description
- Intended users
- Tech stack
- Author info

---

## How to Run Locally

Clone repo
git clone <repo-url>

Install dependencies
pip install -r requirements.txt

Set environment variables
N8N_WEBHOOK_URL=your_webhook_url  
N8N_HEADER_NAME=X-API-KEY  
N8N_HEADER_VALUE=your_key  

Run
streamlit run app.py

---

## Required Environment Variables

N8N_WEBHOOK_URL → n8n webhook endpoint  
N8N_HEADER_NAME → auth header name  
N8N_HEADER_VALUE → auth header value  

---

## Example Input
Brand: Tesla  
Goal: Market insights  

---

## Example Output
The system returns a structured report containing:

- Market trends  
- Value propositions  
- In-demand job roles  
- Skills analysis  
- Skill gaps  
- Strategic recommendations  

---

## Assignment Context
Built for  
Assignment 5 — Public Interface for AI Workflow  


Requirement:  
Wrap an existing intelligent workflow inside a publicly accessible interface usable by non-technical users.

---

## Author
Gunashree Rajakumar  
LinkedIn  
https://www.linkedin.com/in/rajakumargunashree/
