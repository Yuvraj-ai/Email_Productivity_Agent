import streamlit as st
import json
import pandas as pd
import os
from backend.categorizer import categorizer
from backend.agent import get_agent_response
import uuid

# Set page configuration
st.set_page_config(page_title="Email Productivity Agent", layout="wide")

# Initialize session state for page navigation
if 'page' not in st.session_state:
    st.session_state.page = "Home"

# File paths
INBOX_PATH = 'sources/inbox.json'
PROCESSED_PATH = 'sources/processed_inbox.json'
PROMPTS_PATH = 'sources/prompts.json'
DRAFTS_PATH = 'sources/drafts.json'

def load_data(path):
    if os.path.exists(path):
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            st.error(f"Error decoding JSON from {path}")
            return None
    else:
        st.warning(f"File not found: {path}")
        return None

def save_data(path, data):
    try:
        with open(path, 'w') as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
        st.error(f"Error saving data: {e}")
        return False

# --- Sidebar: Navigation & Prompt Settings ---
with st.sidebar:
    st.header("Navigation")
    if st.button("Home"):
        st.session_state.page = "Home"
        st.rerun()
    
    if st.button("Email Agent"):
        st.session_state.page = "Email Agent"
        st.rerun()

    if st.button("Draft Agent"):
        st.session_state.page = "Draft Agent"
        st.rerun()
        
    st.divider()

    st.header("⚙️ Prompt Settings")
    # Using an expander as requested for "expandable contractable side"
    # although the sidebar itself is collapsible, having an expander inside is also good organization.
    with st.expander("Edit Prompts", expanded=False):
        prompts_data = load_data(PROMPTS_PATH)
        if prompts_data:
            with st.form("prompts_form"):
                updated_prompts = {}
                for key, value in prompts_data.items():
                    # Format key for display
                    label = key.replace('_', ' ').title()
                    updated_prompts[key] = st.text_area(label, value, height=150)
                
                if st.form_submit_button("Save Prompts"):
                    if save_data(PROMPTS_PATH, updated_prompts):
                        st.success("Prompts updated successfully!")
                        st.rerun()
        else:
            st.error("Could not load prompts.")

