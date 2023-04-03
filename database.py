import os
import datetime
from sqlalchemy import create_engine, text
from utils import get_cp, get_pqty

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

#-------------------------------Products-------------------------------
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

def update_product(id):
  with engine.connect() as conn:
    conn.execute(text("UPDATE product SET {} = %s WHERE id = %s"), {'val': id})
    return True

#-------------------------------Ledgers-------------------------------
def add_ledger(wname, credit, debit):
  with engine.connect() as conn:
    if credit == "":
      credit = 0
    elif debit == "":
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

#-------------------------------Sales-------------------------------
def add_sale(pname, qty, price, customer):
  with engine.connect() as conn:
    #to get cp
    products = load_inventory()
    amount = int(qty) * int(price)
    cp = get_cp(products, pname)
    new_qty = get_pqty(products, pname) - int(qty) #upadated qty of inventory
    profit = amount - (int(qty) * int(cp))
    query= text("INSERT INTO sales(product, sale_date, sale_qty, sale_price, sale_amt, sale_profit,  customer) VALUES (:product, :sale_date, :sale_qty, :sale_price, :sale_amt, :sale_profit, :customer)")
    conn.execute(query,
                 {
                  'product': pname, 
                  'sale_date': datetime.datetime.now(), 
                  'sale_qty': qty, 
                  'sale_price': price,
                  'sale_amt': amount,
                  'sale_profit': profit,
                  'customer': customer
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

def delete_sale(id):
  with engine.connect() as conn:
    conn.execute(text("DELETE FROM sales WHERE id = :val"), {'val': id})
    return True