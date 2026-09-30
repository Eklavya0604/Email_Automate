import os
import re
import csv
import time
import mimetypes
import smtplib

from pathlib import Path
from email.message import EmailMessage
from email.utils import formataddr
from dotenv import load_dotenv


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

if not SENDER_EMAIL or not EMAIL_PASSWORD:
    raise RuntimeError(
        "ERROR: SENDER_EMAIL or EMAIL_PASSWORD missing in .env"
    )


# ============================================================
# OUTLOOK / MICROSOFT 365 SMTP
# ============================================================
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# ============================================================
# PERSONAL INFORMATION
# ============================================================

NAME = "Aditya Kumar Vaish"

PHONE = "+91 9161726347"

EMAIL = "kumareklavya744@gmail.com"

PORTFOLIO_LINK = "https://adityavaish.dev"

GITHUB_LINK = "https://github.com/Eklavya0604"

LINKEDIN_LINK = "https://linkedin.com/in/aditya-vaish-482a11281"

RESUME_LINK = (
    "https://drive.google.com/file/d/"
    "1XR0cAAQf2OjjlUPU4N7ZK6YB2aotFfy5/"
    "view?usp=drive_link"
)


# ============================================================
# PROJECT DIRECTORIES
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

CSV_FILE = BASE_DIR / "applications.csv"

RESUME_FILE = (
    BASE_DIR
    / "resume"
    / "Aditya_Kumar_Vaish.pdf"
)

ASSETS_DIR = BASE_DIR / "assets"

LOG_FILE = BASE_DIR / "sent_log.csv"


# ============================================================
# IMAGE ASSETS
# ============================================================

PORTFOLIO_ICON = (
    ASSETS_DIR / "icons8-globe-96.png"
)

RESUME_ICON = (
    ASSETS_DIR / "icons8-resume-96.png"
)

GITHUB_ICON = (
    ASSETS_DIR / "icons8-github-90.png"
)

LINKEDIN_ICON = (
    ASSETS_DIR / "linkdin.png"
)

GMAIL_ICON = (
    ASSETS_DIR / "gmail.png"
)


# ============================================================
# EMAIL SETTINGS
# ============================================================

# Keep this TRUE while testing.
#
# TRUE  -> No email is actually sent.
# FALSE -> Emails are actually sent.
#
DRY_RUN = False


# Delay between emails.
DELAY_BETWEEN_EMAILS = 20


# ============================================================
# VALIDATE FILES
# ============================================================

if not CSV_FILE.exists():

    raise FileNotFoundError(
        f"applications.csv not found:\n{CSV_FILE}"
    )


if not RESUME_FILE.exists():

    raise FileNotFoundError(
        f"Resume not found:\n{RESUME_FILE}"
    )


required_assets = [
    PORTFOLIO_ICON,
    RESUME_ICON,
    GITHUB_ICON,
    LINKEDIN_ICON,
    GMAIL_ICON,
]


for asset in required_assets:

    if not asset.exists():

        raise FileNotFoundError(
            f"Asset not found:\n{asset}"
        )


# ============================================================
# HTML ESCAPING
# ============================================================

def escape_html(value):

    if value is None:
        return ""

    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def format_email_text(value):
    """
    Escape user/CSV content safely, then support simple Markdown-style
    formatting inside the email body.

    Supported:
        **bold**
        *italic*
    """

    if value is None:
        return ""

    value = escape_html(value)

    # Convert **text** -> <strong>text</strong>
    value = re.sub(
        r"\*\*(.*?)\*\*",
        r"<strong>\1</strong>",
        value,
        flags=re.DOTALL
    )

    # Convert *text* -> <em>text</em>
    # Avoid matching the asterisks already used for **bold**.
    value = re.sub(
        r"(?<!\*)\*([^*\n]+)\*(?!\*)",
        r"<em>\1</em>",
        value
    )
    #color
    value = re.sub(
        r'==(.*?)==',
        r'<span style="background:#dcfce7; color:#166534; padding:2px 5px; border-radius:4px;">\1</span>',
        value
    )

    # Preserve line breaks if someone uses multiple lines in a CSV field.
    value = value.replace("\r\n", "\n").replace("\n", "<br>")

    return value


# ============================================================
# EMBED IMAGE
# ============================================================

