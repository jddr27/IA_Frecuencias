from flask import Flask, render_template,  redirect, url_for, escape, request
import json
from datetime import datetime
import sys
import os
import pandas as pd
import numpy as np
import random
from DTS.Signal import Signal
from DTS.Filter import Filter
#import conn

   

app = Flask(__name__)

arreglo = []
input1 = Signal()
input2 = Signal()

def ordenarSegundo(val):
    return val[1]


def getprimero(val):
    return val[0]


def obtenerFitness(frec, tipo):
    global input1, input2
    individuo = [0.5999402, -0.5999402, 0, 1, -0.7265425, 0, 1, -2, 1, 1, -1.52169043, 0.6, 1, -2, 1, 1, -1.73631017, 0.82566455]
    ff = 0

    input1.generate(frec - 200, 5, sinoidal=True)
    filtro1 = Filter(individuo) #1.47815634821363e-90
    output1 = filtro1.filter(input1)

    input2.generate(frec + 200, 5, sinoidal=True)
    filtro2 = Filter(individuo)
    output2 = filtro2.filter(input2)

    #print("S1: ", input1.y)
    #print("T1: ", output1.y)

    sum1 = 0
    for a in output1.y:
        sum1 += abs(a) ** 2
    p1 = (1/((2*len(output1.y))-1)) * sum1
    #print("p1: ", p1)

    #print("S2: ", input2.y)
    #print("T2: ", output2.y)

    sum2 = 0
    for a in output2.y:
        sum2 += abs(a) ** 2
    p2 = (1/((2*len(output2.y))-1)) * sum2  
    #print("p2: ", p2)  

    if tipo == 1:
        ff = p1 - p2
        print("pasa bajos: ", ff)
    else:
        ff = p2 - p1
        print("pasa altos: ", ff)

    return ff 


def test(frec,tipo):
    generacion = 0
    fitFinal = obtenerFitness(frec, tipo)
    p = Poblacion()
    fin = Criterio(p, fitFinal, tipo)
    while (fin == None):
        padres = Seleccionar(p, tipo)
        p = Emparejar(padres)
        fin = Criterio(p, fitFinal, tipo)
        generacion += 1
        print(generacion)
    print("SOLUCION: ", fin)
    print("GENERACION: ", generacion)
    return (generacion,fin)


@app.route("/home")
def clientes():
    return render_template("index.html")


@app.route("/entrenar",methods=['POST'])
def entrenar():
    frec = int(request.form['frec'])
    tipo = int(request.form['tipo'])
    
    sol = test(frec,tipo)

    return  redirect(url_for('clientes'))


@app.route("/probar",methods=['POST'])
def probar():
    global arreglo
    padres = int(request.form['padre'])
    criterio = int(request.form['fin'])
    f = request.files['archivo']
    f.save(os.path.join("./archivo", "archivo.csv"))
    data = pd.read_csv(os.path.join("./archivo","archivo.csv"))
    arreglo = data.to_numpy()
    
    dateTimeObj = datetime.now()
    fecha = dateTimeObj.strftime("%d %b %Y")
    hora = dateTimeObj.strftime("%H:%M:%S")
    nombre = f.filename
    sol = test(padres,criterio)
    estructura = {
        "fecha": fecha,
        "hora": hora,
        "nombre" : nombre,
        "fin" : criterio,
        "padres" : padres,
        "gens" : sol[0],
        "solucion" : sol[1] }
    
    text = open(os.path.join("./archivo","log.txt"), 'a')
    text.write(",\n"+json.dumps(estructura))
    text.close()
    return  redirect(url_for('mostrar'))


def Poblacion():
    result = []
    for i in range(24):
        result.append(Inicializar())
    #print(result)    
    return result 


def Criterio(po, final, tipo):
    result = None
    fit = []
    for i in range(24):
        pts = Evaluar(po[i], tipo)
        fit.append(pts)
        if pts > 1.0e+100: #if(pts > final):
            return po[i]
    return None
          

def Evaluar(p, tipo):
    global input1, input2
    MAXIMO = 1.5e+100
    print("Evaluando: ", p)
    ff = 0

    filtro1 = Filter(p)
    output1 = filtro1.filter(input1)

    filtro2 = Filter(p)
    output2 = filtro2.filter(input2)

    #print("Y1: ", output1.y)
    #print("Y2: ", output2.y)
    #print("Tam1: ", len(output1.y))
    #print("Tam2: ", len(output2.y))

    #print("Y1: ", output1.y)
    sum1 = 0
    for a in output1.y:
        sum1 += abs(a) ** 2
        #print("a: ", a)
        #print("sum1: ", sum1)
        if sum1 > MAXIMO:
            break
    p1 = (1/((2*len(output1.y))-1)) * sum1

    #print("Y2: ", output2.y)
    sum2 = 0
    for a in output2.y:
        sum2 += abs(a) ** 2
        #print("a: ", a)
        #print("sum2: ", sum2)
        if sum2 > MAXIMO:
            break
    p2 = (1/((2*len(output2.y))-1)) * sum2    

    if tipo == 1:
        ff = p1 - p2
        print("Resultado: ", ff)
    else:
        ff = p2 - p1
        print("Resultado: ", ff)

    return ff 
 

def Inicializar():
    mat = []
    for i in range(18):
        if i == 3 or i == 9 or i == 15:
            mat.append(1)
        else:
            mat.append(random.uniform(-3,3))
    return mat


def Seleccionar(p, tipo):
    #LOS MEJORES 8 PADRES
    resultado = []
    for item in p:
        resultado.append((item,Evaluar(item, tipo)))
    resultado.sort(key= ordenarSegundo )
    resultado = resultado[:12]
    resultado = list(map(getprimero,resultado))
    return resultado


def Emparejar(po):
    h1 = Cruzar(po[0],po[11])
    h2 = Cruzar(po[1],po[10])
    h3 = Cruzar(po[2],po[9])
    h4 = Cruzar(po[3],po[8])
    h5 = Cruzar(po[4],po[7])
    h6 = Cruzar(po[5],po[6])
    h7 = Cruzar(po[0],po[1])
    h8 = Cruzar(po[2],po[3])
    h9 = Cruzar(po[4],po[5])
    h10 = Cruzar(po[6],po[7])
    h11 = Cruzar(po[8],po[9])
    h12 = Cruzar(po[10],po[11])
    po.append(Mutar(h1))
    po.append(Mutar(h2))
    po.append(Mutar(h3))
    po.append(Mutar(h4))
    po.append(Mutar(h5))
    po.append(Mutar(h6))
    po.append(Mutar(h7))
    po.append(Mutar(h8))
    po.append(Mutar(h9))
    po.append(Mutar(h10))
    po.append(Mutar(h11))
    po.append(Mutar(h12))
    return po


def Cruzar(p1,p2):
    hijo = []
    for i in range(18):
        if random.uniform(0,1)>0.5:
            hijo.append(p1[i])
        else:
            hijo.append(p2[i])
    return hijo
    

def Mutar(hijo):
    while True:  
        pos = random.randrange(0,18)
        if pos != 3 and pos != 9 and pos != 15:
            hijo[pos] += random.uniform(-0.5,0.5) 
            break
    return hijo


@app.route("/log")
def mostrar():
    text = open(os.path.join("./archivo","log.txt"), 'r')
    content = "[" + text.read() + "]"
    text.close()
    y = json.loads(content)
    return render_template('historial.html', text=y)
  

if __name__ == "__main__":
    app.run(debug=True)