from pymongo import MongoClient
client = MongoClient('mongodb+srv://sparta:jungle@cluster0.5ea9dyj.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client.fresh_keeper

# doc = {
#     'user_id':'id',
#     'user_pw':"password",
#     'user_nickname':'forrest'
# }

# db.users.insert_one(doc)

from flask import Flask
app = Flask(__name__)

# 로그인 페이지
@app.route('/login')
def login():
   return 'This is LogIn!'

# 회원가입 페이지
@app.route('/signup')
def signup():
   return 'This is SignUP!'

# 냉장고 페이지
@app.route('/refrigerator')
def refrigerator():
   return 'This is Refrigerator!'

   
if __name__ == '__main__':  
   app.run('0.0.0.0',port=5001,debug=True)