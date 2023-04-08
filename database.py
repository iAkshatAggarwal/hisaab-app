import os
import datetime
from sqlalchemy import create_engine, text
from utils import get_cp, get_pqty, calc_updated_sales

conn_string = os.environ['DB_CONNECTION_STRING']

engine = create_engine(conn_string, connect_args = {
  "ssl":{
    "ssl_ca": "/etc/ssl/cert.pem"
  }
})

def load_users():
  with engine.connect() as conn:
    result = conn.execute(text("SELECT * from users"))
    users = []
    for row in result.fetchall():
        row_dict = dict(zip(result.keys(), row))
        users.append(row_dict)
    return users
    
def load_inventory():
  with engine.connect() as conn:
    result = conn.execute(text("SELECT * from product"))
    products = []
    for row in result.fetchall():
        row_dict = dict(zip(result.keys(), row))
        products.append(row_dict)
    return products

def load_sales():
  with engine.connect() as conn:
    response = conn.execute(text("SELECT * from sales"))
    sales = []
    for row in response.fetchall():
        row_dic = dict(zip(response.keys(), row))
        sales.append(row_dic)
    return sales

def load_wholesalers():
  with engine.connect() as conn:
    response = conn.execute(text("SELECT * from wholesalers"))
    wholesalers = []
    for row in response.fetchall():
        row_dic = dict(zip(response.keys(), row))
        wholesalers.append(row_dic)
    return wholesalers

def load_ledgers():
  with engine.connect() as conn:
    response = conn.execute(text("SELECT * from ledger"))
    ledgers = []
    for row in response.fetchall():
        row_dic = dict(zip(response.keys(), row))
        ledgers.append(row_dic)
    return ledgers

def load_expenses():
  with engine.connect() as conn:
    response = conn.execute(text("SELECT * from expenses"))
    expenses = []
    for row in response.fetchall():
        row_dic = dict(zip(response.keys(), row))
        expenses.append(row_dic)
    return expenses

#------------------------------- Products -------------------------------
def add_product(pname, pcp, psp, pqty):
  with engine.connect() as conn:
    query = text("INSERT INTO product(pname, pcp, psp, pqty) VALUES (:pname, :pcp, :psp, :pqty)")
    conn.execute(query,
                 {'pname': pname,
                  'pcp': pcp,
                  'psp': psp,
                  'pqty': pqty
                 }
    )
    return True

def delete_product(id):
  with engine.connect() as conn:
    conn.execute(text("DELETE FROM product WHERE pid = :val"), {'val': id})
    return True

def update_product(pname, pcp, psp, pqty):
  with engine.connect() as conn:
    query = (text("UPDATE product SET pcp =:pcp, psp =:psp, pqty =:pqty WHERE pname = :pname"))
    conn.execute(query,
                 {
                  'pname': pname, 
                  'pcp': pcp, 
                  'psp': psp, 
                  'pqty': pqty
                 }
    )
    return True

#------------------------------- Ledgers -------------------------------
def add_ledger(wname, credit, debit):
  with engine.connect() as conn:
    ledgers = load_ledgers()
    ledger_subset = [ledger for ledger in ledgers if ledger['wname'] == wname]
    if len(ledger_subset) > 0:
        latest_ledger = sorted(ledger_subset, key=lambda x: x['ttime'])[-1]
        credit = latest_ledger['credit']
        credit -= int(debit)
    for ledger in ledgers:
      if ledger['wname'] != wname and credit == "":
        credit = 0
    if debit == "":
      debit = 0
    
    query = text("INSERT INTO ledger(wname, ttime, credit, debit) VALUES (:wname, :ttime, :credit, :debit)")
    conn.execute(query,
                 {
                  'wname': wname, 
                  'ttime': datetime.datetime.now(), 
                  'credit': credit, 
                  'debit': debit
                 }
    )
    return True

def delete_ledger(id):
  with engine.connect() as conn:
    conn.execute(text("DELETE FROM ledger WHERE wid = :val"), {'val': id})
    return True

