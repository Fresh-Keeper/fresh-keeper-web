from pymongo import MongoClient 
from bson.objectid import ObjectId
client = MongoClient('mongodb+srv://sparta:jungle@cluster0.5ea9dyj.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client.fresh_keeper

from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity


from flask import Flask, request, jsonify, render_template,redirect
from flask_bcrypt import Bcrypt

import datetime, base64
from datetime import timedelta

import jwt

app = Flask(__name__)

CORS(app)
CORS(app,resource={r'*':{'origins':'*'}})

SECRET_KEY = 'this is key' # 토큰 암호화할 key 세팅
app.config['SECRET_KEY'] = 'secretKey'
app.config['BCRYPT_LEVEL'] = 10
bcrypt = Bcrypt(app)

app.config["JWT_COOKIE_SECURE"] = False
app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this!
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24)
app.config['JWT_TOKEN_LOCATION'] = ['cookies','headers','query_string']
app.config['JWT_ACCESS_COOKIE_NAME'] = "userToken"

jwt = JWTManager(app)
jwt = JWTManager(app)

# 토큰이 만료된 경우
@jwt.expired_token_loader
def my_expired_token_callback(expired_token):
    # 만료된 토큰을 재발급하기 위한 URL로 리디렉션
    return jsonify({'message': 'Token has expired', 'redirect_url': '/'})

# 토큰 없거나 인증 불가능 한 경우 
@jwt.unauthorized_loader
def custom_unauthorized_response(_err):
    return redirect("/")

# 로그인 페이지
@app.route('/')
def home():
   return render_template('login.html')

@app.route('/signup')
def signup():
   return render_template('signup.html')
   
# [로그인 API]
@app.route('/login', methods=['POST'])
def user_login():
   id_receive = request.form['id_give']
   pw_receive = request.form['pw_give']

   find_user = db.users.find_one({'user_id': id_receive})
   if not find_user:
      return jsonify({'error': 404})

   user_db_pw = find_user['user_pw']
   decoded_user_db_pw = user_db_pw.decode("utf-8")
   is_same = bcrypt.check_password_hash(decoded_user_db_pw, pw_receive)
   if not is_same:
      return jsonify({'error': 401})

   
   access_token = create_access_token(identity=find_user['user_id'])
   return jsonify({'result' : 200, 'nickname': find_user["user_nickname"], 'token' : access_token })


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

   new_user = {'user_id': user_id_receive, 'user_pw': user_pw_hash, 'user_nickname':user_nickname_receive}
   db.users.insert_one(new_user)
   
   return jsonify({'result': 200})

# 냉장고 페이지
#3 물품 리스트 api--------------------------------------------------------------------
@app.route('/refrigerator/<user_id>', methods=['GET'])
@jwt_required()
def show_food_list(user_id):

   decode_id = base64.b64decode(user_id).decode('ascii')

   # 물품의 정보 리스트 생성 + 남은 기간 계산
   result = list(db.foods.find({'user_id': decode_id}, {}).sort("food_limited_date",-1))
   nickname = db.users.find_one({'user_id': decode_id})['user_nickname']
   cold_list, freeze_list = list(), list()
   for food in result:
      food['food_remained_date'] = int(food['food_limited_date'].replace("-", "")) - int(datetime.datetime.today().strftime("%Y%m%d"))
      # 몽고디비가 자동생성해주는 ObjectId는 json으로 직렬화할 수 없어서 문자열로 변환한다.
      # 또한 받은 str을 이용해서 ObjectId를 찾기 위해서는 ObjectId("문자열")이렇게 감싸줘야 한다.
      food['_id'] = str(food['_id'])
      cold_list.append(food) if food['food_category'] == "냉장" else freeze_list.append(food)
   return render_template('main.html', userName=nickname, cold_food_list=cold_list, frozed_food_list=freeze_list)

#3 추천 리스트 api--------------------------------------------------------------
@app.route('/keywords',methods=['POST'])
def show_keyword_list():

   user_id_receive = request.form['user_id_give']
   
   # 개수가 0인 키워드 리스트 생성
   keywords = list(db.keywords.find({'user_id':user_id_receive},{'_id':0,'keyword':1}))
   keyword_names = set(keyword['keyword'] for keyword in keywords)
   foods = list(db.foods.find({'user_id':user_id_receive},{'_id':0,'food_name':1}))   
   food_names = set(food['food_name'] for food in foods)
   # keywords_not_exist = [keyword for keyword in keywords if keyword['keyword'] not in food_names]
   keywords_not_exist = keyword_names - food_names
   return jsonify({'result': 200, 'keyword_list': list(keywords_not_exist)})
   # if(len(keywords_not_exist)==0):
   #    return jsonify({'result': 400, 'keyword_list': keywords_not_exist})
   # else:
   #    return jsonify({'result': 200, 'keyword_list': keywords_not_exist})

#3-1 물품 추가 api ---------------------------------------------------------------------
@app.route('/foods/add',methods=['POST'])
def add_food():
   food_name_receive = request.form['food_name_give']
   food_purchase_date_receive = request.form['food_purchase_date_give']
   food_limited_date_receive = request.form['food_limited_date_give']
   food_amount_receive = request.form['food_amount_give']
   user_id_receive = request.form['user_id_give']
   food_category_receive= request.form['food_category_give']

   food={'food_name':food_name_receive,
         'food_purchase_date':food_purchase_date_receive,
         'food_limited_date':food_limited_date_receive,
         'food_amount':food_amount_receive,
         'food_category':food_category_receive,
         'user_id':user_id_receive
         }
   db.foods.insert_one(food)
   return jsonify({'result': 'success'})
# 3-2 키워드 관리 ---------------------------------------------------------------------
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

# 키워드 표시
@app.route('/keywords/show',methods=['POST'])
def show_keyword():
   user_id_receive = request.form['user_id_give']
   result = list(db.keywords.find({"user_id":user_id_receive},{"_id":0}))
   return jsonify({'result':'success','show_keys':result})

# 물품 api -------------------------------------------------------------------------
# 3-3 물품 상세 정보 ---------------------------------------------------------------------
@app.route('/foods/detail', methods=['POST'])
def show_food_detail():
   food_id_receive = request.form['food_id_give'] 
   new_food_id = ObjectId(food_id_receive)
   food_detail = db.foods.find_one({'_id': new_food_id}, {"_id":0})
   
   if not food_detail:
      return jsonify({'error': '존재하지 않는 정보 요청'})
   
   food_detail['food_remained_date'] = int(food_detail['food_limited_date'].replace("-","")) - int(datetime.datetime.today().strftime("%Y%m%d"))

   return jsonify({'result': 200, 'food_detail': food_detail})

#4 물품 수량 증감 -> 클라이언트에서 기존 수량 증감해서 update_amount_give로 보냄 -> 서버에서는 해당 amount를 db에 update하기만 하도록 함.
@app.route('/foods/detail/amount', methods=['PUT'])
def update_food_amount():
   food_id_receive = request.form['food_id_give']
   update_amount_receive = request.form['update_amount_give']

   db.foods.update_one({'_id': ObjectId(food_id_receive)}, {'$set': {'food_amount': update_amount_receive}})
   return jsonify({'result': 200})
   

#5 물품 삭제 api 
@app.route('/foods/delete', methods=['POST'])
def remove_food():
   food_id_receive = request.form['food_id_give']

   db.foods.delete_one({'_id': ObjectId(food_id_receive)})
   return jsonify({'result': 200})
   

if __name__ == '__main__':  
   app.run('0.0.0.0',port=5001,debug=True)