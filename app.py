from pymongo import MongoClient
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
def showFoodList():
   category_receive = request.form['category_give']
   user_id_receive = request.form['user_id_give']
   
   result = list(db.foods.find({'food_category':category_receive,'user_id':user_id_receive},
                               {"food_id":1,"food_name":1,"food_purchase_date":1,"food_limited_date":1}))
   for food in result:
      food['food_remained_date']=food['food_purchase_date']-food['food_limited_date']

   if(len(result)==0):
      return jsonify({'result': 400, 'food_list': result})
   else :    
      return jsonify({'result': 200, 'food_list': result})

#3 추천 리스트 보여주는 api--------------------------------------------------------------
@app.route('/keywords',methods=['POST'])
def showKeywordList():
   user_id_receive = request.form['user_id_give']
   
   # 개수가 0인 키워드 리스트 생성
   # '_id':0,'user_id':1
   keywords = list(db.foods.find({'user_id':user_id_receive},{'_id':0,'user_id':1}))
   foods = list(db.keywords.find({'user_id':user_id_receive},{'_id':0,'user_id':1}))
   keywords_not_exist = list(set(keywords) - set(foods))

   if(len(keywords_not_exist)==0):
      return jsonify({'result': 400, 'keyword_list': keywords_not_exist})
   else:
      return jsonify({'result': 200, 'keyword_list': keywords_not_exist})
#------------------------------------------------------------------------------------

if __name__ == '__main__':  
   app.run('0.0.0.0',port=5001,debug=True)