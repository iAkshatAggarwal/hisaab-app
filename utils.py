from datetime import date, datetime, timedelta
from sklearn.linear_model import LinearRegression
import numpy as np

def check_user(users, username, password):
  for user in users:
    # users is a list of dictionary
    if user['uname'] == username and user['upass'] == password:
      return True
  return False

def get_interval_dates(interval, sales):
  end_date =  date.today()
  start_date = date.today()
  if interval == 'thisweek':
    start_date = end_date - timedelta(days=7)
  elif interval == 'thismonth':
    start_date =  end_date.replace(day=1) - timedelta(days=1)
  elif interval == 'thisquarter':
    month = end_date.month - 3 if end_date.month > 3 else end_date.month + 9
    start_date = date(end_date.year, month, 1) - timedelta(days=1)
  elif interval == 'thisyear':
    start_date = end_date.replace(year=end_date.year - 1)
  elif interval == 'alltime':
    start_date = min(sale['sale_date'] for sale in sales)
  return start_date, end_date

def make_chart(table, x, y):
  labels=[]
  values=[]
  for row in table:
    labels.append(row[x])
    values.append(row[y])
  data = {'labels':labels, 'values':values}
  return data

def get_cards_revenue(sales):
  gross_revenue = 0
  gross_profit = 0
  for sale in sales:
    gross_revenue += sale['sale_amt']
    gross_profit += sale['sale_profit']
  return gross_revenue, gross_profit   

def get_cards_expenses(expenses):
  gross_expenses = 0
  for expense in expenses:
    gross_expenses += expense['eprice']
  return gross_expenses

def add_dates_sales(sales):
  date_sums = {}
  for sale in sales: #Sum up the prices for each date
    if sale['sale_date'] in date_sums:
      date_sums[sale['sale_date']] += sale['sale_amt']
    else:
      date_sums[sale['sale_date']] = sale['sale_amt']
    #New list of dictionaries with the summed prices for each date
  output = [{'sale_date': sale_date, 'sale_amt': sale_amt} for sale_date, sale_amt in date_sums.items()]
  return output

def get_cogs(products, sales):
  cogs = 0
  for product in products:
    for sale in sales:
      if sale["product"] == product['pname']:
        cogs += sale["sale_qty"] * product["pcp"]
  return cogs

def add_dates_expenses(expenses):
  date_sums = {}
  for expense in expenses: #Sum up the prices for each date
    if expense['date'] in date_sums:
      date_sums[expense['date']] += expense['eprice']
    else:
      date_sums[expense['date']] = expense['eprice']
    #New list of dictionaries with the summed prices for each date
  output = [{'date': date, 'eprice': eprice} for date, eprice in date_sums.items()]
  return output

def group_sales_by_month(sales):
  sales_by_month = {}
  for sale in sales:
      date = sale['sale_date']
      month = date.strftime('%Y-%m')
      if month in sales_by_month:
          sales_by_month[month]['price'] += sale['sale_amt']
      else:
          sales_by_month[month] = {
              'month': month,
              'price': sale['sale_amt']
          }
  return list(sales_by_month.values())

def get_cp(products, pname):
    for product in products:
        if product["pname"] == pname:
            return product["pcp"]
    return None

def get_pqty(products, pname):
    for product in products:
        if product["pname"] == pname:
            return product["pqty"]
    return None

def calc_updated_sales(id, sales, sale_price, sale_amt, sale_profit, products, product, sale_qty):
  cp = get_cp(products, product)
  for sale in sales: # To update new amount and profit
    if str(sale["id"]) == str(id):
      sale_amt = float(sale_price) * float(sale_qty)
      sale_profit = float(sale_amt) - (float(sale_qty) * float(cp))
      for prod in products: # To update qty in inventory
        if str(prod["pname"]) == str(product):
          pname = prod["pname"] 
          pqty = prod["pqty"]
          if int(sale_qty) > int(sale["sale_qty"]):
            pqty -= (int(sale_qty)- int(sale["sale_qty"]))
          elif int(sale_qty) < int(sale["sale_qty"]):
            pqty += (int(sale["sale_qty"]) - int(sale_qty))
  return sale_amt, sale_profit, pname, pqty

def top_products(sales):
    # Create a dictionary to store the quantity and profit for each product
    product_dict = {}

    # Loop through each sale and update the product dictionary
    for sale in sales:
        name = sale['product']
        qty = sale['sale_qty']
        profit = sale['sale_profit']

        # If the product is already in the dictionary, add the quantity and profit
        if name in product_dict:
            product_dict[name]['qty'] += qty
            product_dict[name]['profit'] += profit
        # If the product is not in the dictionary, add it with the quantity and profit
        else:
            product_dict[name] = {'name': name, 'qty': qty, 'profit': profit}

    # Sort the products by quantity and profit in descending order and take the top 10
    sorted_products_qty = sorted(product_dict.values(), key=lambda x: x['qty'], reverse=True)[:10]
    sorted_products_profit = sorted(product_dict.values(), key=lambda x: x['profit'], reverse=True)[:10]

    # Return separate lists of dictionaries for the top products by quantity and profit
    return (sorted_products_qty, sorted_products_profit)

