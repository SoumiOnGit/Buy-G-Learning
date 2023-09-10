from flask import Flask, redirect , render_template, request, url_for 
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

@app.route('/')
def index():
    return render_template('index.html')

    
class User(db.Model):
        id = db.Column(db.Integer, primary_key = True, autoincrement=True)
        username = db.Column(db.String(200), nullable = False)
        email = db.Column(db.String(200), nullable = False)
        password = db.Column(db.String(200), nullable = False)
        is_store_manager = db.Column(db.Integer, default= 0)
        #user_cart = relationship('Cart', backref='user', lazy=True)

    
        def __repr__(self):
            return '<User %r>' % self.username

class Section(db.Model):
        id = db.Column(db.Integer, primary_key = True, autoincrement=True)
        name = db.Column(db.String(200), nullable = False)
        products = relationship('Product', backref='section', lazy=True)

class Product(db.Model):
        id = db.Column(db.Integer, primary_key = True, autoincrement=True)
        name = db.Column(db.String(200), nullable = False)
        price = db.Column(db.Integer, nullable = False)
        expiry_date = db.Column(db.DateTime , default = datetime.now())
        quantity_available = db.Column(db.Integer, nullable = False)
        section_id = db.Column(db.Integer, db.ForeignKey('section.id'), nullable=False)  # Define a foreign key to establish the relationship
        description = db.Column(db.String(200), nullable = False)



if not os.path.exists("./test.db"):
    with app.app_context():
            db.create_all()
            admin = User.query.filter_by(username='admin').first()
            if admin is None:
                admin = User(id=1,username='admin',email='admin@admin.com',password='admin',is_store_manager=1) # created automatically
                db.session.add(admin)
                db.session.commit()


@app.route('/admin_login',methods =['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        print(email,password)
        users=User.query.all()
        for user in users:
            
            if user.email == email and user.password == password:
                return redirect(url_for('admin_dashboard'))
        return redirect(url_for('admin_login'))
    return render_template('admin_login.html')


@app.route('/admin_dashboard')
def admin_dashboard():
    section=Section.query.all()
    return render_template('admin_dashboard.html',blahblah=section)


if __name__ == '__main__':
    
    app.run(debug=True)

