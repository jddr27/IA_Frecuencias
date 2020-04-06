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
import matplotlib.pyplot as chart
#import conn

   

app = Flask(__name__)

arreglo = ["c0","c1","c2","c3","c4","c5","c6","c7","c8","c9","c10","c11","c12","c13","c14","c15","c16","c17"]
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

    input1.generate(frec - 200, 1.47815634821363e-90, sinoidal=True)
    filtro1 = Filter(individuo) #1.47815634821363e-90
    output1 = filtro1.filter(input1)

    input2.generate(frec + 200, 1.47815634821363e-90, sinoidal=True)
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
    global arreglo
    generacion = 0
    fitFinal = obtenerFitness(frec, tipo)
    p = Poblacion()
    fin = Criterio(p, fitFinal, tipo, 0)
    while (fin == None):
        padres = Seleccionar(p, tipo)
        p = Emparejar(padres)
        fin = Criterio(p, fitFinal, tipo, generacion)
        generacion += 1
        print(generacion)
    print("SOLUCION: ", fin)
    print("GENERACION: ", generacion)
    arreglo = fin
    return generacion


@app.route("/home")
def clientes():
    global arreglo
    return render_template("index.html",sol=arreglo)


@app.route("/entrenar",methods=['POST'])
def entrenar():
    frec = int(request.form['frec'])
    tipo = int(request.form['tipo'])
    
    sol = test(frec,tipo)

    return  redirect(url_for('clientes'))


@app.route("/probar",methods=['POST'])
def probar():
    global arreglo
    f = request.files['archivo']
    f.save(os.path.join("./archivo", "archivo.csv"))
    data = pd.read_csv(os.path.join("./archivo","archivo.csv"))
    entrada = data.to_numpy()
 
    #Asignacion de datos
    datos = [dato[0] for dato in entrada]

    input = Signal()
    input.t = np.linspace(0, 1, len(datos), False)
    input.y = datos
    print("tam input.t",len(input.t)) 
    print("input.t:", input.t)
    print("tam input.y",len(input.y))
    print("input.y: ", input.y)

    output = Signal()
    output.t = np.linspace(0, 1, len(datos), False)
    output.y = datos 
    filtro = Filter(arreglo)

    output = filtro.filterdatos(output)
    print("tam output.t",len(output.t)) 
    print("output.t:", output.t)
    print("tam output.y",len(output.y))
    print("output.y: ", output.y)


    # Generacion de grafica
    fig, (ax1, ax2) = chart.subplots(2, 1, sharex=True)
    ax1.plot(input.t, input.y)
    ax1.set_title('Entrada del filtro')
    ax1.axis([0, 1, -10, 10])
    ax2.plot(output.t, output.y)
    ax2.set_title('Salida del filtro')
    ax2.axis([0, 1, -10, 10])
    ax2.set_xlabel('Tiempo [segundos]')
    chart.tight_layout()
    chart.show()
    return  redirect(url_for('mostrar'))


def Poblacion():
    result = []
    for i in range(24):
        result.append(Inicializar())
    #print(result)    
    return result 


def Criterio(po, final, tipo, gen):
    result = None
    fit = []
    for i in range(24):
        pts = Evaluar(po[i], tipo)
        fit.append(pts)
        if(pts > final) and (gen > 10):
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
    return render_template('historial.html', text="Archivo generado")
  

if __name__ == "__main__":
    app.run(debug=True)