from pymongo import MongoClient
client = MongoClient('mongodb+srv://sparta:jungle@cluster0.5ea9dyj.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client.fresh_keeper
from flask import Flask, request, jsonify, render_template
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
import datetime
import jwt
app = Flask(__name__)

SECRET_KEY = 'this is key' # 토큰 암호화할 key 세팅
app.config['SECRET_KEY'] = 'secretKey'
app.config['BCRYPT_LEVEL'] = 10
bcrypt = Bcrypt(app)

# 로그인 페이지
@app.route('/')
def login():
   return render_template('login.html')
   
# [로그인 API]
@app.route('/login', method=['POST'])
def user_login():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    # PW 암호화
    pw_hash = bcrypt.generate_password_hash(pw_receive)
    # id, 암호화된 PW를가지고 해당 유저 찾기
    result = db.users.find_one({'user_id': id_receive, 'user_pw' : pw_hash })
    # 찾으면 JWT 토큰을 만들어 발급
    if result is not None:
        payload = {
            'user_id' : id_receive,
            'exp' : datetime.datetime.utcnow() + datetime.timedelta(seconds=5)
        }
        # JWT 암호화
        token = jwt.encode(payload,SECRET_KEY, algorithm='HS256')

        return jsonify({'result' : 'success', 'token' : token })
    else :
        return jsonify({'result':'fail', 'msg':'아이디/비밀번호가 일치하지 않습니다.'})
    
@app.route('/login/nick', methods=['GET'])
def api_valid():
    token_receive = request.cookies.get('mytoken')

    try:
        # token을 시크릿키로 디코딩합니다.
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        print(payload)

        # payload 안에 id가 들어있습니다. 이 id로 유저정보를 찾습니다.
        # 여기에선 그 예로 닉네임을 보내주겠습니다.
        userinfo = db.users.find_one({'user_id': payload['id']}, {'_id': 0})
        return jsonify({'result': 'success', 'nickname': userinfo['user_nickname']})
    except jwt.ExpiredSignatureError:
        # 위를 실행했는데 만료시간이 지났으면 에러가 납니다.
        return jsonify({'result': 'fail', 'msg': '로그인 시간이 만료되었습니다.'})
    except jwt.exceptions.DecodeError:
        return jsonify({'result': 'fail', 'msg': '로그인 정보가 존재하지 않습니다.'})

# 회원가입 페이지
@app.route('/signup')
def signup():
   return render_template('signup.html')

# 회원가입 API
@app.route('/signup', methods=['POST'])
def upload_user():
   user_id_receive = request.form['user_id_give']
   user_pw_receive = request.form['user_pw_give']
   user_nickname_receive = request.form['user_nickname_give']
   is_dup_id = list(db.users.find({'user_id': user_id_receive}))
   if is_dup_id:
      return jsonify({'error': 409})
   
   user_pw_hash = bcrypt.generate_password_hash(user_pw_receive)
   new_user = {'user_id': user_id_receive, 'user_pw': str(user_pw_hash), 'user_nickname':user_nickname_receive}
   db.users.insert_one(new_user)
   return jsonify({'result': 200})

# 냉장고 페이지
@app.route('/refrigerator')
def refrigerator():
   return render_template('main.html') # todo: send userName

# 3-2 키워드 관리
# 키워드 추가
@app.route('/keywords/add', methods=['POST'])
def add_keyword():
   keyword_receive = request.form['keyword_give']
   user_id_receive = request.form['user_id_give']
   is_dup_keyword = list(db.keywords.find({'keyword': keyword_receive, 'user_id': user_id_receive}))
   if is_dup_keyword:
      return jsonify({'error': '이미 존재하는 키워드 요청'})
   new_keyword = {'keyword': keyword_receive, 'user_id': user_id_receive}
   db.keywords.insert_one(new_keyword)
   return jsonify({'result': 200})

# 키워드 삭제
@app.route('/keywords/delete', methods=['POST'])
def delete_keyword():
   keyword_receive = request.form['keyword_give']
   user_id_receive = request.form['user_id_give']
   db.keywords.delete_one({'keyword': keyword_receive, 'user_id': user_id_receive})
   return jsonify({'result': 200})
   
if __name__ == '__main__':  
   app.run('0.0.0.0',port=5001,debug=True)
