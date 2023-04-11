import os
from flask import Flask, render_template, request, session, redirect, url_for
from utils import check_user, get_interval_dates, make_chart, add_sales_by_dates , get_cogs, get_grevenue_gmargin, get_gexpenses, add_expenses_by_dates, add_expenses_by_category, group_sales_by_month, top_products, extract_interval_sales_data, extract_interval_expenses_data, add_deleted_sale_qty_to_inventory, predict_sales_revenue, get_unpaid_customers, add_amt_unpaid_customers, get_latest_credits
from database import load_users, load_inventory, load_sales, load_wholesalers, load_ledgers, load_expenses, add_product, delete_product, update_product, add_ledger, delete_ledger, update_ledger, add_sale, delete_sale, update_sale, add_expense, delete_expense, update_expense

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
            return redirect('/dashboard/today')
                        
        else: 
            return render_template('login.html', login_error = True)

@app.route('/logout')
def logout():
    # clear session variables
    session.clear()
    # redirect to login page
    return redirect(url_for('login'))
          
#------------------------------- Dashboard -------------------------------

@app.route('/dashboard/<interval>')
def dashboard(interval="today"):
    # check if user is authenticated
    if session.get('authenticated'):
      # user is authenticated, render dashboard page
      sales = load_sales()
      expenses = load_expenses()
      products = load_inventory()
      # Assigning interval dates
      start_date, end_date = get_interval_dates(interval, sales)
      #Extract Sales data for given interval
      interval_sales = extract_interval_sales_data(sales, start_date, end_date)
      interval_expenses = extract_interval_expenses_data(expenses, start_date, end_date)
      #Gross Revenue and Gross Margin
      g_revenue , g_margin = get_grevenue_gmargin(interval_sales)
      g_expenses = get_gexpenses(interval_expenses)
      #Net Revenue
      n_revenue = g_margin - g_expenses
      #Cost of Goods Sold
      cogs = get_cogs(products, interval_sales)
      #Inventory Cost
      inventory_cost = sum(product['pqty'] * product['pcp'] for product in products)
      #EBITDA i.e Earning before Interest, Taxes, Depreciation and Amortization
      if n_revenue != 0:
        ebitda = "{:.2%}".format((n_revenue/g_revenue))
      else:
        ebitda = 0
      #Revenue Projection and Profit Projection
      p_revenue, p_profit = predict_sales_revenue(sales, interval)
      #Monthly Sales Chart
      monthly_sales = group_sales_by_month(sales)
      monthly_sales_data = make_chart(monthly_sales, 'month', 'price')
      # For Daily Sales Chart
      daily_sales = add_sales_by_dates(interval_sales) #adding amount for same dates 
      daily_sales_data = make_chart(daily_sales, 'sale_date', 'sale_amt')
      #For Expenses by Category Chart
      category_expenses = add_expenses_by_category(interval_expenses)
      category_expenses_data = make_chart(category_expenses, 'type', 'eprice')
      # For Daily Expenses Chart
      daily_expenses = add_expenses_by_dates(interval_expenses)
      daily_expenses_data = make_chart(daily_expenses, 'date', 'eprice')
      #Top Products
      top_products_qty, top_products_profit = top_products(sales)
      
      return render_template('dashboard.html',
                             g_revenue=g_revenue,
                             g_margin=g_margin,
                             g_expenses=g_expenses,
                             n_revenue=n_revenue,
                             cogs=cogs,
                             ebitda=ebitda,
                             p_revenue=p_revenue,
                             p_profit=p_profit,
                             inventory_cost=inventory_cost,
                             monthly_sales_data=monthly_sales_data,
                             daily_sales_data=daily_sales_data,
                             category_expenses_data=category_expenses_data,
                             daily_expenses_data=daily_expenses_data,
                             top_products_qty=top_products_qty,
                             top_products_profit=top_products_profit)
    else:
        # user is not authenticated, redirect to login page
        return redirect(url_for('login'))

#------------------------------- Products -------------------------------
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

@app.route("/add_product", methods=["GET", "POST"])
def add_prod():
    if add_product(request.form["pname"],
                  request.form["pcp"],
                  request.form["psp"],
                  request.form["pqty"]):
      return redirect("/products")

@app.route("/products/<pid>/delete")
def del_prod(pid):
    if delete_product(pid):
      return redirect("/products")

@app.route("/products/update", methods=["GET", "POST"])
def mod_prod():
    if update_product(request.form.get('pname'),
                      request.form.get('pcp'),
                      request.form.get('psp'),
                      request.form.get('pqty')):
      return redirect('/products')

