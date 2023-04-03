import os
from flask import Flask, render_template, request, session, redirect, url_for
from utils import check_user, make_chart, add_dates_sales , get_cards_revenue, get_cards_expenses, add_dates_expenses
from database import load_users, load_inventory, load_sales, load_wholesalers, load_ledgers, load_expenses, add_product, delete_product, add_ledger, delete_ledger, add_sale, delete_sale, add_expense, delete_expense

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
          
#------------------------------- Dashboard -------------------------------
@app.route('/dashboard')
def dashboard():
    # check if user is authenticated
    if session.get('authenticated'):
      # user is authenticated, render dashboard page
        sales = load_sales()
        expenses = load_expenses()
        g_revenue , g_profit = get_cards_revenue(sales)
        g_expenses = get_cards_expenses(expenses)
        n_revenue = g_revenue - g_expenses
        n_profit = g_profit - g_expenses
        ebitda = "{:.2%}".format((n_profit/n_revenue))
        return render_template('dashboard.html',
                               g_revenue=g_revenue,
                               g_profit=g_profit,
                               g_expenses=g_expenses,
                               n_revenue=n_revenue,
                               n_profit=n_profit,
                               ebitda=ebitda)
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

# @app.route("products/<pid>/update", methods=["GET", "POST"])
# def mod_prod(tid):
    
#     return redirect('/run_record')

#------------------------------- Ledgers -------------------------------
@app.route('/ledgers')
def show_ledgers():
  if session.get('authenticated'):
      ledgers = load_ledgers()
      wholesalers = load_wholesalers()
      #wslist = [ws['wname'] for ws in wholesalers] #list of wholesalers' name
      #For chart
      data = make_chart(ledgers, 'wname', 'credit')
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

#------------------------------- Sales -------------------------------
@app.route('/sales')
def show_sales():
  if session.get('authenticated'):
      sales = load_sales()
      products = load_inventory()
      #For chart
      output = add_dates_sales(sales) #adding amount for same dates 
      data = make_chart(output, 'sale_date', 'sale_amt')
      return render_template('sales.html',
                             products = products,
                             sales=sales,
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
      return redirect("/sales")

@app.route("/sales/<id>/delete")
def del_sales(id):
    if delete_sale(id):
      return redirect("/sales") 

#------------------------------- Expenses -------------------------------
@app.route('/expenses')
def show_expenses():
  if session.get('authenticated'):
      expenses = load_expenses()
      output = add_dates_expenses(expenses)
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
