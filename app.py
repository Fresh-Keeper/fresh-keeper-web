from pymongo import MongoClient 
from bson.objectid import ObjectId
client = MongoClient('mongodb+srv://sparta:jungle@cluster0.5ea9dyj.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client.fresh_keeper
   

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
   id_dup_check = list(db.users.find({'user_id': user_id_receive}))
   if id_dup_check:
      return jsonify({'error': 409})
   
   user_pw_hash = bcrypt.generate_password_hash(user_pw_receive)
   new_user = {'user_id': user_id_receive, 'user_pw': str(user_pw_hash), 'user_nickname':user_nickname_receive}
   db.users.insert_one(new_user)
   return jsonify({'result': 200})

# 냉장고 페이지
@app.route('/refrigerator')
def refrigerator():
   return render_template('main.html') # todo: send userName

#3 물품 보여주는 api--------------------------------------------------------------------
@app.route('/foods',methods=['POST'])
def show_food_list():

   category_receive = request.form['category_give']
   user_id_receive = request.form['user_id_give']
   
   # 물품의 정보 리스트 생성 + 남은 기간 계산
   result = list(db.foods.find({'food_category':category_receive,'user_id':user_id_receive},
                               {}))
   
   for food in result:
      food['food_remained_date']=int(food['food_purchase_date'])-int(food['food_limited_date'])
      # 몽고디비가 자동생성해주는 ObjectId는 json으로 직렬화할 수 없어서 문자열로 변환한다.
      # 또한 받은 str을 이용해서 ObjectId를 찾기 위해서는 ObjectId("문자열")이렇게 감싸줘야 한다.
      food['_id'] = str(food['_id'])
      
      
   if(len(result)==0):
      return jsonify({'result': 400, 'food_list': result})
   else :    
      return jsonify({'result': 200, 'food_list': result})

#3 추천 리스트 보여주는 api--------------------------------------------------------------
@app.route('/keywords',methods=['POST'])
def show_keyword_list():

   user_id_receive = request.form['user_id_give']
   print(user_id_receive)
   # 개수가 0인 키워드 리스트 생성
   #todo : type error
   keywords = list(db.keywords.find({'user_id':user_id_receive},{'_id':0,'keyword':1}))
   foods = list(db.foods.find({'user_id':user_id_receive},{'_id':0,'food_name':1}))
   print("-----------------")
   print(keywords)
   foods = set(foods)
   print(foods)
   print("-----------------")
   keywords_not_exist = list(set(keywords) - set(foods))

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




if __name__ == '__main__':  
   app.run('0.0.0.0',port=5001,debug=True)