def embed_image(msg, path, cid):

    mime_type, _ = mimetypes.guess_type(
        str(path)
    )

    if not mime_type:
        mime_type = "image/png"

    maintype, subtype = mime_type.split(
        "/",
        1
    )

    with open(path, "rb") as file:

        image_data = file.read()

    msg.get_payload()[1].add_related(

        image_data,

        maintype=maintype,

        subtype=subtype,

        cid=f"<{cid}>"
    )


# ============================================================
# HTML EMAIL TEMPLATE
# ============================================================

def build_html_email(
    company,
    role,
    intro,
    match,
    interest
):

    company = escape_html(company)
    role = escape_html(role)
    intro = format_email_text(intro)
    match = format_email_text(match)
    interest = format_email_text(interest)

    return f"""
<!DOCTYPE html>
<html>

<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{role} — {NAME}</title>
</head>

<body style="
margin:0;
padding:0;
background:#f7f8fa;
font-family:Arial,Helvetica,sans-serif;
color:#24292f;
">

<table width="100%" cellpadding="0" cellspacing="0" border="0"
       style="background:#f7f8fa;">
<tr>
<td align="center" style="padding:35px 12px;">

<table width="640" cellpadding="0" cellspacing="0" border="0"
       style="
       width:100%;
       max-width:640px;
       background:#ffffff;
       border:1px solid #e1e4e8;
       border-radius:12px;
       overflow:hidden;
       ">

<!-- HEADER -->
<tr>
<td style="
padding:38px 40px 30px 40px;
background:#ffffff;
">

<div style="
font-size:28px;
line-height:34px;
font-weight:700;
letter-spacing:.5px;
color:#111827;
">
ADITYA KUMAR VAISH
</div>

<div style="
margin-top:8px;
font-size:12px;
line-height:18px;
letter-spacing:1.4px;
color:#6b7280;
">
SOFTWARE ENGINEER
&nbsp;·&nbsp;
JAVA
&nbsp;·&nbsp;
SPRING BOOT
&nbsp;·&nbsp;
BACKEND
</div>

<!-- PROFESSIONAL LINKS -->
<table cellpadding="0" cellspacing="0" border="0" style="margin-top:24px;">
<tr>

<!-- PORTFOLIO -->
<td style="padding-right:18px;">
<a href="{PORTFOLIO_LINK}" target="_blank"
   style="
   text-decoration:none;
   color:#2563eb;
   font-size:12px;
   font-weight:600;
   ">
<img src="cid:portfolio"
     width="17" height="17"
     style="vertical-align:middle;border:0;margin-right:5px;">
<span style="vertical-align:middle;">Portfolio</span>
</a>
</td>

<!-- RESUME -->
<td style="padding-right:18px;">
<a href="{RESUME_LINK}" target="_blank"
   style="
   text-decoration:none;
   color:#2563eb;
   font-size:12px;
   font-weight:600;
   ">
<img src="cid:resume"
     width="17" height="17"
     style="vertical-align:middle;border:0;margin-right:5px;">
<span style="vertical-align:middle;">Resume</span>
</a>
</td>

<!-- GITHUB -->
<td style="padding-right:18px;">
<a href="{GITHUB_LINK}" target="_blank"
   style="
   text-decoration:none;
   color:#2563eb;
   font-size:12px;
   font-weight:600;
   ">
<img src="cid:github"
     width="17" height="17"
     style="vertical-align:middle;border:0;margin-right:5px;">
<span style="vertical-align:middle;">GitHub</span>
</a>
</td>

<!-- LINKEDIN -->
<td style="padding-right:18px;">
<a href="{LINKEDIN_LINK}" target="_blank"
   style="
   text-decoration:none;
   color:#2563eb;
   font-size:12px;
   font-weight:600;
   ">
<img src="cid:linkedin"
     width="17" height="17"
     style="vertical-align:middle;border:0;margin-right:5px;">
<span style="vertical-align:middle;">LinkedIn</span>
</a>
</td>

<!-- EMAIL -->
<td>
<a href="mailto:{EMAIL}"
   style="
   text-decoration:none;
   color:#2563eb;
   font-size:12px;
   font-weight:600;
   ">
<img src="cid:gmail"
     width="17" height="17"
     style="vertical-align:middle;border:0;margin-right:5px;">
<span style="vertical-align:middle;">Email</span>
</a>
</td>

</tr>
</table>

</td>
</tr>

<!-- DIVIDER -->
<tr>
<td style="
height:1px;
background:#e5e7eb;
font-size:0;
line-height:0;
">&nbsp;</td>
</tr>

<!-- JOB HEADING -->
<tr>
<td style="padding:35px 40px 0 40px;">

<div style="
font-size:25px;
line-height:32px;
font-weight:700;
color:#111827;
">
{role}
</div>

<div style="
margin-top:5px;
font-size:14px;
color:#6b7280;
">
{company}
</div>

</td>
</tr>

<!-- BODY -->
<tr>
<td style="
padding:25px 40px 38px 40px;
font-size:15px;
line-height:1.75;
color:#374151;
">

<p style="margin:0 0 18px 0;">
Hi {company} Hiring Team,
</p>

<p style="margin:0 0 18px 0;">
{intro}
</p>

<p style="margin:0 0 20px 0;">
{match}
</p>

<p style="margin:0 0 22px 0;">
{interest}
</p>

<!-- RESUME BUTTON -->
<table cellpadding="0" cellspacing="0" border="0" style="margin:26px 0;">
<tr>
<td style="background:#2563eb;border-radius:6px;">
<a href="{RESUME_LINK}" target="_blank"
   style="
   display:inline-block;
   padding:11px 20px;
   font-size:11px;
   font-weight:700;
   letter-spacing:.5px;
   color:#ffffff;
   text-decoration:none;
   ">
VIEW RESUME
</a>
</td>
</tr>
</table>

<p style="margin:0 0 20px 0;">
My resume is also attached for your consideration.
</p>

<p style="margin:25px 0 0 0;">
Thank you for your time and consideration.
</p>

<p style="margin:20px 0 0 0;">
Best regards,<br>
<strong style="color:#111827;">
Aditya Kumar Vaish
</strong>
</p>

</td>
</tr>

<!-- FOOTER -->
<tr>
<td style="
border-top:1px solid #e5e7eb;
padding:20px 40px;
background:#f9fafb;
">

<div style="
font-size:10px;
letter-spacing:.5px;
color:#9ca3af;
">
COMPUTER SCIENCE ENGINEERING
</div>

</td>
</tr>

</table>

</td>
</tr>
</table>

</body>
</html>
"""


