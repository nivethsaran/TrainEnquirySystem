import os
from flask import *
app = Flask(__name__)
import sqlite3
ROOT_FOLDER= os.path.dirname(os.path.abspath(__file__))

app.config['SECRET_KEY'] = 'RailwayManagement'
@app.route('/')
def startup():
   return render_template('startup.html')


@app.route('/login', methods=('GET', 'POST'))
def login():
      error=''
      if request.method == 'POST':
         # Form being submitted; grab data from form.
         try:

            username = request.form['username']
            password = request.form['password']
            # Validate form data
            if len(username) == 0 or len(password) == 0:
               # Form data failed validation; try again
               error = "Please supply both first and last name"
            else:
               conn = None
               try:
                  railway = os.path.join(ROOT_FOLDER, 'railwaydb.db')
                  conn = sqlite3.connect(railway)
                  # cursor=conn.execute("SHOW TABLES")
                  # for row in cursor:
                  # print(row)
                  dbURL = "SELECT username,password,fname,lname,email,mobile FROM user where username=?"
                  print(dbURL)
                  cursor = conn.cursor()
                  cursor.execute(dbURL,(username,))
                  for row in cursor:
                     if row[0]==username and row[1]==password:
                        print("Login Successful")
                        fullname=row[2]+' '+row[3]
                        session['fullname']=fullname
                        session['username']=username
                        # session['mobile']=mobile
                        return redirect(url_for('home'))
                  return redirect(url_for('login'))
               except Exception as e:
                  print(e)
               finally:
                  if conn:
                     conn.close()
               

            
         except:
            pass

      # Render the sign-up page
      return render_template('login.html', message=error)


@app.route('/signup',methods=['GET','POST'])
def signup():
   if request.method=='POST':
      fname=request.form['fname']
      lname=request.form['lname']
      username=request.form['username']
      password=request.form['password']
      email=request.form['email']
      mobile=request.form['mobile']
      print([fname,lname,username,password,email,mobile])

      conn = None
      try:
         railway = os.path.join(ROOT_FOLDER, 'railwaydb.db')
         conn = sqlite3.connect(railway)
         # cursor=conn.execute("SHOW TABLES")
         # for row in cursor:
            # print(row)
         dbURL = "INSERT INTO user values(?,?,?,?,?,?)"
         print(dbURL)
         cursor = conn.cursor()
         cursor.execute(dbURL,(fname,lname,username,password,email,mobile))
         print(cursor)
         conn.commit()
         return redirect(url_for('login'))
      except Exception as e:
         print(e)
      finally:
         if conn:
            conn.close()
   return render_template('signup.html')

@app.route('/home')
def home():
   if 'username' in session:
      return session['username']+' '+session['fullname']
   else:
      return 'yaar nee'

if __name__=='__main__':
    app.run()