def update_ledger(wid, wname, ttime, credit, debit):
  with engine.connect() as conn:
    if credit == "":
      credit = 0
    elif debit == "":
      debit = 0
    query = (text("UPDATE ledger SET wname =:wname, ttime =:ttime, credit =:credit, debit =:debit WHERE wid = :wid"))
    conn.execute(query,
                 {
                  'wid': wid, 
                  'wname': wname, 
                  'ttime': ttime, 
                  'credit': credit, 
                  'debit': debit
                 }
    )
    return True
    
#------------------------------- Sales -------------------------------
def add_sale(pname, qty, price, customer, status):
  with engine.connect() as conn:
    #to get cp
    products = load_inventory()
    amount = int(qty) * int(price)
    cp = get_cp(products, pname)
    new_qty = get_pqty(products, pname) - int(qty) #updated qty of inventory
    profit = amount - (int(qty) * int(cp))
    query= text("INSERT INTO sales(product, sale_date, sale_qty, sale_price, sale_amt, sale_profit,  customer, status) VALUES (:product, :sale_date, :sale_qty, :sale_price, :sale_amt, :sale_profit, :customer, :status)")
    conn.execute(query,
                 {
                  'product': pname, 
                  'sale_date': datetime.datetime.now(), 
                  'sale_qty': qty, 
                  'sale_price': price,
                  'sale_amt': amount,
                  'sale_profit': profit,
                  'customer': customer,
                  'status': status
                 }
    )
    query2 = text("UPDATE product SET pqty = :pqty  WHERE pname = :pname")
    conn.execute(query2,
                {
                  'pqty': new_qty,
                  'pname': pname
                }
    )
    return True

def delete_sale(id, pname, pqty):
  with engine.connect() as conn:
    # To update qty in inventory or product table
    conn.execute(text("UPDATE product SET pqty = :pqty  WHERE pname = :pname"), {'pqty': pqty, 'pname': pname})
    # To delete sale from sales table
    conn.execute(text("DELETE FROM sales WHERE id = :val"), {'val': id})
    return True

def update_sale(id, sale_date, product, sale_qty, 
                sale_price, sale_amt, sale_profit, customer, status):
  with engine.connect() as conn:
    sales = load_sales()
    products = load_inventory()
    sale_amt, sale_profit, pname, pqty = calc_updated_sales(id, sales, sale_price, sale_amt, sale_profit, products, product, sale_qty)
    # To update qty in inventory or product table
    query1 = text("UPDATE product SET pqty = :pqty  WHERE pname = :pname")
    conn.execute(query1,
                  {
                    'pqty': pqty,
                    'pname': pname
                  }
    )
    # Updating Sales 
    query2 = (text("UPDATE sales SET id = :id, sale_date = :sale_date, product = :product, sale_qty = :sale_qty, sale_price = :sale_price, sale_amt = :sale_amt, sale_profit = :sale_profit, customer =:customer, status = :status WHERE id = :id"))
    conn.execute(query2,
                 {
                  'id': id,
                  'sale_date': sale_date, 
                  'product': product, 
                  'sale_qty': sale_qty, 
                  'sale_price': sale_price,
                  'sale_amt': sale_amt,
                  'sale_profit': sale_profit,
                  'customer': customer,
                  'status': status
                 }
    )
    return True

#------------------------------- Expenses -------------------------------

def add_expense(type, eprice):
  with engine.connect() as conn:
    query = text("INSERT INTO expenses(type, eprice, date) VALUES (:type, :eprice, :date)")
    conn.execute(query,
                 {
                  'type': type, 
                  'eprice': eprice, 
                  'date': datetime.datetime.now()
                 }
    )
    return True

def delete_expense(id):
  with engine.connect() as conn:
    conn.execute(text("DELETE FROM expenses WHERE id = :val"), {'val': id})
    return True

def update_expense(id, date, type, eprice):
  with engine.connect() as conn:
    query = (text("UPDATE expenses SET date =:date, type =:type, eprice =:eprice WHERE id = :id"))
    conn.execute(query,
                 {
                  'id': id, 
                  'date': date, 
                  'type': type, 
                  'eprice': eprice
                 }
    )
    return True