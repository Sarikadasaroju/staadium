from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# DB setup
def init_db():
    conn = sqlite3.connect('stadium.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY,
            match TEXT,
            stadium TEXT,
            date TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY,
            name TEXT,
            match_id INTEGER,
            tickets INTEGER,
            FOREIGN KEY (match_id) REFERENCES matches(id)
        )
    ''')
    # Sample data
    cursor.execute("SELECT COUNT(*) FROM matches")
    if cursor.fetchone()[0] == 0:
        cursor.executemany('INSERT INTO matches (match, stadium, date) VALUES (?, ?, ?)', [
            ('India vs Australia', 'Wankhede Stadium', '2025-08-15'),
            ('India vs England', 'Eden Gardens', '2025-08-20'),
            ('India vs Pakistan', 'Narendra Modi Stadium', '2025-09-01')
        ])
    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = sqlite3.connect('stadium.db')
    matches = conn.execute('SELECT * FROM matches').fetchall()
    conn.close()
    return render_template('index.html', matches=matches)

@app.route('/book/<int:match_id>', methods=['GET', 'POST'])
def book(match_id):
    conn = sqlite3.connect('stadium.db')
    match = conn.execute('SELECT * FROM matches WHERE id=?', (match_id,)).fetchone()

    if request.method == 'POST':
        name = request.form['name']
        tickets = int(request.form['tickets'])
        conn.execute('INSERT INTO bookings (name, match_id, tickets) VALUES (?, ?, ?)', (name, match_id, tickets))
        conn.commit()
        conn.close()
        return redirect('/bookings')

    return render_template('book.html', match=match)

@app.route('/bookings')
def bookings():
    conn = sqlite3.connect('stadium.db')
    data = conn.execute('''
        SELECT bookings.name, matches.match, matches.stadium, bookings.tickets
        FROM bookings
        JOIN matches ON bookings.match_id = matches.id
    ''').fetchall()
    conn.close()
    return render_template('bookings.html', bookings=data)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
