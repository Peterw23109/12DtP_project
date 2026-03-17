from flask import Flask, g, render_template, request
import sqlite3

DATABASE = 'element.db'

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

@app.route('/')
def home():
    sql = "SELECT * FROM Element"
    result = query_db(sql)
    return render_template("home.html", result=result)

@app.route('/', methods=["GET", "POST"])
def element():
    result = [] 
    if request.method == "POST":
        element = request.form["element"]
        sql = "SELECT * FROM Element WHERE Element_ID = ?"
        result = query_db(sql, (element,), True)
        row = query_db(sql, (element,), True)  
        if row:
            result = [row]
    return render_template("home.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)