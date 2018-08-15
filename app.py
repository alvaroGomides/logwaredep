from flask import Flask
from flask_cors import CORS, cross_origin
from datetime import datetime
import numpy as np
from scipy.optimize import minimize
from scipy.optimize import fmin
from flask import request
from flask import jsonify
from flask import render_template
import json
import requests


app = Flask(__name__)
CORS(app)


@app.route('/')
def homepage():
    the_time = datetime.now().strftime("%A, %d %b %Y %l:%M %p")
    return """
    <h1>Hello heroku</h1>
    <p>It is currently {time}.</p>
    <img src="http://loremflickr.com/600/400" />
    """.format(time=the_time)





@app.route('/cog', methods=['POST'])
def cog():
    def totalcost(a):
        tc = np.sum(t * m * k * (((x - a[0]) ** 2) + ((y - a[1]) ** 2)) ** tFactor)
        print("Custo = {}, X = {}, Y = {}".format(round(tc, 2), round(a[0], 4), round(a[1], 4)))
        return tc

    x = []
    y = []
    m = []
    t = []

    data = request.get_json()
    table = json.loads(data['table'])

    for j in table:
        x.append(float(j[1]))
        y.append(float(j[2]))
        m.append(float(j[3]))
        t.append(float(j[4]))

    x = np.array(x)
    y = np.array(y)
    m = np.array(m)
    t = np.array(t)

    # Determining total costs
    k = [50]
    k = int(data['power_factor'])


    tFactor = float(data['scale_factor'])
    tFactor = np.array(tFactor)
    tFactor = tFactor.astype(np.float)
    b = []
    a = [2, 0]

    sol = minimize(totalcost, (2, 0), method="SLSQP", tol="0.1")

    return render_template('cog.html', nome=data['name'], custo=round(sol.fun,4),
                           coordenadax=round(sol.x[0],4), coordenaday=round(sol.x[1],4),
                           units=table)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
