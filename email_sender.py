import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit as st
import os
from dotenv import load_dotenv
from modules.llm_models.market_headline import MarketHeadlineLLM
from modules.llm_models.portfolio_alert import PortfolioAlertLLM
from modules.llm_models.risk_warning import RiskWarningLLM
from modules.llm_models.action_required import ActionRequiredLLM
from modules.llm_models.data_processor import DataProcessor
from modules.user_manager import UserManager
from datetime import datetime

# .env 파일의 환경 변수 불러오기
load_dotenv()

class EmailSender:
    def __init__(self):
        """이메일 발송을 위한 초기화"""
        if st.secrets["email"]["user"]:
            self.sender_email = st.secrets["email"]["user"]
        else:
            self.sender_email = os.getenv("EMAIL_USER")

        if st.secrets["email"]["password"]:
            self.sender_password = st.secrets["email"]["password"]
        else:
            self.sender_password = os.getenv("EMAIL_PASSWORD")

        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587

    def send_daily_alerts(self, user_email: str, market_headline: str, portfolio_alert: str, 
                         risk_warning: str, action_required: str) -> bool:
        """일일 알림 이메일 발송"""
        try:
            if not self.sender_email or not self.sender_password:
                print("이메일 계정 정보가 설정되지 않았습니다.")
                return False

            # 이메일 메시지 생성
            msg = MIMEMultipart()
            msg['From'] = f"Fynai <{self.sender_email}>"
            msg['To'] = user_email
            msg['Subject'] = "📈 Fynai - 오늘의 자산관리 알림"

            # HTML 형식의 이메일 본문 생성
            html_content = f"""
            <html>
            <head>
                <style>
                    body {{
                        font-family: 'Arial', sans-serif;
                        line-height: 1.6;
                        color: #333;
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                    }}
                    .header {{
                        background: linear-gradient(135deg, #2E4057 0%, #1a2634 100%);
                        color: white;
                        padding: 30px;
                        text-align: center;
                        border-radius: 10px 10px 0 0;
                    }}
                    .content {{
                        background: #ffffff;
                        padding: 20px;
                        border: 1px solid #e0e0e0;
                        border-radius: 0 0 10px 10px;
                    }}
                    .section {{
                        background-color: #f8f9fa;
                        padding: 20px;
                        border-radius: 8px;
                        margin: 15px 0;
                        border-left: 4px solid #2E4057;
                    }}
                    .section h3 {{
                        color: #2E4057;
                        margin-top: 0;
                        font-size: 1.2em;
                    }}
                    .footer {{
                        text-align: center;
                        margin-top: 30px;
                        padding: 20px;
                        background: #f8f9fa;
                        border-radius: 8px;
                    }}
                    .button {{
                        display: inline-block;
                        background: #4CAF50;
                        color: white;
                        padding: 12px 24px;
                        text-decoration: none;
                        border-radius: 5px;
                        margin-top: 15px;
                        font-weight: bold;
                        font-size: 16px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                        transition: all 0.3s ease;
                    }}
                    .button:hover {{
                        background: #45a049;
                        transform: translateY(-2px);
                        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                    }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1 style="margin: 0; font-size: 24px;"> 📧 오늘의 자산관리 알림</h1>
                    <p style="margin: 10px 0 0 0; opacity: 0.8;">Fynai - AI 기반 스마트 자산 관리 솔루션</p>
                </div>
                
                <div class="content">
                    <div class="section">
                        <h3>📰 시장 헤드라인</h3>
                        <p>{market_headline}</p>
                    </div>

                    <div class="section">
                        <h3>💼 포트폴리오 알림</h3>
                        <p>{portfolio_alert}</p>
                    </div>

                    <div class="section">
                        <h3>⚠️ 리스크 경고</h3>
                        <p>{risk_warning}</p>
                    </div>

                    <div class="section">
                        <h3>🎯 투자 액션</h3>
                        <p>{action_required}</p>
                    </div>

                    <div class="footer">
                        <p style="margin: 0; color: #666;">더 자세한 분석과 인사이트를 확인하세요!</p>
                        <a href="https://capstone-2025-41-assetmanagementdashboard.streamlit.app/" class="button">
                            Fynai 대시보드 바로가기
                        </a>
                        <p style="margin: 15px 0 0 0; font-size: 0.9em; color: #666;">
                            이 이메일은 자동으로 발송되었습니다.<br>
                            © 2025 Fynai. All rights reserved.
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """

            msg.attach(MIMEText(html_content, 'html'))

            # SMTP 서버 연결 및 이메일 발송
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                try:
                    server.login(self.sender_email, self.sender_password)
                except smtplib.SMTPAuthenticationError:
                    print("Gmail 인증 실패: 앱 비밀번호를 확인해주세요.")
                    return False
                except Exception as e:
                    print(f"로그인 중 오류 발생: {str(e)}")
                    return False
                
                try:
                    server.send_message(msg)
                    return True
                except Exception as e:
                    print(f"이메일 발송 중 오류 발생: {str(e)}")
                    return False

        except Exception as e:
            print(f"이메일 발송 중 오류 발생: {str(e)}")
            return False

if __name__ == "__main__":
    # 현재 날짜 가져오기
    current_date = datetime.now().strftime("%Y년 %m월 %d일")
    
    # 사용자 관리자 초기화
    user_manager = UserManager()
    
    # 모든 사용자 이름 가져오기
    all_usernames = user_manager.db.get_all_user_name()
    if not all_usernames:
        print("사용자 정보를 찾을 수 없습니다.")
        exit()

    # LLM 모델 초기화
    market_headline_llm = MarketHeadlineLLM()
    portfolio_alert_llm = PortfolioAlertLLM()
    risk_warning_llm = RiskWarningLLM()
    action_required_llm = ActionRequiredLLM()

    # EmailSender 인스턴스 생성
    email_sender = EmailSender()

    # 각 사용자별로 이메일 발송
    for username in all_usernames:
        # 사용자 정보 가져오기
        user_data = user_manager.get_user_info(username)
        if not user_data:
            print(f"사용자 {username}의 정보를 찾을 수 없습니다.")
            continue
            
        user_email = user_data.get("email", "")
        if not user_email:
            print(f"사용자 {username}의 이메일 정보를 찾을 수 없습니다.")
            continue

        print(f"사용자 {username}에게 이메일 발송 중...")

        # 데이터 프로세서 초기화
        data_processor = DataProcessor(username)

        # LLM을 통해 각 섹션의 내용 생성
        market_data = data_processor.get_market_data()
        portfolio_data = data_processor.get_portfolio_data()
        risk_data = data_processor.get_risk_data()
        investment_data = data_processor.get_investment_data()

        # current_date 추가
        market_data["current_date"] = current_date
        portfolio_data["current_date"] = current_date
        risk_data["current_date"] = current_date
        investment_data["current_date"] = current_date

        market_headline = market_headline_llm.generate(**market_data)
        portfolio_alert = portfolio_alert_llm.generate(**portfolio_data)
        risk_warning = risk_warning_llm.generate(**risk_data)
        action_required = action_required_llm.generate(**investment_data)

        # 이메일 발송
        success = email_sender.send_daily_alerts(
            user_email=user_email,
            market_headline=market_headline,
            portfolio_alert=portfolio_alert,
            risk_warning=risk_warning,
            action_required=action_required
        )

        if success:
            print(f"사용자 {username}에게 이메일이 성공적으로 발송되었습니다.")
        else:
            print(f"사용자 {username}에게 이메일 발송에 실패했습니다.") 