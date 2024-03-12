from pymongo import MongoClient
client = MongoClient('mongodb+srv://sparta:jungle@cluster0.5ea9dyj.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client.fresh_keeper
# JWT 확장 라이브러리 임포트하기
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager
app = Flask(__name__)
# 토큰 생성에 사용될 Secret Key를 flask 환경 변수에 등록
app.config.update(
            DEBUG = True,
            JWT_SECRET_KEY = "Jinyong"
)

#JWT 확장 모듈을 flask 어플리케이션에 등록
jwt = JWTManager(app)

@app.route('/login')
def test_test():
   return "<h1>BAMSONG<h1>"

collection = db.users
userId = collection.find_one()["user_id"]
userPw = collection.find_one()["user_pw"]
print(userId, userPw)


# @app.route('/login1', methods = ['POST'])
# def login_proc():
#    #클라이언트로부터 요청된 값
#    input_data = request.get_json()
#    users_id = input_data['user_id']
#    users_pw = input_data['user_pw']
#    #아이디, 비밀번호가 일치하는 경우
#    if (users_id != userId and
#        users_pw != userPw):
#       return jsonify(
#          result = "success",

#          #검증된 경우, access 토큰 반환
#       )
   

@app.route('/login/memo', methods=['GET'])
def read_users():
    # 1. mongoDB에서 _id 값을 제외한 모든 데이터 조회해오기 (Read)
    result = db.users.find()
    # 2. data라는 키 값으로 article 정보 보내주기
    print('------------')
    print(result)
    return jsonify({'result': 'success', 'data': result})


# doc = {
#     'user_id':'id',
#     'user_pw':"password",
#     'user_nickname':'forrest'
# }

# db.users.insert_one(doc)

from flask import Flask, render_template
app = Flask(__name__)

# 로그인 페이지
@app.route('/')
def login():
   return render_template('login.html')

# 회원가입 페이지
@app.route('/signup')
def signup():
   return render_template('signup.html')

# 냉장고 페이지
@app.route('/refrigerator')
def refrigerator():
   return render_template('main.html') # todo: send userName

   
if __name__ == '__main__':  
   app.run('0.0.0.0',port=5001,debug=True)