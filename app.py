from datetime import date
import urllib3
import os
from flask import *
app = Flask(__name__)
import sqlite3,json
from stationlist import *
from tempjson import *
import re
ROOT_FOLDER= os.path.dirname(os.path.abspath(__file__))
today = date.today()
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
               flash('Please fill both fields to login')
            else:
               conn = None
               try:
                  railway = os.path.join(ROOT_FOLDER,'railwaydb.db')
                  conn = sqlite3.connect(railway)
                  # cursor=conn.execute("SHOW TABLES")
                  # for row in cursor:
                  # print(row)
                  dbURL = "SELECT username,password,fname,lname,email,mobile FROM user where username=?"
                  print(dbURL)
                  cursor = conn.cursor()
                  cursor.execute(dbURL,(username,))
                  rows=cursor.fetchall()
                  clen=int(len(rows))
                  print(clen)
                  if clen==0:
                     flash('Account does not exist')
                  else:
                     for row in rows:
                        if row[0]==username and row[1]==password:
                           print("Login Successful")
                           fullname=row[2]+' '+row[3]
                           session['fullname']=fullname
                           session['username']=username
                           session['mobile']=row[5]
                           session['email']=row[4]
                           # session['mobile']=mobile
                           return redirect(url_for('home'))
                        else:
                           flash('Wrong passwords')
                  
               except Exception as e:
                  flash('Some unexpected error occured, so please try again')
               finally:
                  if conn:
                     conn.close()   
         except Exception as e:
            flash('Some unexpected error occured, so please try again')
            print(e)
      return render_template('login.html')
      # Render the sign-up page
      

def isValidNumber(number):
    Pattern = re.compile("(0/91)?[5-9][0-9]{9}")
    return Pattern.match(number)

def validPassword(password):
   flag = 0
   while True:
       if (len(password) < 8):
           flag = -1
           break
       elif not re.search("[a-z]", password):
           flag = -1
           break
       elif not re.search("[A-Z]", password):
           flag = -1
           break
       elif not re.search("[0-9]", password):
           flag = -1
           break
       elif not re.search("[_@$]", password):
           flag = -1
           break
       elif re.search("\s", password):
           flag = -1
           break
       else:
           flag = 0
           return 'valid'

   if flag == -1:
       return 'invalid'


@app.route('/signup',methods=['GET','POST'])
def signup():
   if request.method=='POST':
      fname=request.form['fname']
      lname=request.form['lname']
      username=request.form['username']
      password=request.form['password']
      email=request.form['email']
      mobile=request.form['mobile']
      regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
      if fname == '' or lname == '' or username == '' or password == '' or email == '' or mobile == '':
         flash('All fields are mandatory')
      elif validPassword(password)=='invalid':
         flash('Weak Password')
      elif not re.search(regex,email):
         flash('Enter Valid email')
      elif not isValidNumber(mobile):
         flash('Invalid Mobile Number')
      else:
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
            flash('Duplicate username')
         finally:
            if conn:
               conn.close()
   return render_template('signup.html')

@app.route('/home',methods=["GET","POST"])
def home():
   listbm = []
   if request.method=='POST' and 'username' in session:
      conn = None
      try:
         railway = os.path.join(ROOT_FOLDER, 'railwaydb.db')
         conn = sqlite3.connect(railway)
         dbURL = "SELECT trainnumber,station FROM trainbookmark where username=?"
         print(dbURL)
         cursor = conn.cursor()
         cursor.execute(dbURL, (session['username'],))
         for row in cursor:
            listbm.append(row)
      except Exception as e:
         print(e)
      return render_template('home.html', listbm=listbm)
   else:
      return render_template('home.html')

@app.route('/livetrain/<string:trainno>/<string:station>')
def livetrainspc(trainno,station):
   return redirect(url_for('livetrain',trainno=trainno,station=station))


@app.route('/livetrain',methods=["GET","POST"])
def livetrain():
   try:
      station=request.args.get('station')
      trainno=request.args.get('trainno')
      d1 = today.strftime("%d-%m-%Y")
      print(d1)
      queryURL = 'https://api.railwayapi.com/v2/live/train/'+trainno+'/station/'+station+'/date/'+d1+'/apikey/'+apikey+'/'
      # print(queryURL)
      # http = urllib3.PoolManager()
      # r = http.request('GET', queryURL)
      # data = json.loads(livetraindata)
      data = json.loads(livetraindata)
      return render_template('livetrain.html', list=sorted(listrail),trainstatus=data)
   except:
      if request.method == "POST":
         stationcode = request.form['station'].split('-')[0]
         trainno=request.form['trainno']
         if trainno == '' or stationcode == 'EMPTY' or not len(trainno)==5:
            flash('Enter valid details')
         else:
            d1 = today.strftime("%d-%m-%Y")
            print(d1)
            queryURL = 'https://api.railwayapi.com/v2/live/train/'+trainno+'/station/'+stationcode+'/date/'+d1+'/apikey/'+apikey+'/'
            # print(queryURL)
            # http = urllib3.PoolManager()
            # r = http.request('GET', queryURL)
            # data = json.loads(livetraindata)
            data = json.loads(livetraindata)
            return render_template('livetrain.html', list=sorted(listrail), trainstatus=data)
   return render_template('livetrain.html', list=sorted(listrail))


@app.route('/livestation',methods=["GET","POST"])
def livestation():
   # print(listrail)
   selected=''
   trainlist = []
   if request.method=="POST":
      stationcode=request.form['station'].split('-')[0]
      if not stationcode=='EMPTY':
         # print(stationcode)
         queryURL = 'https://api.railwayapi.com/v2/arrivals/station/'+stationcode+'/hours/8/apikey/'+apikey+'/'
         # print(queryURL)
         # http = urllib3.PoolManager()
         # r = http.request('GET', queryURL)
         # data=json.loads(livestationdata);

         # print(type(data['trains']))
         data = json.loads(livestationdata);
         if(data['response_code']==200):
            trainlist=data['trains']
            # print(trainlist)

         selected=request.form['station']
      else:

         flash('Choose a station to continue')
   return render_template('livestation.html',list=sorted(listrail),selected=selected,trainlist=trainlist)


@app.route('/trainroute',methods=["GET", "POST"])
def trainroute():
   trainno = ''
   trainlist = []
   if request.method == "POST":
      trainno = request.form['trainno']
      if trainno=='' or not len(trainno)==5:
         flash('Enter valid train no')
      else:
      # print(stationcode)
         queryURL = 'https://api.railwayapi.com/v2/route/train/'+trainno+'/apikey/'+apikey+'/'
         print(queryURL)
         # http = urllib3.PoolManager()
         # r = http.request('GET', queryURL)
         # data = json.loads(trainroutejson)

         # print(type(data['trains']))
         data = json.loads(trainroutejson)
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
