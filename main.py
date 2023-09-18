from flask import Flask, redirect , render_template, request, url_for 
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
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



@app.route('/add_category',methods =['GET', 'POST'])
def add_category():
    if request.method == 'POST':
        name = request.form['name']
        user = Section(name=name)
        try:
                db.session.add(user)
                db.session.commit()
                return redirect('/admin_dashboard')
        except:
                return 'There was an issue adding new user'
    return render_template('add_category.html')



@app.route('/delete_category/<int:id>')
def delete_category(id):
    category_to_delete = Section.query.get_or_404(id)

    try:
        db.session.delete(category_to_delete)
        db.session.commit()
        return redirect('/admin_dashboard')
    except:
        return 'There was a problem deleting that task'
    


@app.route('/rename_category/<int:id>', methods=['GET', 'POST'])
def rename_category(id):
    section = Section.query.get_or_404(id)

    if request.method == 'POST':
        section.name = request.form['name']

        try:
            db.session.commit()
            return redirect('/admin_dashboard')
        except:
            return 'There was an issue renaming your category'

    else:
        return render_template('rename_category.html', section=section)


@app.route('/view_category/<int:category_id>', methods=['GET', 'POST'])
def view_category(category_id):
     category= Section.query.get_or_404(category_id)
     print(category.id,category.name)
     products = Product.query.filter_by(section_id=category_id).all()
     return render_template('view_category.html',cat=category,products=products)





@app.route('/add_product/<int:category_id>', methods=['GET', 'POST'])
def add_product(category_id):
    category= Section.query.get_or_404(category_id)
    if request.method == 'POST':
        name = request.form.get('product_name')
        price = request.form.get('price')
        expiry_date = request.form.get('expiry_date')
        quantity_available = request.form.get('quantity_available')
        description = request.form.get('description')

        expiry_date = datetime.strptime(expiry_date, '%Y-%m-%d')

        new_product = Product(
            name=name,
            price=price,
            expiry_date=expiry_date,
            quantity_available=quantity_available,
            section_id=category.id,  # Set the section_id to the current category
            description=description
        )

        # Add the new product to the database
        db.session.add(new_product)
        db.session.commit()
        return redirect(f"/view_category/{category_id}")
          
    return render_template('add_product.html', category=category)




@app.route('/delete_product/<int:id>')
def delete_product(id):
    product_to_delete = Product.query.get_or_404(id)
    cat_id=product_to_delete.section_id
    try:
        db.session.delete(product_to_delete)
        db.session.commit()
        return redirect(f'/view_category/{cat_id}')
    except:
        return 'There was a problem deleting that product'



@app.route('/update_product/<int:id>', methods=['GET', 'POST'])
def update_product(id):
    product = Product.query.get_or_404(id)
    expiry_date_str = product.expiry_date.strftime('%Y-%m-%d')

    if request.method == 'POST':
        product.name = request.form['product_name']
        product.price = request.form['price']
        expiry_date = request.form['expiry_date']
        product.expiry_date = datetime.strptime(expiry_date, '%Y-%m-%d')
        product.quantity_available = request.form['quantity_available']
        product.description = request.form['description']

        try:
            db.session.commit()
            return redirect(f'/view_category/{product.section_id}')
        except:

            return 'There was an issue updating your category'

    else:
        return render_template('update_product.html', product=product, date=expiry_date_str)


@app.route('/signup',methods =['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['name']
        email = request.form['email']
        password = request.form['password']
        user = User(username=username,email=email,password=password,is_store_manager=0)
        try:
            db.session.add(user)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue adding new user'
            
    return render_template('signup.html')

@app.route('/login',methods =['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        print(email,password)
        users=User.query.all()
        for user in users:
            if user.email == email and user.password == password and user.email!="admin@admin.com":
                print("inside if condition")
                return redirect(f'/user_dashboard/{user.id}')
        return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/user_dashboard/<int:user_id>', methods=['GET'])
def user_dashboard(user_id):
    cats = Section.query \
    .outerjoin(Section.products) \
    .group_by(Section.id) \
    .order_by(desc(db.func.max(Product.id))) \
    .all()
    user = User.query.get_or_404(user_id)
    products = Product.query.all()
    query = request.args.get('query', '').lower()
    selected_categories = request.args.getlist('category')
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')

    # Apply a filter for price range if both min_price and max_price are provided
    if min_price and max_price:
        products = Product.query.filter(Product.price >= float(min_price), Product.price <= float(max_price)).all()

    if query:
        products = Product.query.filter(Product.name.contains(query)).all()
        
    return render_template('user_dashboard.html', cats=cats, user=user, products=products, query=query, selected_categories=selected_categories, min_price=min_price, max_price=max_price)



if __name__ == '__main__':
    app.run(debug=True)

