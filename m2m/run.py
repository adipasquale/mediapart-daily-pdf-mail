import requests
from lxml.html import fromstring
from datetime import datetime, timezone, timedelta
import os
from rmapy.api import Client
from rmapy.document import ZipDocument

# UTC+2 = Paris timezone
YESTERDAY = datetime.now(timezone(timedelta(hours=+2))) - timedelta(days=1)

def validate_environment_variables():
    for key in ["M2M_MEDIAPART_LOGIN", "M2M_MEDIAPART_PASSWORD", "M2M_REMARKABLE_DEVICE_TOKEN"]:
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
    filename = f"Mediapart-{YESTERDAY.strftime('%d-%m-%Y')}.pdf"
    with open(filename, "wb") as f:
        f.write(req.content)
    print("  downloaded!")
    return filename

def send_to_rm(pdf_filename):
    rmapy = Client()
    rmapy.token_set["devicetoken"] = os.environ["M2M_REMARKABLE_DEVICE_TOKEN"]
    rmapy.renew_token()
    if not rmapy.is_auth():
        print("⚠️ could not auth to ReMarkable")
        exit(1)
    raw_document = ZipDocument(doc=pdf_filename)
    if not rmapy.upload(raw_document):
        print("⚠️ could not upload to ReMarkable")
        exit(1)
    print("uploaded to ReMarkable!")

if __name__ == "__main__":
    if not validate_environment_variables():
        exit(1)
    session = get_logged_in_session()
    pdf_url = get_yesterday_pdf_url(session)
    if not pdf_url:
        exit(1)
    pdf_filename = download_pdf(session, pdf_url)
    send_to_rm(pdf_filename)
