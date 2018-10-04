from flask import Flask
from flask_cors import CORS, cross_origin
from datetime import datetime
import numpy as np
from scipy.optimize import minimize
from scipy.optimize import fmin
from scipy.optimize import linprog
from flask import request
from flask import jsonify
from flask import render_template
import json
import requests
import random, math, copy




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
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
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


@app.route('/routeseq', methods=['POST'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def routeseq():

    data = request.get_json()
    table = json.loads(data['table'])
    cities = [];
    cities.append([float(data['dep_x']), float(data['dep_y']),'Depósito'])
    for j in table:
        cities.append([float(j[1]), float(j[2]),j[0]])
    print(cities)
    numbCities = len(cities)

    # Determining random tour
    tour = random.sample(range(numbCities),numbCities)

    for temperature in np.logspace(0, 5, num=100000)[::-1]:
        [i, j] = sorted(random.sample(range(numbCities), 2))
        newTour = tour[:i] + tour[j:j + 1] + tour[i + 1:j] + tour[i:i + 1] + tour[j + 1:]

        if math.exp((sum(
                [math.sqrt(sum([(cities[tour[(k + 1) % numbCities]][d] - cities[tour[k % numbCities]][d]) ** 2 for d in [0, 1]])) for k
                 in [j, j - 1, i, i - 1]]) - sum(
                [math.sqrt(sum([(cities[newTour[(k + 1) % numbCities]][d] - cities[newTour[k % numbCities]][d]) ** 2 for d in [0, 1]]))
                 for k in [j, j - 1, i, i - 1]])) / temperature) > random.random():
            tour = copy.copy(newTour)
    final_tour = []
    for i in range(len(tour)):
        if tour[i] == 0:
            index = i
            final_tour.append(tour[i])
            for y in range(i + 1, len(tour)):
                final_tour.append(tour[y])
    for z in range(index):
        if tour[z] != 0:
            final_tour.append(tour[z])
    print(final_tour)
    listTour = []

    for cityPoint in final_tour:
        listTour.append(cities[cityPoint])

    listTour.append(cities[0])

    return render_template('routeseq.html', nome=data['name'],zip=zip, cities=cities,route=listTour,  listRoute=listTour)

@app.route('/tranlp', methods=['POST'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def tranlp():
    data = request.get_json()
    table = json.loads(data['table'])

    #definindo variáveis zeradas
    objectiveFun = []
    supply = []
    fromArray = []

    #pegar quantidade de linhas e colunas
    lines   = len(table)-2
    columns = len(table[0])-2

    #pegar tabela sem a primeira e a última linha
    cleanLines = table
    toArray = cleanLines[0]
    toArray.pop(0)
    toArray.pop(-1)

    cleanLines.pop(0)
    #pegando demandas
    demand = cleanLines[-1]
    demand.pop(0)
    demand.pop(-1)
    cleanLines.pop(-1)

    #pegar função objetiva
    for point in cleanLines:
        #pegando nome de cada ponto
        fromArray.append(point[0])
        del point[0]
        #pegando ofertas
        supply.append(point[-1])
        del point[-1]
        for subItem in point:
            objectiveFun.append(subItem)
    #criando restrições para oferta
    a_Rest = []
    i = 0
    for line in range(lines):
        #linha atual = cleanLines[line]

        a_Rest.append([])
        for eachColumn in range(lines):
            columnCounter = 0
            while columnCounter < columns:
                if eachColumn != line:
                    a_Rest[line].append(0)
                else:
                    a_Rest[line].append(1)
                columnCounter += 1
        i += 1

    # criando restrições para demanda
    b_Rest = []
    i = 0
    for column in range(columns):
         # linha atual = cleanLines[line]

         b_Rest.append([])
         for eachColumn in range(lines):
             columnCounter = 0
             while columnCounter < columns:
                 if columnCounter != column:
                     b_Rest[column].append(0)
                 else:
                     b_Rest[column].append(1)
                 columnCounter += 1
         i += 1

    #tratando as entradas
    objectiveFun = [int(x) for x in objectiveFun]
    supply = [int(x) for x in supply]
    demand = [int(x) for x in demand]


    #pegar a segunda linha da tabela
    objective = objectiveFun
    A_ub = a_Rest
    b_ub = supply
    A_eq = b_Rest
    b_eq = demand
    #se a demanda for maior que a oferta, inverte as equações e restrições
    if sum(supply) < sum(demand):
        A_ub = b_Rest
        b_ub = demand
        A_eq = a_Rest
        b_eq = supply
    res = linprog(objective, A_ub, b_ub, A_eq, b_eq, options={"disp": True})

    #print(res)
    finalResult = [float(x) for x in res.x]
    print(finalResult)
    tableResults = []

    #tratando resultados
    for line in range(lines):
        tableResults.append([])
        tableResults[line].append(fromArray[line])
        for column in range(columns):
            tableResults[line].append(finalResult[0])
            finalResult.pop(0)
        tableResults[line].append(supply[line])
    print(tableResults)
    return render_template('tranlp.html', nome=data['name'], res=res, lastLine=demand,
                           tableResults=tableResults, toArray=toArray)


@app.route('/lnprog', methods=['POST'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def lnprog():
    data = request.get_json()
    table = json.loads(data['table'])


    #pegar quantidade de linhas e colunas
    lines   = len(table)-2
    columns = len(table[0])-3
    fromArray = []
    supply = []
    bounds = []
    objectiveFun = []

    #pegar tabela sem a primeira e a ultima linha
    cleanLines = table
    toArray = cleanLines[0]
    toArray.pop(0)
    toArray.pop(-1)

    cleanLines.pop(0)
    #pegando demandas
    demand = cleanLines[-1]
    demand.pop(0)
    demand.pop(-1)
    #remover o tipo da restricao
    demand.pop(-1)
    cleanLines.pop(-1)

    #pegar funcao objetiva
    for point in cleanLines:
        #pegando nome de cada ponto
        fromArray.append(point[0])
        del point[0]
        #pegando ofertas
        supply.append(point[-1])
        del point[-1]
        bounds.append(point[-1])
        del point[-1]
        for subItem in point:
            objectiveFun.append(subItem)
    #criando restricoes
    a_Rest = []

    A_ub = []
    b_ub = []
    A_eq = []
    b_eq = []

    i = 0
    for line in range(lines):
        #linha atual = cleanLines[line]
        if bounds[line] == '<':
            b_ub.append(float(supply[line]))
            cleanLines[line] = [float(x) for x in cleanLines[line]]
            A_ub.append(cleanLines[line])
        if bounds[line] == '>':
            thisBound = float(supply[line])
            thisBound *= -1
            b_ub.append(thisBound)
            cleanLines[line] = [-float(x) for x in cleanLines[line]]
            A_ub.append(cleanLines[line])
        if bounds[line] == '=':
            b_eq.append((float(supply[line])))
            cleanLines[line] = [float(x) for x in cleanLines[line]]
            A_eq.append(cleanLines[line])
        i += 1

    #tratando as entradas
    objective = [float(x) for x in demand]

    print(objective)
    if len(A_ub) == 0:
        A_ub = None
        b_ub = None
    print(A_ub)
    print(b_ub)
    if len(A_eq) == 0:
        A_eq = None
        b_eq = None
    print(A_eq)
    print(b_eq)

    res = linprog(objective, A_ub, b_ub, A_eq, b_eq, method="interior-point")

    print(res)
    roundedResult = round(res.fun)
    finalResult = []
    for variable in range(len(res.x)):
        finalResult.append([toArray[variable],round(res.x[variable]), res.x[variable]])
    return render_template('lnprog.html', nome=data['name'], res=res, finalResult=finalResult, roundedResult=roundedResult)



if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
