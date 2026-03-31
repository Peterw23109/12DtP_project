from flask import Flask, g, render_template, request, flash, session, redirect
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

DATABASE = 'element.db'
RANDOM_SYMBOL = None
app = Flask(__name__)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
        
def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

@app.route('/signup', methods=["GET","POST"])
def signup():
    #if the user posts from the signup page
    if request.method == "POST":
        #add the new username and hashed password to the database
        username = request.form['username']
        password = request.form['password']
        #hash it with the cool secutiry function
        hashed_password = generate_password_hash(password)
        #write it as a new user to the database
        sql = "INSERT INTO user (username,password) VALUES (?,?)"
        query_db(sql,(username,hashed_password))
        #message flashes exist in the base.html template and give user feedback
        flash("Sign Up Successful")
    return render_template('signup.html')

@app.route('/')
def index():
    return render_template('home.html')


@app.route('/quiz', methods=["GET", "POST"])
def quiz():
    result = []
    

    global RANDOM_SYMBOL
    if request.method == "POST":
        Element_ID = request.form.get("element")
        sql = "SELECT * FROM Element WHERE Element_ID = ? COLLATE NOCASE"
        row = query_db(sql, (Element_ID,), True)
        if row:
            result = [row]
    else:
        sql = "SELECT * FROM Element"
        result = query_db(sql)

    if RANDOM_SYMBOL is None:
        random_element = query_db("SELECT Element_ID FROM Element ORDER BY RANDOM() LIMIT 1", one=True)
        RANDOM_SYMBOL = random_element['Element_ID']

    if request.method == "POST":
        Element_ID = request.form.get("element")

    
        if Element_ID and Element_ID.lower() == RANDOM_SYMBOL.lower():
            random_element = query_db("SELECT Element_ID FROM Element ORDER BY RANDOM() LIMIT 1", one=True)
            RANDOM_SYMBOL = random_element['Element_ID']

            return render_template("element.html", random_symbol=Element_ID)


        sql = "SELECT * FROM Element WHERE Element_ID = ? COLLATE NOCASE"
        row = query_db(sql, (Element_ID,), True)
        if row:
            result = [row]

    else:
        result = []


    return render_template("element.html", result=result, random_symbol=RANDOM_SYMBOL)

@app.route('/login', methods=["GET","POST"])
def login():
    #if the user posts a username and password
    if request.method == "POST":
        #get the username and password
        username = request.form['username']
        password = request.form['password']
        #try to find this user in the database- note- just keepin' it simple so usernames must be unique
        sql = "SELECT * FROM user WHERE username = ?"
        user = query_db(sql=sql,args=(username,),one=True)
        if user:
            #we got a user!!
            #check password matches-
            if check_password_hash(user[2],password):
                #we are logged in successfully
                #Store the username in the session
                session['user'] = user
                flash("Logged in successfully")
            else:
                flash("Password incorrect")
        else:
            flash("Username does not exist")
    #render this template regardles of get/post
    return render_template('login.html')



@app.route('/logout')
def logout():
    #just clear the username from the session and redirect back to the home page
    session['user'] = None
    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)


