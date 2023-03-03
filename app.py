from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def invest():
    return render_template('invest.html')

@app.route("401k")
def o401k():
    return render_template('401k_optimize.html')
