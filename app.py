from pymongo import MongoClient
client = MongoClient('mongodb+srv://sparta:jungle@cluster0.5ea9dyj.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client.fresh_keeper
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
import datetime
import jwt
app = Flask(__name__)


SECRET_KEY = 'this is key' # 토큰 암호화할 key 세팅
app.config['SECRET_KEY'] = 'secretKey'
app.config['BCRYPT_LEVEL'] = 10
bcrypt = Bcrypt(app)
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


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
    



