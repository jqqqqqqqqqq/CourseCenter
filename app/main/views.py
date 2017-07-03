from flask import render_template, redirect, url_for, flash, request, session, Response
from . import main
from .. import db
import os
from ..models.models import Course, ChatMessage, Teacher, Student
from flask_login import current_user, login_required
from flask import request
from config import basedir
from flask_uploads import UploadNotAllowed
import uuid
import redis
import datetime

@main.before_request
@login_required
def before_request():
    pass


@main.route('/', methods=['GET', 'POST'])
def index():

    #教师特色主页
    if current_user.user_type() == 1:
        courses = Teacher.query.filter_by(id=current_user.id).first().courses
        return render_template('teacher/index.html', courses=courses)

    # 学生特色主页
    if current_user.user_type() == 2:
        courses = Student.query.filter_by(id=current_user.id).first().courses
        return render_template('student/index.html', courses=courses)

    return render_template('index.html')


red = redis.StrictRedis()

def event_stream():
    pubsub = red.pubsub()
    pubsub.subscribe('chat')
    # TODO: handle client disconnection.
    for message in pubsub.listen():
        print(message)
        if not type(message['data']) == int:
            message['data'] = message['data'].decode('utf-8')
        yield 'data: %s\n\n' % message['data']


@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['user'] = request.form['user']
        return redirect(url_for('index'))
    return '<form action="" method="post">user: <input name="user">'


@main.route('/post', methods=['GET', 'POST'])
def post():
    message = request.form['message']
    user = str(current_user.id)
    # now = datetime.datetime.now().replace(microsecond=0).time()
    time = str(datetime.datetime.now()).split('.')[0]

    # 写入数据库
    cm = ChatMessage()
    cm.course_id = request.form['course-id']
    # 当前用户是老师
    if current_user.user_type() == 1:
        cm.student_id = 0
        cm.teacher_id = current_user.id
    # 当前用户是学生
    else:
        cm.student_id = current_user.id
        cm.teacher_id = 0
    cm.time = datetime.datetime.now()
    cm.content = message

    db.session.add(cm)
    db.session.commit()

    red.publish('chat', u'[%s] %s: %s' % (time, user, message))
    return Response(status=204)


@main.route('/stream')
def stream():
    return Response(event_stream(),
                          mimetype="text/event-stream")


@main.route('/<course_id>/chat', methods=['GET', 'POST'])
def chat(course_id):
    cm_list = ChatMessage.query.filter_by(course_id=course_id).order_by(ChatMessage.id.desc()).all()[:10]
    return render_template('chat.html', course_id=course_id, cm_list=cm_list)

    # 下面的代码只是作为具体的template/chat.html的一个参考
    # 注：/post想要获得message和course_id两个参数
    '''
    return """
        <!doctype html>
        <title>chat</title>
        <script src="https://cdn.bootcss.com/jquery/3.2.1/jquery.min.js"></script>
        <style>body { max-width: 500px; margin: auto; padding: 1em; background: white; color: #000; font: 16px/1.6 menlo, monospace; }</style>
        <p><b>Hello!</b></p>
        <p>Message: <input id="in" /></p>
        <pre id="out"></pre>
        <script>
            function sse() {
                var source = new EventSource('/stream');
                var out = document.getElementById('out');
                source.onmessage = function(e) {
                    // XSS in chat is fun
                    out.innerHTML =  e.data + '\\n' + out.innerHTML;
                };
            }
            $('#in').keyup(function(e){
                if (e.keyCode == 13) {
                    $.post('/post', {'message': $(this).val()});
                    $(this).val('');
                }
            });
            sse();
        </script>

    """
    '''


