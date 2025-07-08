import os
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from common.utils import get_db_connection # common/utils.py에서 가져옴

# 'auth_bp'라는 이름의 블루프린트 인스턴스 생성
# url_prefix는 이 블루프린트 안의 모든 라우트 앞에 자동으로 붙을 경로를 의미합니다.
# 여기서는 인증 기능이므로 별도 프리픽스 없이 '/'를 기본으로 사용합니다.
auth_bp = Blueprint('auth', __name__)

# --- 사용자 인증 관련 라우트 ---

@auth_bp.route('/') # @app.route 대신 @auth_bp.route 사용
def index():
    """
    메인 페이지를 렌더링합니다.
    로그인 상태에 따라 다른 UI (인증 폼 또는 링크 메뉴)를 보여줍니다.
    """
    if 'loggedin' in session:
        return render_template('main_logged_in.html', username=session['username'])
    return render_template('default.html')


@auth_bp.route('/register', methods=['POST'])
def register():
    """사용자 등록을 처리합니다."""
    username = request.form['username'].strip()
    password = request.form['password'].strip()

    if not username or not password:
        flash('사용자 이름과 비밀번호를 비워둘 수 없습니다.', 'error')
        return redirect(url_for('auth.index')) # url_for에 블루프린트 이름 명시

    hashed_password = generate_password_hash(password)

    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                flash('이미 존재하는 사용자 이름입니다. 다른 이름을 선택해주세요.', 'error')
                return redirect(url_for('auth.index')) # url_for에 블루프린트 이름 명시

            sql = "INSERT INTO users (username, password) VALUES (%s, %s)"
            cursor.execute(sql, (username, hashed_password))
        conn.commit()
        flash('회원가입에 성공했습니다! 이제 로그인할 수 있습니다.', 'success')
    except Exception as e:
        print(f"데이터베이스 오류 (회원가입): {e}")
        flash('회원가입에 실패했습니다. 잠시 후 다시 시도해주세요.', 'error')
    finally:
        if conn:
            conn.close()
    return redirect(url_for('auth.index')) # url_for에 블루프린트 이름 명시

@auth_bp.route('/login', methods=['POST'])
def login():
    """사용자 로그인을 처리합니다."""
    username = request.form['username'].strip()
    password = request.form['password'].strip()
    print(f"DEBUG: 로그인 시도 사용자: {username}")

    if not username or not password:
        print("DEBUG: 로그인 시도: 사용자 이름 또는 비밀번호가 비어 있습니다.")
        flash('사용자 이름과 비밀번호를 모두 입력해주세요.', 'error')
        return redirect(url_for('auth.index')) # url_for에 블루프린트 이름 명시

    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            sql = "SELECT id, username, password FROM users WHERE username = %s"
            cursor.execute(sql, (username,))
            user = cursor.fetchone()

            if user and check_password_hash(user['password'], password):
                session['loggedin'] = True
                session['id'] = user['id']
                session['username'] = user['username']
                print(f"DEBUG: 사용자 {username} 로그인 성공. 대시보드로 리디렉션.")
                flash(f'환영합니다, {user["username"]}님!', 'success')
                return redirect(url_for('auth.dashboard')) # url_for에 블루프린트 이름 명시
            else:
                print(f"DEBUG: 사용자 {username} 로그인 실패: 잘못된 자격 증명.")
                flash('잘못된 사용자 이름 또는 비밀번호입니다. 다시 시도해주세요.', 'error')
    except Exception as e:
        print(f"DEBUG: 로그인 처리 중 일반 오류: {e}")
        flash('로그인에 실패했습니다. 서버 오류입니다. 잠시 후 다시 시도해주세요.', 'error')
    finally:
        if conn:
            conn.close()
            print("DEBUG: 로그인 라우트에서 DB 연결 닫음.")
    return redirect(url_for('auth.index')) # url_for에 블루프린트 이름 명시

@auth_bp.route('/logout')
def logout():
    """현재 사용자를 로그아웃합니다."""
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    flash('성공적으로 로그아웃되었습니다.', 'success')
    return redirect(url_for('auth.index')) # url_for에 블루프린트 이름 명시

@auth_bp.route('/dashboard')
def dashboard():
    """
    로그인한 사용자에게는 메인 페이지로 리디렉션하고,
    로그아웃 상태이면 로그인 페이지로 리디렉션합니다.
    """
    if 'loggedin' in session:
        return redirect(url_for('auth.index')) # url_for에 블루프린트 이름 명시
    flash('이 페이지에 접근하려면 로그인해야 합니다.', 'error')
    return redirect(url_for('auth.index')) # url_for에 블루프린트 이름 명시

