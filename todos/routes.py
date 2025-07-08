from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from common.utils import get_db_connection # common/utils.py에서 가져옴
import pymysql.cursors
from datetime import datetime, timedelta
import calendar

# 'todos_bp'라는 이름의 블루프린트 인스턴스 생성
todos_bp = Blueprint('todos', __name__) # url_prefix는 app.py에서 등록 시 지정

# --- To-Do List 관련 라우트 ---

@todos_bp.route('/') # 실제 경로는 /todos
def todos_list():
    """To-Do 목록을 표시하고 필터링 옵션을 제공합니다."""
    if 'loggedin' not in session:
        flash('To-Do List를 보려면 로그인해야 합니다.', 'error')
        return redirect(url_for('auth.index')) # auth 블루프린트의 index로 리디렉션

    user_id = session['id']
    status_filter = request.args.get('status', 'all').strip()
    search_query = request.args.get('query', '').strip()

    conn = None
    todos = []
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            sql = "SELECT id, task, DATE_FORMAT(due_date, '%%Y-%%m-%%d') AS due_date, status, created_at FROM todos WHERE user_id = %s"
            params = [user_id]

            if status_filter != 'all':
                sql += " AND status = %s"
                params.append(status_filter)

            if search_query:
                sql += " AND task LIKE %s"
                params.append(f"%{search_query}%")

            sql += " ORDER BY created_at DESC" # 또는 due_date ASC

            cursor.execute(sql, params)
            todos = cursor.fetchall()
    except Exception as e:
        print(f"DEBUG: To-Do 목록 불러오기 오류: {e}")
        flash('To-Do 목록을 불러오는 데 실패했습니다. 잠시 후 다시 시도해주세요.', 'error')
    finally:
        if conn:
            conn.close()

    return render_template('todos_list.html',
                           todos=todos,
                           username=session['username'],
                           status_filter=status_filter,
                           search_query=search_query,
                           all_statuses=['미완료', '진행중', '완료', '기간연장'])


@todos_bp.route('/add', methods=['POST']) # 실제 경로는 /todos/add
def add_todo():
    """새 To-Do 항목을 추가합니다."""
    if 'loggedin' not in session:
        flash('To-Do 항목을 추가하려면 로그인해야 합니다.', 'error')
        return redirect(url_for('auth.index'))

    user_id = session['id']
    task = request.form['task'].strip()
    due_date_str = request.form.get('due_date', '').strip()
    status = request.form.get('status', '미완료').strip() # 기본 상태 '미완료'

    if not task:
        flash('할 일 내용을 비워둘 수 없습니다.', 'error')
        return redirect(url_for('todos.todos_list')) # url_for에 블루프린트 이름 명시

    due_date = None
    if due_date_str:
        try:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('유효하지 않은 마감일 형식입니다.', 'error')
            return redirect(url_for('todos.todos_list')) # url_for에 블루프린트 이름 명시

    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            sql = "INSERT INTO todos (user_id, task, due_date, status) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (user_id, task, due_date, status))
        conn.commit()
        flash('To-Do 항목이 성공적으로 추가되었습니다!', 'success')
    except Exception as e:
        print(f"DEBUG: To-Do 항목 추가 오류: {e}")
        flash('To-Do 항목 추가에 실패했습니다. 잠시 후 다시 시도해주세요.', 'error')
    finally:
        if conn:
            conn.close()
    return redirect(url_for('todos.todos_list')) # url_for에 블루프린트 이름 명시

