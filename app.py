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


def test(padres,crit):
    generacion = 0
    p = Poblacion()
    fin = Criterio(p,crit,generacion)
    while (fin == None):
        padres = Seleccionar(p,1)
        p = Emparejar(padres)
        fin = Criterio(p,crit,generacion)
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
    for i in range(16):
        result.append(Inicializar())
    #print(result)    
    return result 

def Criterio(po,i,generacion):
    result = None
    fit = []
    fitnesFinal = 15
    generacionFinal = 100
    fitnesPromedio = 35
    #Primer fitnes en cumplir criterio
    if i == 1:
        for i in range(16):
            pts = Evaluar(po[i])
            fit.append(pts)
            if(pts < fitnesFinal):
                return po[i]
    # GENEACION MAXIMA
    if i==2:
        if generacion >= generacionFinal:
            return po[0]
    # Fitnes Promedio
    promedio = 0
    if i==3:
        for i in range(16):
            pts = Evaluar(po[i])
            promedio += pts
        promedio /= len(po)    
        print("PROMEDIO :" , promedio)
        if promedio < fitnesPromedio:
            return po[0]
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
    for i in range(8):
        mat.append(random.uniform(-1,1))
    return mat


def Seleccionar(p,i):
    #LOS MEJORES 8 PADRES
    resultado = []
    if(i == 1):
        for item in p:
            resultado.append((item,Evaluar(item)))
        resultado.sort(key= ordenarSegundo )
        resultado = resultado[:8]
        resultado = list(map(getprimero,resultado))
        return resultado
    #OCho elegidos al azar
    if(i == 2):
        lista = []
        while len(lista) < 8:
            numrandom = random.randint(0,16)
            if numrandom not in lista:
                lista.append(numrandom)
                resultado.append(p[numrandom])
        return resultado
    #Los mejores padres tienen mas probabilidad de ser elegidos 70% mejores 80% peores
    if(i == 3):
        for item in p:
            resultado.append((item,Evaluar(item)))
        resultado.sort(key= ordenarSegundo )
        mejores = resultado[:8]
        mejores = list(map(getprimero,resultado))
        peores = resultado[8:]
        peores = list(map(getprimero,resultado))
        # hijo[0] = p1[0] if random.uniform(0,1)>0.5 else p2[0]
        for i in range(8):
            resultado[i] = mejores[i] if random.uniform(0,1)>0.70 else peores[i]
        return resultado    
    return None

def Emparejar(po):
    h1 = Cruzar(po[0],po[7])
    h2 = Cruzar(po[1],po[6])
    h3 = Cruzar(po[2],po[5])
    h4 = Cruzar(po[3],po[4])
    h5 = Cruzar(po[0],po[1])
    h6 = Cruzar(po[2],po[3])
    h7 = Cruzar(po[4],po[5])
    h8 = Cruzar(po[6],po[7])
    po.append(Mutar(h1))
    po.append(Mutar(h2))
    po.append(Mutar(h3))
    po.append(Mutar(h4))
    po.append(Mutar(h5))
    po.append(Mutar(h6))
    po.append(Mutar(h7))
    po.append(Mutar(h8))
    return po

def Cruzar(p1,p2):
    hijo = [-1,-1,-1]
    hijo[0] = p1[0] if random.uniform(0,1)>0.5 else p2[0]
    hijo[1] = p1[1] if random.uniform(0,1)>0.5 else p2[1]
    hijo[2] = p1[2] if random.uniform(0,1)>0.5 else p2[2]
    return hijo
    

def Mutar(hijo):
    pos = random.randrange(0,3)
    hijo[pos] += random.uniform(-0.3,0.3) 
    return hijo

@app.route("/log")
def mostrar():
    text = open(os.path.join("./archivo","log.txt"), 'r')
    content = "[" + text.read() + "]"
    text.close()
    y = json.loads(content)
    return render_template('historial.html', text=y)

#@app.route("/ingresoCliente",methods=['POST'])
#def ingresoclientes(): 
#    nit = request.form['nit']
#    usuario = request.form['username']
#    monto = request.form['monto']
#    direccion = request.form['direccion']
#    telefono = request.form['telefono']
#    email = request.form['email']
#    regimen = request.form['regimen']
#    saldo = request.form['saldo']
#    sql = "INSERT INTO cliente (NIT,NOMBRE,MENSUAL,DIRECCION,TELEFONO,EMAIL,REGIMEN,SALDO) VALUES(%i,'%s',%f,'%s','%s','%s','%s',%f)" % (int(nit),usuario,float(monto),direccion,telefono,email,regimen,float(saldo))
#    run_query(sql)
#    return  redirect(url_for('clientes'))
  

if __name__ == "__main__":
    app.run(debug=True)


