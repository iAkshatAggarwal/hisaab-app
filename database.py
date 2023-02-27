from sqlalchemy import create_engine, text

conn_string = "mysql+pymysql://znsmp0aqaral2oxvygxv:pscale_pw_vQLskbi00nDiith9BVn6W9Hg5iegxScqhVcNL9tdANP@ap-south.connect.psdb.cloud/hisaab?charset=utf8mb4"

engine = create_engine(conn_string, connect_args = {
  "ssl":{
    "ssl_ca": "/etc/ssl/cert.pem"
  }
})

with engine.connect() as conn:
    result = conn.execute(text("SELECT * from product"))
    products = []
    for row in result.fetchall():
        row_dict = dict(zip(result.keys(), row))
        products.append(row_dict)

    print(products)
