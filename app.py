import os
from flask import Flask, render_template, request, redirect
from flask_login import LoginManager, login_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User
import sentry_sdk

sentry_sdk.init(dsn=os.environ.get("SENTRY_DSN", ""), traces_sample_rate=1.0)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///local.db').replace(
    'postgres://', 'postgresql://', 1
)

db.init_app(app)
login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return render_template('index.html', user=current_user)

@app.route('/health')
def health():
    return {"status": "ok"}, 200

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form['username']
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return "That username is already taken. <a href='/'>Go back</a>", 400
    password = generate_password_hash(request.form['password'])
    db.session.add(User(username=username, password_hash=password))
    db.session.commit()
    return redirect('/')

@app.route('/login', methods=['POST'])
def login():
    user = User.query.filter_by(username=request.form['username']).first()
    if user and check_password_hash(user.password_hash, request.form['password']):
        login_user(user)
    return redirect('/')

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)