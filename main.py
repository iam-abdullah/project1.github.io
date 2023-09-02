from flask import Flask, render_template, request,redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_mail import Mail
import json,math,os
from flask import session,flash
from werkzeug.utils import secure_filename

with open('config.json', 'r') as c:
    params = json.load(c)["params"]

local_server = True

app = Flask(__name__)
app.secret_key = 'super-secret-key'
app.config['UPLOAD_FOLDER'] = params['upload_location']
app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = params['gmail-user'],
    MAIL_PASSWORD=  params['gmail-password']
)
mail = Mail(app)


if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']
db = SQLAlchemy(app)



class Contacts(db.Model):
    '''
    sno, name phone_num, msg, date, email
    '''
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(20), nullable=False)
    reg_no= db.Column(db.String(11), nullable=False)
    phone_no = db.Column(db.String(12), nullable=False)
    mes = db.Column(db.String(120), nullable=False)
    user = db.Column(db.String(80), nullable=False)
    date = db.Column(db.String(12), nullable=True)


class Posts1(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(21), nullable=False)
    tagline = db.Column(db.String(21), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    by_whom = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(20), nullable=True)
    img_file = db.Column(db.String(30), nullable=True)


class User_id(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(30), nullable=False)
    lname = db.Column(db.String(20), nullable=False)
    user_id = db.Column(db.String(80), nullable=False)
    phone_no = db.Column(db.String(12), nullable=False)
    password = db.Column(db.String(80), nullable=False)







@app.route("/")
def home():
    flash("Support Our work,for getting more content","success")
    post = Posts1.query.filter_by().all()
    last = math.ceil(len(post) / int(params['no_of_posts']))
    page = request.args.get('page')
    if (not str(page).isnumeric()):
        page = 1
    page = int(page)
    post = post[(page - 1) * int(params['no_of_posts']):(page - 1) * int(params['no_of_posts']) + int(
        params['no_of_posts'])]
    if page == 1:
        prev = "#"
        next = "/?page=" + str(page + 1)
    elif page == last:
        prev = "/?page=" + str(page - 1)
        next = "#"
    else:
        prev = "/?page=" + str(page - 1)
        next = "/?page=" + str(page + 1)

    return render_template('index.html', params=params, post=post, prev=prev, next=next)

@app.route("/about")
def about():
    return render_template('about.html', params=params)




@app.route("/blog")
def blog():
    post = Posts1.query.filter_by().all()
    last = math.ceil(len(post) / int(params['no_of_posts']))
    page = request.args.get('page')
    if (not str(page).isnumeric()):
        page = 1
    page = int(page)
    post = post[(page - 1) * int(params['no_of_posts']):(page - 1) * int(params['no_of_posts']) + int(
        params['no_of_posts'])]
    if page == 1:
        prev = "#"
        next = "/?page=" + str(page + 1)
    elif page == last:
        prev = "/?page=" + str(page - 1)
        next = "#"
    else:
        prev = "/?page=" + str(page - 1)
        next = "/?page=" + str(page + 1)

    return render_template('blog.html', params=params, post=post, prev=prev, next=next)



@app.route("/contact", methods = ['GET', 'POST'])
def contact():
    if(params['admin_user']== ""):
      return redirect("/")
    if(request.method=='POST' and params['admin_user']!= ""):
        '''Add entry to the database'''
        name = request.form.get('name')
        email = request.form.get('email')
        reg_no = request.form.get('reg_no')
        phone = request.form.get('phone')
        message = request.form.get('message')
        entry = Contacts(name=name,email = email, reg_no=reg_no,phone_no = phone, mes = message, user=email,date= datetime.now() )
        db.session.add(entry)
        db.session.commit()
        '''mail.send_message('New message from ' + name,
                          sender=email,
                          recipients = [params['gmail-user']],
                          body = message + "\n" + phone
                          )'''
        flash("Thank you for submit your details,we will get back to you ASAP","success")
    return render_template('contact.html',params=params)

@app.route("/post/<string:post_slug>/", methods=['GET'])
def post_route(post_slug):
    post = Posts1.query.filter_by(slug=post_slug).first()
    return render_template('post.html', params=params, post=post)

@app.route("/uploader" , methods=['GET', 'POST'])
def uploader():
    if "user" in session and session['user']==params['admin_user']:
        if request.method=='POST':
            f = request.files['file1']
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
            return "Uploaded successfully!"


@app.route("/dashboard",methods=['GET','POST'])
def dashboard():
    if "user" in session and session['user'] == params['admin_user']:
        post = Posts1.query.all()
        contacts = Contacts.query.filter_by(user=params['admin_user'])
        return render_template("dashboard.html", params=params, post=post, contacts=contacts)

    if request.method == "POST":
        username = request.form.get("uname")
        userpass = request.form.get("pass")
        login = User_id.query.filter_by(user_id = username, password=userpass).first()
        if login is not None:
            params['admin_user'] = username
            # set the session variable
            session['user'] = username
            post = Posts1.query.filter_by(by_whom=username)
            contacts = Contacts.query.filter_by(user=username)
            return render_template("dashboard.html", params=params,post=post,contacts=contacts)
        else:
            return render_template("login.html", params=params)

    return render_template("loginpage.html", params=params)

@app.route('/logout')
def logout():
    session.pop('user')
    params['admin_user']=""
    return redirect('/dashboard')
@app.route('/login')
def test():
    return render_template('login.html', params=params)
@app.route('/signup',methods=['GET','POST'])
def test2():
    if(request.method=='POST'):
        '''Add entry to the database'''

        fname = request.form.get('fname')
        lname = request.form.get('lname')
        user_id = request.form.get('email')
        phone_no = request.form.get('phone_no')
        password  = request.form.get('password')
        entry = User_id(fname=fname,lname=lname,user_id=user_id, phone_no = phone_no,password=password)
        db.session.add(entry)
        db.session.commit()
    return render_template('signup.html')

@app.route("/edit/<string:sno>", methods=['GET', 'POST'])
def edit(sno):
    if "user" in session and session['user'] == params['admin_user']:
        if request.method == "POST":
            box_title = request.form.get('title')
            tline = request.form.get('tline')
            slug = request.form.get('slug')
            content = request.form.get('content')
            by_whom= params['admin_user']
            img_file = request.form.get('img_file')
            date = datetime.now()

            if sno == '0':
                post = Posts1(title= box_title, slug=slug, tagline=tline, content=content,by_whom= params['admin_user'], date=date, img_file=img_file)
                db.session.add(post)
                db.session.commit()
            else:
                post = Posts1.query.filter_by(sno=sno).first()
                post.title = box_title
                post.slug = slug
                post.tagline = tline
                post.content = content
                post.img_file = img_file
                post.date = date
                db.session.commit()
                return redirect('/edit/' + sno)

        post = Posts1.query.filter_by(sno=sno).first()
        return render_template('edit.html', params=params, post=post,sno=sno)

@app.route("/delete/<string:sno>" , methods=['GET', 'POST'])
def delete(sno):
    if "user" in session and session['user']==params['admin_user']:
        post = Posts1.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect("/dashboard")
app.run(debug=True)