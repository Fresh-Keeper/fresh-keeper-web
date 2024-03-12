from pymongo import MongoClient
client = MongoClient('mongodb+srv://sparta:jungle@cluster0.5ea9dyj.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client.fresh_keeper

# doc = {
#     'user_id':'id',
#     'user_pw':"password",
#     'user_nickname':'forrest'
# }

# db.users.insert_one(doc)

from flask import Flask, render_template, jsonify, request
from flask_bcrypt import Bcrypt
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secretKey'
app.config['BCRYPT_LEVEL'] = 10
bcrypt = Bcrypt(app)

# 로그인 페이지
@app.route('/')
def login():
   return render_template('login.html')

# 회원가입 페이지
@app.route('/signup')
def signup():
   return render_template('signup.html')

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