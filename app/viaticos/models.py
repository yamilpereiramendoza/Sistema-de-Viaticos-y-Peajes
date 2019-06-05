# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from app.empleado.models import empleado,Secretaria
from django.db import models
from django.db.models.signals import pre_save
from django.utils.text import slugify
import datetime
import random
from django.core.urlresolvers import reverse
from django.core import validators
from .validators import validate_ncontrol

class Tipo_viatico(models.Model):
    Tipo_Viajante=models.CharField(max_length=50)
    def __str__(self):
        return '{}'.format(self.Tipo_Viajante)
    class Meta:
        permissions=(            
            ("Ver_list_tipo_viatico","Ver Tipo viatico"),                     
        )

class Monto(models.Model):
    Nombre=models.CharField(max_length=50)
    Cantidad=models.IntegerField()
    identificacion=models.IntegerField()
    valido=models.IntegerField()
    Tipo_viatico=models.ForeignKey(Tipo_viatico, null=True,blank=True,on_delete=models.CASCADE)
    def __str__(self):
        bs=""        
        if self.identificacion == 1:
                bs=str(self.Cantidad)+" Bs."
        else:
                bs=str(self.Cantidad)+" $."
        return '{} '' {}'.format(self.Nombre,bs)

    class Meta:
        permissions=(            
            ("Ver_list_monto","Ver Monto"),                     
        )

class DescripcionSecre(models.Model):
    descripcion=models.TextField(max_length=500,null=True,blank=True)
class SecresubSecre(models.Model):
    ue=models.IntegerField()
    prog=models.IntegerField()
    proy=models.IntegerField()
    act=models.IntegerField()
    descripcion=models.ForeignKey(DescripcionSecre, null=True,blank=True,on_delete=models.CASCADE)
    gestion=models.IntegerField()


class viaticodiario(models.Model):
    cod_u=models.IntegerField()
    id_solicitante=models.IntegerField(null=True,blank=True)
      
    Monto_pagado=models.FloatField() #importe
    RC_IVA=models.FloatField()
    Liquido_pagable=models.FloatField()
    pasaje=models.FloatField(null=True,blank=True,default=0)
    peaje=models.FloatField(null=True,blank=True,default=0)
    Extra=models.FloatField(null=True,blank=True,default=0)  # otro
    totalC=models.FloatField()
    
    cantidad_dias_fuera_pais=models.IntegerField(null=True,blank=True)

    resolucion=models.NullBooleanField(null=True,blank=True,default=False)
    cambio_moneda=models.FloatField(null=True,blank=True)

    ue=models.IntegerField()
    prog=models.IntegerField()
    act=models.IntegerField()
    proy=models.IntegerField(null=True,blank=True,default=0)

    fecha_salida=models.DateField(null=True,blank=True)
    fecha_legada=models.DateField(null=True,blank=True)
    horaSalida=models.TimeField(null=True,blank=True)
    horallegada=models.TimeField(null=True,blank=True)
    fechav=models.CharField(max_length=40)
    calculohora=models.CharField(max_length=40,null=True,blank=True)
    dias=models.FloatField(null=True,blank=True)
    timestamp=models.DateField(null=True,blank=True)
    actualizado =models.DateTimeField(auto_now_add=False,auto_now=True,null=True,blank=True)
    slug=models.SlugField(null=True,blank=True)

    encargado=models.CharField(max_length=20)
    lugar=models.CharField(max_length=70)
    ncontrol=models.CharField(max_length=20)
    estado=models.CharField(max_length=10,null=True,blank=True,default=1)
    obs=models.TextField(max_length=500,null=True,blank=True)

    centralizador=models.IntegerField(null=True,blank=True,default=0)

    solicitante=models.ForeignKey(empleado,null=True,blank=True,on_delete=models.CASCADE)
    monto=models.ForeignKey(Monto,null=True,blank=True,on_delete=models.CASCADE)
    tipo_viatico=models.ForeignKey(Tipo_viatico,null=True,blank=True,on_delete=models.CASCADE)
    secretaria=models.ForeignKey(Secretaria,null=True,blank=True,on_delete=models.CASCADE)
    class Meta:
        permissions=(            
            ("Centralizar","Ver Centralizador"),
            ("Reportes_Centralizar","Reportes Centralizador"),  
            ("Reportes","Reportes"),
            ("Realizar_reportes_viaticos","Reportes Viaticos"),
            ("Realizar_reportes_servidor","Reportes Servidor Publico"),
            ("Busquedas","Busquedas"),
            ("Busquedas_viaticos","Busquedas Viaticos"),
            ("Busquedas_servidor","Busquedas Servidor Publico"),           
        )
    
class OtrosViajes(models.Model):

    slug_viaticos=models.SlugField(null=True,blank=True)

    fecha_inicial_frontera=models.DateField(null=True,blank=True)
    fecha_llegada_frontera=models.DateField(null=True,blank=True)
    horaSalida_frontera=models.TimeField(null=True,blank=True)
    horallegada_frontera=models.TimeField(null=True,blank=True)
    lugar_frontera=models.CharField(max_length=70,null=True,blank=True)
    fechav_frontera=models.CharField(max_length=40,null=True,blank=True)
    calculohora_frontera=models.CharField(max_length=40,null=True,blank=True)
    dias_frontera=models.FloatField(null=True,blank=True)

    fecha_inicial_urbana=models.DateField(null=True,blank=True)
    fecha_llegada_urbana=models.DateField(null=True,blank=True)
    horaSalida_urbana=models.TimeField(null=True,blank=True)
    horallegada_urbana=models.TimeField(null=True,blank=True)
    lugar_urbana=models.CharField(max_length=70,null=True,blank=True)
    fechav_urbana=models.CharField(max_length=40,null=True,blank=True)
    calculohora_urbana=models.CharField(max_length=40,null=True,blank=True)
    dias_urbana=models.FloatField(null=True,blank=True)

    fecha_inicial_rural=models.DateField(null=True,blank=True)
    fecha_llegada_rural=models.DateField(null=True,blank=True)
    horaSalida_rural=models.TimeField(null=True,blank=True)
    horallegada_rural=models.TimeField(null=True,blank=True)
    lugar_rural=models.CharField(max_length=70,null=True,blank=True)
    fechav_rural=models.CharField(max_length=40,null=True,blank=True)
    calculohora_rural=models.CharField(max_length=40,null=True,blank=True)
    dias_rural=models.FloatField(null=True,blank=True)
    tipos_viajante=models.IntegerField(null=True,blank=True)
def create_slug(instance,new_slug=None):
    date = datetime.date.today()
    numero_control='%s-%s'%(listaAleatorios(10),instance.ncontrol)
    slug=u'%s-%s' % (slugify(numero_control),slugify(date.year))
    if new_slug is not None:
        slug=new_slug
    qs=viaticodiario.objects.filter(slug=slug).order_by("-1")
    exists=qs.exists()
    
    if exists:
        slug="%s-%s-%s"%(slug,date.year,qs.first().id)
        return create_slug(instance,new_slug=new_slug)
    return slug

def pre_save_post_receiver(sender,instance,*args,**kwargs):
    if not instance.slug:
        instance.slug=create_slug(instance)

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

pre_save.connect(pre_save_post_receiver,sender=viaticodiario)

