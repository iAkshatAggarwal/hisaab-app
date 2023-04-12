from datetime import date, timedelta
from statsmodels.tsa.arima.model import ARIMA
import pandas as pd

def check_user(users, username, password):
  for user in users:
    # users is a list of dictionary
    if user['uname'] == username and user['upass'] == password:
      return user['uid'], user['company']
  return None

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

def get_grevenue_gmargin(sales):
  gross_revenue = 0
  gross_profit = 0
  for sale in sales:
    gross_revenue += sale['sale_amt']
    gross_profit += sale['sale_profit']
  return gross_revenue, gross_profit   

def get_gexpenses(expenses):
  gross_expenses = 0
  for expense in expenses:
    gross_expenses += expense['eprice']
  return gross_expenses

def add_sales_by_dates(sales):
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

def add_expenses_by_dates(expenses):
  date_sums = {}
  for expense in expenses: #Sum up the prices for each date
    if expense['date'] in date_sums:
      date_sums[expense['date']] += expense['eprice']
    else:
      date_sums[expense['date']] = expense['eprice']
    #New list of dictionaries with the summed prices for each date
  output = [{'date': date, 'eprice': eprice} for date, eprice in date_sums.items()]
  return output

def add_expenses_by_category(expenses):
  date_sums = {}
  for expense in expenses: #Sum up the prices for each category
    if expense['type'] in date_sums:
      date_sums[expense['type']] += expense['eprice']
    else:
      date_sums[expense['type']] = expense['eprice']
    #New list of dictionaries with the summed prices for each category
  output = [{'type': type, 'eprice': eprice} for type, eprice in date_sums.items()]
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
    if len(sales_data) == 0:
      return 0, 0
    daily_sales_data = add_sales_by_dates(sales_data)
  
    # Convert list of dictionaries to DataFrame
    df = pd.DataFrame(daily_sales_data)
    
    # Convert date string to datetime object and set as index
    df['sale_date'] = pd.to_datetime(df['sale_date'])
    df.set_index('sale_date', inplace=True)

    # Train ARIMA model
    model = ARIMA(df['sale_amt'], order=(2,1,1))  # ARIMA(2,1,1) model
    model_fit = model.fit()
    
    # Make predictions
    try:
        today_revenue = model_fit.forecast()[0][-1]
    except IndexError:
        today_revenue = 0
    # today_revenue = model_fit.forecast()[0][-1]  # Today's revenue
    one_week_revenue = model_fit.forecast(steps=7)[-1]  # Revenue in 1 week
    end_of_month_revenue = model_fit.forecast(steps=30)[-1]  # Revenue at end of month
    end_of_quarter_revenue = model_fit.forecast(steps=90)[-1]  # Revenue at end of quarter
    end_of_year_revenue = model_fit.forecast(steps=365)[-1]  # Revenue at end of year
  
    if interval == "today":
        p_revenue = round(today_revenue,2)
        p_profit = 0
    elif interval == "thisweek":
        p_revenue = round(one_week_revenue,2)
        p_profit = 0
    elif interval == "thismonth":
        p_revenue = round(end_of_month_revenue,2)
        p_profit = 0
    elif interval == "thisquarter":
        p_revenue = round(end_of_quarter_revenue,2)
        p_profit = 0
    elif interval == "thisyear":
        p_revenue = round(end_of_year_revenue,2)
        p_profit = 0
      
    return p_revenue, p_profit
