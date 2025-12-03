import smtplib
import os
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader, select_autoescape
from datetime import datetime
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()


class BaseMailer:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER")
        self.smtp_port = int(os.getenv("SMTP_PORT"))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("FROM_EMAIL")
        self.frontend_url = os.getenv("FRONTEND_URL")

        template_dir = Path(__file__).parent.parent / "templates/mailer"
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )

        self.env.filters['format_date'] = self.format_date

    @staticmethod
    def format_date(value, format='%B %d, %Y'):
        """Jinja2 filter to format dates"""
        if isinstance(value, datetime):
            return value.strftime(format)
        return value

    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render HTML template with context"""
        template = self.env.get_template(template_name)
        # Add current year to all templates
        context['current_year'] = datetime.now().year
        return template.render(**context)

    def send_email(
            self,
            to_email: str,
            subject: str,
            template_name: str,
            context: Dict[str, Any],
            cc: Optional[list] = None,
            bcc: Optional[list] = None
    ) -> bool:
        """Send email using HTML template"""
        try:
            # Render HTML template
            html_content = self.render_template(template_name, context)

            # Create plain text version (optional but recommended)
            plain_text = self.html_to_plain_text(html_content)

            # Create email message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email

            if cc:
                msg['Cc'] = ', '.join(cc)
            if bcc:
                msg['Bcc'] = ', '.join(bcc)

            # Attach both HTML and plain text versions
            msg.attach(MIMEText(plain_text, 'plain'))
            msg.attach(MIMEText(html_content, 'html'))

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                recipients = [to_email]
                if cc:
                    recipients.extend(cc)
                if bcc:
                    recipients.extend(bcc)
                server.send_message(msg, from_addr=self.from_email, to_addrs=recipients)

            print(f"Email sent successfully to {to_email}")
            return True

        except Exception as e:
            print(f"Failed to send email to {to_email}: {str(e)}")
            # Log the error properly in production
            return False

    @staticmethod
    def html_to_plain_text(html: str) -> str:
        """Convert HTML to plain text (basic implementation)"""
        import re
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', html)
        # Convert HTML entities
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        # Collapse multiple spaces
        text = re.sub(r'\s+', ' ', text).strip()
        return text