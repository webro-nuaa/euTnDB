import logging
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional

from app.core.config import settings

logger = logging.getLogger("tndb.email")


def send_email(
    to_email: str,
    subject: str,
    body_html: str,
    attachment_content: Optional[bytes] = None,
    attachment_filename: Optional[str] = None,
) -> bool:
    if not settings.SMTP_HOST or not settings.SMTP_USER:
        return False

    try:
        msg = MIMEMultipart()
        msg["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_USER}>"
        msg["To"] = to_email
        msg["Subject"] = subject

        msg.attach(MIMEText(body_html, "html", "utf-8"))

        if attachment_content and attachment_filename:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment_content)
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename={attachment_filename}",
            )
            msg.attach(part)

        if settings.SMTP_USE_SSL:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT, context=context) as server:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.sendmail(settings.SMTP_USER, to_email, msg.as_string())
        else:
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.sendmail(settings.SMTP_USER, to_email, msg.as_string())

        return True
    except Exception as e:
        logger.error("Failed to send email: %s", e)
        return False


def send_download_approved_email(
    to_email: str,
    requester_name: str,
    data_description: str,
    attachment_content: Optional[bytes] = None,
    attachment_filename: Optional[str] = None,
) -> bool:
    subject = "euTnDB Data Download Approved"
    body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
      <div style="background: #1a73e8; color: white; padding: 20px; border-radius: 8px 8px 0 0;">
        <h2 style="margin: 0;">euTnDB - Download Request Approved</h2>
      </div>
      <div style="padding: 20px; border: 1px solid #e0e0e0; border-top: none; border-radius: 0 0 8px 8px;">
        <p>Dear {requester_name or 'Researcher'},</p>
        <p>Your download request has been <strong style="color: #34a853;">approved</strong> by the euTnDB administrator.</p>
        <p><strong>Requested Data:</strong> {data_description}</p>
        <p>The data file is attached to this email. You can also visit <a href="https://tndb.org">euTnDB</a> for more information.</p>
        <hr style="border: none; border-top: 1px solid #e0e0e0; margin: 20px 0;">
        <p style="color: #80868b; font-size: 12px;">This is an automated email from euTnDB. Please do not reply directly.</p>
      </div>
    </div>
    """
    return send_email(to_email, subject, body, attachment_content, attachment_filename)


def send_download_rejected_email(
    to_email: str,
    requester_name: str,
    data_description: str,
    reason: str,
) -> bool:
    subject = "euTnDB Data Download Request Rejected"
    body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
      <div style="background: #ea4335; color: white; padding: 20px; border-radius: 8px 8px 0 0;">
        <h2 style="margin: 0;">euTnDB - Download Request Rejected</h2>
      </div>
      <div style="padding: 20px; border: 1px solid #e0e0e0; border-top: none; border-radius: 0 0 8px 8px;">
        <p>Dear {requester_name or 'Researcher'},</p>
        <p>We regret to inform you that your download request has been <strong style="color: #ea4335;">rejected</strong>.</p>
        <p><strong>Requested Data:</strong> {data_description}</p>
        <p><strong>Reason:</strong></p>
        <div style="background: #fce8e6; padding: 12px; border-radius: 6px; border-left: 3px solid #ea4335;">
          {reason}
        </div>
        <p>If you have questions, please contact the euTnDB team.</p>
        <hr style="border: none; border-top: 1px solid #e0e0e0; margin: 20px 0;">
        <p style="color: #80868b; font-size: 12px;">This is an automated email from euTnDB. Please do not reply directly.</p>
      </div>
    </div>
    """
    return send_email(to_email, subject, body)
