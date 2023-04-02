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

def add_dates(sales):
  date_sums = {}
  for sale in sales: #Sum up the prices for each date
    if sale['sold_date'] in date_sums:
      date_sums[sale['sold_date']] += sale['sale_price']
    else:
      date_sums[sale['sold_date']] = sale['sale_price']
    #New list of dictionaries with the summed prices for each date
  output = [{'sold_date': sold_date, 'sale_price': sale_price} for sold_date, sale_price in date_sums.items()]
  return output

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