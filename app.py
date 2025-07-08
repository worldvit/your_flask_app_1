import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
# config.py에서 설정 클래스 임포트
from config import Config

# 모든 블루프린트 임포트
from auth.routes import auth_bp
from board.routes import board_bp
from diary.routes import diary_bp
from todos.routes import todos_bp

# Flask 애플리케이션 인스턴스 생성
app = Flask(__name__)

# config.py에서 정의한 설정 적용
app.config.from_object(Config)

# FLASK_SECRET_KEY는 app.config['SECRET_KEY']로 접근
print(f"DEBUG: Flask secret key loaded from app.config: {'exists' if app.secret_key else 'NOT FOUND'}")


# --- 블루프린트 등록 ---
# 각 블루프린트를 메인 앱에 등록합니다.
# url_prefix는 해당 블루프린트 안의 모든 라우트 앞에 자동으로 붙을 경로를 의미합니다.
app.register_blueprint(auth_bp) # 인증 블루프린트는 기본 경로('/')를 사용
app.register_blueprint(board_bp, url_prefix='/board') # 게시판 블루프린트는 /board로 시작
app.register_blueprint(diary_bp, url_prefix='/diary') # 일기장 블루프린트는 /diary로 시작
app.register_blueprint(todos_bp, url_prefix='/todos') # To-Do List 블루프린트는 /todos로 시작


# --- 개발용 블록 (Apache/mod_wsgi로 배포 시에는 사용되지 않습니다.) ---
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')


