import time
from datetime import datetime

import pandas as pd
import streamlit as st

from src.database import (
    create_campaign,
    get_campaigns,
    get_email_logs,
    init_db,
    log_email,
    update_campaign_stats,
)
from src.email_sender import send_email
from src.recipient_loader import load_recipients
from src.template_engine import find_placeholders, personalize_text
from src.utils import load_smtp_config, mask_email_password
from src.validator import validate_recipient

st.set_page_config(
    page_title="AutoMail Pro",
    page_icon="📧",
    layout="wide",
)

init_db()

if "recipients_df" not in st.session_state:
    st.session_state.recipients_df = None
if "subject_template" not in st.session_state:
    st.session_state.subject_template = "Hello {first_name}, message for {company_name}"
if "body_template" not in st.session_state:
    st.session_state.body_template = """Dear {first_name} {last_name},

I hope you are doing well.

This is a personalized message for {company_name}.

Best regards,
Kishan"""
if "campaign_name" not in st.session_state:
    st.session_state.campaign_name = f"Campaign {datetime.now().strftime('%Y-%m-%d %H:%M')}"

st.title("📧 AutoMail Pro")
st.caption("A simple email automation tool to import recipients, personalize templates, send emails, and track delivery status.")

with st.sidebar:
    st.header("Navigation")
    page = st.radio(
        "Go to",
        [
            "Dashboard",
            "Upload Recipients",
            "Create Template",
            "Preview Emails",
            "Send Emails",
            "Campaign History",
            "SMTP Settings",
        ],
    )

    st.divider()
    st.subheader("Current Session")
    if st.session_state.recipients_df is not None:
        df = st.session_state.recipients_df
        st.write(f"Recipients: {len(df)}")
        st.write(f"Ready: {(df['status'] == 'pending').sum()}")
        st.write(f"Invalid: {(df['status'] == 'failed').sum()}")
    else:
        st.write("No recipients uploaded yet.")


def render_status_metrics(df: pd.DataFrame):
    total = len(df)
    pending = int((df["status"] == "pending").sum()) if not df.empty else 0
    sent = int((df["status"] == "sent").sum()) if not df.empty else 0
    failed = int((df["status"] == "failed").sum()) if not df.empty else 0
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total", total)
    col2.metric("Pending", pending)
    col3.metric("Sent", sent)
    col4.metric("Failed", failed)


if page == "Dashboard":
    st.header("Dashboard")
    campaigns = get_campaigns()

    if campaigns.empty:
        st.info("No campaign history yet. Upload recipients and send a test campaign to see statistics here.")
    else:
        total_campaigns = len(campaigns)
        total_sent = int(campaigns["sent"].sum())
        total_failed = int(campaigns["failed"].sum())
        total_emails = int(campaigns["total"].sum())

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Campaigns", total_campaigns)
        col2.metric("Total Emails", total_emails)
        col3.metric("Sent", total_sent)
        col4.metric("Failed", total_failed)

        st.subheader("Recent Campaigns")
        st.dataframe(campaigns, use_container_width=True)

elif page == "Upload Recipients":
    st.header("Upload Recipients")
    st.write("Upload a CSV or Excel file with these columns: `first_name`, `last_name`, `company_name`, `email`.")

    uploaded_file = st.file_uploader("Choose CSV or Excel file", type=["csv", "xlsx", "xls"])

    with st.expander("Sample CSV format"):
        st.code("""first_name,last_name,company_name,email
John,Doe,ABC Corp,test1@example.com
Emma,Brown,DataSoft,test2@example.com""", language="csv")

    if uploaded_file is not None:
        try:
            df, _ = load_recipients(uploaded_file)
            st.session_state.recipients_df = df
            st.success("Recipients imported successfully.")
            render_status_metrics(df)
            st.dataframe(df, use_container_width=True)
        except Exception as exc:
            st.error(str(exc))
    elif st.session_state.recipients_df is not None:
        st.subheader("Current uploaded recipients")
        render_status_metrics(st.session_state.recipients_df)
        st.dataframe(st.session_state.recipients_df, use_container_width=True)

elif page == "Create Template":
    st.header("Create Email Template")
    st.write("Use placeholders: `{first_name}`, `{last_name}`, `{company_name}`, `{email}`.")

    st.session_state.campaign_name = st.text_input("Campaign name", value=st.session_state.campaign_name)
    st.session_state.subject_template = st.text_input("Email subject", value=st.session_state.subject_template)
    st.session_state.body_template = st.text_area("Email body", value=st.session_state.body_template, height=300)

    combined_template = st.session_state.subject_template + "\n" + st.session_state.body_template
    placeholders = find_placeholders(combined_template)

    st.subheader("Detected placeholders")
    if placeholders:
        st.write(", ".join([f"`{p}`" for p in placeholders]))
    else:
        st.warning("No placeholders detected. Personalization will not be applied.")

    st.subheader("Template Example")
    example = {
        "first_name": "John",
        "last_name": "Doe",
        "company_name": "ABC Corp",
        "email": "john@example.com",
    }
    st.markdown("**Subject Preview**")
    st.code(personalize_text(st.session_state.subject_template, example))
    st.markdown("**Body Preview**")
    st.code(personalize_text(st.session_state.body_template, example))

