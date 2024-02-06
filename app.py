# app.py

from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask import jsonify


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = 'sponge'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    saved_text = db.Column(db.String(500))
    profit = db.Column(db.Integer)

# Create the database
db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='sha256')
        new_user = User(username=username, password=hashed_password, saved_text="", profit=0)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        user = User.query.filter_by(id=session['user_id']).first()
        return render_template('dashboard.html', user=user)
    return redirect(url_for('login'))

@app.route('/save_text', methods=['POST'])
def save_text():
    if 'user_id' in session:
        user = User.query.filter_by(id=session['user_id']).first()
        if request.method == 'POST':
            text_input = request.form.get('text_input', '')
            if user.saved_text:
                user.saved_text += ", "
            user.saved_text += text_input
            db.session.commit()

    return redirect(url_for('dashboard', user=user))

# ... (existing code)

@app.route('/clear_text', methods=['POST'])
def clear_text():
    if 'user_id' in session:
        user = User.query.filter_by(id=session['user_id']).first()

        # Clear the user's saved text
        user.saved_text = ""
        user.profit = 0

        db.session.commit()
        return redirect(url_for('dashboard', user=user))
 

# ... (existing code)



@app.route('/update_profit', methods=['POST'])
def update_profit():
    if 'user_id' in session:
        user = User.query.filter_by(id=session['user_id']).first()
        if request.method == 'POST':
            try:
                profit_update = float(request.form['profit_update'])
                user.profit += profit_update
                db.session.commit()
            except ValueError:
                pass  # Handle invalid input (non-numeric)

    return redirect(url_for('dashboard', user=user))  # Pass 'user' to the template



@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=2000,debug=True)
