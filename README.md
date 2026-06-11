# AutoMail Pro - Email Automation Tool

AutoMail Pro is a simple email automation MVP that allows a user to import recipients, create personalized email templates, preview generated emails, send emails through SMTP, and track the status of each email.

This project was created as a small development exercise to demonstrate the logic of email automation without using real personal data.

---

## 1. Project Objective

The objective of this project is to automate repetitive email sending tasks. Instead of manually writing and sending emails one by one, the user can upload a recipient list, define an email subject and body, personalize the content using variables, and send emails automatically.

The solution helps to:

- Save time.
- Reduce repetitive manual work.
- Personalize emails easily.
- Track email sending status.
- Handle basic errors such as invalid emails or missing recipient data.

---

## 2. Main Features

- Import recipients from CSV or Excel files.
- Validate required recipient fields.
- Validate email address format.
- Create a custom email subject and body.
- Personalize emails using variables:
  - `{first_name}`
  - `{last_name}`
  - `{company_name}`
  - `{email}`
- Preview emails before sending.
- Send emails using SMTP.
- Display email status:
  - `pending`
  - `sent`
  - `failed`
- Store campaign history in SQLite.
- Show basic dashboard statistics.
- Demo mode to test the workflow without actually sending emails.

---

## 3. Technical Choices

### Python
Python was chosen because it is simple, readable, and suitable for automation tasks.

### Streamlit
Streamlit was chosen to create a simple web interface quickly without building a complex frontend.

### Pandas
Pandas is used to read and process CSV and Excel recipient files.

### SMTP
SMTP is used for sending emails because it works with common email providers such as Gmail, Outlook, and SendGrid.

### SQLite
SQLite is used as a lightweight local database to store campaign history and email logs.

---

## 4. Project Structure

```text
email-automation-tool/
│
├── app.py
├── requirements.txt
├── README.md
├── .env.example
│
├── data/
│   └── sample_recipients.csv
│
├── database/
│   └── email_automation.db
│
├── src/
│   ├── __init__.py
│   ├── email_sender.py
│   ├── template_engine.py
│   ├── recipient_loader.py
│   ├── validator.py
│   ├── database.py
│   └── utils.py
```

---

## 5. Installation

Clone or download the project, then open the project folder in the terminal.

Create a virtual environment:

```bash
python3 -m venv venv
```

Activate the virtual environment:

### macOS / Linux

```bash
source venv/bin/activate
```

### Windows

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## 6. Email Configuration

Create a `.env` file in the project root.

You can copy `.env.example`:

```bash
cp .env.example .env
```

Then update the values:

```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
SENDER_NAME=AutoMail Pro
```

### Important for Gmail

For Gmail, do not use your normal Gmail password. Use a Gmail App Password.

General steps:

1. Enable 2-step verification on your Google account.
2. Create an App Password.
3. Paste the App Password in the `.env` file.

For demonstration, you can use `Demo mode` inside the app, which does not actually send emails.

---

## 7. Recipient File Format

The uploaded CSV or Excel file must contain these columns:

```csv
first_name,last_name,company_name,email
John,Doe,ABC Corp,test1@example.com
Emma,Brown,DataSoft,test2@example.com
Lucas,Martin,Cloudify,test3@example.com
```

A sample file is available here:

```text
data/sample_recipients.csv
```

---

## 8. How to Run the App

Run this command from the project folder:

```bash
streamlit run app.py
```

The app will open in your browser.

---

## 9. How to Use

### Step 1: Upload Recipients

Go to `Upload Recipients` and upload a CSV or Excel file.

The system validates:

- Missing first name.
- Missing last name.
- Missing company name.
- Missing email address.
- Invalid email format.

### Step 2: Create Template

Go to `Create Template` and write your subject and email body.

Example subject:

```text
Hello {first_name}, message for {company_name}
```

Example body:

```text
Dear {first_name} {last_name},

I hope you are doing well.

This is a personalized message for {company_name}.

Best regards,
Kishan
```

### Step 3: Preview Emails

Go to `Preview Emails` and check the personalized email before sending.

### Step 4: Send Emails

Go to `Send Emails`.

For safe testing, keep this enabled:

```text
Demo mode: do not actually send emails
```

To actually send emails, configure the `.env` file and disable demo mode.

### Step 5: View Campaign History

Go to `Campaign History` to view sent campaigns and email logs.

---

## 10. Error Handling

The project handles basic errors such as:

- Missing required columns.
- Missing recipient information.
- Invalid email address.
- SMTP authentication failure.
- SMTP sending failure.
- Unsupported file type.

Each email gets one of these statuses:

```text
pending
sent
failed
```

---

## 11. Demonstration Scenario

Use the sample recipient file:

```text
data/sample_recipients.csv
```

Then:

1. Upload the file.
2. Create a template using placeholders.
3. Preview a personalized email.
4. Run sending in demo mode.
5. Open Campaign History to show sent/failed logs.

This demonstrates the full automation logic without sending real emails.

---

## 12. Future Improvements

Possible improvements:

- Email scheduling.
- User authentication.
- Save and reuse templates.
- HTML email templates.
- File attachments.
- SendGrid API integration.
- Reply tracking.
- Open/click tracking.
- Unsubscribe handling.
- Role-based access control.
- Deployment on Streamlit Cloud.

---

## 13. Important Note

This project should be tested only with fake data or personal test email addresses. Do not use real personal data or send emails to real users without consent.
