import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
import streamlit as st

class EmailSender:
    def __init__(self):
        load_dotenv()
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = st.secrets["email"]["user"]
        self.sender_password = st.secrets["email"]["password"]

    def send_email(self, recipient_email, subject, body):
        """이메일 발송"""
        try:
            # 이메일 메시지 생성
            message = MIMEMultipart()
            message["From"] = self.sender_email
            message["To"] = recipient_email
            message["Subject"] = subject

            # HTML 본문 추가
            html_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #2c3e50;">📊 오늘의 투자 알림</h2>
                    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0;">
                        {body}
                    </div>
                    <div style="margin-top: 30px; font-size: 12px; color: #666;">
                        <p>본 메일은 자동으로 발송되었습니다.</p>
                        <p>문의사항이 있으시면 고객센터로 연락해 주세요.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            message.attach(MIMEText(html_body, "html"))

            # SMTP 서버 연결 및 이메일 발송
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)

            return True
        except Exception as e:
            print(f"이메일 발송 중 오류 발생: {str(e)}")
            return False

    def send_daily_alerts(self, user_email, market_headline, portfolio_alert, risk_warning, action_required):
        """일일 투자 알림 이메일 발송"""
        subject = f"📈 {market_headline}"
        
        body = f"""
        <div style="margin-bottom: 20px;">
            <h3 style="color: #2c3e50;">💼 포트폴리오 현황</h3>
            <p>{portfolio_alert}</p>
        </div>
        
        <div style="margin-bottom: 20px;">
            <h3 style="color: #2c3e50;">⚠️ 리스크 경고</h3>
            <p>{risk_warning}</p>
        </div>
        
        <div style="margin-bottom: 20px;">
            <h3 style="color: #2c3e50;">🎯 투자 액션</h3>
            <p>{action_required}</p>
        </div>
        """
        
        return self.send_email(user_email, subject, body) 