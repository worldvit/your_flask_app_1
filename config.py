import os
from dotenv import load_dotenv, find_dotenv
import binascii # os.urandom().hex() 대신 binascii.hexlify 사용 (바이트 -> 16진수)

# .env 파일의 절대 경로를 명시하여 환경 변수를 로드합니다.
dotenv_path = find_dotenv('/var/www/html/your_flask_app/.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
    print("DEBUG: .env variables loaded from explicit path in config.py.")
else:
    print(f"WARNING: .env file not found at {dotenv_path} in config.py. Environment variables might not be loaded.")

class Config:
    """Flask 애플리케이션의 기본 설정 클래스."""

    # FLASK_SECRET_KEY 설정
    # 환경 변수에서 SECRET_KEY를 가져옵니다. 없을 경우 임시 키를 생성합니다.
    # 프로덕션 환경에서는 반드시 .env에 유효하고 고유한 키가 존재해야 합니다.
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
    if not SECRET_KEY:
        # os.urandom().hex()는 Python 3.12에서 bytes.hex()로 대체됨.
        # 또는 binascii.hexlify 사용.
        SECRET_KEY = binascii.hexlify(os.urandom(24)).decode('utf-8') # 임시 키 생성
        print(f"WARNING: FLASK_SECRET_KEY not found in .env. Using newly generated key for this run: {SECRET_KEY}")
        print("Please add 'FLASK_SECRET_KEY={}' to your .env file for persistent security.".format(SECRET_KEY))
    print(f"DEBUG: Flask secret key loaded in Config: {'exists' if SECRET_KEY else 'NOT FOUND'}")

    # 데이터베이스 연결 설정
    # 환경 변수가 설정되지 않았을 경우 사용할 기본값(폴백)을 지정합니다.
    DB_HOST = os.getenv('DB_HOST', '10.10.8.4')
    DB_USER = os.getenv('DB_USER', 'flask_user')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'P@ssw0rd')
    DB_NAME = os.getenv('DB_NAME', 'flask_auth_db')

    # 필수 DB 환경 변수가 없는 경우 경고 (앱 시작 시 get_db_connection에서 더 엄격하게 체크)
    if not all([DB_HOST, DB_USER, DB_PASSWORD, DB_NAME]):
        print("WARNING: One or more DB environment variables are not set. Using fallback values.")


