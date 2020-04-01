from flask import Flask, render_template,  redirect, url_for, escape, request
import json
from datetime import datetime
import sys
import os
import pandas as pd
import numpy as np
import random
#import conn

   

app = Flask(__name__)

arreglo = []

def ordenarSegundo(val):
    return val[1]


def getprimero(val):
    return val[0]


def obtenerFitness(frec):
    ff = 0 * frec
    return ff 


def test(frec,tipo):
    generacion = 0
    fitFinal = obtenerFitness(frec)
    p = Poblacion()
    fin = Criterio(p, fitFinal)
    while (fin == None):
        padres = Seleccionar(p,1)
        p = Emparejar(padres)
        fin = Criterio(p, fitFinal)
        generacion += 1
        #print(generacion)
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


def Criterio(po, final):
    result = None
    fit = []
    for i in range(24):
        pts = Evaluar(po[i])
        fit.append(pts)
        if(pts < final):
            return po[i]
    return None
          

def Evaluar(p):
    nc = 0
    error = 0 
    print("Evaluando:  ", p)
    for a in arreglo:
        nc = p[0] * a[0] +  p[1] * a[1] + p[2] * a[2]
        error += (a[3] - nc)**2  
    error *= 1/len(arreglo)
    print("Resultado :" , error)
    return error 


def Inicializar():
    mat = []
    for i in range(18):
        if i == 3 or i == 9 or i == 15:
            mat.append(1)
        else:
            mat.append(random.uniform(-3,3))
    return mat


def Seleccionar(p):
    #LOS MEJORES 8 PADRES
    resultado = []
    for item in p:
        resultado.append((item,Evaluar(item)))
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
    while:  
        pos = random.randrange(0,18)
        if pos != 3 or pos != 9 or pos != 15:
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