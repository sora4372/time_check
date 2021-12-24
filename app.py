from pymongo import MongoClient
import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

app = Flask(__name__)

SECRET_KEY = 'Timecheck'
client = MongoClient('localhost', 27017)
db = client.sora_prac02


@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

        myname = db.sign_users.find_one({'username': payload['id']})['name']
        department = db.sign_users.find_one({'username': payload['id']})['department']

        return render_template('main.html', name=myname, department=department)

    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login"))


@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)


@app.route('/sign_in', methods=['POST'])
def sign_in():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.sign_users.find_one({'username': username_receive, 'password': pw_hash})

    if result is not None:

        payload = {
            'id': username_receive,
            # 지금부터 timedelta로 60초*60초*24
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        # payload에 token을 만들어서 secret key로 암호화를 해준다음에,
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')

        # client에게 던져줌
        return jsonify({'result': 'success', 'token': token})

    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    name_receive = request.form['name_give']
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    department_receive = request.form['department_give']

    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest();

    doc = {
        "name": name_receive,
        "username": username_receive,
        "password": password_hash,
        "department": department_receive
    }

    db.sign_users.insert_one(doc)
    return jsonify({'result': 'success'})


@app.route('/sign_up/checkup', methods=['POST'])
def check_up():
    username_receive = request.form['username_give']
    # username 으로 찾아서 있으면 가져오고 찾아서 없으면 bool이면 false가 됨(가져오지 않음)
    exists = bool(db.sign_users.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})


@app.route('/checking', methods=['POST'])
def check():
    name_receive = request.form['name_give']
    department_receive = request.form['department_give']

    today = datetime.now()
    now = today.strftime('%H:%M:%S')
    fixed_date = today.strftime('08:30:00')

    if(now > fixed_date) :
        doc = {
            'name': name_receive,
            'department': department_receive,
            'date': today.strftime('%H:%M:%S'),
            'check': '遅刻'
        }
        db.checking.insert_one(doc)

    else :
        doc = {
            'name': name_receive,
            'department': department_receive,
            'date': today.strftime('%H:%M:%S'),
            'check': 'SAFE'
        }

        db.checking.insert_one(doc)
    return jsonify({'result': 'success', 'msg': '추가 완료'})


@app.route('/listing', methods=['GET'])
def listing():
    check_list = list(db.checking.find({}, {'_id': False}))
    print(check_list)

    return jsonify({'result': 'success', 'listing': check_list})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
