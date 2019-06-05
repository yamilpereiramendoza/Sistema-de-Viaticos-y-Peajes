import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','Viatico.settings')
import django
django.setup()

import random

from datetime import datetime,date
from django.contrib.auth.models import User
from app.viaticos.models import viaticodiario

'''from faker import Faker
fakegen=Faker()
fake_name=fakegen.name()

fake_lastname=fakegen.last_name()
fake_email=fakegen.email()
fake_number=fakegen.phone_number()

def generate_fake(N=50):
        i = 1
        while i <= N:
                user = User.objects.get_or_create(password='yamilpereira',last_login='2018-11-12 20:00:00-04',is_superuser='f',username=fake_name,first_name=fake_name,last_name=fake_lastname,email=fake_email,is_staff='f',is_active='t',date_joined='2018-11-13 10:22:26-04') 
                i+=1'''
#       s=Departamento.objects.get_or_create(departamento=random.choice(departamento))[0]
'''
16,72,74,75,73,5,62,43,41,44,45,53,57,58,38,40,39,52,91,90,89,85,84,63,49,50,51,86,20,21
22,23,46,54,55,26,24,31,25,71,66,67,47,70,77,59,11,4,7,10,9,12,56,1,17,2,37,3,6,42
92,93,87,116,102,101,15,98,107,108,88,82,83,109,81,28,115,105,29,48,27,69,68,60,103,79,80,30,104,100
94,95,96,36,8,15,18,19,65,32,33,34,61,64,78,97,14,113,111,110,106,112,114
151,150,142,123,140,138,146,145,144,143,117,124,125,126,139,127,131,137,130,148,149,119,122,118,121,120,133,132,136,134
186,183,182,184,152,176,177,178,179,175,158,157,154,162,153,174,185,129,173,155,13,161,171,172,160,159,170,169,168,167

'''

letranumero=235

numero_control=[92,93,87,116,102,101,15,98,107,108,88,82,83,109,81,28,115,105,29,48,27,69,68,60,103,79,80,30,104,100]
date = datetime.now()

def cantidad_viaticos():
        cont=0
        for x in xrange(len(numero_control)):
                cont=cont+1
        print(cont)
def buscar():
        date = datetime.now()
        cont=0
        for x in xrange(len(numero_control)):                
                numero='%s-%s'%(numero_control[x],date.year)                
                #print(numero)
                viaticodiario.objects.filter(slug=numero).update(centralizador=letranumero)
                if viaticodiario.objects.filter(slug=numero).exists():                        
                        cont=cont+1
                else:
                        print('%s %s'%("No existe el =",numero))
        print(cont)     
def mostrar_todo(num):
        resultado=[]
        pasaje=0
        peaje=0
        importe=0
        rciva=0
        liqpagable=0
        totalcancelar=0
        #viatico=viaticodiario.objects.filter(timestamp__year=(date.year)-1).distinct('centralizador')
        #for vis in viatico:
        ViaticoControl=viaticodiario.objects.filter(centralizador=num,timestamp__year=(date.year)).order_by('ue','prog')                                        
        if ViaticoControl.exists():
                for vis in ViaticoControl:
                        resultado.append({
                                "ue":vis.ue,
                                "prog":vis.prog,
                                "act":vis.act,
                                "proy":vis.proy
                        })
                no_repetidos = []
                monto_agrupacion_secre=[]
                for item in resultado:
                        if item not in no_repetidos:
                                no_repetidos.append(item)
                for item in ViaticoControl:
                        print('%s %s %s %s %s %s %s %s %s %s %s %s %s %s'%(" N.Control = ",item.ncontrol," pasaje= ",item.pasaje, "peaje= ",item.peaje," importe= ",item.Monto_pagado," rciva=",item.RC_IVA," Liq pagable= ",item.Liquido_pagable," totalcancelar =",item.totalC))                        
                        pasaje=pasaje+item.pasaje
                        peaje=peaje+item.peaje
                        importe=importe+item.Monto_pagado
                        rciva=rciva+item.RC_IVA
                        liqpagable=liqpagable+item.Liquido_pagable
                        totalcancelar=totalcancelar+item.totalC
        print('%s %s %s %s %s %s %s %s %s %s %s %s'%(" pasaje= ",pasaje, "peaje= ",peaje," importe= ",importe," rciva=",rciva," Liq pagable= ",liqpagable," totalcancelar =",totalcancelar))
        via=viaticodiario.objects.filter(centralizador=num).order_by('ue')
        print(via.count())
        for x in via:                
                print('%s %s %s %s %s %s %s %s %s %s '%(" ue= ",x.ue, "prog= ",x.prog," act= ",x.act," proy=",x.proy," Numero control= ",x.ncontrol))


def listaAleatorios(n):
        lista = ""
        cont=0        
        while cont < n:
                if cont == n-1:
                        lista =lista+(letras()+(str(numeros())))
                else:
                        lista =lista+(letras()+(str(numeros())))+"-"
                cont=cont+1                
        return lista
def numeros():
        return random.randint(1,9)
def letras():        
        letras=("a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z")
        return random.choice(letras)

SIMBOLOS_TRANSFORMADOS = "0123456789abcdefghijklmnopqrstuvwxyz" 
SIMBOLOS_ORIGINALES = "abcdefghijklmnopqrstuvwxyz0123456789"
def encriptacion (mensaje):
    mensaje_encriptado = ""
    for caracter in mensaje:
        i = SIMBOLOS_ORIGINALES.find(caracter)
        mensaje_encriptado += SIMBOLOS_TRANSFORMADOS[i]
    i = 0
    primeros_caracteres = ""
    ultimos_caracteres = ""
    for caracter in mensaje_encriptado:
        if i < 3:
            primeros_caracteres += caracter
        else:
            ultimos_caracteres += caracter
        i += 1
    mensaje_encriptado = ultimos_caracteres + primeros_caracteres
    return mensaje_encriptado
def desencriptar (mensaje):
    ultimos_caracteres = ""
    primeros_caracteres = ""
    mensaje_encriptado = ""
    i = 0
    for caracter in mensaje:
        if i <= len(mensaje) - 4:
            ultimos_caracteres += caracter
        else:
            primeros_caracteres += caracter
        i += 1
    mensaje = primeros_caracteres + ultimos_caracteres
    for caracter in mensaje:
        i = SIMBOLOS_TRANSFORMADOS.find(caracter)
        mensaje_encriptado += SIMBOLOS_ORIGINALES[i]
    return mensaje_encriptado

if __name__=='__main__':
    
    # add_school(20)
    #cantidad_viaticos()
    #buscar()
    #mostrar_todo(235)
        mensaje="123213"
        print(encriptacion(mensaje))
        print(desencriptar(mensaje))
   
        #aleatorios=listaAleatorios(10)
        #print(aleatorios)         

    


