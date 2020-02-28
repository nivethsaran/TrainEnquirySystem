from flask import *
app = Flask(__name__)
import sqlite3

app.config['SECRET_KEY'] = 'RailwayManagement'
@app.route('/')
def startup():
   return render_template('startup.html')


@app.route('/login', methods=('GET', 'POST'))
def contact():
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
               # Form data is valid; move along
               print(username,password)
               session['username']=username
               return redirect(url_for('another'))
         except:
            pass

      # Render the sign-up page
      return render_template('login.html', message=error)


@app.route('/signup',methods=['GET','POST'])
def signup():
   return render_template('signup.html')

@app.route('/home')
def another():
   if 'username' in session:
      return session['username']
   else:
      return 'yaar nee'

if __name__=='__main__':
    app.run()