import os
from flask import Flask, render_template, jsonify, request, session, redirect, url_for
# from flask_sqlalchemy import SQLAlchemy
import datetime
# import pandas as pd
# from sklearn.linear_model import LinearRegression
from utils import check_user, make_chart
from database import load_users, load_inventory, load_sales, load_wholesalers, delete_products

app = Flask(__name__)
app.secret_key = os.environ['SECRET_KEY']

# def predict_growth():
#     sales_data = pd.read_sql_table('sale', con=db.engine)
#     sales_data['month'] = pd.to_datetime(sales_data['date']).dt.to_period('M')
#     monthly_sales = sales_data.groupby('month')['quantity'].sum().reset_index()
#     X = pd.to_numeric((monthly_sales['month'] - monthly_sales['month'].min()) / pd.offsets.MonthBegin(1))
#     X = X.values.reshape(-1, 1)
#     y = monthly_sales['quantity']
#     model = LinearRegression()
#     model.fit(X, y)
#     next_month = pd.Period(datetime.date.today(), freq='M') + 1
#     next_month_sales = model.predict([[pd.to_numeric((next_month - monthly_sales['month'].min()) / pd.offsets.MonthBegin(1))]])
#     return next_month_sales[0]

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
      
    elif request.method == "POST": 
        session['login_error'] = False
        users = load_users()
        username = request.form["username"]
        password = request.form["password"]
      
        if check_user(users, username, password):
            return render_template("dashboard.html")
        login_error = session.pop('login_error', False)
        return render_template('login.html', login_error=login_error)

#Dashboard
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

#Products
@app.route('/products')
def show_products():
  products = load_inventory()
  #For chart
  data = make_chart(products, 'pname', 'pqty')
  return render_template('products.html',
                         products=products,
                         data=data)

# @app.route("/products/<int:pid>/delete")
# delete_products(id)

#Ledgers
@app.route('/ledgers')
def show_ledgers():
  ledgers = load_wholesalers()
  #For chart
  data = make_chart(ledgers, 'wname', 'credit')
  return render_template('ledger.html',
                         ledgers=ledgers,
                         data=data)

@app.route('/orders')
def show_sales():
  sales = load_sales()
  return render_template('sales.html', sales=sales)

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
