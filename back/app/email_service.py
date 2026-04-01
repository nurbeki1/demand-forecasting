"""
Email Service using Resend
"""
import os
import random
import string
from datetime import datetime, timedelta
from typing import Optional

import resend

# Initialize Resend
RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")
FROM_EMAIL = os.environ.get("FROM_EMAIL", "Forecast AI <noreply@resend.dev>")

resend.api_key = RESEND_API_KEY


def generate_verification_code() -> str:
    """Generate a 6-digit verification code"""
    return ''.join(random.choices(string.digits, k=6))


def send_verification_email(to_email: str, code: str) -> bool:
    """
    Send verification code to user's email
    Returns True if sent successfully
    """
    if not RESEND_API_KEY:
        print(f"[DEV MODE] Verification code for {to_email}: {code}")
        return True

    try:
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: 'Inter', -apple-system, sans-serif; background: #0a0a0f; color: #fff; padding: 40px; }}
                .container {{ max-width: 480px; margin: 0 auto; background: linear-gradient(145deg, #14171f 0%, #0d1017 100%); border-radius: 24px; padding: 40px; border: 1px solid rgba(255,255,255,0.08); }}
                .logo {{ text-align: center; margin-bottom: 24px; }}
                .logo svg {{ width: 48px; height: 48px; }}
                h1 {{ text-align: center; font-size: 24px; margin-bottom: 16px; color: #f4f4f5; }}
                p {{ color: #a1a1aa; font-size: 15px; line-height: 1.6; text-align: center; }}
                .code {{ background: linear-gradient(135deg, #10b981 0%, #06b6d4 100%); color: #000; font-size: 32px; font-weight: 700; letter-spacing: 8px; padding: 20px 32px; border-radius: 16px; text-align: center; margin: 32px 0; }}
                .footer {{ text-align: center; color: #71717a; font-size: 13px; margin-top: 32px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="logo">
                    <svg viewBox="0 0 48 48" fill="none">
                        <circle cx="24" cy="24" r="20" stroke="#10b981" stroke-width="2"/>
                        <circle cx="24" cy="24" r="8" fill="#10b981"/>
                    </svg>
                </div>
                <h1>Код подтверждения</h1>
                <p>Используйте этот код для завершения регистрации в Forecast AI</p>
                <div class="code">{code}</div>
                <p>Код действителен 10 минут.</p>
                <p>Если вы не запрашивали этот код, просто проигнорируйте это письмо.</p>
                <div class="footer">
                    <p>Forecast AI - Интеллектуальное прогнозирование спроса</p>
                </div>
            </div>
        </body>
        </html>
        """

        params = {
            "from": FROM_EMAIL,
            "to": [to_email],
            "subject": f"Код подтверждения: {code}",
            "html": html_content,
        }

        resend.Emails.send(params)
        return True

    except Exception as e:
        print(f"Failed to send email: {e}")
        return False


def get_code_expiry() -> datetime:
    """Get expiry time for verification code (10 minutes from now)"""
    return datetime.utcnow() + timedelta(minutes=10)
