# backend/services/email_service.py
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import base64
import os
from dotenv import load_dotenv

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/gmail.send', 'https://www.googleapis.com/auth/gmail.readonly']

class EmailService:
    def __init__(self):
        self.creds = None
        self.service = None

    def authenticate(self):
        flow = InstalledAppFlow.from_client_config({
            "installed": {
                "client_id": os.getenv('GMAIL_CLIENT_ID'),
                "client_secret": os.getenv('GMAIL_CLIENT_SECRET'),
                "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob"],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        }, SCOPES)

        self.creds = flow.run_local_server(port=0)
        self.service = build('gmail', 'v1', credentials=self.creds)

    def send_email(self, to, subject, body):
        try:
            if not self.service:
                self.authenticate()

            message = MIMEText(body)
            message['to'] = to
            message['subject'] = subject

            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            self.service.users().messages().send(userId='me', body={'raw': raw_message}).execute()
            
            return {'success': True, 'message': 'Email sent successfully'}
        except Exception as e:
            return {'error': str(e)}

    def get_emails(self, max_results=10):
        try:
            if not self.service:
                self.authenticate()

            results = self.service.users().messages().list(userId='me', maxResults=max_results).execute()
            messages = results.get('messages', [])

            emails = []
            for message in messages:
                msg = self.service.users().messages().get(userId='me', id=message['id']).execute()
                headers = msg['payload']['headers']
                
                subject = next(h['value'] for h in headers if h['name'] == 'Subject')
                sender = next(h['value'] for h in headers if h['name'] == 'From')
                
                emails.append({
                    'id': msg['id'],
                    'subject': subject,
                    'sender': sender,
                    'snippet': msg['snippet']
                })

            return emails
        except Exception as e:
            return {'error': str(e)}