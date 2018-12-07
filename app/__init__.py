from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps


app = Flask(__name__)
secret_key='/QCS8Z5*pSzuZwI'

#config Mysl

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'ElsieKalei34'
app.config['MYSQL_DB'] = 'business_Port'
app.config['MYSQL_CURSORCLASS']  = 'DictCursor'

#initialize MYSQL

mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/signup', methods =['GET','POST'])
def signup():
    form = SignUpForm(request.form)
    if request.method == 'POST' and form.validate():

        business_id = form.business_id.data
        business_name = form.business_name.data
        business_email = form.business_email.data
        password = sha256_crypt.encrypt(str(form.password.data))

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO business(business_id, business_name, business_email, password) VALUES(%s, %s, %s, %s)", (business_id, business_name, business_email, password))

        mysql.connection.commit()
        cur.close()
        flash('You are now registered and can log in', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        business_id = request.form['business_id']
        password_candidate = request.form['password']

        cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM business WHERE business_id = %s", [business_id])
        if result > 0:
            data = cur.fetchone()
            password = data['password']

            if sha256_crypt.verify(password_candidate, password):
                session['logged_in'] = True
                session['business_id'] = business_id


                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid Login'
                return render_template('login.html', error=error)
            cur.close()
        else:
            error = 'Business Number not found'
            return render_template('login.html', error=error)


    return render_template('login.html')

def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please Login', 'danger')
            return redirect(url_for('login'))
        return wrap

@app.route('/logout')
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))


@app.route('/reviews')
def reviews():
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM reviews")
    reviews = cur.fetchall()

    if result > 0:
        return render_template('reviews.html', reviews=reviews)
    else:
        msg = "No Reviews/Description Found"
        return render_template('reviews.html', msg=msg)
    cur.close()


@app.route('/review/<string:id>/')
def review(id):
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM reviews WHERE id = %s", [id])

    review = cur.fetchone()
    return render_template('review.html', review=review)




@app.route('/dashboard')
#@is_logged_in
def dashboard():
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM reviews")
    reviews = cur.fetchall()

    if result > 0:
        return render_template('dashboard.html', reviews=reviews)
    else:
        msg = "No Reviews/Description Found"
        return render_template('dashboard.html', msg=msg)
    cur.close()




class SignUpForm(Form):
    business_id = StringField('Business_id', [validators.Length(min=1, max=50)])
    business_name = StringField('Business_name', [validators.Length(min=1, max=50)])
    business_email = StringField('Business_Email', [validators.Length(min=6, max=60)])
    password = PasswordField('Password', [
                validators.DataRequired(),
                validators.EqualTo('confirm', message='Password do not match')

    ])
    confirm = PasswordField('Confirm Password')

class ReviewForm(Form):
    title = StringField('Title', [validators.Length(min=1, max=200)])
    body = TextAreaField('Body', [validators.Length(min=30)])

@app.route('/add_review', methods=['GET', 'POST'])
#@is_logged_in
def add_review():
    form = ReviewForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        body = form.body.data

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO reviews(title, body, author) VALUES(%s, %s, %s)", (title, body, session['business_id']))

        mysql.connection.commit()
        cur.close()

        flash('Review Created', 'success')
        return redirect(url_for('dashboard'))

    return render_template('add_review.html', form=form)

@app.route('/edit_review/<string:id>', methods=['GET', 'POST'])
#@is_logged_in
def edit_review(id):
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM reviews WHERE id = %s", [id])
    review = cur.fetchone()

    form = ReviewForm(request.form)

    form.title.data = review['title']
    form.body.data = review['body']

    if request.method == 'POST' and form.validate():
        title = request.form['title']
        body = request.form['body']

        cur = mysql.connection.cursor()
        cur.execute("UPDATE reviews SET title=%s, body=%s WHERE id=%s", (title, body, id))

        mysql.connection.commit()
        cur.close()

        flash('Review Updated', 'success')
        return redirect(url_for('dashboard'))

    return render_template('edit_review.html', form=form)

@app.route('/delete_review/<string:id>', methods=['POST'])
def delete_review(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM reviews WHERE id = %s", [id])
    mysql.connection.commit()
    cur.close()
    flash('Review Deleted', 'success')
    return redirect(url_for('dashboard'))


if __name__ == '__main__':
    app.secret_key='/QCS8Z5*pSzuZwI'
    app.run(debug=True)
