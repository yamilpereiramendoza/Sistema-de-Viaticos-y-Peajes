# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
class Secretaria(models.Model):
    nombreS=models.CharField(max_length=100)
    numeroS=models.DecimalField(max_digits=5,decimal_places=0)
    def __str__(self):
        return '{}'.format(self.nombreS)
class SaldosTotales(models.Model):
    MontoDesignado=models.BigIntegerField(null=True,blank=True)
    secretaria=models.ForeignKey(Secretaria,null=True,blank=True,on_delete=models.CASCADE)

class Unidad(models.Model):
    unidad=models.DecimalField(max_digits=5,decimal_places=0)
    def __str__(self):
        return '{}'.format(self.unidad)
class empleado(models.Model):
    cod_usu=models.IntegerField()
    nombre=models.CharField(max_length=30)
    apaterno=models.CharField(max_length=30,null=True,blank=True)
    amaterno=models.CharField(max_length=30,null=True,blank=True)
    ci=models.IntegerField()
    ue=models.ForeignKey(Unidad,null=True,blank=True,on_delete=models.CASCADE)
    secretaria=models.ForeignKey(Secretaria,null=True,blank=True,on_delete=models.CASCADE)
    fechaReg=models.DateField(null=True,blank=True)
    bcontrol=models.BigIntegerField(null=True,blank=True)
    