import requests
from lxml.html import fromstring
from datetime import datetime, timezone, timedelta
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
import smtplib
import os

YESTERDAY = datetime.now(timezone(timedelta(hours=+2))) - timedelta(days=1)

def validate_environment_variables():
    for key in ["M2M_MEDIAPART_LOGIN", "M2M_MEDIAPART_PASSWORD", "M2M_SMTP_SERVER_HOST", "M2M_SMTP_FROM_EMAIL", "M2M_SMTP_PASSWORD", "M2M_SMTP_TO_EMAIL"]:
        if not os.environ.get(key):
            print(f"missing env variable {key}, aborting")
            return False
    return True

def get_logged_in_session():
    session = requests.Session()
    session.post(
        "https://www.mediapart.fr/login_check",
        {
            "name": os.environ["M2M_MEDIAPART_LOGIN"],
            "password": os.environ["M2M_MEDIAPART_PASSWORD"]
        }
    )
    return session

def get_yesterday_pdf_url(session):
    req = session.get("https://www.mediapart.fr/journal/pdf")
    doc = fromstring(req.text)
    print(f"looking for a URL for yesterday {YESTERDAY.strftime('%d/%m/%Y')}...")
    download_links = doc.xpath(
        '//a[@data-smarttag-type="download"][@data-smarttag-chapter2=%s]' % \
        (YESTERDAY.strftime("%d%m%y"), )
    )
    if len(download_links) == 0:
        print("⚠️ no URLs found, aborting")
        return None
    if len(download_links) > 1:
        print("⚠️ too many URLs found, aborting")
        return None
    path = download_links[0].attrib.get("href")
    return f"https://www.mediapart.fr{path}" if path.startswith("/") else path


def download_pdf(session, pdf_url):
    print(f"downloading file {pdf_url}...")
    req = session.get(pdf_url, allow_redirects=True)
    print("  downloaded!")
    return req.content

# method inspired by https://alexwlchan.net/2016/05/python-smtplib-and-fastmail/
def send_mail(pdf_content):
    print("logging to SMTP...")
    smtp = smtplib.SMTP_SSL(os.environ["M2M_SMTP_SERVER_HOST"], port=465)
    smtp.login(os.environ["M2M_SMTP_FROM_EMAIL"], os.environ["M2M_SMTP_PASSWORD"])
    msg_root = MIMEMultipart()
    msg_root['Subject'] = f"Journal Mediapart {YESTERDAY.strftime('%d/%m/%Y')}"
    msg_root['From'] = os.environ["M2M_SMTP_FROM_EMAIL"]
    msg_root['To'] = os.environ["M2M_SMTP_TO_EMAIL"]
    msg_alternative = MIMEMultipart('alternative')
    msg_root.attach(msg_alternative)
    prt = MIMEBase('application', "octet-stream")
    prt.set_payload(pdf_content)
    encoders.encode_base64(prt)
    filename = "mediapart_%s.pdf" % YESTERDAY.strftime('%d/%m/%Y')
    prt.add_header('Content-Disposition', 'attachment; filename="%s"' % (filename, ))
    msg_root.attach(prt)
    print("Sending mail with PDF attached...")
    smtp.sendmail(
        os.environ["M2M_SMTP_FROM_EMAIL"],
        os.environ["M2M_SMTP_TO_EMAIL"],
        msg_root.as_string()
    )
    print("  sent!")

if __name__ == "__main__":
    if not validate_environment_variables():
        exit(1)
    session = get_logged_in_session()
    pdf_url = get_yesterday_pdf_url(session)
    if not pdf_url:
        exit(1)
    pdf_content = download_pdf(session, pdf_url)
    send_mail(pdf_content)
