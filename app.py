from pymongo import MongoClient
client = MongoClient('mongodb+srv://sparta:jungle@cluster0.5ea9dyj.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client.fresh_keeper
   

from flask import Flask, render_template, jsonify, request
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