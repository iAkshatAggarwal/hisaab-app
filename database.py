import os
from sqlalchemy import create_engine, text

conn_string = os.environ['DB_CONNECTION_STRING']

engine = create_engine(conn_string, connect_args = {
  "ssl":{
    "ssl_ca": "/etc/ssl/cert.pem"
  }
})

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
    ledgers = []
    for row in response.fetchall():
        row_dic = dict(zip(response.keys(), row))
        ledgers.append(row_dic)
    return ledgers

def add_products():
  with engine.connect() as conn:
    query = text("INSERT INTO products(pname, pcp, psp, pqt) VALUES (:pname, :pcp, :psp, :pqt)")

    conn.execute(query)
