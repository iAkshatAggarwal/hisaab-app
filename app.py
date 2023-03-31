import os
from flask import Flask, render_template, jsonify, request, session, redirect, url_for
import datetime
from utils import check_user, make_chart
from database import load_users, load_inventory, load_sales, load_wholesalers, delete_product

app = Flask(__name__)
app.secret_key = os.environ['SECRET_KEY']


@app.route('/')
def index():
    return render_template('home.html')

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
      
    elif request.method == "POST": 
        users = load_users()
        if check_user(users, 
                      request.form["username"],
                      request.form["password"]):
            session['authenticated'] = True
            return redirect(url_for('dashboard'))
                        
        else: 
            return render_template('login.html', login_error = True)

@app.route('/logout')
def logout():
    # clear session variables
    session.clear()
    # redirect to login page
    return redirect(url_for('login'))
          
#Dashboard
@app.route('/dashboard')
def dashboard():
    # check if user is authenticated
    if session.get('authenticated'):
      # user is authenticated, render dashboard page
        return render_template('dashboard.html')
    else:
        # user is not authenticated, redirect to login page
        return redirect(url_for('login'))

#Products
@app.route('/products')
def show_products():
  if session.get('authenticated'):
      products = load_inventory()
      #For chart
      data = make_chart(products, 'pname', 'pqty')
      return render_template('products.html',
                             products=products,
                             data=data)
  else:
      return redirect(url_for('login'))
    
@app.route("/products/<pid>/delete")
def del_prod(pid):
    if delete_product(pid):
      return redirect("/products")

#Ledgers
@app.route('/ledgers')
def show_ledgers():
  if session.get('authenticated'):
      ledgers = load_wholesalers()
      #For chart
      data = make_chart(ledgers, 'wname', 'credit')
      return render_template('ledger.html',
                             ledgers=ledgers,
                             data=data)
  else:
      return redirect(url_for('login'))
    
@app.route('/orders')
def show_sales():
  if session.get('authenticated'):
      sales = load_sales()
      return render_template('sales.html', sales=sales)

  else:
      return redirect(url_for('login'))

# @app.route('/product/add', methods=['GET', 'POST'])
# def add_product():
#     if request.method == 'POST':
#         name = request.form['name']
#         price = float(request.form['price'])
#         product = Product(name=name, price=price)
#         db.session.add(product)
#         db.session.commit()
#         return redirect(url_for('index'))
#     else:
#         return render_template('add_product.html')

# @app.route('/sale/add', methods=['GET', 'POST'])
# def add_sale():
#     if request.method == 'POST':
#         product_id = int(request.form['product'])
#         product = Product.query.get(product_id)
#         date = datetime.datetime.strptime(request.form['date'], '%Y-%m-%d').date()
#         quantity = int(request.form['quantity'])
#         sale = Sale(product=product, date=date, quantity=quantity)
#         db.session.add(sale)
#         db.session.commit()
#         return redirect(url_for('index'))
#     else:
#         products = Product.query.all()
#         return render_template('add_sale.html', products=products)

# @app.route('/revenue')
# def revenue():
#     sales_data = pd.read_sql_table('sale', con=db.engine)
#     revenue = (sales_data['quantity'] * sales_data['product'].apply(lambda x: x.price)).sum()
#     return render_template('revenue.html', revenue=revenue)

# @app.route('/growth')
# def growth():
#     next_month_sales = predict_growth()
#     return render_template('growth.html', next_month_sales=next_month_sales)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
