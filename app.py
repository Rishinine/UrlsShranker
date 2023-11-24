#importing required libraries
from flask import Flask,render_template,request,redirect,session
from time import sleep

import random
import string
from requests import get
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String
from sqlalchemy.orm import DeclarativeBase,Mapped, mapped_column

def generate_short_link(length = 5):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string+str(random.randint(0,1000))
# inheriting flask class 
app = Flask(__name__)
class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///links.db"
app.secret_key = 'your_secret_key_here'
db.init_app(app)
class Links(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    olink: Mapped[str] = mapped_column(String, nullable=False)
    nlink: Mapped[str] = mapped_column(String)
    
    def __init__(self,olink,nlink):
        self.olink=olink
        self.nlink = nlink        

with app.app_context():
    db.create_all()

@app.route('/',methods = ['POST','GET'])
def link_generate():
    session['link'] = request.base_url
    if request.method == 'POST':
        link = request.form['linkurl'] 
        if 'http' not in link:
            link = 'https://'+link 
        try:
            a = get(link)
        except Exception as e:
            return redirect('/invalid')
        if a.status_code != 404:
            nlink = generate_short_link()  
            linktoadd = Links(link,nlink)
            db.session.add(linktoadd)
            db.session.commit()
            session['msg'] = link
            return redirect('/success')                               
    return render_template('index.html')
@app.route('/invalid')
def invalid_url():
    return render_template('error.html')


@app.route('/success')
def success():
    users = db.session.execute(db.select(Links).order_by(Links.id)).scalars()
    users_data = users
    for i in users_data:
        if i.olink==session['msg']:
            nlink = session['link']+i.nlink
    return render_template('success.html',success=session['msg'],nlink=nlink)
@app.route('/<nlinks>')
def redirect_to_olink(nlinks):
    users = db.session.execute(db.select(Links).order_by(Links.id)).scalars()
    users_data = users
    for i in users_data:
        if i.nlink == nlinks:
            link = i.olink
            return redirect(link)
    else:
        return redirect('/invalid')
@app.route('/links_stored')
def show_links():
    users = db.session.execute(db.select(Links).order_by(Links.id)).scalars()
    users_data = users
    return render_template('data.html',users_data=users_data,url=session['link'])
if __name__ == '__main__':
    app.run(debug=True)
