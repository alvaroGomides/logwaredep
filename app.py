from flask import Flask
from flask_cors import CORS, cross_origin
from datetime import datetime
import numpy as np
from scipy.optimize import minimize
from scipy.optimize import fmin
from flask import request

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

def totalcost(a):
    tc = np.sum(t*m*k*(((x-a[0])**2)+((y-a[1])**2))**0.5)
    print("Custo = {}, X = {}, Y = {}".format(tc, a[0], a[1]))
    return tc

@app.route('/cog', methods=['POST'])
def cog():
    global t
    global m
    global k
    global x
    global y
    #getting the parameters of the request
    jdata = request.get_json()
    x = []
    y = []
    m = []
    t = []
    for j in jdata:
        x.extend(j[1])
        y.extend(j[2])
        m.extend(j[3])
        t.extend(j[4])
    #x = [2, 5, 9, 7, 2]
    x = np.array(x)
    #y = [1, 2, 1, 4, 5]
    y = np.array(y)
    #m = [300, 500, 170, 120, 900]
    m = np.array(m)
    #t = [0.002, 0.0015, 0.002, 0.0013, 0.0015]
    t = np.array(t)
    #Determining total costs
    k = 50
    b = []
    a = [2, 0]
    #print(totalcost(a))
    #print(type(totalcost(a)))
    sol = minimize(totalcost, (2,0), method="SLSQP", tol="0.1")
    return """
    A instalacao vai ser localizada nas seguintes coordenadas: x-> {} e y-> {}
    """.format(sol.x[0], sol.x[1])

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)

