from flask import Flask, g, render_template, request,session
import sqlite3

DATABASE = 'element.db'
RANDOM_SYMBOL = None
app = Flask(__name__)
app.secret_key = "my_secret_key"

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
def index():
    return render_template('home.html')


@app.route('/quiz', methods=["GET", "POST"])
def quiz():


    global RANDOM_SYMBOL

    
    if "guesses" not in session:
        session["guesses"] = []

    if RANDOM_SYMBOL is None:
        random_element = query_db("SELECT Element_ID FROM Element ORDER BY RANDOM() LIMIT 1", one=True)
        RANDOM_SYMBOL = random_element['Element_ID']
    target_row = query_db("SELECT * FROM Element WHERE Element_ID = ? COLLATE NOCASE", (RANDOM_SYMBOL,), one=True)

    if request.method == "POST":
        Element_ID = request.form.get("element")
        row = query_db("SELECT * FROM Element WHERE Element_ID = ? COLLATE NOCASE",(Element_ID,),True)
        if row:
            guesses = session["guesses"]
            guesses.append(dict(row))
            session["guesses"] = guesses


        if Element_ID and Element_ID.lower() == RANDOM_SYMBOL.lower():
            session["guesses"] = []
            random_element = query_db( "SELECT Element_ID FROM Element ORDER BY RANDOM() LIMIT 1", one=True)
            RANDOM_SYMBOL = random_element['Element_ID']
            return render_template("result.html", answer=Element_ID)


    return render_template("element.html", result=session["guesses"], random_symbol=RANDOM_SYMBOL,target=target_row)




if __name__ == "__main__":
    app.run(debug=True)