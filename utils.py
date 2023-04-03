# from sklearn.linear_model import LinearRegression

def check_user(users, username, password):
  for user in users:
    # users is a list of dictionary
    if user['uname'] == username and user['upass'] == password:
      return True
  return False

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