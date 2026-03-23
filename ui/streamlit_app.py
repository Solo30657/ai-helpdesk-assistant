import os

import requests
import streamlit as st

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

st.set_page_config(page_title="AI Helpdesk Triage Assistant", page_icon="🛠️", layout="centered")
st.title("🛠️ AI Helpdesk Triage Assistant")
st.caption("Classify tickets, assign priority, route issues, and draft a response.")

sample_ticket = """I clicked a suspicious email link and now my laptop is acting strange. Two coworkers said they received the same message. Please help quickly."""

with st.form("ticket_form"):
    ticket_id = st.text_input("Ticket ID (optional)", placeholder="INC-10023")
    ticket_text = st.text_area("Ticket text", value=sample_ticket, height=180)
    submitted = st.form_submit_button("Classify ticket")

if submitted:
    if not ticket_text.strip():
        st.error("Please enter a ticket before classifying.")
    else:
        with st.spinner("Analyzing ticket..."):
            try:
                response = requests.post(
                    f"{API_BASE_URL}/classify",
                    json={"ticket_id": ticket_id or None, "ticket_text": ticket_text},
                    timeout=60,
                )
                response.raise_for_status()
                payload = response.json()
                st.success("Ticket classified successfully.")
                st.json(payload)
            except requests.RequestException as exc:
                st.error(f"Unable to reach the API: {exc}")
