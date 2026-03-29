from flask import Flask, g, render_template, request
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

@app.route('/', methods=["GET", "POST"])
def home():
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

        sql = "SELECT * FROM Element WHERE Element_ID = ? COLLATE NOCASE"
        row = query_db(sql, (Element_ID,), True)
        if row:
            result = [row]

    else:
        sql = "SELECT * FROM Element"
        result = query_db(sql)


    return render_template("home.html", result=result, random_symbol=RANDOM_SYMBOL)
if __name__ == "__main__":
    app.run(debug=True)


