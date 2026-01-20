import smtplib
import sys
import os

try:
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    import markdown
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

# Configuration
# Hardcoded for user convenience based on chat
SMTP_SERVER = "smtp.exmail.qq.com"
SMTP_PORT = 587 # STARTTLS
SMTP_USER = "zephyr@wen2tu.com"
SMTP_PASSWORD = "Wzf2920051Fzw"
RECIPIENT_EMAIL = "77213305@qq.com"

def send_email(subject, markdown_content):
    if SMTP_USER == "your_email@gmail.com":
        print("Error: SMTP not configured. Please set SMTP_USER and SMTP_PASSWORD environment variables.")
        return False

    try:
        # Convert Markdown to HTML
        html_content = markdown.markdown(markdown_content)

        msg = MIMEMultipart()
        msg['From'] = SMTP_USER
        msg['To'] = RECIPIENT_EMAIL
        msg['Subject'] = subject

        msg.attach(MIMEText(html_content, 'html'))

        print(f"Connecting to {SMTP_SERVER}:{SMTP_PORT}...")
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10) # 10s timeout
        server.set_debuglevel(1)
        
        print("Starting TLS...")
        server.starttls()
        
        print("Logging in...")
        server.login(SMTP_USER, SMTP_PASSWORD)
        
        print("Sending mail...")
        text = msg.as_string()
        server.sendmail(SMTP_USER, RECIPIENT_EMAIL, text)
        
        server.quit()
        print("Email sent successfully!")
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python email_sender.py <markdown_file_path>")
        sys.exit(1)

    file_path = sys.argv[1]
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract title from content or use default
    subject = f"AI Daily Brief - {os.getenv('TODAY_DATE', 'Update')}"
    
    send_email(subject, content)
