from pymongo import MongoClient
client = MongoClient('mongodb+srv://sparta:jungle@cluster0.5ea9dyj.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client.fresh_keeper


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