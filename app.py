from pymongo import MongoClient 
from bson.objectid import ObjectId
client = MongoClient('mongodb+srv://sparta:jungle@cluster0.5ea9dyj.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client.fresh_keeper
from flask import Flask, request, jsonify, render_template
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
import datetime, base64
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

   # 비밀번호가 일치하면 JWT 토큰을 만들어 발급
   payload = {
      'user_id' : id_receive,
      'exp' : datetime.datetime.utcnow() + datetime.timedelta(seconds=5)
   }
   # JWT 암호화
   token = jwt.encode(payload,SECRET_KEY, algorithm='HS256')

   return jsonify({'result' : 'success', 'token' : token })
    
@app.route('/login/nick', methods=['GET'])
def api_valid():
    token_receive = request.cookies.get('mytoken')
    try:
        # token을 시크릿키로 디코딩합니다.
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        print(payload)
        # payload 안에 id가 들어있습니다. 이 id로 유저정보를 찾습니다.
        # 여기에선 그 예로 닉네임을 보내주겠습니다.
        userinfo = db.users.find_one({'user_id': payload['id']}, {'_id': 0,'user_nickname':1})
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

   new_user = {'user_id': user_id_receive, 'user_pw': user_pw_hash, 'user_nickname':user_nickname_receive}
   db.users.insert_one(new_user)
   
   return jsonify({'result': 200})

# 냉장고 페이지
#3 물품 리스트 api--------------------------------------------------------------------
@app.route('/refrigerator', methods=['POST'])
def show_food_list():

   category_receive = request.form['category_give']
   user_id_receive = request.form['user_id_give']
   
   # 물품의 정보 리스트 생성 + 남은 기간 계산
   result = list(db.foods.find({'food_category':category_receive,'user_id':user_id_receive}, {}))
   
   for food in result:
      food['food_remained_date'] = int(food['food_limited_date']) - int(datetime.datetime.today().strftime("%Y%m%d"))
      # 몽고디비가 자동생성해주는 ObjectId는 json으로 직렬화할 수 없어서 문자열로 변환한다.
      # 또한 받은 str을 이용해서 ObjectId를 찾기 위해서는 ObjectId("문자열")이렇게 감싸줘야 한다.
      food['_id'] = str(food['_id'])
      
   if(len(result)==0):
      return jsonify({'result': 400, 'food_list': result})
   else :    
      return render_template('main.html', jsonify({'food_list': result}))
   

#3 추천 리스트 api--------------------------------------------------------------
@app.route('/keywords',methods=['POST'])
def show_keyword_list():

   user_id_receive = request.form['user_id_give']
   print(user_id_receive)
   
   # 개수가 0인 키워드 리스트 생성
   keywords = list(db.keywords.find({'user_id':user_id_receive},{'_id':0,'keyword':1}))
   foods = list(db.foods.find({'user_id':user_id_receive},{'_id':0,'food_name':1}))   
   food_names = set(food['food_name'] for food in foods)
   keywords_not_exist = [keyword for keyword in keywords if keyword['keyword'] not in food_names]

   if(len(keywords_not_exist)==0):
      return jsonify({'result': 400, 'keyword_list': keywords_not_exist})
   else:
      return jsonify({'result': 200, 'keyword_list': keywords_not_exist})
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
   
# 물품 api -------------------------------------------------------------------------
# 3-3 물품 상세 정보 ---------------------------------------------------------------------
@app.route('/foods/detail', methods=['POST'])
def show_food_detail():
   food_id_receive = request.form['food_id_give'] 
   new_food_id = ObjectId(food_id_receive)
   food_detail = db.foods.find_one({'_id': new_food_id}, {"_id":0})
   
   if not food_detail:
      return jsonify({'error': '존재하지 않는 정보 요청'})
   
   food_detail['food_remained_date'] = int(food_detail['food_limited_date']) - int(datetime.datetime.today().strftime("%Y%m%d"))

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