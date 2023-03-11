from flask import Flask, render_template, jsonify, request, redirect, url_for
# from flask_sqlalchemy import SQLAlchemy
import datetime
# import pandas as pd
# from sklearn.linear_model import LinearRegression
from database import load_inventory, load_sales

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bookkeeping.db'
# db = SQLAlchemy(app)

# class Product(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(50), nullable=False)
#     price = db.Column(db.Float, nullable=False)

# class Sale(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
#     product = db.relationship('Product', backref=db.backref('sales', lazy=True))
#     date = db.Column(db.Date, nullable=False)
#     quantity = db.Column(db.Integer, nullable=False)

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
    products = load_inventory()
    return render_template('home.html', products=products)

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')
  
@app.route('/products')
def show_products():
  products = load_inventory()
  #For chart
  labels=[]
  values=[]
  for row in products:
    labels.append(row['name'])
    values.append(row['qty'])
  data = {'labels':labels, 'values':values}
  
  return render_template('products.html',
                         products=products,
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