@todos_bp.route('/update_status/<int:todo_id>/<string:new_status>', methods=['POST']) # 실제 경로는 /todos/update_status/<id>/<status>
def update_todo_status(todo_id, new_status):
    """To-Do 항목의 상태를 업데이트합니다."""
    if 'loggedin' not in session:
        flash('To-Do 항목 상태를 변경하려면 로그인해야 합니다.', 'error')
        return redirect(url_for('auth.index'))

    user_id = session['id']
    valid_statuses = ['미완료', '진행중', '완료', '기간연장'] # 모든 유효 상태 포함

    if new_status not in valid_statuses:
        flash('유효하지 않은 To-Do 상태입니다.', 'error')
        return redirect(url_for('todos.todos_list')) # url_for에 블루프린트 이름 명시

    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            sql_check = "SELECT id FROM todos WHERE id = %s AND user_id = %s"
            cursor.execute(sql_check, (todo_id, user_id))
            if not cursor.fetchone():
                flash('To-Do 항목을 찾을 수 없거나 권한이 없습니다.', 'error')
                return redirect(url_for('todos.todos_list')) # url_for에 블루프린트 이름 명시

            sql = "UPDATE todos SET status = %s WHERE id = %s AND user_id = %s"
            cursor.execute(sql, (new_status, todo_id, user_id))
        conn.commit()
        flash('To-Do 항목 상태가 성공적으로 업데이트되었습니다!', 'success')
    except Exception as e:
        print(f"DEBUG: To-Do 상태 업데이트 오류: {e}")
        flash('To-Do 항목 상태 업데이트에 실패했습니다. 잠시 후 다시 시도해주세요.', 'error')
    finally:
        if conn:
            conn.close()
    return redirect(url_for('todos.todos_list')) # url_for에 블루프린트 이름 명시

@todos_bp.route('/delete/<int:todo_id>', methods=['POST']) # 실제 경로는 /todos/delete/<id>
def delete_todo(todo_id):
    """To-Do 항목을 삭제합니다."""
    if 'loggedin' not in session:
        flash('To-Do 항목을 삭제하려면 로그인해야 합니다.', 'error')
        return redirect(url_for('auth.index'))

    user_id = session['id']

    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            sql_check = "SELECT id FROM todos WHERE id = %s AND user_id = %s"
            cursor.execute(sql_check, (todo_id, user_id))
            if not cursor.fetchone():
                flash('To-Do 항목을 찾을 수 없거나 권한이 없습니다.', 'error')
                return redirect(url_for('todos.todos_list')) # url_for에 블루프린트 이름 명시

            sql = "DELETE FROM todos WHERE id = %s AND user_id = %s"
            cursor.execute(sql, (todo_id, user_id))
        conn.commit()
        flash('To-Do 항목이 성공적으로 삭제되었습니다!', 'success')
    except Exception as e:
        print(f"DEBUG: To-Do 항목 삭제 오류: {e}")
        flash('To-Do 항목 삭제에 실패했습니다. 잠시 후 다시 시도해주세요.', 'error')
    finally:
        if conn:
            conn.close()
    return redirect(url_for('todos.todos_list')) # url_for에 블루프린트 이름 명시

# --- To-Do 기간 연장 (재조정) 라우트 ---