if st.session_state.page == "Home":
    st.title("📧 Email Productivity Agent")

    # --- Section 1: Load Raw Emails ---
    st.header("📥 Inbox")
    if st.button("Load Emails"):
        data = load_data(INBOX_PATH)
        if data:
            # Handle structure: {"emails": [...]} or [...]
            emails = data.get("emails", []) if isinstance(data, dict) else data
            
            if emails:
                st.success(f"Found {len(emails)} emails.")
                for i, email in enumerate(emails):
                    subject = email.get('subject', 'No Subject')
                    sender = email.get('sender', 'Unknown Sender')
                    with st.expander(f"{i+1}. {subject} | {sender}"):
                        st.write(f"**From:** {sender}")
                        st.write(f"**To:** {', '.join(email.get('recipients', []))}")
                        st.write(f"**Date:** {email.get('timestamp', 'N/A')}")
                        st.text_area("Body", email.get('body', ''), height=150, key=f"body_{i}")
                        st.json(email)
        else:
            st.info("Inbox is empty.")

    # --- Section 2: Processed Emails ---
    st.header("🏷️ Categorized & Processed Emails")

    # Initialize session state for processed data visibility
    if 'show_processed' not in st.session_state:
        st.session_state.show_processed = False

    if st.button("Re / Categorize Processed Emails"):
        with st.spinner("Categorizing emails... This may take a while."):
            try:
                categorizer()
                st.success("Emails categorized successfully!")
                st.session_state.show_processed = True
            except Exception as e:
                st.error(f"An error occurred during categorization: {e}")

    if st.session_state.show_processed:
        processed_data = load_data(PROCESSED_PATH)
        
        if processed_data:
            # Ensure it's a list
            emails_list = processed_data.get("emails", []) if isinstance(processed_data, dict) else processed_data
            
            if isinstance(emails_list, list) and len(emails_list) > 0:
                df = pd.DataFrame(emails_list)
                
                # Select columns to display in the table (avoid cluttering with full body)
                display_cols = ['id', 'category', 'priority', 'subject', 'sender', 'timestamp']
                # Filter cols that actually exist in df
                cols_to_show = [c for c in display_cols if c in df.columns]
                
                st.subheader("Processed Emails Table")
                st.caption("Click on a row to view full details.")
                
                # Interactive Dataframe
                selection = st.dataframe(
                    df[cols_to_show],
                    use_container_width=True,
                    hide_index=True,
                    on_select="rerun",
                    selection_mode="single-row"
                )
                
                # Show details for selected row
                selected_rows = selection.get("selection", {}).get("rows", [])
                if selected_rows:
                    selected_idx = selected_rows[0]
                    selected_email = emails_list[selected_idx]
                    
                    st.divider()
                    st.subheader(f"Details: {selected_email.get('subject', 'No Subject')}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.info(f"**Category:** {selected_email.get('category')}")
                        st.write(f"**Sender:** {selected_email.get('sender')}")
                    with col2:
                        st.warning(f"**Priority:** {selected_email.get('priority')}")
                        st.write(f"**Date:** {selected_email.get('timestamp')}")
                    
                    st.write("---")
                    st.write("**Summary:**")
                    st.write(selected_email.get('summary', 'N/A'))
                    
                    st.write("**Action Items:**")
                    st.write(selected_email.get('action_items', 'None'))
                    
                    with st.expander("Full Email Body"):
                        st.text(selected_email.get('body', ''))
                    
                    with st.expander("Raw JSON Data"):
                        st.json(selected_email)
        else:
            st.info("No processed emails found.")

        # --- Section 3: Action Items List ---
        if isinstance(emails_list, list) and len(emails_list) > 0:
            st.divider()
            st.header("📝 Action Items List")
            
            # Filter emails that have action items
            action_emails = [e for e in emails_list if e.get('action_items')]
            
            if action_emails:
                for email in action_emails:
                    sender_name = email.get('sender_name', 'Unknown Name')
                    sender_email = email.get('sender', 'Unknown Email')
                    action_items = email.get('action_items')
                    
                    with st.container():
                        st.markdown(f"**From:** {sender_name} (`{sender_email}`)")
                        st.info(action_items)
            else:
                st.info("No action items found.")

elif st.session_state.page == "Email Agent":
    st.title("🤖 Email Agent")
    
    # Load Data
    processed_data = load_data(PROCESSED_PATH)
    prompts_data = load_data(PROMPTS_PATH)
    
    emails_list = []
    if processed_data:
        emails_list = processed_data.get("emails", []) if isinstance(processed_data, dict) else processed_data

    # --- Sidebar: Email Selection ---
    with st.sidebar:
        st.divider()
        st.subheader("Select Context")
        
        email_options = ["None (General Inbox)"] + [f"{i+1}. {e.get('subject')} | {e.get('sender')}" for i, e in enumerate(emails_list)]
        selected_option = st.selectbox("Select an email to discuss:", email_options)
        
        selected_email = None
        if selected_option != "None (General Inbox)":
            index = int(selected_option.split('.')[0]) - 1
            selected_email = emails_list[index]
            st.info(f"**Focus:** {selected_email.get('subject')}")

    # --- Chat Interface ---
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat Input
    if prompt := st.chat_input("Ask the agent (e.g., 'Summarize this', 'Draft a reply')..."):
        # 1. Display user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 2. Get Agent Response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = get_agent_response(
                        user_query=prompt,
                        chat_history=st.session_state.messages[:-1], # Pass history excluding current prompt
                        selected_email=selected_email,
                        inbox=emails_list,
                        prompts=prompts_data if prompts_data else {}
                    )
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    st.error(f"Error: {e}")

