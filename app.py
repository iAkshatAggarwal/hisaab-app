from flask import Flask, render_template, request, redirect, url_for


@app.route('/')
def index():
    products = Product.query.all()
    return render_template('home.html', products=products)



if __name__ == '__main__':
    app.run(debug=True)