elif page == "Preview Emails":
    st.header("Preview Personalized Emails")

    df = st.session_state.recipients_df
    if df is None:
        st.warning("Please upload recipients first.")
    else:
        render_status_metrics(df)
        valid_df = df[df["status"] == "pending"].copy()
        if valid_df.empty:
            st.error("No valid pending recipients available for preview.")
        else:
            selected_index = st.selectbox(
                "Select recipient to preview",
                valid_df.index,
                format_func=lambda i: f"{valid_df.loc[i, 'first_name']} {valid_df.loc[i, 'last_name']} <{valid_df.loc[i, 'email']}>",
            )
            recipient = valid_df.loc[selected_index].to_dict()
            subject = personalize_text(st.session_state.subject_template, recipient)
            body = personalize_text(st.session_state.body_template, recipient)

            st.markdown(f"**To:** {recipient['email']}")
            st.markdown(f"**Subject:** {subject}")
            st.text_area("Body", value=body, height=300, disabled=True)

elif page == "Send Emails":
    st.header("Send Emails")
    st.warning("Use fake/test recipients for demonstration. Do not send to real users without consent.")

    df = st.session_state.recipients_df
    config = load_smtp_config()

    if df is None:
        st.warning("Please upload recipients first.")
    else:
        render_status_metrics(df)
        st.subheader("Sending configuration")
        col1, col2 = st.columns(2)
        col1.write(f"SMTP server: `{config['smtp_server'] or 'Not configured'}`")
        col1.write(f"SMTP port: `{config['smtp_port'] or 'Not configured'}`")
        col2.write(f"Email account: `{config['email_address'] or 'Not configured'}`")
        col2.write(f"Password: `{mask_email_password(config['email_password'])}`")

        dry_run = st.checkbox("Demo mode: do not actually send emails", value=True)
        only_first = st.checkbox("Send only first valid email for safe testing", value=True)

        valid_pending_df = df[df["status"] == "pending"].copy()
        if only_first and not valid_pending_df.empty:
            valid_pending_df = valid_pending_df.head(1)

        st.write(f"Emails ready in this run: **{len(valid_pending_df)}**")

        if st.button("Start Sending", type="primary"):
            if valid_pending_df.empty:
                st.error("No valid pending emails to send.")
            elif not dry_run and (
                not config["smtp_server"]
                or not config["smtp_port"]
                or not config["email_address"]
                or not config["email_password"]
            ):
                st.error("SMTP configuration is incomplete. Add your settings in the .env file.")
            else:
                campaign_id = create_campaign(
                    st.session_state.campaign_name,
                    st.session_state.subject_template,
                    len(valid_pending_df),
                )
                progress_bar = st.progress(0)
                status_box = st.empty()

                for count, (idx, row) in enumerate(valid_pending_df.iterrows(), start=1):
                    recipient = row.to_dict()
                    subject = personalize_text(st.session_state.subject_template, recipient)
                    body = personalize_text(st.session_state.body_template, recipient)

                    valid, validation_error = validate_recipient(recipient)
                    if not valid:
                        st.session_state.recipients_df.at[idx, "status"] = "failed"
                        st.session_state.recipients_df.at[idx, "error"] = validation_error
                        log_email(
                            campaign_id,
                            recipient.get("first_name", ""),
                            recipient.get("last_name", ""),
                            recipient.get("company_name", ""),
                            recipient.get("email", ""),
                            "failed",
                            validation_error,
                        )
                    else:
                        if dry_run:
                            success, message = True, "Demo mode: email not actually sent"
                            time.sleep(0.3)
                        else:
                            success, message = send_email(
                                config["smtp_server"],
                                int(config["smtp_port"]),
                                config["email_address"],
                                config["email_password"],
                                config["sender_name"],
                                recipient["email"],
                                subject,
                                body,
                            )

                        status = "sent" if success else "failed"
                        error = "" if success else message
                        st.session_state.recipients_df.at[idx, "status"] = status
                        st.session_state.recipients_df.at[idx, "error"] = error
                        log_email(
                            campaign_id,
                            recipient.get("first_name", ""),
                            recipient.get("last_name", ""),
                            recipient.get("company_name", ""),
                            recipient.get("email", ""),
                            status,
                            error,
                        )

                    progress_bar.progress(count / len(valid_pending_df))
                    status_box.info(f"Processed {count}/{len(valid_pending_df)} emails")

                update_campaign_stats(campaign_id)
                st.success("Sending process completed.")
                st.dataframe(st.session_state.recipients_df, use_container_width=True)

elif page == "Campaign History":
    st.header("Campaign History")
    campaigns = get_campaigns()

    if campaigns.empty:
        st.info("No campaigns found yet.")
    else:
        st.dataframe(campaigns, use_container_width=True)
        campaign_ids = campaigns["id"].tolist()
        selected_campaign = st.selectbox("View logs for campaign", campaign_ids)
        logs = get_email_logs(selected_campaign)
        st.subheader("Email Logs")
        st.dataframe(logs, use_container_width=True)

elif page == "SMTP Settings":
    st.header("SMTP Settings")
    config = load_smtp_config()
    st.write("Create a `.env` file in the project root using `.env.example` as reference.")

    st.code("""SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
SENDER_NAME=AutoMail Pro""", language="env")

    st.subheader("Current loaded configuration")
    st.write(f"SMTP server: `{config['smtp_server'] or 'Not configured'}`")
    st.write(f"SMTP port: `{config['smtp_port'] or 'Not configured'}`")
    st.write(f"Email address: `{config['email_address'] or 'Not configured'}`")
    st.write(f"Password: `{mask_email_password(config['email_password'])}`")

    st.info("For Gmail, enable 2-step verification and create an App Password. Do not use your normal Gmail password.")