#------------------------------- Ledgers -------------------------------

@app.route('/ledgers')
def show_ledgers():
  if session.get('authenticated'):
      ledgers = load_ledgers()
      wholesalers = load_wholesalers()
      result = get_latest_credits(ledgers)
      #For chart
      data = make_chart(result, 'wname', 'credit')
      return render_template('ledger.html',
                             ledgers=ledgers,
                             wholesalers=wholesalers,
                             data=data)
  else:
      return redirect(url_for('login'))

@app.route("/add_ledger", methods=["GET", "POST"])
def add_led():
    if add_ledger(request.form["wname"],
                  request.form["credit"],
                  request.form["debit"]):
      return redirect("/ledgers")

@app.route("/ledgers/<wid>/delete")
def del_led(wid):
    if delete_ledger(wid):
      return redirect("/ledgers")  

@app.route("/ledgers/update", methods=["GET", "POST"])
def mod_led():
    if update_ledger(request.form.get('wid'),
                      request.form.get('wname'),
                      request.form.get('ttime'),
                      request.form.get('credit'),
                      request.form.get('debit')):
      return redirect('/ledgers')

#------------------------------- Sales -------------------------------

@app.route('/sales/<interval>')
def show_sales(interval = "thisweek"):
  if session.get('authenticated'):
      sales = load_sales()
      products = load_inventory()
      # Assigning interval dates
      start_date, end_date = get_interval_dates(interval, sales)
      #Extract Sales data for given interval
      interval_sales = extract_interval_sales_data(sales, start_date, end_date)
      #For chart
      output = add_sales_by_dates(interval_sales) #adding amount for same dates 
      data = make_chart(output, 'sale_date', 'sale_amt')
      return render_template('sales.html',
                             products = products,
                             sales=interval_sales,
                             data=data)

  else:
      return redirect(url_for('login'))

@app.route("/add_sale", methods=["GET", "POST"])
def add_sales():
    if add_sale(request.form["pname"],
                  request.form["qty"],
                  request.form["price"],
                  request.form["customer"],
                  request.form['status']):
      return redirect("/sales/thisweek")

@app.route("/sales/<id>/delete")
def del_sales(id):
    products = load_inventory()
    product = request.args.get('product')
    sale_qty = request.args.get('sale_qty')
    print(product)
    new_qty = add_deleted_sale_qty_to_inventory(products, product, sale_qty)
    if delete_sale(id, product, new_qty):
      return redirect("/sales/thisweek")

@app.route("/sales/update", methods=["GET", "POST"])
def mod_sale():
    if update_sale(request.form.get('id'),
                request.form.get('sale_date'),
                request.form.get('product'),
                request.form.get('sale_qty'),
                request.form.get('sale_price'),
                request.form.get('sale_amt'),
                request.form.get('sale_profit'),
                request.form.get('customer'),
                request.form.get('status')):
      return redirect("/sales/thisweek")

#------------------------------- Expenses -------------------------------
@app.route('/expenses')
def show_expenses():
  if session.get('authenticated'):
      expenses = load_expenses()
      output = add_expenses_by_dates(expenses)
      data = make_chart(output, 'date', 'eprice')
      return render_template('expenses.html',
                              expenses=expenses,
                              data=data)
  else:
      return redirect(url_for('login'))

@app.route("/add_expense", methods=["GET", "POST"])
def add_ex():
    if add_expense(request.form["type"],
                  request.form["eprice"]):
      return redirect("/expenses")

@app.route("/expenses/<id>/delete")
def del_ex(id):
    if delete_expense(id):
      return redirect("/expenses") 

@app.route("/expenses/update", methods=["GET", "POST"])
def mod_expense():
    if update_expense(request.form.get('id'),
                      request.form.get('date'),
                      request.form.get('type'),
                      request.form.get('eprice')):
      return redirect('/expenses')

#------------------------------- Customers -------------------------------
@app.route('/customers')
def show_customers():
  if session.get('authenticated'):
      sales = load_sales()
      unpaid_customers = get_unpaid_customers(sales)
      #For chart
      output = add_amt_unpaid_customers(unpaid_customers) #adding amount for same dates 
      data = make_chart(output, 'customer', 'sale_amt')
      return render_template('customers.html',
                             unpaid_customers=unpaid_customers,
                             data=data)
  else:
      return redirect(url_for('login'))
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
