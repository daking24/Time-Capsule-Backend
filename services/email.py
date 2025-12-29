from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr
import os
# Determine port and SSL settings dynamically
mail_port = int(os.getenv("MAIL_PORT", 465))
use_ssl = (mail_port == 465)

print(f"📧 EMAIL CONFIG: Server={os.getenv('MAIL_SERVER')}, Port={mail_port}, SSL={use_ssl}, User={os.getenv('MAIL_USERNAME')}")

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=mail_port,
    MAIL_SERVER=os.getenv("MAIL_SERVER", "smtp.gmail.com"),
    MAIL_STARTTLS=not use_ssl, # True if 587
    MAIL_SSL_TLS=use_ssl,      # True if 465
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

async def send_email(email_to: EmailStr, subject: str, message_text: str):
    """Generic email sender"""
    html = f"""
    <div style="font-family: sans-serif; padding: 20px;">
        <h2>{subject}</h2>
        <p>{message_text}</p>
    </div>
    """
    message = MessageSchema(
        subject=subject,
        recipients=[email_to],
        body=html,
        subtype=MessageType.html
    )
    fm = FastMail(conf)
    await fm.send_message(message)

async def send_time_capsule_email(email_to: EmailStr, content: str, media_url: str = None, media_type: str = "text"):
    
    subject = "Your Time Capsule has arrived! 🕰️"
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital@0;1&family=Inter:wght@300;400&display=swap');
            
            body {{
                font-family: 'Inter', sans-serif;
                background-color: #0f0f18;
                color: #d4af37;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 40px auto;
                background-color: #1a1a24;
                border: 1px solid #d4af37;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 0 20px rgba(212, 175, 55, 0.2);
            }}
            .header {{
                background: linear-gradient(135deg, #d4af37 0%, #b4941f 100%);
                color: #0f0f18;
                padding: 30px;
                text-align: center;
            }}
            .header h1 {{
                font-family: 'Playfair Display', serif;
                margin: 0;
                font-size: 28px;
                letter-spacing: 2px;
                text-transform: uppercase;
            }}
            .content {{
                padding: 40px;
                background-image: radial-gradient(circle at center, rgba(212, 175, 55, 0.05) 0%, transparent 70%);
            }}
            .message-box {{
                border-left: 3px solid #d4af37;
                padding-left: 20px;
                margin: 30px 0;
                font-style: italic;
                color: #e2e8f0;
                font-size: 16px;
                line-height: 1.6;
            }}
            .media-link {{
                display: block;
                width: 100%;
                text-align: center;
                background-color: rgba(212, 175, 55, 0.1);
                border: 1px solid #d4af37;
                color: #d4af37;
                text-decoration: none;
                padding: 15px 0;
                border-radius: 4px;
                margin-top: 20px;
                font-weight: bold;
                transition: all 0.3s ease;
            }}
            .media-link:hover {{
                background-color: #d4af37;
                color: #0f0f18;
            }}
            .footer {{
                text-align: center;
                padding: 20px;
                font-size: 12px;
                color: #64748b;
                border-top: 1px solid rgba(212, 175, 55, 0.2);
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>TimeCapsule Unlocked</h1>
            </div>
            <div class="content">
                <p style="text-align: center; color: #94a3b8; margin-bottom: 30px;">
                    A memory you preserved has arrived from the past.
                </p>
                
                <div class="message-box">
                    "{content}"
                </div>
                
                {f'<a href="{media_url}" class="media-link">View Attached Media ({media_type})</a>' if media_url else ''}
            </div>
            <div class="footer">
                &copy; 2025 TimeCapsule. Preserving digital legacy.
            </div>
        </div>
    </body>
    </html>
    """

    message = MessageSchema(
        subject=subject,
        recipients=[email_to],
        body=html,
        subtype=MessageType.html
    )

    fm = FastMail(conf)
    await fm.send_message(message)

async def send_verification_email(email_to: EmailStr, code: str):
    """
    Sends a verification code email using the premium template.
    """
    subject = "🔑 Your Vault Access Code"
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family: 'Playfair Display', serif; background-color: #0f0f18; color: #d4af37; padding: 40px; text-align: center;">
        <div style="max-width: 400px; margin: 0 auto; border: 1px solid #d4af37; padding: 30px; border-radius: 8px; background-color: #1a1a24; box-shadow: 0 0 20px rgba(212, 175, 55, 0.2);">
            <h2 style="color: #d4af37; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 30px; border-bottom: 1px solid #d4af37; padding-bottom: 10px;">Vault Access</h2>
            <p style="color: #94a3b8; font-family: sans-serif; margin-bottom: 20px;">Your magic key to enter the time capsule:</p>
            <div style="background-color: rgba(212, 175, 55, 0.1); color: #d4af37; font-size: 32px; letter-spacing: 5px; font-weight: bold; padding: 20px; border-radius: 4px; border: 1px dashed #d4af37; margin-bottom: 30px;">
                {code}
            </div>
            <p style="color: #64748b; font-size: 12px; font-family: sans-serif;">This code is valid for 10 minutes. Do not share it.</p>
        </div>
    </body>
    </html>
    """
    
    message = MessageSchema(
        subject=subject,
        recipients=[email_to],
        body=html,
        subtype=MessageType.html
    )

    fm = FastMail(conf)
    await fm.send_message(message)