@todos_bp.route('/reschedule/<int:todo_id>') # 실제 경로는 /todos/reschedule/<id>
@todos_bp.route('/reschedule/<int:todo_id>/<int:year>/<int:month>') # 실제 경로는 /todos/reschedule/<id>/<year>/<month>
def reschedule_todo_calendar(todo_id, year=None, month=None):
    """
    특정 To-Do 항목의 마감일을 재조정하기 위한 달력을 표시합니다.
    """
    if 'loggedin' not in session:
        flash('To-Do 항목 마감일을 재조정하려면 로그인해야 합니다.', 'error')
        return redirect(url_for('auth.index'))

    user_id = session['id']
    todo_item = None
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            sql = "SELECT id, task, DATE_FORMAT(due_date, '%%Y-%%m-%%d') AS due_date, status FROM todos WHERE id = %s AND user_id = %s"
            cursor.execute(sql, (todo_id, user_id))
            todo_item = cursor.fetchone()
            if not todo_item:
                flash('To-Do 항목을 찾을 수 없거나 권한이 없습니다.', 'error')
                if conn: conn.close()
                return redirect(url_for('todos.todos_list')) # url_for에 블루프린트 이름 명시
    except Exception as e:
        print(f"DEBUG: Error fetching todo item for reschedule: {e}")
        flash('To-Do 항목 정보를 불러오는 데 실패했습니다.', 'error')
        if conn: conn.close()
        return redirect(url_for('todos.todos_list')) # url_for에 블루프린트 이름 명시
    finally:
        if conn: conn.close()

    today = datetime.now()
    if year is None:
        year = today.year
    if month is None:
        month = today.month

    if not (1 <= month <= 12 and 1900 <= year <= 2100):
        flash('유효하지 않은 연도 또는 월입니다.', 'error')
        return redirect(url_for('todos.reschedule_todo_calendar', todo_id=todo_id)) # url_for에 블루프린트 이름 명시

    prev_month_date = (datetime(year, month, 1) - timedelta(days=1)).replace(day=1)
    next_month_date = (datetime(year, month, 1) + timedelta(days=31)).replace(day=1)

    prev_year, prev_month = prev_month_date.year, prev_month_date.month
    next_year, next_month = next_month_date.year, next_month_date.month

    cal = calendar.Calendar(firstweekday=6) # 일요일부터 시작
    month_days = cal.monthdayscalendar(year, month)

    return render_template('todos_reschedule.html',
                           todo_item=todo_item,
                           year=year,
                           month=month,
                           month_name=datetime(year, month, 1).strftime('%B'),
                           month_days=month_days,
                           prev_year=prev_year,
                           prev_month=prev_month,
                           next_year=next_year,
                           next_month=next_month,
                           current_day=today.day if today.year == year and today.month == month else None,
                           today=today, # today 변수도 템플릿으로 전달
                           username=session['username'])

@todos_bp.route('/set_due_date/<int:todo_id>', methods=['POST']) # 실제 경로는 /todos/set_due_date/<id>
def set_new_due_date(todo_id):
    """선택된 날짜로 To-Do 항목의 마감일을 설정합니다."""
    if 'loggedin' not in session:
        flash('To-Do 항목 마감일을 설정하려면 로그인해야 합니다.', 'error')
        return redirect(url_for('auth.index'))

    user_id = session['id']
    new_due_date_str = request.form.get('new_due_date').strip()

    if not new_due_date_str:
        flash('새로운 마감일을 선택해야 합니다.', 'error')
        return redirect(url_for('todos.todos_list')) # url_for에 블루프린트 이름 명시

    new_due_date = None
    try:
        new_due_date = datetime.strptime(new_due_date_str, '%Y-%m-%d').date()
    except ValueError:
        flash('유효하지 않은 날짜 형식입니다.', 'error')
        return redirect(url_for('todos.todos_list')) # url_for에 블루프린트 이름 명시

    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            sql_check = "SELECT id, status FROM todos WHERE id = %s AND user_id = %s"
            cursor.execute(sql_check, (todo_id, user_id))
            item_data = cursor.fetchone()
            if not item_data:
                flash('To-Do 항목을 찾을 수 없거나 권한이 없습니다.', 'error')
                return redirect(url_for('todos.todos_list')) # url_for에 블루프린트 이름 명시

            new_status_after_reschedule = item_data['status']
            if item_data['status'] == '완료':
                new_status_after_reschedule = '미완료'
            elif item_data['status'] == '기간연장':
                new_status_after_reschedule = '기간연장'
            else:
                new_status_after_reschedule = '진행중'

            sql_update = "UPDATE todos SET due_date = %s, status = %s WHERE id = %s AND user_id = %s"
            cursor.execute(sql_update, (new_due_date, new_status_after_reschedule, todo_id, user_id))
        conn.commit()
        flash(f'할 일의 마감일이 {new_due_date_str}으로 성공적으로 재조정되었습니다!', 'success')
    except Exception as e:
        print(f"DEBUG: To-Do 마감일 설정 오류: {e}")
        flash('마감일 재조정에 실패했습니다. 잠시 후 다시 시도해주세요.', 'error')
    finally:
        if conn:
            conn.close()
    return redirect(url_for('todos.todos_list')) # url_for에 블루프린트 이름 명시

