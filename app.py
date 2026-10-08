from flask import Flask, g, render_template, request, session, redirect, url_for
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
    invalid = None
    global RANDOM_SYMBOL
    if "guesses" not in session:
        session["guesses"] = []
    #select a random element from the database 
    if RANDOM_SYMBOL is None:
        random_element = query_db("SELECT Element_name FROM Element ORDER BY RANDOM() LIMIT 1", one=True)
        RANDOM_SYMBOL = random_element['Element_name']
    #the random element's info
    target_row = query_db("""SELECT Element.*, state.state AS state_name, category.category AS category_name
                            FROM Element LEFT JOIN state ON Element.State = state.id 
                            LEFT JOIN category ON Element.Category = category.id 
                            WHERE Element.Element_name = ? COLLATE NOCASE""", (RANDOM_SYMBOL,), one=True)
    #get the user's guess
    if request.method == "POST":
        Element_ID = request.form.get("element")
        row = query_db("""SELECT Element.*, state.state AS state_name, category.category AS category_name
                          FROM Element LEFT JOIN state ON Element.State = state.id 
                          LEFT JOIN category ON Element.Category = category.id 
                          WHERE Element.Element_name = ? COLLATE NOCASE""", (Element_ID,), True)
        #the user guessed an existing element, add it to the guess list
        if row:
            guesses = session["guesses"]
            names = [g["Element_name"].lower() for g in guesses]
            if Element_ID.lower() not in names:
                guesses.insert(0, dict(row))
                session["guesses"] = guesses
        #the user type in a non-exist element
        if not row:
            invalid = "Invalid Element. Please try again."

        #the user guessed the right element and start a new element
        if Element_ID and Element_ID.lower() == RANDOM_SYMBOL.lower():
            session["guesses"] = []
            random_element = query_db( "SELECT Element_name FROM Element ORDER BY RANDOM() LIMIT 1", one=True)
            RANDOM_SYMBOL = random_element['Element_name']
            return render_template("result.html", answer=Element_ID)
        
    #calculate the remaining hints
    remaining = 3 - session.get ("hint_count", 0)
    return render_template("element.html", result=session["guesses"], random_symbol=RANDOM_SYMBOL, target=target_row, invalid=invalid, remaining=remaining)
    

@app.route('/hint')
def hint():
    #hint page, user can only access 3 hints, after that they will be told no more hints left
    if "hint_count" not in session:
        session["hint_count"] = 0
    if session["hint_count"] >= 3:
        return redirect(url_for('quiz'))

    session["hint_count"] += 1

    return render_template('hint.html', remaining=3 - session["hint_count"])


if __name__ == "__main__":
    app.run(debug=True)