elif st.session_state.page == "Draft Agent":
    st.title("📝 Draft Generation Agent")
    
    # Load Data
    processed_data = load_data(PROCESSED_PATH)
    prompts_data = load_data(PROMPTS_PATH)
    drafts_data = load_data(DRAFTS_PATH) or []
    
    emails_list = []
    if processed_data:
        emails_list = processed_data.get("emails", []) if isinstance(processed_data, dict) else processed_data

    tab1, tab2 = st.tabs(["✨ Create Draft", "📂 Saved Drafts"])
    
    with tab1:
        st.subheader("Generate New Draft")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            draft_type = st.radio("Draft Type", ["New Email", "Reply to Email"])
            
            selected_email_context = None
            if draft_type == "Reply to Email":
                email_options = [f"{i+1}. {e.get('subject')} | {e.get('sender')}" for i, e in enumerate(emails_list)]
                selected_option = st.selectbox("Select Email to Reply to:", email_options)
                if selected_option:
                    index = int(selected_option.split('.')[0]) - 1
                    selected_email_context = emails_list[index]
                    st.caption(f"Replying to: {selected_email_context.get('subject')}")
        
        with col2:
            instructions = st.text_area("Instructions for Agent", placeholder="e.g., 'Polite refusal', 'Ask for meeting next Tuesday', 'Accept the offer'")
            
            if st.button("Generate Draft"):
                if not instructions:
                    st.warning("Please provide instructions.")
                else:
                    with st.spinner("Drafting..."):
                        # Construct prompt for the agent
                        prompt_text = f"Draft a {draft_type}."
                        if draft_type == "Reply to Email":
                            prompt_text += " This is a reply."
                        prompt_text += f"\nInstructions: {instructions}"
                        prompt_text += "\n\nIMPORTANT: Return the draft in the following format:\nSubject: [Subject Line]\n\n[Body Text]"
                        
                        try:
                            response = get_agent_response(
                                user_query=prompt_text,
                                chat_history=[],
                                selected_email=selected_email_context,
                                inbox=emails_list,
                                prompts=prompts_data if prompts_data else {}
                            )
                            
                            # Simple parsing (robustness can be improved)
                            subject = "Draft Subject"
                            body = response
                            
                            if "Subject:" in response:
                                parts = response.split("\n", 1)
                                if len(parts) > 0:
                                    subject_line = parts[0]
                                    if subject_line.startswith("Subject:"):
                                        subject = subject_line.replace("Subject:", "").strip()
                                        body = parts[1].strip() if len(parts) > 1 else ""
                            
                            st.session_state.generated_subject = subject
                            st.session_state.generated_body = body
                            st.success("Draft Generated!")
                            
                        except Exception as e:
                            st.error(f"Error generating draft: {e}")

        st.divider()
        st.subheader("Editor")
        
        # Editor State
        if 'generated_subject' not in st.session_state:
            st.session_state.generated_subject = ""
        if 'generated_body' not in st.session_state:
            st.session_state.generated_body = ""
            
        with st.form("draft_editor"):
            draft_subject = st.text_input("Subject", value=st.session_state.generated_subject)
            draft_body = st.text_area("Body", value=st.session_state.generated_body, height=300)
            
            if st.form_submit_button("Save Draft"):
                new_draft = {
                    "id": str(uuid.uuid4()),
                    "type": draft_type,
                    "related_email_id": selected_email_context.get('id') if selected_email_context else None,
                    "subject": draft_subject,
                    "body": draft_body,
                    "status": "saved"
                }
                drafts_data.append(new_draft)
                if save_data(DRAFTS_PATH, drafts_data):
                    st.success("Draft saved successfully!")
                    # Clear state
                    st.session_state.generated_subject = ""
                    st.session_state.generated_body = ""
                    st.rerun()

    with tab2:
        st.subheader("Saved Drafts")
        if drafts_data:
            for draft in drafts_data:
                with st.expander(f"{draft.get('subject', 'No Subject')} ({draft.get('status')})"):
                    st.write(f"**Type:** {draft.get('type')}")
                    st.text_area("Body", draft.get('body'), height=200, key=f"view_{draft['id']}")
                    if st.button("Delete", key=f"del_{draft['id']}"):
                        drafts_data.remove(draft)
                        save_data(DRAFTS_PATH, drafts_data)
                        st.rerun()
        else:
            st.info("No saved drafts.")