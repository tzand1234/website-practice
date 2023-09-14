from flask import Flask, render_template, flash, redirect, url_for, session
import postgresqlite
import datetime
from forms import LoginForm, DeclarationForm
from flask_mail import Mail, Message
from flask_login import  LoginManager, login_user, login_required, logout_user, current_user
from models import User, Meals, db, LoginToken
import secrets
import os

app = Flask(__name__)

# Configure Flask app settings
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = postgresqlite.get_uri()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = '/home/tom/lms/1.2/dynweb/website-practice/static/screenshots'
db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = '/'
login_manager.init_app(app)


# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.ethereal.email'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'maude.cronin@ethereal.email'
app.config['MAIL_PASSWORD'] = 'jvdfFNjXEFexHnRDFH'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)



@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return User.query.get(int(user_id))


@app.errorhandler(404)
@login_required
def not_found(e):
    """Handles 404 errors and redirects to the dashboard page."""
    flash("An error occurred")
    return redirect("/dashboard")


@app.route("/", methods=["GET", "POST"])
def login():
    """Handles the login page."""
    
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        token = secrets.token_hex(16)

        # Store the token and its expiration time in the database
        login_token = LoginToken(secret=token)
        db.session.add(login_token)
        db.session.commit()

        msg = Message(
            subject="Login to Your Account",
            sender="maude.cronin@ethereal.email",
            recipients=["maude.cronin@ethereal.email"]
        )

        login_url = url_for(
            'authenticate',
            username=username,
            token=token,
            _external=True
        )

        msg.html = f"Click the following link to log in: <a href='{login_url}' target='_blank' rel='noopener noreferrer'>Log In</a>"

        mail.send(msg)

        return render_template("login_sent.html", email=f"{username}@huizebrak.nl")

    return render_template("login.html", form=form)


@app.route("/auth/<username>/<token>")
def authenticate(username, token):
    """Authenticates the login token and redirects to the dashboard if valid."""
    login_token = LoginToken.query.filter_by(secret=token).first()

    if login_token and login_token.is_valid_token():
        user = User.query.filter_by(name=username).first()
        if not user:
            # Create a new user if it doesn't exist
            user = User()
            user.name = username
            db.session.add(user)

        # Delete the login token from the database to ensure it can only be used once
        db.session.delete(login_token)
        db.session.commit()

        login_user(user)  # Store the username in the session

        return redirect(url_for('dashboard'))

    flash("Token is invalid or has expired")
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    """Renders the dashboard page with meal and user data."""
    
    today = datetime.date.today()
    meal_for_today = Meals.query.filter(Meals.date == today).first()

    if not meal_for_today:
        meal_for_today = Meals(date=today)
        db.session.add(meal_for_today)
        db.session.commit()

    users = User.query.all()
    meals = Meals.query.order_by(Meals.date.desc()).limit(14).all()

    return render_template('dashboard.html', meals=meals, users=users)


@app.route("/form/<int:meal_id>", methods=["GET", "POST"])
@login_required
def form(meal_id=None):
    """Renders and handles the meal form."""
    
    meal = Meals.query.get_or_404(meal_id)

    username = current_user.name

    if not username:
        return redirect("/")

    change = username == meal.cook

    form = DeclarationForm(obj=meal)

    if form.validate_on_submit():
        form.populate_obj(meal)
        add_image(form.photo.data, meal)
        db.session.commit()
        flash("Meal reported successfully!")
        return redirect("/dashboard")

    screenshot_url = url_for("static", filename=f"screenshots/{meal.photo_filename}") if meal.photo_filename else None

    return render_template("form.html", form=form, meal=meal, screenshot_url=screenshot_url, meal_id=meal.id, change=change)


@login_required
def add_image(photo, meal):
    try:
        filename = f"{secrets.token_hex(16)}.png"
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        photo.save(filepath)

        if meal.photo_filename:
            old_filepath = os.path.join(app.config["UPLOAD_FOLDER"], meal.photo_filename)
            if os.path.exists(old_filepath):
                os.remove(old_filepath)

        meal.photo_filename = filename

    except Exception as e:
        flash(f"Error saving photo: {e}", "error")
        return redirect("/")


@app.route("/participate/<int:meal_id>/cook", methods=["GET", "POST"])
@login_required
def signup_cook(meal_id=None):
    """Handles signing up as a cook for a meal."""
    
    username = current_user.name

    if not username:
        return redirect("/")

    user = User.query.filter_by(name=username).first()
    meal = Meals.query.get(meal_id)
    meal.cook = user.name

    meal.participants.append(user)

    db.session.commit()
    return redirect(url_for("form", meal_id=meal_id))


@app.route("/participate/<int:meal_id>")
@login_required
def participate(meal_id):
    """Handles participating or unparticipating in a meal."""
    
    username = current_user.name

    if username:
        user = User.query.filter_by(name=username).first()
        meal = Meals.query.get_or_404(meal_id)

        if user.name != meal.cook:
            if user in meal.participants:
                meal.participants.remove(user)
                flash("You have successfully unparticipated from the meal.")
            else:
                meal.participants.append(user)
                flash("You have successfully participated in the meal.")

            db.session.commit()
        else:
            flash("You are the cook.")

    return redirect(url_for("form", meal_id=meal_id))


@app.route("/logout")
def logout():
    """Logs out the user and redirects to the login page."""
    logout_user()
    return redirect(url_for("login"))


if __name__ == '__main__':
    app.run(debug=True)