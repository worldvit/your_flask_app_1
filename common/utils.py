import os
import pymysql.cursors
from flask import flash, current_app # current_app 임포트 추가

def get_db_connection():
    """데이터베이스 연결을 설정하고 반환합니다."""
    print("DEBUG: Attempting to get DB connection...") # 디버깅용 로그

    # Flask 앱의 현재 설정(app.config)에서 DB 정보 가져오기
    # app.config는 config.py의 Config 클래스에서 로드된 설정들을 포함합니다.
    db_host = current_app.config.get('DB_HOST')
    db_user = current_app.config.get('DB_USER')
    db_password = current_app.config.get('DB_PASSWORD')
    db_name = current_app.config.get('DB_NAME')

    # 필수 DB 환경 변수가 없는 경우 RuntimeError 발생 (엄격한 체크)
    if not all([db_host, db_user, db_password, db_name]):
        raise RuntimeError("데이터베이스 연결 환경 변수(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)가 모두 설정되지 않았습니다. Apache 설정(flask_auth.conf) 또는 config.py를 확인해주세요.")

    DB_CONFIG_RUNTIME = {
        'host': db_host,
        'user': db_user,
        'password': db_password,
        'db': db_name,
        'charset': 'utf8mb4',
        'cursorclass': pymysql.cursors.DictCursor
    }

    try:
        conn = pymysql.connect(**DB_CONFIG_RUNTIME)
        print("DEBUG: DB connection successful!") # 디버깅용 로그
        return conn
    except pymysql.Error as e:
        print(f"DEBUG: DB connection failed in get_db_connection: {e}") # 디버깅용 로그
        flash('데이터베이스 연결 오류가 발생했습니다. 잠시 후 다시 시도해주세요.', 'error')
        raise