# ============================================================
# PLAIN TEXT VERSION
# ============================================================

def build_plain_text(
    company,
    role,
    intro,
    match,
    interest
):

    # Remove Markdown markers for the plain-text fallback.
    plain_intro = re.sub(r"\*\*(.*?)\*\*", r"\1", intro)
    plain_intro = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"\1", plain_intro)

    plain_match = re.sub(r"\*\*(.*?)\*\*", r"\1", match)
    plain_match = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"\1", plain_match)

    plain_interest = re.sub(r"\*\*(.*?)\*\*", r"\1", interest)
    plain_interest = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"\1", plain_interest)

    return f"""
ADITYA KUMAR VAISH
Software Engineer | Java | Spring Boot | Backend

Portfolio: {PORTFOLIO_LINK}
Resume: {RESUME_LINK}
GitHub: {GITHUB_LINK}
LinkedIn: {LINKEDIN_LINK}
Email: {EMAIL}


{role}
{company}


Hi {company} Hiring Team,

{plain_intro}

{plain_match}

{plain_interest}

My resume is attached for your consideration.

Thank you for your time.

Best regards,

Aditya Kumar Vaish
"""


# ============================================================
# CREATE EMAIL MESSAGE
# ============================================================

def create_email(row):

    company = row["company"].strip()

    role = row["role"].strip()

    recipient = row["recipient"].strip()

    subject = row["subject"].strip()

    intro = row["intro"].strip()

    match = row["match"].strip()

    interest = row["interest"].strip()


    msg = EmailMessage()


    # --------------------------------------------------------
    # HEADERS
    # --------------------------------------------------------

    msg["Subject"] = subject

    msg["From"] = formataddr(
        (
            NAME,
            SENDER_EMAIL
        )
    )

    msg["To"] = recipient


    # --------------------------------------------------------
    # PLAIN TEXT
    # --------------------------------------------------------

    msg.set_content(
        build_plain_text(
            company,
            role,
            intro,
            match,
            interest
        )
    )


    # --------------------------------------------------------
    # HTML
    # --------------------------------------------------------

    msg.add_alternative(
        build_html_email(
            company,
            role,
            intro,
            match,
            interest
        ),
        subtype="html"
    )


    # --------------------------------------------------------
    # EMBED PNG ICONS
    # --------------------------------------------------------

    embed_image(
        msg,
        PORTFOLIO_ICON,
        "portfolio"
    )

    embed_image(
        msg,
        RESUME_ICON,
        "resume"
    )

    embed_image(
        msg,
        GITHUB_ICON,
        "github"
    )

    embed_image(
        msg,
        LINKEDIN_ICON,
        "linkedin"
    )

    embed_image(
        msg,
        GMAIL_ICON,
        "gmail"
    )


    # --------------------------------------------------------
    # ATTACH RESUME
    # --------------------------------------------------------

    with open(
        RESUME_FILE,
        "rb"
    ) as file:

        resume_data = file.read()


    msg.add_attachment(

        resume_data,

        maintype="application",

        subtype="pdf",

        filename="Aditya_Kumar_Vaish.pdf"
    )


    return msg


