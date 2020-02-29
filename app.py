import urllib3
import os
from flask import *
app = Flask(__name__)
import sqlite3,json
from stationlist import *
from tempjson import *
ROOT_FOLDER= os.path.dirname(os.path.abspath(__file__))

app.config['SECRET_KEY'] = 'RailwayManagement'
@app.route('/')
def startup():
   message=''
   if 'username' in session:
      message='Working'
   return render_template('startup.html',message=message)


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
                        session['mobile']=row[5]
                        session['email']=row[4]
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
      return render_template('home.html',message=session['username']+' '+session['fullname'])
   else:
      return render_template('home.html', message='yaar nee')


@app.route('/livetrain')
def livetrain():
   return render_template('livetrain.html')


@app.route('/livestation',methods=["GET","POST"])
def livestation():
   # print(listrail)
   selected=''
   trainlist = []
   if request.method=="POST":
      stationcode=request.form['station'].split('-')[0]
      # print(stationcode)
      queryURL = 'https://api.railwayapi.com/v2/arrivals/station/'+stationcode+'/hours/8/apikey/'+apikey+'/'
      # print(queryURL)
      # http = urllib3.PoolManager()
      # r = http.request('GET', queryURL)
      data=json.loads(livestationdata);
      # print(type(data['trains']))
      
      if(data['response_code']==200):
         trainlist=data['trains']
         # print(trainlist)
      
      selected=request.form['station']
   return render_template('livestation.html',list=sorted(listrail),selected=selected,trainlist=trainlist)


@app.route('/trainroute',methods=["GET", "POST"])
def trainroute():
   trainno = ''
   trainlist = []
   if request.method == "POST":
      trainno = request.form['trainno']
      # print(stationcode)
      queryURL = 'https://api.railwayapi.com/v2/route/train/'+trainno+'/apikey/'+apikey+'/'
      print(queryURL)
      # http = urllib3.PoolManager()
      # r = http.request('GET', queryURL)
      data = json.loads(trainroutejson)
      # print(type(data['trains']))

      if(data['response_code'] == 200):
         trainlist = data['route']
         print(trainlist)
   # return render_template('livestation.html', list=sorted(listrail), selected=selected, trainlist=trainlist)
   return render_template('trainroute.html',trainlist=trainlist)


@app.route('/about')
def about():
   return render_template('about.html')


@app.route('/logout')
def logout():
   session.pop('username',None)
   session.pop('fullname',None)
   session.pop('mobile',None)
   session.pop('email',None)
   return render_template('login.html')



@app.route('/addtobookmarks/<string:trainno>/<string:stationcode>')
def addtobookmarks(trainno,stationcode):
   print(trainno,stationcode)
   username=session['username']
   conn = None
   try:
       railway = os.path.join(ROOT_FOLDER, 'railwaydb.db')
       conn = sqlite3.connect(railway)
       # cursor=conn.execute("SHOW TABLES")
       # for row in cursor:
         # print(row)
       dbURL = "INSERT INTO trainbookmark values(?,?,?)"
       print(dbURL)
       cursor = conn.cursor()
       cursor.execute(
           dbURL, (username, trainno, stationcode))
       print(cursor)
       conn.commit()
       return redirect(url_for('livestation'))
   except Exception as e:
      print(e)
   finally:
      if conn:
         conn.close()
   return redirect(url_for('livestation'))

if __name__=='__main__':
    app.run()
