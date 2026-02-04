import asyncio
import re
import sys
import subprocess
from auth import auth
import base64
EMAIL_REGEX = r"<(.+?)>"
def get_content(msg_data):
    encoded_text = msg_data.get("payload",{})["parts"][0]["body"]["data"]
    content = base64.urlsafe_b64decode(encoded_text).decode("utf-8")
    return content
def run_send_email(email_id, content):
     run_ = subprocess.run([sys.executable , "mail.py",email_id,content],capture_output=True,text=True)
     print(email_id)
     return run_
async def get_primary_emails(max_result=5):
    page_token = None
    service = auth()

    while True:
        gmail_ids = service.users().messages().list(
            userId="me",
            maxResults=max_result,
            pageToken=page_token,
            q="category:primary"
        ).execute()

        messages = gmail_ids.get("messages", [])

        for msg in messages:
            msg_data = service.users().messages().get(
                userId="me",
                id=msg["id"],
                format="full",
                metadataHeaders=["From","subject"]
            ).execute()
            labels = msg_data.get("labelIds",[])
            for i in labels:
                if i=="UNREAD":
                    content = get_content(msg_data)
                    headers = msg_data.get("payload", {}).get("headers", [])
                    for h in headers:
                        if h["name"] == "From":
                            from_value = h["value"]
                            match = re.search(EMAIL_REGEX, from_value)
                            email = match.group(1) if match else from_value
                    if email:
                        run_send_email(email,content)
                        service.users().messages().modify(
                            userId= "me",
                            id = msg["id"],
                            body = {
                                "removeLabelIds" : ["UNREAD"],
                                "addLabelIds" : ["TRASH"]
                            }
                        ).execute()

                    
        page_token = gmail_ids.get("nextPageToken")
        if not page_token:
            print("No new Messages")
            continue
        await asyncio.sleep(5)
asyncio.run(get_primary_emails())
