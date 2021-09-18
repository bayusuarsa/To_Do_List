from flask import Flask, render_template, redirect, url_for, flash, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_bootstrap import Bootstrap
from flask_login import UserMixin, LoginManager, login_user, login_required, current_user, logout_user
from datetime import datetime
from form import TodoListForm, RegisterForm, LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'LLLKKKKLLLKKKLL'
Bootstrap(app)


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///new-todo-list.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), unique=True, nullable=False)


    # todo_list = relationship("TodoList", back_populates="writer")

    def __repr__(self):
        return f"<User {self.name}>"


class Todolist(db.Model):
    __tablename__ = "todolist"
    id = db.Column(db.Integer, primary_key=True)

    # writer_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    # writer = relationship("User", back_populates="todo_list")

    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    todo = db.Column(db.String(250), unique=True, nullable=False)

    def __repr__(self):
        return f"Todo_list{self.todo}"


db.create_all()


@app.route("/")
def home_page():
    return render_template("index.html")


@app.route("/sign-up", methods=["POST","GET"])
def sign_up():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            print(User.query.filter_by(email=form.email.data).first())

            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))

        user = User(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
        )
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('home_page'))
    return render_template('register.html', form=form, current_user=current_user)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()
        if not user:
            flash("That email doesn't exist, please try again!")
            return redirect(url_for('login'))
        elif not password(user.password, password):
            flash("Password incorrect, please try again!")
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('home_page'))
    return render_template("login.html", form=form)


@app.route("/create-task", methods=["POST","GET"])
def create_task():
    form = TodoListForm()
    if form.validate_on_submit():
        add_new_todo = Todolist(
            date=form.date.data,
            todo=form.todo.data
        )
        db.session.add(add_new_todo)
        db.session.commit()
        return redirect(url_for('home_page'))
    return render_template("todo.html", form=form)


if __name__ == "__main__":
    app.run(debug=True)
