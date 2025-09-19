import os
from dotenv import load_dotenv, find_dotenv
import binascii

# .env 파일에서 환경 변수 로드
dotenv_path = find_dotenv('/var/www/html/your_flask_app/.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
    print("DEBUG: .env variables loaded from explicit path in config.py.")
else:
    print(f"WARNING: .env file not found at {dotenv_path}. Environment variables might not be loaded.")

class Config:
    """Flask 애플리케이션의 기본 설정 클래스."""

    # 1. SECRET_KEY 설정 (기존 로직 유지)
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
    if not SECRET_KEY:
        SECRET_KEY = binascii.hexlify(os.urandom(24)).decode('utf-8')
        print(f"WARNING: FLASK_SECRET_KEY not found. Using temporary key: {SECRET_KEY}")

    # 2. 데이터베이스 연결 정보 로드 (기존 로직 유지)
    DB_USER = os.getenv('DB_USER', 'flask_user')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'P@ssw0rd')
    DB_HOST = os.getenv('DB_HOST', '192.168.0.4')
    DB_NAME = os.getenv('DB_NAME', 'flask_auth_db')
    DB_PORT = os.getenv('DB_PORT', '3306') # 포트도 환경 변수에서 가져오도록 추가

    # 3. SQLAlchemy 설정 추가 (가장 중요한 부분)
    # 위에서 로드한 DB 정보들을 조합하여 SQLAlchemy 연결 URI를 생성합니다.
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
    )

    # SQLAlchemy의 이벤트 처리 옵션 (False로 설정하여 오버헤드 줄임)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # (선택사항) 실행되는 SQL 쿼리를 터미널에 출력하고 싶을 때 True로 설정
    # 개발 시에는 True로 두면 디버깅에 매우 유용합니다.
    SQLALCHEMY_ECHO = False