# ============================================================
# LOG APPLICATION
# ============================================================

def log_result(
    company,
    role,
    recipient,
    status
):

    file_exists = LOG_FILE.exists()


    with open(
        LOG_FILE,
        "a",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)


        if not file_exists:

            writer.writerow(
                [
                    "company",
                    "role",
                    "recipient",
                    "status",
                    "timestamp"
                ]
            )


        writer.writerow(
            [
                company,
                role,
                recipient,
                status,
                time.strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            ]
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 65)
    print("       ADITYA KUMAR VAISH — JOB APPLICATION MAILER")
    print("=" * 65)
    print()


    print(
        f"Sender    : {SENDER_EMAIL}"
    )

    print(
        f"Resume    : {RESUME_FILE.name}"
    )

    print(
        f"Portfolio : {PORTFOLIO_LINK}"
    )

    print()


    # --------------------------------------------------------
    # READ CSV
    # --------------------------------------------------------

    try:
        with open(
            CSV_FILE,
            "r",
            encoding="utf-8-sig",
            newline=""
        ) as file:
            reader = csv.DictReader(file)
            rows = list(reader)

    except UnicodeDecodeError:
        print("⚠️ UTF-8 decoding failed. Trying Windows-1252...")

        with open(
            CSV_FILE,
            "r",
            encoding="cp1252",
            newline=""
        ) as file:
            reader = csv.DictReader(file)
            rows = list(reader)


    if not rows:

        print(
            "No applications found in applications.csv."
        )

        return


    print(
        f"Applications loaded: {len(rows)}"
    )

    print()


    # --------------------------------------------------------
    # DRY RUN
    # --------------------------------------------------------

    if DRY_RUN:

        print(
            "⚠️ DRY RUN MODE"
        )

        print(
            "No emails will actually be sent."
        )

        print()


        for index, row in enumerate(
            rows,
            start=1
        ):

            print(
                f"{index}. "
                f"{row['company']} | "
                f"{row['role']} | "
                f"{row['recipient']}"
            )


        print()

        print(
            "Change DRY_RUN = False "
            "when you are ready to send."
        )

        return


    # --------------------------------------------------------
    # CONNECT SMTP
    # --------------------------------------------------------

    print(
        "Connecting to Gmail SMTP..."
    )


    server = smtplib.SMTP(
        SMTP_SERVER,
        SMTP_PORT
    )


    server.ehlo()


    server.starttls()


    server.ehlo()


    server.login(
        SENDER_EMAIL,
        EMAIL_PASSWORD
    )


    print(
        "✅ Gmail SMTP connected."
    )

    print()


    # --------------------------------------------------------
    # SEND EMAILS
    # --------------------------------------------------------

    for index, row in enumerate(
        rows,
        start=1
    ):

        company = row["company"].strip()

        role = row["role"].strip()

        recipient = row["recipient"].strip()


        print(
            f"[{index}/{len(rows)}] "
            f"{company} — {role}"
        )

        print(
            f"To: {recipient}"
        )


        try:

            msg = create_email(row)


            server.send_message(msg)


            print(
                "✅ Email sent."
            )


            log_result(
                company,
                role,
                recipient,
                "SENT"
            )


        except Exception as error:

            print(
                f"❌ Failed: {error}"
            )


            log_result(
                company,
                role,
                recipient,
                f"FAILED: {error}"
            )


        # ----------------------------------------------------
        # DELAY
        # ----------------------------------------------------

        if index < len(rows):

            print(
                f"Waiting {DELAY_BETWEEN_EMAILS} seconds..."
            )

            time.sleep(
                DELAY_BETWEEN_EMAILS
            )

            print()


    # --------------------------------------------------------
    # CLOSE CONNECTION
    # --------------------------------------------------------

    server.quit()


    print()
    print("=" * 65)
    print("🎉 ALL APPLICATION EMAILS PROCESSED")
    print("=" * 65)
    print()


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()