def extract_interval_sales_data(data_list, start_date, end_date):
    extracted_data = []
    for data in data_list:
        if start_date <= data["sale_date"] <= end_date:
            extracted_data.append(data)
    return extracted_data

def extract_interval_expenses_data(data_list, start_date, end_date):
    extracted_data = []
    for data in data_list:
        if start_date <= data["date"] <= end_date:
            extracted_data.append(data)
    return extracted_data

def extract_interval_products_data(data_list, start_date, end_date):
    extracted_data = []
    for data in data_list:
        if start_date <= data["date"] <= end_date:
            extracted_data.append(data)
    return extracted_data

def add_deleted_sale_qty_to_inventory(products, product, sale_qty):
    for prod in products: # To update qty in inventory
      if str(prod["pname"]) == str(product):
        pqty = int(prod["pqty"])
        pqty += int(sale_qty)
        break
    return pqty

def get_unpaid_customers(sales):
    unpaid_customers = []
    for sale in sales:
      if sale['status'] == 'Unpaid':
        unpaid_customers.append(
          {
            'customer': sale['customer'], 
            'sale_date': sale['sale_date'],
            'product': sale['product'],
            'sale_qty': sale['sale_qty'],
            'sale_amt': sale['sale_amt']
          }
        )   
    return unpaid_customers

def add_amt_unpaid_customers(sales):
  date_sums = {}
  for sale in sales: #Sum up the amount for each customer
    if sale['customer'] in date_sums:
      date_sums[sale['customer']] += sale['sale_amt']
    else:
      date_sums[sale['customer']] = sale['sale_amt']
    #New list of dictionaries with the summed prices for each date
  output = [{'customer': customer, 'sale_amt': sale_amt} for customer, sale_amt in date_sums.items()]
  return output

def get_latest_credits(ledgers):
    result = {}
    for ledger in sorted(ledgers, key=lambda x: x['ttime'], reverse=True):
        wname, credit = ledger['wname'], ledger['credit']
        if wname not in result:
            result[wname] = credit
    return [{'wname': k, 'credit': v} for k, v in result.items()]
        
# ------------------------------ Revenue Prediction ------------------------------

def predict_sales_revenue(sales_data, interval):
    # Convert sales_data to a numpy array for easier processing
    sales_array = np.array([[sale['sale_qty'], sale['sale_price'], sale['sale_amt'], sale['sale_profit']] for sale in sales_data])
    X = sales_array[:, :2]  # select first two columns as input features
    y = sales_array[:, 2]

    model = LinearRegression()
    model.fit(X, y)

    today_date = datetime.now().strftime('%Y-%m-%d')
    next_week_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
    next_month_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
    next_quarter_date = (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d')
    next_year_date = (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')

    predicted_revenue_today = model.predict([[0, 0.0]])[0]
    predicted_revenue_next_week = model.predict([[7, 0.0]])[0]
    predicted_revenue_next_month = model.predict([[30, 0.0]])[0]
    predicted_revenue_next_quarter = model.predict([[90, 0.0]])[0]
    predicted_revenue_next_year = model.predict([[365, 0.0]])[0]

    predicted_profit_today = predicted_revenue_today - model.predict([[0, 0.0]])[0]
    predicted_profit_next_week = predicted_revenue_next_week - model.predict([[7, 0.0]])[0]
    predicted_profit_next_month = predicted_revenue_next_month - model.predict([[30, 0.0]])[0]
    predicted_profit_next_quarter = predicted_revenue_next_quarter - model.predict([[90, 0.0]])[0]
    predicted_profit_next_year = predicted_revenue_next_year - model.predict([[365, 0.0]])[0]
  
    p_revenue = 0
    p_profit = 0
    if interval == "today":
        p_revenue = round(predicted_revenue_today,2)
        p_profit = round(predicted_profit_today,2)
    elif interval == "thisweek":
        p_revenue = round(predicted_revenue_next_week,2)
        p_profit = round(predicted_profit_next_week,2)
    elif interval == "thismonth":
        p_revenue = round(predicted_revenue_next_month,2)
        p_profit = round(predicted_profit_next_month,2)
    elif interval == "thisquarter":
        p_revenue = round(predicted_revenue_next_quarter,2)
        p_profit = round(predicted_profit_next_quarter,2)
    elif interval == "thisyear":
        p_revenue = round(predicted_revenue_next_year,2)
        p_profit = round(predicted_profit_next_year,2)
      
    return p_revenue, p_profit
