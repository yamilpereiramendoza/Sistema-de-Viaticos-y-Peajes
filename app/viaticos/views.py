# encoding: utf-8
from __future__ import unicode_literals
from django.shortcuts import render,redirect,get_object_or_404,render_to_response
from django.template import RequestContext

from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import permission_required
from django.views.generic import View,TemplateView,DetailView,DeleteView,CreateView
from .reportes import ReportsView,BusquedaView
from .base_excel import Base_Excel
from .base_viatico import BaseViatico
from app.empleado.models import empleado,Secretaria,SaldosTotales
from django.contrib.auth.models import User
from .models import viaticodiario,Monto,DescripcionSecre,SecresubSecre,Tipo_viatico,OtrosViajes
from .forms import viaticodiarioFormModificado,otrosform
import json
from django.http import HttpResponseRedirect,HttpResponse,JsonResponse
from django.http import Http404
from django.contrib import messages
from django.urls.base import reverse
from django.core.urlresolvers import reverse_lazy
from django.db.models import Q
from django.core import serializers
from datetime import datetime,date
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

import urllib2 

# todo de aca es para excel
from PIL import Image
from io import BytesIO
from django.conf import settings
import os
import random
import xlwt
from xlwt import Workbook
from xlwt import Font
from xlwt import XFStyle
from xlwt import Borders

# todo de aca para reportlab
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.pagesizes import landscape

from reportlab.platypus import Table, TableStyle, Spacer
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.pagesizes import A3, A4, landscape, portrait
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from .BaseReport import *
# fin de reportlab 
from dateutil.relativedelta import relativedelta 

from django.contrib.auth.decorators import login_required


# GESTION DE VIATICOS

class ViaticoListView(TemplateView):
        template_name = 'viaticos/index.html'
        date = datetime.now()
        def get_context_data(self, *args, **kwargs):
                context =  super(ViaticoListView, self).get_context_data(**kwargs)
                via_ano=viaticodiario.objects.filter(timestamp__year=self.date.year)
                via = viaticodiario.objects.filter(
                                timestamp__day=self.date.day,
                                timestamp__month=self.date.month,
                                timestamp__year=self.date.year,
                                estado=1).order_by('-centralizador','ue','prog','act')
                #via=viaticodiario.objects.all()
                paginator = Paginator(via,15)
                page = self.request.GET.get('page')
                try:
                        viatic = paginator.page(page)
                except PageNotAnInteger:                       
                        viatic = paginator.page(1)
                except EmptyPage:                       
                        viatic = paginator.page(paginator.num_pages)

                context['viatico'] = viatic
                context['viaticolen'] = len(via)        
                context['via_ano'] = len(via_ano)
                return context
        
class Reporte_Excel_Via_Todo_View(Base_Excel):
        date = datetime.now()
        model=viaticos=viaticodiario.objects.filter(
                timestamp__year=date.year).order_by('ue','prog','act')                     
        preparandojson=[]
        meses_container=""
        tamano=7
        monto_agrupacion_secre=[]
        uno=True
        fini_total=0
        def __init__(self):
                # header , result_style
                self.begin(nombre = 'ViaticoTodo',header=8,result=9)
	
        def cabecera(self,worksheet,centralizacion=None):
                meseslist=['ENERO','FEBRERO','MARZO','ABRIL','MAYO','JUNIO','JULIO','AGOSTO','SEPTIEMBRE','OCTUBRE','NOVIEMBRE','DICIEMBRE']                  
                resultado=[]
                meses=[]
                self.meses_container=""
                self.monto_agrupacion_secre=[]
                no_repetidos_meses=[]                
                no_repetidos = []
                
                ViaticoControl=viaticodiario.objects.filter(centralizador=centralizacion,timestamp__year=self.date.year).order_by('ue','prog','act')                                                      
                if ViaticoControl.exists():
                        for vis in ViaticoControl:
                                resultado.append({
                                        "ue":vis.ue,
                                        "prog":vis.prog,
                                        "act":vis.act,
                                        "proy":vis.proy
                                })

                        for vis in ViaticoControl:                                        
                                meses.append({
                                        "meses":datetime.strptime(str(vis.fecha_salida),'%Y-%m-%d').strftime('%m')                                            
                                })  
                        
                        for item in resultado:
                                if item not in no_repetidos:
                                        no_repetidos.append(item)

                        for item in meses:
                                if item not in no_repetidos_meses:
                                        no_repetidos_meses.append(item)
                        
                        
                        Nombre=""                                                                  
                        for item in no_repetidos:                                        
                                NombreSecre=SecresubSecre.objects.filter(ue=item["ue"],prog=item["prog"],act=item["act"])                                
                                for secre in NombreSecre:
                                        Nombre=secre.descripcion.descripcion  
                                        break
                                if Nombre == "":                                
                                        Nombre="ADVERTENCIA NO EXISTE ESA SECRETARIA"
                                self.monto_agrupacion_secre.append({                                                
                                        "secreatria":Nombre                                
                                })
                        
                        for va in xrange(len(no_repetidos_meses)):                                        
                                numero=no_repetidos_meses[va]["meses"]
                                self.meses_container=self.meses_container+meseslist[int(numero)-1]
                                if va != len(no_repetidos_meses)-1:
                                        self.meses_container=self.meses_container+", "
                        self.meses_container=self.meses_container+"/"+str(self.date.year)
                        #self.preparandojson.append({                                   
                        #        "Secretarias" : self.monto_agrupacion_secre,
                        #        "meses":self.meses_container                                   
                        #})
                        #self.monto_agrupacion_secre
                        #meses_container  
                        #resultado=[]
                        #no_repetidos=[]
                        #self.monto_agrupacion_secre=[]

                        #no_repetidos_meses=[]
                        #meses=[]
                        #meses_container=""  
                                                                 
	def tabla(self,worksheet,centralizador=None):
                row_num = self.tamano                
                inicio_total=row_num
                if self.uno:
                        inicio_total=inicio_total+2   
                cont=9
                worksheet.col(0).width = 8 * 90
                worksheet.col(1).width = 8 * 840   
                worksheet.col(2).width = 8 * 360
                worksheet.col(3).width = 8 * 220
                worksheet.col(4).width = 8 * 230
                worksheet.col(5).width = 8 * 250
                worksheet.col(6).width = 8 * 250
                worksheet.col(7).width = 8 * 350
                worksheet.col(8).width = 8 * 500
                worksheet.col(9).width = 8 * 170
                worksheet.col(10).width = 8 * 160
                worksheet.col(11).width = 8 * 160
                worksheet.col(12).width = 8 * 160
                worksheet.col(13).width = 8 * 510
                worksheet.col(14).width = 8 * 360
                worksheet.col(15).width = 8 * 540
                worksheet.col(16).width = 8 * 580
                worksheet.col(17).width = 8 * 240
                worksheet.col(18).width = 8 * 240
                worksheet.col(19).width = 8 * 500
                worksheet.col(20).width = 8 * 1150
                #worksheet.col(20).width = 8 * 200

                alignmenttitle = xlwt.Alignment()
                alignmenttitle.horz = xlwt.Alignment.HORZ_CENTER

                title_via = Font()        
                title_via.name = 'Arial'
                title_via.height = 20 * 8
                title_via.bold = False
                title_viatico = XFStyle() 
                title_viatico.font = title_via

                title_subTitle = Font()
                title_subTitle.name = 'Calibri'
                
                title_subTitle.height = 20 * 8
                title_subTitle.bold = False

                title_subTi = XFStyle() 
                title_subTi.font = title_subTitle
                title_subTi.alignment=alignmenttitle

                fecha_lic = Font()        
                fecha_lic.name = 'Arial Narrow'
                fecha_lic.height = 20 * 9
                fecha_lic.bold = True
                fecha_lic.colour_index = xlwt.Style.colour_map['red']

        
                fecha_licencia = XFStyle() 
                fecha_licencia.font = fecha_lic
                fecha_licencia.alignment=alignmenttitle

                title_mes = Font()        
                title_mes.name = 'Calibri'
                title_mes.height = 20 * 9
                title_mes.bold = True

                title_mestico = XFStyle() 
                title_mestico.font = title_mes
                title_mestico.alignment=alignmenttitle

                title_Secre = Font()        
                title_Secre.name = 'Calibri'
                title_Secre.height_mismatch = True
                title_Secre.height = 20 * 8
                title_Secre.bold = False

                al = xlwt.Alignment()
                al.wrap = xlwt.Alignment.WRAP_AT_RIGHT
                al.horz = xlwt.Alignment.HORZ_CENTER

                title_Secretico = XFStyle() 
                title_Secretico.font = title_Secre
                title_Secretico.alignment=al

                secret=""
                for mo in xrange(len(self.monto_agrupacion_secre)):
                        secret=secret+self.monto_agrupacion_secre[mo]["secreatria"]
                        if mo != len(self.monto_agrupacion_secre)-1:
                                secret=secret+", "                                        

                worksheet.write_merge((row_num-7), (row_num-7), 1, 1,'Gobierno  Autónomo Dptal, de Potosí',title_viatico)
                worksheet.write_merge((row_num-6), (row_num-6), 1, 1,'Unidad de Contabilidad',title_viatico)
                worksheet.write_merge((row_num-5), (row_num-5), 1, 12,'DETALLE DE PASAJES Y VIÁTICOS AL PERSONAL CORRESPONDIENTE AL MES DE:',title_subTi)
                worksheet.write_merge((row_num-4), (row_num-4), 1, 12,str(self.meses_container),title_mestico)
                pala="SECRETARIA DEPARTAMENTAL DE LA MADRE TIERRA, SECRETARIA DEPARTAMENTAL DE LA MADRE TIERRA, SECRETARIA DEPARTAMENTAL DE LA MADRE TIERRA, SECRETARIA DEPARTAMENTAL DE LA MADRE TIERRA, SECRETARIA DEPARTAMENTAL DE LA MADRE TIERRA, SECRETARIA DEPARTAMENTAL DE LA MADRE TIERRA"
                tama=0
                secre=0
                cero=True
                one=True
                two=True
                tree=True
                
                if cero and len(secret) <= 150:
                        print("ENtro 150")
                        tama=0
                        secre=3
                        one=False
                        two=False
                        tree=False
                if one and len(secret) <= 300:
                        #print("ENtro 350")
                        tama=1
                        secre=2
                        two=False
                        tree=False
                if two and len(secret) <= 400:
                        #print("ENtro 400")
                        tama=2
                        secre=1
                        tree=False
                if tree and len(secret) <= 600:
                        #print("ENtro 600")
                        tama=3
                        secre=0
                       
      
                worksheet.write_merge((row_num-3), (row_num-secre), 1, 12,unicode(str(secret)),title_Secretico)
                row_num = row_num + tama 
                worksheet.write_merge((row_num-2), (row_num-2), 1, 12,'INFORME CONT,  Nº  '+str(centralizador),title_mestico)

                worksheet.write_merge((row_num-1),(row_num), 0, 0, 'N', self.header_style)
                worksheet.write_merge((row_num-1),(row_num), 1, 1, 'NOMBRE Y APELLIDO', self.header_style)
                worksheet.write_merge((row_num-1),(row_num), 2, 2, 'C.I.', self.header_style)
                worksheet.write_merge((row_num-1),(row_num), 3, 3, 'PASAJE', self.header_style)
                worksheet.write_merge((row_num-1),(row_num), 4, 4, 'PEAJE', self.header_style)

                worksheet.write_merge((row_num-1),(row_num-1), 5, 7,' VIATICOS',self.header_style)
                worksheet.write_merge((row_num),(row_num), 5, 5, 'IMPORTE', self.header_style)
                worksheet.write_merge((row_num),(row_num), 6, 6, 'RC-IVA', self.header_style)
                worksheet.write_merge((row_num),(row_num), 7, 7, 'LIQ. PAGABLE', self.header_style)
                worksheet.write_merge((row_num-1),(row_num), 8, 8, 'TOTAL A CANCELAR', self.header_style)

                worksheet.write_merge((row_num-1), (row_num-1), 9, 12,' CONTROL DE PRESUPUESTO',self.header_style)
                worksheet.write_merge((row_num),(row_num), 9, 9, 'U.E.', self.header_style)
                worksheet.write_merge((row_num),(row_num), 10, 10, 'PROG.', self.header_style)
                worksheet.write_merge((row_num),(row_num), 11, 11, 'PROY.', self.header_style)
                worksheet.write_merge((row_num),(row_num), 12, 12, 'ACT.', self.header_style)

                worksheet.write_merge((row_num-1),(row_num), 13, 13, 'N DE CUENTA', self.header_style)

                worksheet.write_merge((row_num-1),(row_num), 14, 14, 'N DE CONTROL', self.header_style)
                worksheet.write_merge((row_num-1),(row_num), 15, 15, 'LUGAR', self.header_style)
                worksheet.write_merge((row_num-1),(row_num), 16, 16, 'FECHA VIAJE', self.header_style)

                worksheet.write_merge((row_num-1),(row_num-1), 17, 18,'HORAS',self.header_style)
                worksheet.write_merge((row_num),(row_num), 17, 17, 'SALIDA', self.header_style)
                worksheet.write_merge((row_num),(row_num), 18, 18, 'LLEGADA.', self.header_style)

                worksheet.write_merge((row_num-1),(row_num), 19, 19, 'CALCULO DE TIEMPO', self.header_style)
                worksheet.write_merge((row_num-1),(row_num), 20, 20, 'SECRETARIA', self.header_style)
                worksheet.write_merge((row_num-1),(row_num), 21, 21, 'OBSERVACIONES', self.header_style)
                viaticoss=viaticodiario.objects.filter(centralizador=centralizador,timestamp__year=self.date.year).order_by('ue','prog','act')
                #viaticoss=viaticodiario.objects.all()
                #self.fini_total=self.fini_total+(tama+1)+7
                self.fini_total=row_num
                print(row_num)
                n=0
                for viatico in viaticoss:
                        cont=cont+1
                     
                        n=n+1
                        row_num += 1
                        row = [ (n),
                                '%s %s %s'%(viatico.solicitante.nombre.upper(),viatico.solicitante.apaterno.upper(),viatico.solicitante.amaterno.upper()),
                                viatico.solicitante.ci,
                                viatico.pasaje,
                                viatico.peaje,
                                viatico.Monto_pagado,
                                viatico.RC_IVA,
                                viatico.Liquido_pagable,
                                viatico.totalC,
                                viatico.ue,
                                viatico.prog,
                                viatico.proy,
                                viatico.act,
                                unicode(viatico.solicitante.bcontrol),
                                viatico.ncontrol,
                                viatico.lugar,
                                '%s al %s'%((datetime.strptime(str(viatico.fecha_salida),'%Y-%m-%d').strftime('%d-%m')),
                                        (datetime.strptime(str(viatico.fecha_legada),'%Y-%m-%d').strftime('%d-%m-%Y'))),
                                (viatico.horaSalida).strftime('%H:%M'),
                                (viatico.horallegada).strftime('%H:%M'),
                                viatico.calculohora,
                                self.buscarSecre(viatico.ue),
                                viatico.obs]
                        for col_num in range(len(row)):
                                if col_num == 1:
                                        worksheet.write(row_num,col_num, row[col_num],self.result_style)
                                else:                                
                                        if col_num == 3 or col_num == 4 or col_num == 5 or  col_num == 6 or col_num == 7 or col_num == 8:
                                                worksheet.write(row_num,col_num, row[col_num],self.redondeos_style)
                                        else:
                                                worksheet.write(row_num,col_num, row[col_num],self.body_style)
                
 
                

                fila=row_num+1
                worksheet.write(row_num+1,0,"",self.redondeos_style)
                worksheet.write(row_num+1,1,"TOTAL",self.result_style)

         

                worksheet.write(row_num+1,2,"",self.redondeos_style)
                worksheet.write(row_num+1,3,xlwt.Formula('SUM(D%s:D%s)'%(self.fini_total+2,fila)),self.redondeos_style)
                worksheet.write(row_num+1,4,xlwt.Formula('SUM(E%s:E%s)'%(self.fini_total+2,fila)),self.redondeos_style)
                worksheet.write(row_num+1,5,xlwt.Formula('SUM(F%s:F%s)'%(self.fini_total+2,fila)),self.redondeos_style)
                worksheet.write(row_num+1,6,xlwt.Formula('SUM(G%s:G%s)'%(self.fini_total+2,fila)),self.redondeos_style)
                worksheet.write(row_num+1,7,xlwt.Formula('SUM(H%s:H%s)'%(self.fini_total+2,fila)),self.redondeos_style)
                worksheet.write(row_num+1,8,xlwt.Formula('SUM(I%s:I%s)'%(self.fini_total+2,fila)),self.redondeos_style)
                if self.uno:
                        cont=(cont+tama)-1
                else:
                        cont=cont+tama
  
                columns_result=['DESCRIPCION',"VIATICOS","PEAJES","PASAJES","TOTAL","Menos RC-IVA","LIQ. PAGABLE"]       
                
                for col_num in range(len(columns_result)):
                        worksheet.write((row_num+col_num)+3,2, columns_result[col_num],self.result_style)
                                          
                posicion=row_num+5
                worksheet.write_merge(row_num+3, row_num+3,3, 5,'IMPORTES EN BS.',self.result_style)
                worksheet.write_merge(row_num+4, row_num+4,3, 5,xlwt.Formula('SUM(F%s:F%s)'%(self.fini_total+2,fila)),self.redondeos_style)
                worksheet.write_merge(row_num+5, row_num+5,3, 5,xlwt.Formula('SUM(E%s:E%s)'%(self.fini_total+2,fila)),self.redondeos_style)
                worksheet.write_merge(row_num+6, row_num+6,3, 5,xlwt.Formula('SUM(D%s:D%s)'%(self.fini_total+2,fila)),self.redondeos_style)
                worksheet.write_merge(row_num+7, row_num+7,3, 5,xlwt.Formula('SUM(D%s:D%s)'%(posicion,posicion+2)),self.redondeos_style)
                worksheet.write_merge(row_num+8, row_num+8,3, 5,xlwt.Formula('SUM(G%s:G%s)'%(self.fini_total+2,fila)),self.redondeos_style)
                worksheet.write_merge(row_num+9, row_num+9,3, 5,xlwt.Formula('SUM(I%s:I%s)'%(self.fini_total+2,fila)),self.redondeos_style)
                worksheet.write_merge(row_num+7, row_num+7,7, 8,'Lic,  Reyna  Oporto  Mamani',fecha_licencia)
                worksheet.write_merge(row_num+8, row_num+8,7, 8,'TEC. ANALISTA CONTABLE',fecha_licencia)
                worksheet.write_merge(row_num+9, row_num+9,7, 8,'Potosí, 19 de  diciembre de '+str(self.date.year),fecha_licencia)
                
                self.fini_total=self.fini_total+2
                inicio_total=inicio_total+2
                self.tamano=self.tamano+len(columns_result)+1
                if self.uno:
                        self.tamano=cont+9
                        self.tamano=self.tamano+len(columns_result)+1                        
                else:
                        self.tamano=(self.tamano+cont)+1
                self.uno=False
                #for via in self.model:
                #        viaticodiario.objects.filter(slug=via.slug).update(estado=0)                                      
                
	def get(self, request, *args, **kwargs):
                
                viatico=viaticodiario.objects.filter(~Q(centralizador__isnull=True),timestamp__year=self.date.year).distinct('centralizador').order_by('centralizador')
                
                for vis in viatico:                
                        self.cabecera(self.worksheet,vis.centralizador)
                        self.tabla(self.worksheet,vis.centralizador)
                        #break
                self.workbook.save(self.response)
		return self.response
class Reporte_Excel_ViaView(Base_Excel):
        date = datetime.now()
        model=viaticos=viaticodiario.objects.filter(
                timestamp__day=date.day, 
                timestamp__month=date.month, 
                timestamp__year=date.year,estado=1).order_by('-centralizador','ue','prog','act')                     
        preparandojson=[]
        meses_container=""
        tamano=7
        monto_agrupacion_secre=[]
        uno=True
        fini_total=0
        def __init__(self):
                # header , result_style
                self.begin(nombre = 'Viatico',header=8,result=9)
	
        def cabecera(self,worksheet,viatico=None):
                meseslist=['ENERO','FEBRERO','MARZO','ABRIL','MAYO','JUNIO','JULIO','AGOSTO','SEPTIEMBRE','OCTUBRE','NOVIEMBRE','DICIEMBRE']                  
                resultado=[]
                meses=[]
                self.meses_container=""
                self.monto_agrupacion_secre=[]
                no_repetidos_meses=[]                
                no_repetidos = []
                # centralizacion = None
                #ViaticoControl=viaticodiario.objects.filter(centralizador=centralizacion,timestamp__year=self.date.year,estado=1)                                                      
                if viatico.exists():
                        for vis in viatico:
                                resultado.append({
                                        "ue":vis.ue,
                                        "prog":vis.prog,
                                        "act":vis.act,
                                        "proy":vis.proy
                                })

                        for vis in viatico:                                        
                                meses.append({
                                        "meses":datetime.strptime(str(vis.fecha_salida),'%Y-%m-%d').strftime('%m')                                            
                                })  
                        
                        for item in resultado:
                                if item not in no_repetidos:
                                        no_repetidos.append(item)

                        for item in meses:
                                if item not in no_repetidos_meses:
                                        no_repetidos_meses.append(item)
                        
                        
                        Nombre=""                                                                  
                        for item in no_repetidos:                                        
                                NombreSecre=SecresubSecre.objects.filter(ue=item["ue"],prog=item["prog"],act=item["act"])                                
                                for secre in NombreSecre:
                                        Nombre=secre.descripcion.descripcion  
                                        break
                                if Nombre == "":                                
                                        Nombre="ADVERTENCIA NO EXISTE ESA SECRETARIA"
                                self.monto_agrupacion_secre.append({                                                
                                        "secreatria":Nombre                                
                                })
                        
                        for va in xrange(len(no_repetidos_meses)):                                        
                                numero=no_repetidos_meses[va]["meses"]
                                self.meses_container=self.meses_container+meseslist[int(numero)-1]
                                if va != len(no_repetidos_meses)-1:
                                        self.meses_container=self.meses_container+", "
                        self.meses_container=self.meses_container+"/"+str(self.date.year)
                        #self.preparandojson.append({                                   
                        #        "Secretarias" : self.monto_agrupacion_secre,
                        #        "meses":self.meses_container                                   
                        #})
                        #self.monto_agrupacion_secre
                        #meses_container  
                        #resultado=[]
                        #no_repetidos=[]
                        #self.monto_agrupacion_secre=[]

                        #no_repetidos_meses=[]
                        #meses=[]
                        #meses_container=""  
                                                                 
	'''
        def tabla(self,worksheet,centralizador=None):
                row_num = self.tamano                
                inicio_total=row_num
                if self.uno:
                        inicio_total=inicio_total+2   
                cont=9
                worksheet.col(0).width = 8 * 90
                worksheet.col(1).width = 8 * 840   
                worksheet.col(2).width = 8 * 360
                worksheet.col(3).width = 8 * 220
                worksheet.col(4).width = 8 * 230
                worksheet.col(5).width = 8 * 250
                worksheet.col(6).width = 8 * 250
                worksheet.col(7).width = 8 * 350
                worksheet.col(8).width = 8 * 500
                worksheet.col(9).width = 8 * 170
                worksheet.col(10).width = 8 * 160
                worksheet.col(11).width = 8 * 160
                worksheet.col(12).width = 8 * 160
                worksheet.col(13).width = 8 * 510
                worksheet.col(14).width = 8 * 360
                worksheet.col(15).width = 8 * 540
                worksheet.col(16).width = 8 * 580
                worksheet.col(17).width = 8 * 240
                worksheet.col(18).width = 8 * 240
                worksheet.col(19).width = 8 * 500
                worksheet.col(20).width = 8 * 1150
                #worksheet.col(20).width = 8 * 200

                alignmenttitle = xlwt.Alignment()
                alignmenttitle.horz = xlwt.Alignment.HORZ_CENTER

                title_via = Font()        
                title_via.name = 'Arial'
                title_via.height = 20 * 8
                title_via.bold = False
                title_viatico = XFStyle() 
                title_viatico.font = title_via

                title_subTitle = Font()
                title_subTitle.name = 'Calibri'
                title_subTitle.height = 20 * 8
                title_subTitle.bold = False
                title_subTi = XFStyle() 
                title_subTi.font = title_subTitle
                title_subTi.alignment=alignmenttitle

                fecha_lic = Font()        
                fecha_lic.name = 'Arial Narrow'
                fecha_lic.height = 20 * 9
                fecha_lic.bold = True
                fecha_lic.colour_index = xlwt.Style.colour_map['red']

                fecha_licencia = XFStyle() 
                fecha_licencia.font = fecha_lic
                fecha_licencia.alignment=alignmenttitle

                title_mes = Font()        
                title_mes.name = 'Calibri'
                title_mes.height = 20 * 9
                title_mes.bold = True

                title_mestico = XFStyle() 
                title_mestico.font = title_mes
                title_mestico.alignment=alignmenttitle

                title_Secre = Font()        
                title_Secre.name = 'Calibri'
                title_Secre.height_mismatch = True
                title_Secre.height = 20 * 8
                title_Secre.bold = False

                al = xlwt.Alignment()
                al.wrap = xlwt.Alignment.WRAP_AT_RIGHT
                al.horz = xlwt.Alignment.HORZ_CENTER

                title_Secretico = XFStyle() 
                title_Secretico.font = title_Secre
                title_Secretico.alignment=al

                secret=""
                for mo in xrange(len(self.monto_agrupacion_secre)):
                        secret=secret+self.monto_agrupacion_secre[mo]["secreatria"]
                        if mo != len(self.monto_agrupacion_secre)-1:
                                secret=secret+", "                                        

                worksheet.write_merge((row_num-7), (row_num-7), 1, 1,'Gobierno  Autónomo Dptal, de Potosí',title_viatico)
                worksheet.write_merge((row_num-6), (row_num-6), 1, 1,'Unidad de Contabilidad',title_viatico)
                worksheet.write_merge((row_num-5), (row_num-5), 1, 12,'DETALLE DE PASAJES Y VIÁTICOS AL PERSONAL CORRESPONDIENTE AL MES DE:',title_subTi)
                worksheet.write_merge((row_num-4), (row_num-4), 1, 12,str(self.meses_container),title_mestico)
                pala="SECRETARIA DEPARTAMENTAL DE LA MADRE TIERRA, SECRETARIA DEPARTAMENTAL DE LA MADRE TIERRA, SECRETARIA DEPARTAMENTAL DE LA MADRE TIERRA, SECRETARIA DEPARTAMENTAL DE LA MADRE TIERRA, SECRETARIA DEPARTAMENTAL DE LA MADRE TIERRA, SECRETARIA DEPARTAMENTAL DE LA MADRE TIERRA"
                tama=0
                secre=0
                cero=True
                one=True
                two=True
                tree=True
                
                if cero and len(secret) <= 150:
                        print("ENtro 150")
                        tama=0
                        secre=3
                        one=False
                        two=False
                        tree=False
                if one and len(secret) <= 300:
                        #print("ENtro 350")
                        tama=1
                        secre=2
                        two=False
                        tree=False
                if two and len(secret) <= 400:
                        #print("ENtro 400")
                        tama=2
                        secre=1
                        tree=False
                if tree and len(secret) <= 600:
                        #print("ENtro 600")
                        tama=3
                        secre=0
                       
      
                worksheet.write_merge((row_num-3), (row_num-secre), 1, 12,unicode(str(secret)),title_Secretico)
                row_num = row_num + tama 
                worksheet.write_merge((row_num-2), (row_num-2), 1, 12,'INFORME CONT,  Nº  '+str(centralizador),title_mestico)

                worksheet.write_merge((row_num-1),(row_num), 0, 0, 'N', self.header_style)
                worksheet.write_merge((row_num-1),(row_num), 1, 1, 'NOMBRE Y APELLIDO', self.header_style)
                worksheet.write_merge((row_num-1),(row_num), 2, 2, 'C.I.', self.header_style)
                worksheet.write_merge((row_num-1),(row_num), 3, 3, 'PASAJE', self.header_style)
                worksheet.write_merge((row_num-1),(row_num), 4, 4, 'PEAJE', self.header_style)

                worksheet.write_merge((row_num-1),(row_num-1), 5, 7,' VIATICOS',self.header_style)
                worksheet.write_merge((row_num),(row_num), 5, 5, 'IMPORTE', self.header_style)
                worksheet.write_merge((row_num),(row_num), 6, 6, 'RC-IVA', self.header_style)
                worksheet.write_merge((row_num),(row_num), 7, 7, 'LIQ. PAGABLE', self.header_style)
                worksheet.write_merge((row_num-1),(row_num), 8, 8, 'TOTAL A CANCELAR', self.header_style)

                worksheet.write_merge((row_num-1), (row_num-1), 9, 12,' CONTROL DE PRESUPUESTO',self.header_style)
                worksheet.write_merge((row_num),(row_num), 9, 9, 'U.E.', self.header_style)
                worksheet.write_merge((row_num),(row_num), 10, 10, 'PROG.', self.header_style)
                worksheet.write_merge((row_num),(row_num), 11, 11, 'PROY.', self.header_style)
                worksheet.write_merge((row_num),(row_num), 12, 12, 'ACT.', self.header_style)

                worksheet.write_merge((row_num-1),(row_num), 13, 13, 'N DE CUENTA', self.header_style)

                worksheet.write_merge((row_num-1),(row_num), 14, 14, 'N DE CONTROL', self.header_style)
                worksheet.write_merge((row_num-1),(row_num), 15, 15, 'LUGAR', self.header_style)
                worksheet.write_merge((row_num-1),(row_num), 16, 16, 'FECHA VIAJE', self.header_style)

                worksheet.write_merge((row_num-1),(row_num-1), 17, 18,'HORAS',self.header_style)
                worksheet.write_merge((row_num),(row_num), 17, 17, 'SALIDA', self.header_style)
                worksheet.write_merge((row_num),(row_num), 18, 18, 'LLEGADA.', self.header_style)

                worksheet.write_merge((row_num-1),(row_num), 19, 19, 'CALCULO DE TIEMPO', self.header_style)
                worksheet.write_merge((row_num-1),(row_num), 20, 20, 'SECRETARIA', self.header_style)
                worksheet.write_merge((row_num-1),(row_num), 21, 21, 'OBSERVACIONES', self.header_style)
                viaticoss=viaticodiario.objects.filter(centralizador=centralizador,timestamp__year=self.date.year).order_by('ue','prog','act')
                #viaticoss=viaticodiario.objects.all()
                #self.fini_total=self.fini_total+(tama+1)+7
                self.fini_total=row_num
                print(row_num)
                n=0

                for viatico in viaticoss:
                        cont=cont+1
                     
                        n=n+1
                        row_num += 1
                        row = [ (n),
                                '%s %s %s'%(viatico.solicitante.nombre,viatico.solicitante.apaterno,viatico.solicitante.amaterno),
                                viatico.solicitante.ci,
                                viatico.pasaje,
                                viatico.peaje,
                                viatico.Monto_pagado,
                                viatico.RC_IVA,
                                viatico.Liquido_pagable,
                                viatico.totalC,
                                viatico.ue,
                                viatico.prog,
                                viatico.proy,
                                viatico.act,
                                unicode(viatico.solicitante.bcontrol),
                                viatico.ncontrol,
                                viatico.lugar,
                                '%s al %s'%((datetime.strptime(str(viatico.fecha_salida),'%Y-%m-%d').strftime('%d-%m')),
                                        (datetime.strptime(str(viatico.fecha_legada),'%Y-%m-%d').strftime('%d-%m-%Y'))),
                                (viatico.horaSalida).strftime('%H:%M'),
                                (viatico.horallegada).strftime('%H:%M'),
                                viatico.calculohora,
                                self.buscarSecre(viatico.ue),
                                viatico.obs]
                        for col_num in range(len(row)):
                                if col_num == 1:
                                        worksheet.write(row_num,col_num, row[col_num],self.result_style)
                                else:                                
                                        if col_num == 3 or col_num == 4 or col_num == 5 or  col_num == 6 or col_num == 7 or col_num == 8:
                                                worksheet.write(row_num,col_num, row[col_num],self.redondeos_style)
                                        else:
                                                worksheet.write(row_num,col_num, row[col_num],self.body_style)
                fila=row_num+1
                worksheet.write(row_num+1,0,"",self.redondeos_style)
                worksheet.write(row_num+1,1,"TOTAL",self.result_style)

                worksheet.write(row_num+1,2,"",self.redondeos_style)
                worksheet.write(row_num+1,3,xlwt.Formula('SUM(D%s:D%s)'%(self.fini_total+2,fila)),self.redondeos_style)
                worksheet.write(row_num+1,4,xlwt.Formula('SUM(E%s:E%s)'%(self.fini_total+2,fila)),self.redondeos_style)
                worksheet.write(row_num+1,5,xlwt.Formula('SUM(F%s:F%s)'%(self.fini_total+2,fila)),self.redondeos_style)
                worksheet.write(row_num+1,6,xlwt.Formula('SUM(G%s:G%s)'%(self.fini_total+2,fila)),self.redondeos_style)
                worksheet.write(row_num+1,7,xlwt.Formula('SUM(H%s:H%s)'%(self.fini_total+2,fila)),self.redondeos_style)
                worksheet.write(row_num+1,8,xlwt.Formula('SUM(I%s:I%s)'%(self.fini_total+2,fila)),self.redondeos_style)
                if self.uno:
                        cont=(cont+tama)-1
                else:
                        cont=cont+tama
  
                columns_result=['DESCRIPCION',"VIATICOS","PEAJES","PASAJES","TOTAL","Menos RC-IVA","LIQ. PAGABLE"]       
                
                for col_num in range(len(columns_result)):
                        worksheet.write((row_num+col_num)+3,2, columns_result[col_num],self.result_style)
                       
                   
                posicion=row_num+5
                worksheet.write_merge(row_num+3, row_num+3,3, 5,'IMPORTES EN BS.',self.result_style)
                worksheet.write_merge(row_num+4, row_num+4,3, 5,xlwt.Formula('SUM(F%s:F%s)'%(self.fini_total+2,fila)),self.redondeos_style)
                worksheet.write_merge(row_num+5, row_num+5,3, 5,xlwt.Formula('SUM(E%s:E%s)'%(self.fini_total+2,fila)),self.redondeos_style)
                worksheet.write_merge(row_num+6, row_num+6,3, 5,xlwt.Formula('SUM(D%s:D%s)'%(self.fini_total+2,fila)),self.redondeos_style)
                worksheet.write_merge(row_num+7, row_num+7,3, 5,xlwt.Formula('SUM(D%s:D%s)'%(posicion,posicion+2)),self.redondeos_style)
                worksheet.write_merge(row_num+8, row_num+8,3, 5,xlwt.Formula('SUM(G%s:G%s)'%(self.fini_total+2,fila)),self.redondeos_style)
                worksheet.write_merge(row_num+9, row_num+9,3, 5,xlwt.Formula('SUM(I%s:I%s)'%(self.fini_total+2,fila)),self.redondeos_style)
                worksheet.write_merge(row_num+7, row_num+7,7, 8,'Lic,  Reyna  Oporto  Mamani',fecha_licencia)
                worksheet.write_merge(row_num+8, row_num+8,7, 8,'TEC. ANALISTA CONTABLE',fecha_licencia)
                worksheet.write_merge(row_num+9, row_num+9,7, 8,'Potosí, 19 de  diciembre de '+str(self.date.year),fecha_licencia)
                
                self.fini_total=self.fini_total+2
                inicio_total=inicio_total+2
                self.tamano=self.tamano+len(columns_result)+1
                if self.uno:
                        self.tamano=cont+9
                        self.tamano=self.tamano+len(columns_result)+1                        
                else:
                        self.tamano=(self.tamano+cont)+1
                self.uno=False
                #for via in self.model:
                #        viaticodiario.objects.filter(slug=via.slug).update(estado=0)                                      
        '''   
        def tabla(self,worksheet,viatico=None):
                row_num = self.tamano                
                inicio_total=row_num
                if self.uno:
                        inicio_total=inicio_total+2   
                cont=9
                worksheet.col(0).width = 8 * 90
                worksheet.col(1).width = 8 * 840   
                worksheet.col(2).width = 8 * 360
                worksheet.col(3).width = 8 * 220
                worksheet.col(4).width = 8 * 230
                worksheet.col(5).width = 8 * 250
                worksheet.col(6).width = 8 * 250
                worksheet.col(7).width = 8 * 350
                worksheet.col(8).width = 8 * 500
                worksheet.col(9).width = 8 * 170
                worksheet.col(10).width = 8 * 160
                worksheet.col(11).width = 8 * 160
                worksheet.col(12).width = 8 * 160
                worksheet.col(13).width = 8 * 510
                worksheet.col(14).width = 8 * 360
                worksheet.col(15).width = 8 * 540
                worksheet.col(16).width = 8 * 580
                worksheet.col(17).width = 8 * 240
                worksheet.col(18).width = 8 * 240
                worksheet.col(19).width = 8 * 500
                worksheet.col(20).width = 8 * 1150
                #worksheet.col(20).width = 8 * 200

                alignmenttitle = xlwt.Alignment()
                alignmenttitle.horz = xlwt.Alignment.HORZ_CENTER

                title_via = Font()        
                title_via.name = 'Arial'
                title_via.height = 20 * 8
                title_via.bold = False
                title_viatico = XFStyle() 
                title_viatico.font = title_via

                title_subTitle = Font()
                title_subTitle.name = 'Calibri'
                title_subTitle.height = 20 * 8
                title_subTitle.bold = False
                title_subTi = XFStyle() 
                title_subTi.font = title_subTitle
                title_subTi.alignment=alignmenttitle

                fecha_lic = Font()        
                fecha_lic.name = 'Arial Narrow'
                fecha_lic.height = 20 * 9
                fecha_lic.bold = True
                fecha_lic.colour_index = xlwt.Style.colour_map['red']

                fecha_licencia = XFStyle() 
                fecha_licencia.font = fecha_lic
                fecha_licencia.alignment=alignmenttitle

                title_mes = Font()        
                title_mes.name = 'Calibri'
                title_mes.height = 20 * 9
                title_mes.bold = True

                title_mestico = XFStyle() 
                title_mestico.font = title_mes
                title_mestico.alignment=alignmenttitle

                title_Secre = Font()        
                title_Secre.name = 'Calibri'
                title_Secre.height_mismatch = True
                title_Secre.height = 20 * 8
                title_Secre.bold = False

                al = xlwt.Alignment()
                al.wrap = xlwt.Alignment.WRAP_AT_RIGHT
                al.horz = xlwt.Alignment.HORZ_CENTER

                title_Secretico = XFStyle() 
                title_Secretico.font = title_Secre
                title_Secretico.alignment=al

                secret=""
                for mo in xrange(len(self.monto_agrupacion_secre)):
                        secret=secret+self.monto_agrupacion_secre[mo]["secreatria"]
                        if mo != len(self.monto_agrupacion_secre)-1:
                                secret=secret+", "                                        

                worksheet.write_merge((row_num-7), (row_num-7), 1, 1,'Gobierno  Autónomo Dptal, de Potosí',title_viatico)
                worksheet.write_merge((row_num-6), (row_num-6), 1, 1,'Unidad de Contabilidad',title_viatico)
                worksheet.write_merge((row_num-5), (row_num-5), 1, 12,'DETALLE DE PASAJES Y VIÁTICOS AL PERSONAL CORRESPONDIENTE AL MES DE:',title_subTi)
                worksheet.write_merge((row_num-4), (row_num-4), 1, 12,str(self.meses_container),title_mestico)
                pala="SECRETARIA DEPARTAMENTAL DE LA MADRE TIERRA, SECRETARIA DEPARTAMENTAL DE LA MADRE TIERRA, SECRETARIA DEPARTAMENTAL DE LA MADRE TIERRA, SECRETARIA DEPARTAMENTAL DE LA MADRE TIERRA, SECRETARIA DEPARTAMENTAL DE LA MADRE TIERRA, SECRETARIA DEPARTAMENTAL DE LA MADRE TIERRA"
                tama=0
                secre=0
                cero=True
                one=True
                two=True
                tree=True
                
                if cero and len(secret) <= 150:
                        print("ENtro 150")
                        tama=0
                        secre=3
                        one=False
                        two=False
                        tree=False
                if one and len(secret) <= 300:
                        #print("ENtro 350")
                        tama=1
                        secre=2
                        two=False
                        tree=False
                if two and len(secret) <= 400:
                        #print("ENtro 400")
                        tama=2
                        secre=1
                        tree=False
                if tree and len(secret) <= 600:
                        #print("ENtro 600")
                        tama=3
                        secre=0
                       
      
                worksheet.write_merge((row_num-3), (row_num-secre), 1, 12,unicode(str(secret)),title_Secretico)
                row_num = row_num + tama 
                #worksheet.write_merge((row_num-2), (row_num-2), 1, 12,'INFORME CONT,  Nº  '+str(centralizador),title_mestico)

                worksheet.write_merge((row_num-1),(row_num), 0, 0, 'N', self.header_style)
                worksheet.write_merge((row_num-1),(row_num), 1, 1, 'NOMBRE Y APELLIDO', self.header_style)
                worksheet.write_merge((row_num-1),(row_num), 2, 2, 'C.I.', self.header_style)
                worksheet.write_merge((row_num-1),(row_num), 3, 3, 'PASAJE', self.header_style)
                worksheet.write_merge((row_num-1),(row_num), 4, 4, 'PEAJE', self.header_style)

                worksheet.write_merge((row_num-1),(row_num-1), 5, 7,' VIATICOS',self.header_style)
                worksheet.write_merge((row_num),(row_num), 5, 5, 'IMPORTE', self.header_style)
                worksheet.write_merge((row_num),(row_num), 6, 6, 'RC-IVA', self.header_style)
                worksheet.write_merge((row_num),(row_num), 7, 7, 'LIQ. PAGABLE', self.header_style)
                worksheet.write_merge((row_num-1),(row_num), 8, 8, 'TOTAL A CANCELAR', self.header_style)

                worksheet.write_merge((row_num-1), (row_num-1), 9, 12,' CONTROL DE PRESUPUESTO',self.header_style)
                worksheet.write_merge((row_num),(row_num), 9, 9, 'U.E.', self.header_style)
                worksheet.write_merge((row_num),(row_num), 10, 10, 'PROG.', self.header_style)
                worksheet.write_merge((row_num),(row_num), 11, 11, 'PROY.', self.header_style)
                worksheet.write_merge((row_num),(row_num), 12, 12, 'ACT.', self.header_style)

                worksheet.write_merge((row_num-1),(row_num), 13, 13, 'N DE CUENTA', self.header_style)

                worksheet.write_merge((row_num-1),(row_num), 14, 14, 'N DE CONTROL', self.header_style)
                worksheet.write_merge((row_num-1),(row_num), 15, 15, 'LUGAR', self.header_style)
                worksheet.write_merge((row_num-1),(row_num), 16, 16, 'FECHA VIAJE', self.header_style)

                worksheet.write_merge((row_num-1),(row_num-1), 17, 18,'HORAS',self.header_style)
                worksheet.write_merge((row_num),(row_num), 17, 17, 'SALIDA', self.header_style)
                worksheet.write_merge((row_num),(row_num), 18, 18, 'LLEGADA.', self.header_style)

                worksheet.write_merge((row_num-1),(row_num), 19, 19, 'CALCULO DE TIEMPO', self.header_style)
                worksheet.write_merge((row_num-1),(row_num), 20, 20, 'SECRETARIA', self.header_style)
                worksheet.write_merge((row_num-1),(row_num), 21, 21, 'OBSERVACIONES', self.header_style)
               
                self.fini_total=row_num
                print(row_num)
                n=0

                for viatico in viatico:
                        cont=cont+1
                     
                        n=n+1
                        row_num += 1        
                        row = [ (n),
                                '%s %s %s'%(self.Upper(viatico.solicitante.nombre),self.Upper(viatico.solicitante.apaterno),self.Upper(viatico.solicitante.amaterno)),
                                viatico.solicitante.ci,
                                viatico.pasaje,
                                viatico.peaje,
                                viatico.Monto_pagado,
                                viatico.RC_IVA,
                                viatico.Liquido_pagable,
                                viatico.totalC,
                                self.control_presupuesto(viatico.ue),
                                self.control_presupuesto(viatico.prog),
                                self.control_presupuesto(viatico.proy),
                                self.control_presupuesto(viatico.act),
                                unicode(viatico.solicitante.bcontrol),
                                viatico.ncontrol,
                                viatico.lugar,
                                '%s al %s'%((datetime.strptime(str(viatico.fecha_salida),'%Y-%m-%d').strftime('%d-%m')),
                                        (datetime.strptime(str(viatico.fecha_legada),'%Y-%m-%d').strftime('%d-%m-%Y'))),
                                (viatico.horaSalida).strftime('%H:%M'),
                                (viatico.horallegada).strftime('%H:%M'),
                                viatico.calculohora,
                                self.buscarSecre(viatico.ue),
                                viatico.obs]
                        for col_num in range(len(row)):
                                if col_num == 1:
                                        worksheet.write(row_num,col_num, row[col_num],self.result_style)
                                else:                                
                                        if col_num == 3 or col_num == 4 or col_num == 5 or  col_num == 6 or col_num == 7 or col_num == 8:
                                                worksheet.write(row_num,col_num, row[col_num],self.redondeos_style)
                                        else:
                                                worksheet.write(row_num,col_num, row[col_num],self.body_style)
                fila=row_num+1
                worksheet.write(row_num+1,0,"",self.redondeos_style)
                worksheet.write(row_num+1,1,"TOTAL",self.result_style)

                worksheet.write(row_num+1,2,"",self.redondeos_style)
                worksheet.write(row_num+1,3,xlwt.Formula('SUM(D%s:D%s)'%(self.fini_total+2,fila)),self.redondeos_style)
                worksheet.write(row_num+1,4,xlwt.Formula('SUM(E%s:E%s)'%(self.fini_total+2,fila)),self.redondeos_style)
                worksheet.write(row_num+1,5,xlwt.Formula('SUM(F%s:F%s)'%(self.fini_total+2,fila)),self.redondeos_style)
                worksheet.write(row_num+1,6,xlwt.Formula('SUM(G%s:G%s)'%(self.fini_total+2,fila)),self.redondeos_style)
                worksheet.write(row_num+1,7,xlwt.Formula('SUM(H%s:H%s)'%(self.fini_total+2,fila)),self.redondeos_style)
                worksheet.write(row_num+1,8,xlwt.Formula('SUM(I%s:I%s)'%(self.fini_total+2,fila)),self.redondeos_style)
                if self.uno:
                        cont=(cont+tama)-1
                else:
                        cont=cont+tama
  
                columns_result=['DESCRIPCION',"VIATICOS","PEAJES","PASAJES","TOTAL","Menos RC-IVA","LIQ. PAGABLE"]       
                
                for col_num in range(len(columns_result)):
                        worksheet.write((row_num+col_num)+3,2, columns_result[col_num],self.result_style)
                       
                   
                posicion=row_num+5
                worksheet.write_merge(row_num+3, row_num+3,3, 5,'IMPORTES EN BS.',self.result_style)
                worksheet.write_merge(row_num+4, row_num+4,3, 5,xlwt.Formula('SUM(F%s:F%s)'%(self.fini_total+2,fila)),self.redondeos_style)
                worksheet.write_merge(row_num+5, row_num+5,3, 5,xlwt.Formula('SUM(E%s:E%s)'%(self.fini_total+2,fila)),self.redondeos_style)
                worksheet.write_merge(row_num+6, row_num+6,3, 5,xlwt.Formula('SUM(D%s:D%s)'%(self.fini_total+2,fila)),self.redondeos_style)
                worksheet.write_merge(row_num+7, row_num+7,3, 5,xlwt.Formula('SUM(D%s:D%s)'%(posicion,posicion+2)),self.redondeos_style)
                worksheet.write_merge(row_num+8, row_num+8,3, 5,xlwt.Formula('SUM(G%s:G%s)'%(self.fini_total+2,fila)),self.redondeos_style)
                worksheet.write_merge(row_num+9, row_num+9,3, 5,xlwt.Formula('SUM(I%s:I%s)'%(self.fini_total+2,fila)),self.redondeos_style)                

	def get(self, request, *args, **kwargs):
                #self.tama(self.worksheet)
                
                viatico=viaticodiario.objects.filter(timestamp__day=self.date.day,
                                                        timestamp__month=self.date.month,
                                                        timestamp__year=self.date.year,
                                                        estado=1).order_by('ue','prog','act')
                self.cabecera(self.worksheet,viatico)
                self.tabla(self.worksheet,viatico)
                        #break
                self.workbook.save(self.response)
		return self.response

def buscar_paices(request):
        if request.is_ajax():
                secre=Secretaria.objects.filter(nombreS__icontains=request.GET['secre'])
                if secre.exists():                               
                        secretarias=[]                        
                        for se in secre:                                       
                                secretarias.append({
                                        'nombresecre':se.nombreS,                                
                                })
                                                                      
                        data_json=json.dumps(secretarias)
                        print(secretarias)
                else:
                        print("No existe  con esa palabra")
                        data_json='fail'
                mimetype="application/json"
                return HttpResponse(data_json,mimetype)


def llamar_ho_fec(valor):
        var1='%s %s:00'%(valor[0],valor[2])
        var2='%s %s:00'%(valor[1],valor[3])
        #var1=str(valor[0]+valor[2]+":00")
        #var2=str(valor[1]+valor[3]+":00")
        #print(var1)
        start = datetime.strptime(var1, '%Y-%m-%d %H:%M:%S') 
        ends = datetime.strptime(var2, '%Y-%m-%d %H:%M:%S')
        diff = relativedelta(start, ends) 
        dias=(diff.days)*(-1)
        horas=(diff.hours)*(-1)
        minutos=(diff.minutes)*(-1)
        diasviatico=0
        if horas < 6:
                diasviatico='%s.%s'%(dias,0)
        else:
                diasviatico='%s.%s'%(dias,5)
        return [dias,horas,minutos,diasviatico]
def is_null(valor):
        ver_espacio=str(valor)
        for i in xrange(len(ver_espacio)):
                if ver_espacio[i] == " ":
                        return True
        return False
def empty(valor):
        if len(valor) == 0:
                return True
        return False
def is_unique(valor):
        date = datetime.now()
        slug='%s-%s'%(str(valor),date.year)
        if viaticodiario.objects.filter(slug=slug).exists():
                return True
        return False
def buscarCoPun(valor):
        numero=str(valor)
        coma=False        
        for n in xrange(len(numero)):
                if numero[n]==',':
                        coma=True
        if coma==True:
                return True
        return False

def mont_viatico(monts,tipo,valor,dias_result):
        mont=int(monts)
        mont_urbana=dias_result[mont-1]['valor']    
        numerouno=""                                        
        if mont % 2 != 0 :
                numero=str(mont_urbana)
                numerouno=""                                                                                                                                                                      
                for n in xrange(len(numero)):                                                              
                        if numero[n]!='.':
                                numerouno=numerouno+numero[n]
                        else:
                                break
        mont_urba=get_object_or_404(Monto,Tipo_viatico_id=tipo,Nombre=valor,valido=1)
        resultado=0
        if mont % 2 != 0 :
                resultado=resultado+mont_urba.Cantidad*int(numerouno)+(float(mont_urba.Cantidad)/2)
        else:
                resultado=resultado+mont_urba.Cantidad*mont_urbana
        return resultado

class BaseUpdateView(View):
        model=Tipo_viatico
        model2=Monto
        tipo_via=[]
        otro_tipos=[]
        resolucion=[]
        Montos=[]
        error=''
        errorppl=''
        errorfecha=''
        varificar=False 
        date = datetime.now()       
        def form_valid(self,valor,empty=None,notempty=None,is_null=None,isNumber=None,isSolo=None,tipo=99):                
                        if empty != None and self.empty(valor[0]):
                                self.mensaje([valor[1],'ESTA VACIO',tipo])                                
                        else:
                                if notempty == False:
                                        if self.empty(valor[0]) == False:
                                                if is_null != None:
                                                        if self.is_null(valor[0]):
                                                                self.mensaje([valor[1],'CONTIENE ESPACIOS',tipo])                                                
                                                        if isNumber != None:
                                                                if self.isNumber(valor[0]):
                                                                        self.mensaje([valor[1],'TIENE QUE SER NUMERO ENTERO',tipo])                                                        
                                else:   
                                        if is_null != None:
                                                if self.is_null(valor[0]):
                                                        self.mensaje([valor[1],'CONTIENE ESPACIOS',tipo])                                                
                                        if isNumber != None:
                                                if self.isNumber(valor[0]):
                                                        self.mensaje([valor[1],'TIENE QUE SER NUMERO ENTERO',tipo])      
                        if isSolo != None:
                                if self.empty(valor[0])== False:
                                        if self.isSolo(valor[0]):
                                                if self.isNumber(valor[0]):
                                                        self.mensaje([valor[1],' TIENE QUE SER NUMERO VALIDO',tipo])
                                        else:
                                                if self.isDouble(self.isConvert(valor[0])):
                                                        self.mensaje([valor[1],' TIENE QUE SER NUMERO',tipo])                                                                                        
        def mensaje(self,valor):
                if valor[2] == 1:
                        self.error=self.error+'EL CAMPO '+valor[0]+' '+valor[1]+'\n'
                if valor[2] == 2:
                        self.errorppl=self.errorppl+'EL CAMPO '+valor[0]+' '+valor[1]+'\n'
                if valor[2] == 3:
                        self.errorfecha=self.errorfecha+'EL CAMPO '+valor[0]+' '+valor[1]+'\n'
                self.varificar=True
        def mensaje2(self,valor):
                if valor[1] == 1:
                        self.error=self.error+valor[0]+'\n'
                if valor[1] == 2:
                        self.errorppl=self.errorppl+valor[0]+'\n'
                if valor[1] == 3:
                        self.errorfecha=self.errorfecha+valor[0]+'\n'
                self.varificar=True

        def empty(self,valor):
                if len(valor) == 0:
                        return True
                return False
        def is_null(self,valor):
                ver_espacio=str(valor)
                for i in xrange(len(ver_espacio)):
                        if ver_espacio[i] == " ":
                                return True
                return False
        def isNumber(self,valor):
                if valor.isdigit() == False:
                        return True
                return False
        def isDouble(self,valor):
                numero=str(valor)
                numerouno=""
                numerodos=""
                uno=True
                dos=False
                coma=False
                punto=False
                number=False
                for n in xrange(len(numero)):
                        if numero[n]==',':
                                coma=True
                                break
                        if numero[n]=='.':
                                punto=True
                                break
                if coma==False and punto==False:
                        number=True
                for n in xrange(len(numero)):
                
                        if number:
                                numerouno=numerouno+numero[n] 
                        if coma:
                                if numero[n]!=',':
                                        if uno:
                                                numerouno=numerouno+numero[n]
                                        if dos:
                                                numerodos=numerodos+numero[n]
                                else:
                                        uno=False
                                        dos=True
                        if punto:
                                if numero[n]!='.':
                                        if uno:
                                                numerouno=numerouno+numero[n]
                                        if dos:
                                                numerodos=numerodos+numero[n]
                        else:
                                uno=False
                                dos=True

                if self.isDecimal(numerouno):
                        if self.isDecimal(numerodos):
                                return False
                        return False
                else:
                        return True
        def isSolo(self,valor):
                numero=str(valor)
                coma=False
                punto=False
                for n in xrange(len(numero)):
                        if numero[n]==',':
                                coma=True
                                break
                        if numero[n]=='.':
                                punto=True
                                break
                if coma==True or punto==True:
                        return False
                return True     
        def isConvert(self,valor):
                numero=str(valor)
                numerouno=""
                numerodos=""
                uno=True
                dos=False
                coma=False
                punto=False
                number=False 
                for n in xrange(len(numero)):
                        if numero[n]==',':
                                coma=True
                                break
                        if numero[n]=='.':
                                punto=True
                                break

                if coma==False and punto==False:
                        number=True

                for n in xrange(len(numero)):
                        if number:
                                numerouno=numerouno+numero[n] 
                        if coma:
                                if numero[n]!=',':
                                        if uno:
                                                numerouno=numerouno+numero[n]
                                        if dos:
                                                numerodos=numerodos+numero[n]
                                else:
                                        uno=False
                                        dos=True
                        if punto:
                                if numero[n]!='.':
                                        if uno:
                                                numerouno=numerouno+numero[n]
                                        if dos:
                                                numerodos=numerodos+numero[n]
                                else:
                                        uno=False
                                        dos=True
                if number:
                        return '%s.%s'%(numerouno,0)
                if isDecimal(numerouno):
                        if isDecimal(numerodos):
                                return '%s.%s'%(numerouno,numerodos)
        
        def isString(self,valor):
                if valor.isalpha() == True:
                        return True
                return False
        def isDecimal(self,valor):
                if valor.isdecimal() == True:
                        return True
                return False
        # FIN DE FUNCIONES EXTRAS
        def cargar_tipo_viajante(self):
                tipo_viatico=self.model.objects.all()
                self.tipo_via=[]
                self.otro_tipos=[]
                self.tipo_via.append({
                        "id":"",
                        "tipo_viajante":"..."
                        })
                
                for ti in tipo_viatico:     
                        if ti.Tipo_Viajante  == "Gobernador" or ti.Tipo_Viajante  == "Servidor Publico":
                                self.otro_tipos.append({
                                        "id":ti.id,
                                        "tipo_viajante":ti.Tipo_Viajante,
                                })  
                        self.tipo_via.append({
                                "id":ti.id,
                                "tipo_viajante":ti.Tipo_Viajante,
                        })
           
                return self.tipo_via
        def cargar_montos(self,valor):
                self.Montos=[]
                monto=self.model2.objects.filter(Tipo_viatico_id=valor,valido=1)
                p=""
                for m in monto:

                        if m.identificacion == 1:
                                p="Bs."
                        else:
                                p="$."
                        self.Montos.append({
                                "id":m.id,
                                "descripcion":'%s %s %s'%(m.Nombre,m.Cantidad,p),    
                        })
                return self.Montos
        def cargar(self):
                no_ue=[]
                no_prog=[]
                no_act=[]
                no_proy=[]
                self.resultado=[]
                for item in SecresubSecre.objects.filter(gestion=2018):                
                        if item.ue not in no_ue:
                                no_ue.append(item.ue)
                        if item.prog not in no_prog:
                                no_prog.append(item.prog)
                        if item.act not in no_act:
                                no_act.append(item.act)
                        if item.proy not in no_proy:
                                no_proy.append(item.proy)
                self.resultado={
                        'ue':no_ue,
                        'prog':no_prog,
                        'act':no_act,
                        'proy':no_proy,
                }
                return self.resultado
        def cargar_resolucion(self):
                self.resolucion=[]
                self.resolucion.append({"pk":False,"tipo":"Anular"})
                self.resolucion.append({"pk":True,"tipo":"Validor"})
                return self.resolucion
@method_decorator(permission_required('viaticos.change_viaticodiario'),name='dispatch')
class ViativoUpdateView(BaseUpdateView):        
        verificar=False
        context={}                
        viaticos=[] 
        resultado=[]  
        
        def post(self,request,*args,**kwargs):  
                slug=kwargs['slug']                
                viati=get_object_or_404(viaticodiario,slug=slug)
                empleados=get_object_or_404(empleado,ci=viati.id_solicitante)                 
                self.form_valid([request.POST['ue'],'UE'],empty=1,is_null=1,isNumber=1,tipo=1)
                self.form_valid([request.POST['prog'],'PROG'],empty=1,is_null=1,isNumber=1,tipo=1)
                self.form_valid([request.POST['act'],'ACT'],empty=1,is_null=1,isNumber=1,tipo=1)   
                self.form_valid([request.POST['proy'],'PROY'],notempty=False,is_null=1,isNumber=1,tipo=1)
                self.form_valid([request.POST['ncontrol'],'NUMERO DE CONTROL'],empty=1,is_null=1,isNumber=1,tipo=1)
                self.form_valid([request.POST['centralizador'],'CENTRALIZADOR'],empty=1,is_null=1,isNumber=1,tipo=1)
                self.form_valid([request.POST['Extra'],'EXTRA'],notempty=False,is_null=1,tipo=2)
                self.form_valid([request.POST['pasaje'],'PASAJE'],notempty=False,is_null=1,isSolo=False,tipo=2)
                self.form_valid([request.POST['peaje'],'PEAJE'],notempty=False,is_null=1,isSolo=False,tipo=2)
                self.form_valid([request.POST['lugar'],'LUGAR'],empty=1,tipo=2)
                self.form_valid([request.POST['fecha_salida'],'FECHA SALIDA'],empty=1,tipo=3)                        
                self.form_valid([request.POST['horaSalida'],'HORA SALIDA'],empty=1,tipo=3)                        
                self.form_valid([request.POST['fecha_legada'],'FECHA LLEGADA'],empty=1,tipo=3)                        
                self.form_valid([request.POST['horallegada'],'HORA LLEGADA'],empty=1,tipo=3)  
                if self.empty(request.POST['tipo_viatico'])== False:
                        if int(request.POST['tipo_viatico']) == 3:                                                                      
                                validaciones=['fecha_salida_urbana','fecha_legada_urbana',
                                        'horaSalida_urbana','horallegada_urbana',
                                        'lugar_urbana',

                                        'fecha_salida_rural','fecha_legada_rural',
                                        'horaSalida_rural','horallegada_rural',
                                        'lugar_rural',

                                        'fecha_salida_frontera','fecha_legada_frontera',
                                        'horaSalida_frontera','horallegada_frontera',
                                        'lugar_frontera',
                                        ]                            
                                i=0                                
                                vaciouno=False
                                vaciodos=False
                                vaciotres=False
                                vaciocuatro=False
                                vaciocinco=False
                                vali=[]
                                
                                while i < len(validaciones):
                                        if self.empty(request.POST[validaciones[i]]):
                                                vaciouno=True
                                        if self.empty(request.POST[validaciones[i+1]]):
                                                vaciodos=True
                                        if self.empty(request.POST[validaciones[i+2]]):
                                                vaciotres=True
                                        if self.empty(request.POST[validaciones[i+3]]):
                                                vaciocuatro=True
                                        if self.empty(request.POST[validaciones[i+4]]):
                                                vaciocinco=True

                                        if  vaciouno and vaciodos and vaciotres and vaciocuatro and vaciocinco:
                                                vali.append({"valor":True}) 
                                        else:
                                                vali.append({"valor":False})

                                        vaciouno=False
                                        vaciodos=False
                                        vaciotres=False
                                        vaciocuatro=False
                                        vaciocinco=False
                                        i=i+5
                                cont=0
                       
                                for m in xrange(len(vali)):                                       
                                        if vali[m]["valor"] == True:                                                
                                                cont=cont+1
                                
                                if cont == 3:
                                        self.mensaje2(['SELECCIONE POR LO MENOS ALGUNA FECHA Y HORA DE VIAJE',3])                                      
                                else:
                                        pos=0
                                        n=0
                                        pala=["URBANA","RURAL","FRONTERA"]
                                        for m in xrange(len(vali)):
                                                
                                                if vali[m]["valor"]== False:
                                                        pos=m*4
                                                        if m == 0:
                                                                n=4
                                                        if m == 1:
                                                                n=9
                                                        if m == 2:     
                                                                n=14
                                                       
                                                        if self.empty(request.POST[validaciones[n-4]]):
                                                                self.varificar=True
                                                                self.errorfecha=self.errorfecha+'SELECCIONE FECHA DE SALIDA '+pala[m]+'\n'
                                                        else:
                                                                if int(datetime.strptime(str(request.POST[validaciones[n-4]]),'%Y-%m-%d').strftime('%Y')) != int(self.date.year):
                                                                        self.varificar=True
                                                                        self.errorfecha=self.errorfecha+'LA FECHA SALIDA '+pala[m]+' TIENE QUE SER DE ESTE AÑO'+'\n'

                                                        if self.empty(request.POST[validaciones[n-3]]):
                                                                self.varificar=True
                                                                self.errorfecha=self.errorfecha+'SELECCIONE FECHA DE LLEGADA '+pala[m]+'\n'
                                                        else:
                                                                if int(datetime.strptime(str(request.POST[validaciones[n-3]]),'%Y-%m-%d').strftime('%Y')) != int(self.date.year):
                                                                        self.varificar=True
                                                                        self.errorfecha=self.errorfecha+'LA FECHA LLEGADA '+pala[m]+' TIENE QUE SER DE ESTE AÑO'+'\n'

                                                        if self.empty(request.POST[validaciones[n-2]]):
                                                                self.varificar=True
                                                                self.errorfecha=self.errorfecha+'SELECCIONE HORA DE SALIDA '+pala[m]+'\n'
                                                                        
                                                        if self.empty(request.POST[validaciones[n-1]]):
                                                                self.varificar=True
                                                                self.errorfecha=self.errorfecha+'SELECCIONE HORA DE LLEGADA '+pala[m]+'\n'
                                                        if self.empty(request.POST[validaciones[n]]):
                                                                self.varificar=True
                                                                self.errorfecha=self.errorfecha+'SELECCIONE EL LUGAR '+pala[m]+'\n'
                                                        
                                                        if self.empty(request.POST[validaciones[n-4]])==False and self.empty(request.POST[validaciones[n-3]])==False:                                                                                      
                                                                if request.POST[validaciones[n-3]] < request.POST[validaciones[n-4]]:
                                                                        self.varificar=True
                                                                        self.errorfecha=self.errorfecha+'LA FECHA DE LLEGADA NO PUEDE SER MENOR A LA FECHA SALIDA EN '+pala[m]+'\n'
                                                        if self.empty(request.POST[validaciones[n-2]]) == False and self.empty(request.POST[validaciones[n-1]]) == False:
                                                                salida=datetime.strptime(request.POST[validaciones[n-4]],'%Y-%m-%d')
                                                                llegada=datetime.strptime(request.POST[validaciones[n-3]],'%Y-%m-%d')
                                                                horasalida=request.POST[validaciones[n-2]]
                                                                horallegada=request.POST[validaciones[n-1]]
                                                                if salida == llegada:
                                                                        if horallegada < horasalida :
                                                                                self.varificar=True
                                                                                self.errorfecha=self.errorfecha+'LA HORA DE LLEGADA NO PUEDE SER MENOR A LA HORA SALIDA EN '+pala[m]+'\n'
                                        

                        if int(request.POST['tipo_viatico']) == 1 or int(request.POST['tipo_viatico']) == 2:                         
                                if self.empty(request.POST['fecha_salida']) == False and self.empty(request.POST['fecha_legada']) == False:
 
                                        salida=datetime.strptime(request.POST['fecha_salida'],'%Y-%m-%d')
                                        llegada=datetime.strptime(request.POST['fecha_legada'],'%Y-%m-%d')
                                        horasalida=request.POST['horaSalida']
                                        horallegada=request.POST['horallegada']
                                        if salida == llegada:
                                                if horallegada < horasalida :
                                                        self.mensaje2(['LA HORA DE LLEGADA NO PUEDE SER MENOR A LA HORA SALIDA',3])                                                                                                
                                        if self.empty(request.POST['fecha_salida'])== False:                                                                                 
                                                if int(datetime.strptime(request.POST['fecha_salida'],'%Y-%m-%d').strftime('%Y')) != int(self.date.year):
                                                        self.mensaje2(['LA FECHA SALIDA TIENE QUE SER DE ESTE AÑO',3])                    
                                        if self.empty(request.POST['fecha_legada'])== False:                          
                                                if int(datetime.strptime(request.POST['fecha_legada'],'%Y-%m-%d').strftime('%Y')) != int(self.date.year):                                
                                                        self.mensaje2(['LA FECHA LLEGADA TIENE QUE SER DE ESTE AÑO',3])
                                                
                                        if self.empty(request.POST['fecha_legada'])==False and empty(request.POST['fecha_salida'])==False:                        
                                                if request.POST['fecha_legada'] < request.POST['fecha_salida']:    
                                                        self.mensaje2(['LA FECHA DE LLEGADA NO PUEDE SER MENOR A LA FECHA SALIDA',3])                                                                        
                if self.empty(request.POST['tipo_viatico']):
                        self.mensaje2(['SELECCIONE ALGUN TIPO DE VIAJE',2])   
                        self.mensaje(['MONTO','ESTA VACIO',2])                          
                                                         
                if len(self.error)==0 and len(self.errorppl)==0 and len(self.errorfecha)==0:
                        self.varificar=False  
            
                if self.varificar:
                        self.viaticos=[]  
                        Otrosviajes=[]
                        if self.empty(request.POST['tipo_viatico'])==False:
                                if int(request.POST['tipo_viatico']) == 1 or int(request.POST['tipo_viatico']) ==2:  
                                        monto_id=request.POST['monto']
                                        m=get_object_or_404(Monto,id=monto_id)
                                        
                                        if m.identificacion == 1:
                                                self.viaticos.append({
                                                        'ue':request.POST['ue'],
                                                        'prog':request.POST['prog'],
                                                        'act':request.POST['act'],
                                                        'proy':request.POST['proy'],
                                                        'ncontrol':request.POST['ncontrol'],
                                                        'centralizador':request.POST['centralizador'],
                                                        'pasaje':request.POST['pasaje'],
                                                        'peaje':request.POST['peaje'],
                                                        'lugar':request.POST['lugar'],
                                                        'tipo_viatico_id':request.POST['tipo_viatico'],
                                                        'monto':request.POST['monto'],
                                                        'Extra':request.POST['Extra'],
                                                        'id_solicitante':request.POST['id_solicitante'],
                                                        'fecha_salida':request.POST['fecha_salida'],
                                                        'horaSalida':request.POST['horaSalida'],
                                                        'fecha_legada':request.POST['fecha_legada'],
                                                        'horallegada':request.POST['horallegada'],
                                                        'obs':request.POST['obs'],
                                                })
                                        elif m.identificacion == 2:
                                                print(m.identificacion)
                                                self.viaticos.append({
                                                        'ue':request.POST['ue'],
                                                        'prog':request.POST['prog'],
                                                        'act':request.POST['act'],
                                                        'proy':request.POST['proy'],
                                                        'ncontrol':request.POST['ncontrol'],
                                                        'centralizador':request.POST['centralizador'],
                                                        'pasaje':request.POST['pasaje'],
                                                        'peaje':request.POST['peaje'],
                                                        'lugar':request.POST['lugar'],
                                                        'tipo_viatico_id':request.POST['tipo_viatico'],
                                                        'monto':request.POST['monto'],
                                                        'Extra':request.POST['Extra'],
                                                        'id_solicitante':request.POST['id_solicitante'],
                                                        'fecha_salida':request.POST['fecha_salida'],
                                                        'horaSalida':request.POST['horaSalida'],
                                                        'fecha_legada':request.POST['fecha_legada'],
                                                        'horallegada':request.POST['horallegada'],
                                                        'obs':request.POST['obs'],
                                                        'cambiomoneda':request.POST['cambiomoneda'],
                                                        
                                                })                                                                
                                else:
                                        if int(request.POST['tipo_viatico']) == 3:
                                                self.viaticos.append({
                                                'ue':request.POST['ue'],
                                                'prog':request.POST['prog'],
                                                'act':request.POST['act'],
                                                'proy':request.POST['proy'],
                                                'ncontrol':request.POST['ncontrol'],
                                                'centralizador':request.POST['centralizador'],
                                                'pasaje':request.POST['pasaje'],
                                                'peaje':request.POST['peaje'],
                                                'lugar':request.POST['lugar'],
                                                #'monto':request.POST['monto'],
                                                'tipo_viatico_id':request.POST['tipo_viatico'],
                                                #'monto':request.POST['mont'],
                                                'Extra':request.POST['Extra'],
                                                'id_solicitante':request.POST['id_solicitante'],
                                                'fecha_salida':request.POST['fecha_salida'],
                                                'horaSalida':request.POST['horaSalida'],
                                                'fecha_legada':request.POST['fecha_legada'],
                                                'horallegada':request.POST['horallegada'],
                                                'obs':request.POST['obs'],                                                
                                                })   
                                                
                                                fecha_inicial_u=None
                                                fecha_llegada_u=None
                                                fecha_inicial_r=None
                                                fecha_llegada_r=None
                                                fecha_inicial_f=None                                                                                                 
                                                fecha_llegada_f=None                                      
                                                if self.empty(request.POST['fecha_salida_urbana'])==False and self.empty(request.POST['fecha_legada_urbana'])==False:
                                                        fecha_inicial_u=datetime.strptime(str(request.POST['fecha_salida_urbana']),'%Y-%m-%d').date()
                                                        fecha_llegada_u=datetime.strptime(str(request.POST['fecha_legada_urbana']),'%Y-%m-%d').date()
                                                if self.empty(request.POST['fecha_salida_rural'])==False and self.empty(request.POST['fecha_legada_rural'])==False:
                                                        fecha_inicial_r=datetime.strptime(str(request.POST['fecha_salida_rural']),'%Y-%m-%d').date()
                                                        fecha_llegada_r=datetime.strptime(str(request.POST['fecha_legada_rural']),'%Y-%m-%d').date()
                                                if self.empty(request.POST['fecha_salida_frontera'])==False and self.empty(request.POST['fecha_legada_frontera'])==False:
                                                        fecha_inicial_f=datetime.strptime(str(request.POST['fecha_salida_frontera']),'%Y-%m-%d').date()
                                                        fecha_llegada_f=datetime.strptime(str(request.POST['fecha_legada_frontera']),'%Y-%m-%d').date()
                                                Otrosviajes.append({
                                                        'fecha_inicial_urbana':fecha_inicial_u,
                                                        'fecha_llegada_urbana':fecha_llegada_u,
                                                        'horaSalida_urbana':request.POST['horaSalida_urbana'],
                                                        'horallegada_urbana':request.POST['horallegada_urbana'],
                                                        'lugar_urbana':request.POST['lugar_urbana'],
                                                        'fecha_inicial_rural':fecha_inicial_r,
                                                        'fecha_llegada_rural':fecha_llegada_r,
                                                        'horaSalida_rural':request.POST['horaSalida_rural'],
                                                        'horallegada_rural':request.POST['horallegada_rural'],
                                                        'lugar_rural':request.POST['lugar_rural'],
                                                        'fecha_inicial_frontera':fecha_inicial_f,
                                                        'fecha_llegada_frontera':fecha_llegada_f,
                                                        'horaSalida_frontera':request.POST['horaSalida_frontera'],
                                                        'horallegada_frontera':request.POST['horallegada_frontera'],
                                                        'lugar_frontera':request.POST['lugar_frontera'],
                                                }) 
                                                    
                        else:
                                self.viaticos.append({
                                        'ue':request.POST['ue'],
                                        'prog':request.POST['prog'],
                                        'act':request.POST['act'],
                                        'proy':request.POST['proy'],
                                        'ncontrol':request.POST['ncontrol'],
                                        'centralizador':request.POST['centralizador'],
                                        'pasaje':request.POST['pasaje'],
                                        'peaje':request.POST['peaje'],
                                        'lugar':request.POST['lugar'],                                        
                                        'tipo_viatico_id':request.POST['tipo_viatico'],                                       
                                        'Extra':request.POST['Extra'],
                                        'id_solicitante':request.POST['id_solicitante'],
                                        'fecha_salida':request.POST['fecha_salida'],
                                        'horaSalida':request.POST['horaSalida'],
                                        'fecha_legada':request.POST['fecha_legada'],
                                        'horallegada':request.POST['horallegada'],
                                        'obs':request.POST['obs'],
                                })   
                                 
                        self.context={
                                'error':self.error, 
                                'errorppl':self.errorppl,
                                'errorfecha':self.errorfecha,
                                'empleado':empleados,
                                'subsecre':self.cargar(),
                                'tipo_viajant':self.cargar_tipo_viajante(),
                                'Montos':self.cargar_montos(viati.tipo_viatico.id),
                                'viaticos':self.viaticos,
                                "resolucion":self.cargar_resolucion(),
                                'otherviajes':Otrosviajes,
                                "otro_tipos":self.otro_tipos[::-1],
                                "otherviajess":request.POST['tipo_viatico_others'],
                        }
                    
                        return render(request,"viaticos/viaticoView.html",self.context)
                else:                  
                        ue1=request.POST['ue']
                        prog1=request.POST['prog']
                        act1=request.POST['act']
                        proy1=request.POST['proy']
                        ncontrol1=request.POST['ncontrol']
                        centralizador1=request.POST['centralizador']
                        pasaje1=request.POST['pasaje']
                        peaje1=request.POST['peaje']
                        lugar1=request.POST['lugar']
                        tipo_viatico1=request.POST['tipo_viatico']                                        
                        Extra1=request.POST['Extra']
                        id_solicitante1=request.POST['id_solicitante']
                        fecha_salida1=request.POST['fecha_salida']
                        horaSalida1=request.POST['horaSalida']
                        fecha_legada1=request.POST['fecha_legada']
                        horallegada1=request.POST['horallegada']
                        obs1=request.POST['obs']                  
                        viaticosss=viaticodiario.objects.filter(slug=kwargs['slug']) 
                                       
                        for viatico in viaticosss:                                
                                viatico.ue=ue1
                                viatico.prog=prog1
                                viatico.act=act1
                                if self.empty(proy1)==False:
                                        viatico.proy=proy1
                                viatico.centralizador=centralizador1
                                viatico.lugar=lugar1
                                viatico.obs=obs1                                         
                                cont_rural_fronte_urb_dias=0
                                cont_rural_fronte_urb_horas=0
                                cont_rural_fronte_urb_minutos=0
                                orden_fechas=[]                        
                                otros_viajes=[]
                                if int(tipo_viatico1) == 1 or int(tipo_viatico1)==2:
                                        resolucion=request.POST['resolucion_aprovado']                                                                
                                        var1='%s %s:00'%(fecha_salida1,horaSalida1)
                                        var2='%s %s:00'%(fecha_legada1,horallegada1)                                                                        
                                        start = datetime.strptime(var1, '%Y-%m-%d %H:%M:%S') 
                                        ends = datetime.strptime(var2, '%Y-%m-%d %H:%M:%S')
                                        diff = relativedelta(start, ends) 
                                        dias=(diff.days)*(-1)
                                        horas=(diff.hours)*(-1)
                                        minutos=(diff.minutes)*(-1)
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                
                                        diastotales=[]
                                        
                                        dias_totales = ((start - ends).days)*(-1)
                                        dias_totales = (ends - start).days
                                        for days in range(dias_totales + 1): 
                                                fecha = start + relativedelta(days=days)
                                                nuevo=fecha.strftime('%A')
                                                diastotales.append(nuevo)
                                        longitud = len(diastotales)
                                        contdias=0
                                        conthoras=horas
                                        contminutos=minutos
                                        j=0
                                        while j<dias:
                                                contdias=contdias+24
                                                j=j+1
                                        conthoras=conthoras+contdias                                        
                                        print('%s horas, %s minutos'%(conthoras,contminutos))
                                        totalhoras=0
                                        totalminutos=0
                                        cont=conthoras
                                        uno=True
                                        dos=True
                                        tres=True
                                        if int(tipo_viatico1) == 2:    
                                                if resolucion == True:                            
                                                        for i in xrange(len(diastotales)):
                                                                if uno:
                                                                        if diastotales[i] == "Monday" or diastotales[i] == "Tuesday" or diastotales[i] ==  "Wednesday" or diastotales[i] == "Thursday" or diastotales[i] == "Friday":
                                                                                dos=False
                                                                                tres=False                                                   
                                                                                if diastotales[i] == "Friday" and i < longitud:
                                                                                        print("si entra")
                                                                                        if (i+1) < longitud:
                                                                                                print("si entra hasta aqui")
                                                                                                if diastotales[i+1] == "Saturday":
                                                                                                        if (i+2) < longitud:     
                                                                                                                if diastotales[i+2] == "Sunday":
                                                                                                                        if (i+3) < longitud:
                                                                                                                                if diastotales[i+3] == "Monday":
                                                                                                                                        print("si hay lunes")
                                                                                                                                        menoshoras=viatico.horallegada
                                                                                                                                        totalhoras=(cont-48)
                                                                                                                                        cont=cont-48
                                                                                                                                        totalminutos=contminutos
                                                                                                                                        #print('%s horas, %s minutos'%(cont,totalminutos))
                                                                                                                        else:
                                                                                                                                print("si hay domingo")
                                                                                                                                menoshoras=viatico.horallegada
                                                                                                                                totalhoras=(conthoras-menoshoras.hour)-24
                                                                                                                                totalminutos=contminutos-menoshoras.minute
                                                                                                                                #print('%s horas, %s minutos'%(totalhoras,totalminutos))                   
                                                                                                        else:
                                                                                                                print("si hay sabado")
                                                                                                                menoshoras=viatico.horallegada
                                                                                                                totalhoras=conthoras-menoshoras.hour
                                                                                                                totalminutos=contminutos-menoshoras.minute
                                                                                                                #print('%s horas, %s minutos'%(totalhoras,totalminutos))                               
                                                                if dos:
                                                                        if i==0 and (i) < longitud and diastotales[i] == "Saturday" and (i+1) < longitud and  diastotales[i+1] == "Sunday":
                                                                                uno=False
                                                                                tres=False
                                                                                if (i+2) < longitud:
                                                                                        if diastotales[i+2] == "Monday":
                                                                                                if (i+3) < longitud:
                                                                                                        if diastotales[i+3] == "Tuesday":
                                                                                                                if (i+4) < longitud:
                                                                                                                        if diastotales[i+4] == "Wednesday":
                                                                                                                                if (i+5) < longitud:
                                                                                                                                        if diastotales[i+5] == "Thursday":
                                                                                                                                                if (i+6) < longitud:
                                                                                                                                                        if diastotales[i+6] == "Friday":
                                                                                                                                                                print("si hay viernes")
                                                                                                                                                                #menoshoras=viatico.horallegada
                                                                                                                                                                menoshorassalida=viatico.horaSalida
                                                                                                                                                                totalhoras=(cont-24-(24-menoshorassalida.hour))
                                                                                                                                                                totalminutos=contminutos-menoshorassalida.minute
                                                                                                                                                                print('%s horas, %s minutos'%(cont,totalminutos))        
                                                                                                                                                else:
                                                                                                                                                        print("si hay jueves")
                                                                                                                                                        #menoshoras=viatico.horallegada
                                                                                                                                                        menoshorassalida=viatico.horaSalida
                                                                                                                                                        totalhoras=(cont-24-(24-menoshorassalida.hour))
                                                                                                                                                        totalminutos=contminutos-menoshorassalida.minute
                                                                                                                                                        print('%s horas, %s minutos'%(cont,totalminutos))
                                                                                                                                else:
                                                                                                                                        print("si hay miercoles")
                                                                                                                                        #menoshoras=viatico.horallegada
                                                                                                                                        menoshorassalida=viatico.horaSalida
                                                                                                                                        totalhoras=(cont-24-(24-menoshorassalida.hour))
                                                                                                                                        totalminutos=contminutos-menoshorassalida.minute
                                                                                                                                        print('%s horas, %s minutos'%(cont,totalminutos))
                                                                                                                else:
                                                                                                                        print("si hay martes")
                                                                                                                        #menoshoras=viatico.horallegada
                                                                                                                        menoshorassalida=viatico.horaSalida
                                                                                                                        totalhoras=(cont-24-(24-menoshorassalida.hour))
                                                                                                                        totalminutos=contminutos-menoshorassalida.minute
                                                                                                                        print('%s horas, %s minutos'%(cont,totalminutos))
                                                                                                else:
                                                                                                        print("si hay lunes")
                                                                                                        #menoshoras=viatico.horallegada
                                                                                                        menoshorassalida=viatico.horaSalida
                                                                                                        totalhoras=(cont-24-(24-menoshorassalida.hour))
                                                                                                        totalminutos=contminutos-menoshorassalida.minute
                                                                                                        print('%s horas, %s minutos'%(cont,totalminutos))
                                                                                                                        
                                                                                else:
                                                                                        print("si hay sabado")
                                                                                        #print('%s horas, %s minutos'%(totalhoras,totalminutos))
                                                                if tres:
                                                                        if i==0 and (i) < longitud and diastotales[i] == "Sunday":
                                                                                uno=False
                                                                                dos=False
                                                                                if (i+1) < longitud:
                                                                                        if diastotales[i+1] == "Monday":
                                                                                                if (i+2) < longitud:
                                                                                                        if diastotales[i+2] == "Tuesday":
                                                                                                                if (i+3) < longitud:
                                                                                                                        if diastotales[i+3] == "Wednesday":
                                                                                                                                if (i+4) < longitud:
                                                                                                                                        if diastotales[i+4] == "Thursday":
                                                                                                                                                if (i+5) < longitud:
                                                                                                                                                        if diastotales[i+5] == "Friday":
                                                                                                                                                                if (i+6) < longitud:
                                                                                                                                                                        if diastotales[i+6] == "Saturday":
                                                                                                                                                                                print("si hay sabado")
                                                                                
                                                                                                                                                                                menoshoras=viatico.horallegada
                                                                                                                                                                                menoshorassalida=viatico.horaSalida
                                                                                                                                                                                totalhoras=(cont-(24-menoshorassalida.hour)-menoshoras.hour)
                                                                                                                                                                                totalminutos=contminutos-menoshorassalida.minute-menoshoras.minute
                                                                                                                                                                        #print('%s horas, %s minutos'%(cont,totalminutos))
                                                                                                                                                else:
                                                                                                                                                        print("si hay domingo")
                                                                                                                                                        menoshorassalida=viatico.horaSalida
                                                                                                                                                        totalhoras=(cont-(24-menoshorassalida.hour))
                                                                                                                                                        totalminutos=contminutos-menoshorassalida.minute
                                                                                                                                else:
                                                                                                                                        print("si hay domingo")
                                                                                                                                        menoshorassalida=viatico.horaSalida
                                                                                                                                        totalhoras=(cont-(24-menoshorassalida.hour))
                                                                                                                                        totalminutos=contminutos-menoshorassalida.minute
                                                                                                                else:
                                                                                                                        print("si hay domingo")
                                                                                                                        menoshorassalida=viatico.horaSalida
                                                                                                                        totalhoras=(cont-(24-menoshorassalida.hour))
                                                                                                                        totalminutos=contminutos-menoshorassalida.minute
                                                                                                        
                                                                                                else:
                                                                                                        print("si hay domingo")
                                                                                                        menoshorassalida=viatico.horaSalida
                                                                                                        totalhoras=(cont-(24-menoshorassalida.hour))
                                                                                                        totalminutos=contminutos-menoshorassalida.minute
                                                                                                        #print('%s horas, %s minutos'%(totalhoras,totalminutos))                                                                                        
                                        contadordias=0
                                        contadorhoras=0
                                        contadorminutos=0
                                        if totalhoras > 0 and totalminutos >= 0:
                                                if totalhoras < 24:
                                                        contadordias=0
                                                        contadorhoras=totalhoras
                                                        contadorminutos=totalminutos
                                                else:
                                                        while totalhoras >= 24:
                                                                contadordias=contadordias+1
                                                                totalhoras=totalhoras-24
                                                        contadorhoras=totalhoras
                                                        contadorminutos=totalminutos
                                        else:
                                                contadordias=dias
                                                contadorhoras=horas
                                                contadorminutos=contminutos
                                       
                                        if contadorhoras < 6:
                                                diasviatico='%s.%s'%(contadordias,0)
                                        else:
                                                diasviatico='%s.%s'%(contadordias,5)
                                        viatico.dias=diasviatico

                                        Montos=get_object_or_404(Monto,id=request.POST['monto'])
                                        viatico.monto=Montos
                                        
                                        ti_viatico=get_object_or_404(Tipo_viatico,id=tipo_viatico1)
                                        viatico.tipo_viatico=ti_viatico

                                        if Montos.identificacion == 1:
                                                result=0
                                                monto=Montos.Cantidad
                                                i=1
                                                cantidad_de_hora=6

                                                if contadordias != 0:
                                                        while i <= contadordias:
                                                                result=result+monto
                                                                i = i + 1
                                                if contadorhoras>=cantidad_de_hora:
                                                        result=result+float(monto)/2
                                                resultado=round(result*concatenar(13),0)
                                                viatico.RC_IVA=int(resultado)
                                                viatico.Liquido_pagable=result-resultado
                                                viatico.Monto_pagado=result

                                                pasaje=0
                                                peaje=0
                                                Extra=0                        
                                                if self.empty(pasaje1)==False:
                                                        viatico.pasaje=float(self.isConvert(pasaje1))
                                                else:
                                                        viatico.pasaje=pasaje
                                                if self.empty(peaje1)==False:
                                                        viatico.peaje=float(self.isConvert(peaje1))
                                                else:
                                                        viatico.peaje=peaje
                                                if self.empty(Extra1)==False:
                                                        viatico.Extra=float(self.isConvert(Extra1))
                                                else:
                                                        viatico.Extra=Extra

                                                viatico.resolucion=resolucion
                                                viatico.totalC=viatico.Liquido_pagable+float(self.isConvert(pasaje1))+float(self.isConvert(peaje1))+float(self.isConvert(Extra1))
                                        else:
                                                if Montos.identificacion == 2:
                                                        result=0
                                                        monto=Montos.Cantidad
                                                        cambiomoneda=request.POST['cambiomoneda']
                                                        dias_afuera=request.POST['cantidad_dias_fuera_dias']
                                                        moneda_cambio=monto*float(self.isConvert(cambiomoneda))
                                                        resultado_cambio=0
                                                        j=0
                                                        while j < int(dias_afuera):
                                                                resultado_cambio=resultado_cambio+moneda_cambio
                                                                j=j+1                         
                                                        resultado=round(resultado_cambio*concatenar(13),0)                                         
                                                                                                                                                                                                                            
                                                        viatico.RC_IVA=int(resultado)
                                                        viatico.Liquido_pagable=resultado_cambio-resultado
                                                        viatico.Monto_pagado=resultado_cambio

                                                        pasaje=0
                                                        peaje=0
                                                        Extra=0
                                                
                                                        if self.empty(pasaje1)==False:
                                                                viatico.pasaje=float(self.isConvert(pasaje1))
                                                        else:
                                                                viatico.pasaje=pasaje

                                                        if self.empty(peaje1)==False:
                                                                viatico.peaje=float(self.isConvert(peaje1))
                                                        else:
                                                                viatico.peaje=peaje

                                                        if self.empty(Extra1)==False:
                                                                viatico.Extra=float(self.isConvert(Extra1))
                                                        else:
                                                                viatico.Extra=Extra

                                                        viatico.cambio_moneda=cambiomoneda
                                                        viatico.cantidad_dias_fuera_pais=dias_afuera
                                                        viatico.totalC=viatico.Liquido_pagable+float(self.isConvert(request.POST['pasaje']))+float(self.isConvert(request.POST['peaje']))+float(self.isConvert(request.POST['Extra']))                                                        
                                        viatico.fecha_salida=datetime.strptime(fecha_salida1,'%Y-%m-%d').strftime('%Y-%m-%d')
                                        viatico.horaSalida=horaSalida1
                                        viatico.fecha_legada=datetime.strptime(fecha_legada1,'%Y-%m-%d').strftime('%Y-%m-%d')
                                        viatico.horallegada=horallegada1
                                        viatico.calculohora='%s d, %s h, %s m '%(contadordias,contadorhoras,contadorminutos)
                                        viatico.fechav='%s al %s'%(datetime.strptime(fecha_salida1,'%Y-%m-%d').strftime('%m-%d'),datetime.strptime(fecha_legada1,'%Y-%m-%d').strftime('%Y-%m-%d'))
                                elif int(tipo_viatico1) == 3:
                                        errorfecha=[]
                                        tipo_others=request.POST['tipo_viatico_others']
                                        mont_frontera=0
                                        valor_de_horas_fechas=[]
                                        nombre=""

                                        validaciones=['fecha_salida_urbana','fecha_legada_urbana',
                                                'horaSalida_urbana','horallegada_urbana',
                                                'lugar_urbana',

                                                'fecha_salida_rural','fecha_legada_rural',
                                                'horaSalida_rural','horallegada_rural',                                                
                                                'lugar_rural',

                                                'fecha_salida_frontera','fecha_legada_frontera',
                                                'horaSalida_frontera','horallegada_frontera',
                                                'lugar_frontera']
                                        i=0                                
                                        vaciouno=False
                                        vaciodos=False
                                        vaciotres=False
                                        vaciocuatro=False
                                        vaciocinco=False
                                        vali=[]
                                        
                                        while i < len(validaciones):
                                                if self.empty(request.POST[validaciones[i]]):
                                                        vaciouno=True
                                                if self.empty(request.POST[validaciones[i+1]]):
                                                        vaciodos=True
                                                if self.empty(request.POST[validaciones[i+2]]):
                                                        vaciotres=True
                                                if self.empty(request.POST[validaciones[i+3]]):
                                                        vaciocuatro=True
                                                if self.empty(request.POST[validaciones[i+4]]):
                                                        vaciocinco=True

                                                if  vaciouno and vaciodos and vaciotres and vaciocuatro and vaciocinco:
                                                        vali.append({"valor":True}) 
                                                else:
                                                        vali.append({"valor":False})

                                                vaciouno=False
                                                vaciodos=False
                                                vaciotres=False
                                                vaciocuatro=False
                                                vaciocinco=False
                                                i=i+5
                                        
                                        NombreValores=["Urbana","Rural","F. Frontera"]  
                                        
                                        for m in xrange(len(vali)):                                                
                                                if vali[m]["valor"]== False:
                                                        pos=m*3
                                                        if m == 0:
                                                                n=4
                                                        if m == 1:
                                                                n=9
                                                        if m == 2:     
                                                                n=14
                                                        
                                                        #print(request.POST[validaciones[0]])
                                                        fecha_salida_valor=request.POST[validaciones[n-4]]
                                                        #print(fecha_salida_valor)                                                    
                                                        fecha_legada_valor=request.POST[validaciones[n-3]]
                                                        horaSalida_valor=request.POST[validaciones[n-2]]
                                                        horallegada_valor=request.POST[validaciones[n-1]]

                                                        orden_fechas.append({"id":m,"key":fecha_legada_valor,"key1":horallegada_valor})
                                                        orden_fechas.append({"id":m,"key":fecha_salida_valor,"key1":horaSalida_valor})

                                                        nombre=nombre+request.POST[validaciones[n]]+"-"                                                                                                        
                                                        va=llamar_ho_fec([fecha_salida_valor,fecha_legada_valor,horaSalida_valor,horallegada_valor])
                                                        
                                                        cont_rural_fronte_urb_dias=cont_rural_fronte_urb_dias+va[0]
                                                        cont_rural_fronte_urb_horas=cont_rural_fronte_urb_horas+va[1]
                                                        cont_rural_fronte_urb_minutos=cont_rural_fronte_urb_minutos+va[2]

                                                        montoss=get_object_or_404(Monto,Tipo_viatico_id=tipo_others,Nombre=NombreValores[m],valido=1)
                                                        result=0
                                                        monto=montoss.Cantidad
                                                        
                                                        i=1
                                                        cantidad_de_hora=6
                                                        if va[0] != 0:
                                                                while i <= va[0]:
                                                                        result=result+monto
                                                                        i = i + 1

                                                        if va[1]>=cantidad_de_hora:
                                                                result=result+float(monto)/2
                                                       
                                                        temporal=[]
                                                        resultado=round(result*concatenar(13),0)
                                                        temporal.append({"RC_IVA":int(resultado),
                                                                        "Liquido_pagable":result-resultado,
                                                                        "Monto_pagado":result})
                                                        
                                                        valor_de_horas_fechas.append({"posicion":m,"valor":temporal})
                                                        
                                                        otr_fech_salid=datetime.strptime(str(fecha_salida_valor),'%Y-%m-%d').date()                                                
                                                        otr_fehc_llegad=datetime.strptime(str(fecha_legada_valor),'%Y-%m-%d').date()
                                                                                                                                                  
                                                    
                                                        otros_fechav='%s al %s'%(otr_fech_salid.strftime('%d-%m'),otr_fehc_llegad.strftime('%d-%m-%Y'))
                                                        otros_calculohora='%s d, %s h, %s m '%(va[0],va[1],va[2])
                                                        otros_dias=va[3]
                                                        otros_viajes.append({                                                                
                                                                "fecha_salida":fecha_salida_valor,
                                                                "fecha_legada":fecha_legada_valor,
                                                                "horaSalida":horaSalida_valor,
                                                                "horallegada":horallegada_valor,
                                                                "lugar":request.POST[validaciones[n]],
                                                                "fechav":otros_fechav,
                                                                "calculohora":otros_calculohora,
                                                                "dias":otros_dias
                                                        })
                                                else:
                                                        valor_de_horas_fechas.append({"posicion":m,"valor":False})
                                                        otros_viajes.append({                                                                
                                                                "fecha_salida":"9999-09-09",
                                                                "fecha_legada":"9999-09-09",
                                                                "horaSalida":"00:00",
                                                                "horallegada":"00:00",
                                                                "lugar":"(null)",
                                                                "fechav":"(null)",
                                                                "calculohora":"(null)",
                                                                "dias":"0"
                                                        })
                                                                                  
                                        for cal in xrange(len(valor_de_horas_fechas)):
                                                if valor_de_horas_fechas[cal]["valor"]!= False:                                                        
                                                        for mo in valor_de_horas_fechas[cal]["valor"]: 
                                                                                                                  
                                                                mont_frontera=float(mont_frontera)+float(mo["Monto_pagado"])
                                     
                                        result=mont_frontera                                                                       
                                        tipo_viaticoss=""
                                        id_tipo=0
                                        tipo_monto=""                                        
                                        tipo_viaticoss=Monto.objects.filter(Tipo_viatico_id=request.POST['tipo_viatico'])
                                        for tis in tipo_viaticoss:
                                                id_tipo=tis.id
                                        tipo_monto=get_object_or_404(Monto,id=id_tipo)                
                                        pasaje=0
                                        peaje=0
                                        Extra=0
                                        if empty(request.POST['pasaje'])==False:
                                                viatico.pasaje=float(isConvert(request.POST['pasaje']))
                                        else:
                                                viatico.pasaje=pasaje

                                        if empty(request.POST['peaje'])==False:
                                                viatico.peaje=float(isConvert(request.POST['peaje']))
                                        else:
                                                viatico.peaje=peaje

                                        if empty(request.POST['Extra'])==False:
                                                viatico.Extra=float(isConvert(request.POST['Extra']))
                                        else:
                                                viatico.Extra=Extra
                                                                                
                                        ti_viatico=get_object_or_404(Tipo_viatico,id=request.POST['tipo_viatico'])
                                        viatico.tipo_viatico=ti_viatico

                                        viatico.monto=tipo_monto

                                        resultado=round(float(isConvert(result))*0.13,2)
                                        viatico.Monto_pagado=float(isConvert(result))
                                        viatico.RC_IVA=int(resultado)
                                        viatico.Liquido_pagable=float(isConvert(result))-float(isConvert(viatico.RC_IVA))
                                        viatico.totalC=viatico.Liquido_pagable+float(isConvert(request.POST['pasaje']))+float(isConvert(request.POST['peaje']))+float(isConvert(request.POST['Extra']))                                                                        
                                        nombre_oficial=""
                                        for pa in xrange(len(nombre)):
                                                if pa == (len(nombre)-1):
                                                        if nombre[pa] != "-":
                                                                nombre_oficial=nombre_oficial+nombre[pa]
                                                else:        
                                                        nombre_oficial=nombre_oficial+nombre[pa]                                      
                                        viatico.lugar=nombre_oficial

                                        fecha1=0
                                        fecha2=0
                                        var_dias=0
                                        var_horas=0
                                        var_minutos=0
                                        var_fecha_Salida=0
                                        var_fecha_llegada=0
                                        var_hora_salida=0
                                        var_hora_llegada=0
                                        dias_sumando=0
                                        
                                        sorted_date = sorted(orden_fechas, key=lambda x: (datetime.strptime(x['key'], '%Y-%m-%d'),x['id'],x['key1']))
                                        fecha1=sorted_date[0]["key"]
                                        fecha2=sorted_date[len(sorted_date)-1]["key"]
                                        if cont_rural_fronte_urb_horas > 0 and cont_rural_fronte_urb_minutos >= 0:
                                                if cont_rural_fronte_urb_horas < 24:
                                                        var_dias=cont_rural_fronte_urb_dias
                                                        var_horas=cont_rural_fronte_urb_horas
                                                        var_minutos=cont_rural_fronte_urb_minutos
                                                else:
                                                        while cont_rural_fronte_urb_horas >= 24:                                                        
                                                                cont_rural_fronte_urb_dias=cont_rural_fronte_urb_dias+1
                                                                cont_rural_fronte_urb_horas=cont_rural_fronte_urb_horas-24
                                                        var_dias=cont_rural_fronte_urb_dias
                                                        var_horas=cont_rural_fronte_urb_horas
                                                        var_minutos=cont_rural_fronte_urb_minutos
                                        else:
                                                var_dias=cont_rural_fronte_urb_dias
                                                var_horas=cont_rural_fronte_urb_horas
                                                var_minutos=cont_rural_fronte_urb_minutos
                                        for otros in xrange(len(otros_viajes)):
                                                dias_sumando=dias_sumando+float(self.isConvert(otros_viajes[otros]["dias"]))

                                        var_fecha_Salida=fecha1
                                        var_fecha_llegada=fecha2                        
                                        var_hora_salida=sorted_date[0]["key1"]
                                        var_hora_llegada=sorted_date[len(sorted_date)-1]["key1"]

                                        viatico.dias=dias_sumando 
                                        var_dia=str(dias_sumando)
                                        for di in xrange(len(var_dia)):
                                                if var_dia[di] ==".":
                                                        numero=int(var_dia[di+1])                                                
                                                        if numero == 0:
                                                                var_horas=random.randint(1, 5)
                                                        else:
                                                                var_horas=random.randint(7, 22)   
                                                        break                               
                                        viatico.calculohora='%s d, %s h, %s m '%(var_dias,var_horas,var_minutos)

                                        otros_fecha_inicial_urbana=None
                                        otros_fecha_llegada_urbana=None
                                        otros_horaSalida_urbana=None
                                        otros_horallegada_urbana=None
                                        otros_lugar_urbana=None
                                        otros_fechav_urbana=None
                                        otros_cal_urbana=None
                                        otros_dias_urbana=None
                                        
                                        otros_fecha_inicial_rural=None
                                        otros_fecha_llegada_rural=None
                                        otros_horaSalida_rural=None
                                        otros_horallegada_rural=None
                                        otros_lugar_rural=None
                                        otros_fechav_rural=None
                                        otros_cal_rural=None
                                        otros_dias_rural=None
                                        
                                        otros_fecha_inicial_frontera=None
                                        otros_fecha_llegada_frontera=None
                                        otros_horaSalida_frontera=None
                                        otros_horallegada_frontera=None
                                        otros_lugar_frontera=None
                                        otros_fechav_frontera=None
                                        otros_cal_frontera=None
                                        otros_dias_frontera=None


                                        if vali[0]["valor"]== False:                                                                                        
                                                otros_fecha_inicial_urbana=datetime.strptime(str(otros_viajes[0]["fecha_salida"]),'%Y-%m-%d').date() 
                                                otros_fecha_llegada_urbana=datetime.strptime(str(otros_viajes[0]["fecha_legada"]),'%Y-%m-%d').date() 
                                                otros_horaSalida_urbana=datetime.strptime(str(otros_viajes[0]["horaSalida"]+':00'),'%H:%M:%S').time()
                                                otros_horallegada_urbana=datetime.strptime(str(otros_viajes[0]["horallegada"]+':00'),'%H:%M:%S').time()
                                                otros_lugar_urbana=otros_viajes[0]["lugar"]
                                                otros_fechav_urbana=otros_viajes[0]["fechav"]
                                                otros_cal_urbana=otros_viajes[0]["calculohora"]
                                                otros_dias_urbana=otros_viajes[0]["dias"]
                   

                                        if vali[1]["valor"]== False:                                              
                                                otros_fecha_inicial_rural=datetime.strptime(str(otros_viajes[1]["fecha_salida"]),'%Y-%m-%d').date() 
                                                otros_fecha_llegada_rural=datetime.strptime(str(otros_viajes[1]["fecha_legada"]),'%Y-%m-%d').date() 
                                                otros_horaSalida_rural=datetime.strptime(str(otros_viajes[1]["horaSalida"]+':00'),'%H:%M:%S').time()
                                                otros_horallegada_rural=datetime.strptime(str(otros_viajes[1]["horallegada"]+':00'),'%H:%M:%S').time()
                                                otros_lugar_rural=otros_viajes[1]["lugar"]
                                                otros_fechav_rural=otros_viajes[1]["fechav"]
                                                otros_cal_rural=otros_viajes[1]["calculohora"]
                                                otros_dias_rural=otros_viajes[1]["dias"]                                     
                                        
                                        if vali[2]["valor"]== False:                                                
                                                otros_fecha_inicial_frontera=datetime.strptime(str(otros_viajes[2]["fecha_salida"]),'%Y-%m-%d').date() 
                                                otros_fecha_llegada_frontera=datetime.strptime(str(otros_viajes[2]["fecha_legada"]),'%Y-%m-%d').date() 
                                                otros_horaSalida_frontera=datetime.strptime(str(otros_viajes[2]["horaSalida"]+':00'),'%H:%M:%S').time()
                                                otros_horallegada_frontera=datetime.strptime(str(otros_viajes[2]["horallegada"]+':00'),'%H:%M:%S').time()
                                                otros_lugar_frontera=otros_viajes[2]["lugar"]
                                                otros_fechav_frontera=otros_viajes[2]["fechav"]
                                                otros_cal_frontera=otros_viajes[2]["calculohora"]
                                                otros_dias_frontera=otros_viajes[2]["dias"]                                        
                                        
                                        fech_salid=datetime.strptime(str(var_fecha_Salida),'%Y-%m-%d').date()                                                
                                        
                                        fehc_llegad=datetime.strptime(str(var_fecha_llegada),'%Y-%m-%d').date()
                                                                        
                                        viatico.fecha_salida=fech_salid
                                        viatico.fecha_legada=fehc_llegad
                                        viatico.horaSalida=datetime.strptime(str(var_hora_salida)+":00",'%H:%M:%S').time()
                                        viatico.horallegada=datetime.strptime(str(var_hora_llegada+":00"),'%H:%M:%S').time()
                                        
                                        viatico.fechav='%s al %s'%(fech_salid.strftime('%d-%m'),fehc_llegad.strftime('%d-%m-%Y'))

                                        #for via in OtrosViajes.objects.filter(slug_viaticos=viatico.slug):
                                        OtrosViajes.objects.filter(slug_viaticos=viatico.slug).update(                                                
                                                        fecha_inicial_urbana=otros_fecha_inicial_urbana,
                                                        fecha_llegada_urbana=otros_fecha_llegada_urbana,
                                                        horaSalida_urbana=otros_horaSalida_urbana,
                                                        horallegada_urbana=otros_horallegada_urbana,
                                                        lugar_urbana=otros_lugar_urbana,
                                                        fechav_urbana=otros_fechav_urbana,
                                                        calculohora_urbana=otros_cal_urbana,
                                                        dias_urbana=otros_dias_urbana,

                                                        fecha_inicial_rural=otros_fecha_inicial_rural,
                                                        fecha_llegada_rural=otros_fecha_llegada_rural,
                                                        horaSalida_rural=otros_horaSalida_rural,
                                                        horallegada_rural=otros_horallegada_rural,
                                                        lugar_rural=otros_lugar_rural,
                                                        fechav_rural=otros_fechav_rural,
                                                        calculohora_rural=otros_cal_rural,
                                                        dias_rural=otros_dias_rural,

                                                        fecha_inicial_frontera=otros_fecha_inicial_frontera,
                                                        fecha_llegada_frontera=otros_fecha_llegada_frontera,
                                                        horaSalida_frontera=otros_horaSalida_frontera,
                                                        horallegada_frontera=otros_horallegada_frontera,
                                                        lugar_frontera=otros_lugar_frontera,
                                                        fechav_frontera=otros_fechav_frontera,
                                                        calculohora_frontera=otros_cal_frontera,
                                                        dias_frontera=otros_dias_frontera,
                                                        tipos_viajante=request.POST['tipo_viatico_others']                                      
                                                )
                                viatico.save()
                                messages.success(request, 'Se edito correctamente el viatico')
                                return redirect('viaticos:detail')


                return render(request,"viaticos/viaticoView.html",self.context) 
        def get(self,request,*args,**kwargs):
                slug=kwargs['slug']                
                viati=get_object_or_404(viaticodiario,slug=slug)                      
                if viati.monto.Cantidad == 0:
                        mon=viati.Monto_pagado
                else:
                        mon=viati.monto.id  
                self.viaticos=[]  
                monto_id=viati.monto_id
                m=get_object_or_404(Monto,id=monto_id)
                
                if m.identificacion == 1:
                        self.viaticos.append({
                                'ue':viati.ue,
                                'prog':viati.prog,
                                'act':viati.act,
                                'proy':viati.proy,
                                'ncontrol':viati.ncontrol,
                                'centralizador':viati.centralizador,
                                'pasaje':viati.pasaje,
                                'peaje':viati.peaje,
                                'lugar':viati.lugar,                
                                'tipo_viatico_id':viati.tipo_viatico.id,
                                'monto':mon,
                                'Extra':viati.Extra,
                                'id_solicitante':viati.id_solicitante,
                                'fecha_salida':unicode(viati.fecha_salida),
                                'horaSalida':viati.horaSalida,
                                'fecha_legada':unicode(viati.fecha_legada),
                                'horallegada':viati.horallegada,
                                'obs':viati.obs,
                                'resolucion':viati.resolucion,  
                        })
                elif m.identificacion == 2:           

                        self.viaticos.append({
                                'ue':viati.ue,
                                'prog':viati.prog,
                                'act':viati.act,
                                'proy':viati.proy,
                                'ncontrol':viati.ncontrol,
                                'centralizador':viati.centralizador,
                                'pasaje':viati.pasaje,
                                'peaje':viati.peaje,
                                'lugar':viati.lugar,                
                                'tipo_viatico_id':viati.tipo_viatico.id,
                                'monto':mon,
                                'Extra':viati.Extra,
                                'id_solicitante':viati.id_solicitante,
                                'fecha_salida':unicode(viati.fecha_salida),
                                'horaSalida':viati.horaSalida,
                                'fecha_legada':unicode(viati.fecha_legada),
                                'horallegada':viati.horallegada,
                                'obs':viati.obs,  
                                'cantidad_dias_fuera_pais':viati.cantidad_dias_fuera_pais,
                                'cambiomoneda':viati.cambio_moneda,
                                'resolucion':viati.resolucion,
                        })
                empleados=get_object_or_404(empleado,ci=viati.id_solicitante)
                if OtrosViajes.objects.filter(slug_viaticos=slug).exists():
                        otrosviaticoss=get_object_or_404(OtrosViajes,slug_viaticos=slug)
                        tipos=otrosviaticoss.tipos_viajante
                        otrosviaticos=OtrosViajes.objects.filter(slug_viaticos=slug)
                        self.context={
                                'empleado':empleados,
                                'viaticos':self.viaticos,
                                'subsecre':self.cargar(),
                                'tipo_viajant':self.cargar_tipo_viajante(),
                                'Montos':self.cargar_montos(viati.tipo_viatico.id),
                                "otro_tipos":self.otro_tipos[::-1],
                                "otherviajes":otrosviaticos,
                                "otherviajess":tipos, 
                                "resolucion":self.cargar_resolucion(),
                        }  
                else:                        
                        self.context={
                                'empleado':empleados,
                                'viaticos':self.viaticos,
                                'subsecre':self.cargar(),
                                'tipo_viajant':self.cargar_tipo_viajante(),
                                'Montos':self.cargar_montos(viati.tipo_viatico.id),
                                'resolucion':self.cargar_resolucion(),
                                "otro_tipos":self.otro_tipos[::-1],                                 
                        }             
                return render(request,"viaticos/viaticoView.html",self.context)
@method_decorator(permission_required('viaticos.delete_viaticodiario'),name='dispatch')
class ViaticoDeleteView(DeleteView):
    model=viaticodiario
    model2=OtrosViajes
    template_name = 'viaticos/templates/solicitud_delete.html'
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Se elimino correctamente')
        via=get_object_or_404(self.model, slug=self.kwargs.get("slug"))  
        self.model2.objects.filter(slug_viaticos=via.slug).delete()
        via.delete()        
        return redirect('viaticos:detail')

class DetailViaticoView(DetailView):     
        template_name = 'viaticos/templates/detail_viatico.html'
        model = viaticodiario
        def get_context_data(self, **kwargs):                        
                context = super(DetailViaticoView,self).get_context_data(**kwargs)
                try:
                        context['viatico'] = get_object_or_404(self.model,slug=self.kwargs['slug'])
                        otros=get_object_or_404(self.model,slug=self.kwargs['slug'])
                        otrosviaticos=OtrosViajes.objects.filter(slug_viaticos=otros.slug)
                        if otrosviaticos.exists():
                                via_urbana=[]
                                via_rural=[]
                                via_frontera=[]
                                for v in otrosviaticos:
                                        if v.fecha_inicial_urbana is not None and v.fecha_llegada_urbana is not None:
                                                via_urbana.append({                                                        
                                                        "fecha_inicial":v.fecha_inicial_urbana,
                                                        "fecha_llegada":v.fecha_llegada_urbana,
                                                        "hora_salida":v.horaSalida_urbana,
                                                        "hora_llegada":v.horallegada_urbana,
                                                        "lugar":v.lugar_urbana,                                                        
                                                        "tiempo":v.calculohora_urbana                                                        
                                                })
                                        if v.fecha_inicial_rural is not None and v.fecha_llegada_rural is not None:
                                                via_rural.append({                                                        
                                                        "fecha_inicial":v.fecha_inicial_rural,
                                                        "fecha_llegada":v.fecha_llegada_rural,
                                                        "hora_salida":v.horaSalida_rural,
                                                        "hora_llegada":v.horallegada_rural,
                                                        "lugar":v.lugar_rural,                                                        
                                                        "tiempo":v.calculohora_rural                                      
                                                })
                                        if v.fecha_inicial_frontera is not None and v.fecha_llegada_frontera is not None:
                                                via_frontera.append({                                                        
                                                        "fecha_inicial":v.fecha_inicial_frontera,
                                                        "fecha_llegada":v.fecha_llegada_frontera,
                                                        "hora_salida":v.horaSalida_frontera,
                                                        "hora_llegada":v.horallegada_frontera,
                                                        "lugar":v.lugar_frontera,                                                                      
                                                        "tiempo":v.calculohora_frontera                                
                                                })     

                                if len(via_urbana) != 0:
                                        context['otrosviajes']= via_urbana
                                if len(via_rural) != 0:
                                        context['otros_rural']= via_rural
                                if len(via_frontera) != 0:
                                        context['otros_frontera']= via_frontera
                                context["valor"] =True
                        else:
                                context["valor"] =False

                except Http404:
                        return redirect('viaticos:detail')       
                return context


#return HttpResponse(slug)
def concatenar(numero_factura):
        cadena=str(numero_factura)
        cadena="0."+cadena
        number=float(cadena)
        return  number
class ReporteViatico(BasePlatypusReportOther):
    def __init__(self):
        self.begin(orientation = 'LANDSCAPE', rightMargin = 28, leftMargin = 28, topMargin = 36, bottomMargin = 28)

    def get(self, request, *args, **kwargs):        
        self.draw()
        self.write(onFirstPage = self.title)
        return self.response

    def title(self,canvas, document,**kwargs):

        title = 'BOLETAS REGISTRADAS'
        canvas.saveState()
        
        archivo_imagen = settings.MEDIA_ROOT+'\images\logoo.png'
        archivo_imagen1 = settings.MEDIA_ROOT+'\images\money.png'
                
        canvas.setFont("Helvetica-Bold", 11)
        canvas.drawCentredString(self.x_start + self.width_internal / 2, self.y_start - 25, u"GOBIERNO AUTONOMO DEPARTAMENTAL DE POTOSI")
        canvas.setFont("Helvetica-Bold", 11)
        canvas.drawCentredString(self.x_start + self.width_internal / 2, self.y_start - 45, u"Secretaria Departamental Administracion y Financiera")
      
        canvas.drawImage(archivo_imagen1, self.x_start + 600,self.y_start - 64, 55, 55, preserveAspectRatio = True)
        
        canvas.setLineWidth(1)
        canvas.line(self.x_start+180, self.y_start-60, 585, self.y_start-60)
        
        canvas.setFont("Helvetica-Bold", 10)
        canvas.drawCentredString(self.x_start + self.width_internal / 2, self.y_start - 72, u"DETALLE DE PASAJES Y VIÁTICOS DEL PERSONAL DEL GOBIERNO AUTÓNOMO")
        
        #gestion=2019
        #canvas.setFont("Helvetica-Bold", 10)
        #canvas.drawCentredString(self.x_start + self.width_internal / 2, self.y_start - 87, gestion)

        self.draw_left_image(canvas = canvas,
            url = archivo_imagen,
            x = self.x_start + 70, 
            y = self.y_start - 8, 
            w = 55, 
            h = 55
        )
    def draw(self,):
        self.add(Spacer(1, 90))
        self.draw_table()
    def draw_table(self):
        basic_style_full_doble = self.get_basic_style_full_doble()
        basic_style_body = self.get_basic_style_body()
        basic_style_full_doble_void = self.get_basic_style_full_doble_void()
        
        date = datetime.now()
        viaticos=viaticodiario.objects.filter(
                timestamp__day=date.day, 
                timestamp__month=date.month, 
                timestamp__year=date.year,estado=1).order_by('-centralizador','ue','prog','act')
        
        #viaticos=viaticodiario.objects.all()
        self.add(self.draw_in_table_top(0,viaticos,self.get_basic_style_full_doble_top(),basic_style_body, basic_style_full_doble_void, True))
        self.add(self.draw_in_table_result(0,viaticos,self.get_basic_style_full_doble_button(), basic_style_body, basic_style_full_doble_void, True)) 
        self.add(Spacer(1, 20))
        self.add(self.draw_in_table_resumen(0,viaticos,self.get_basic_style_full_doble_resumen(), basic_style_body, basic_style_full_doble_void, True)) 
    def draw_in_table_top(self,index = 0,datereference = None,style = None,stylealt = None, stylevoid = None, hasheader = False):
        supercabecera = [
                'N°',
                'NOMBRES Y APELLIDOS',
                'C.I.',
                'PASAJES',
                'PEAJES',
                'VIATICO',
                '',
                '',
                'TOTAL A CANCELAR',
                'CONTROL PRESUPUESTARIO',
                '',
                '',
                '',
                'N° CUENTA'
        ]
        cabecera = [
            '',
            '',
            '',
            '',
            '',
            'IMPORTES',
            'RC-IVA',
            'LIQ. PAGABLE',
            '',
            'U.E',
            'PROG',
            'PROY',
            'ACT',
            ''		
        ]
        preparandojson = []
        cont=1
        if datereference.exists(): 
                for viatico in datereference:                        
                        ue=0
                        prog=0
                        act=0
                        proy=0
                        if viatico.ue < 10:
                                ue='%s%s'%(0,viatico.ue)
                        else:
                                ue=viatico.ue
                        
                        if viatico.prog < 10:
                                prog='%s%s'%(0,viatico.prog)
                        else:
                                prog=viatico.prog

                        if viatico.act < 10:
                                act='%s%s'%(0,viatico.act)
                        else:
                                act=viatico.act

                        if viatico.proy < 10:
                                proy='%s%s'%(0,viatico.proy)
                        else:
                                proy=viatico.proy
                        
                        preparandojson.append({
                                "ci":viatico.solicitante.ci,
                                "NombreCompleto":'%s %s %s'%(viatico.solicitante.nombre.upper(),viatico.solicitante.apaterno.upper(),viatico.solicitante.amaterno.upper()),
                                "id":cont,
                                "pasaje": self.redondear(viatico.pasaje),
                                "peaje": self.redondear(viatico.peaje),
                                "importe": self.redondear(viatico.Monto_pagado),
                                "rciva": self.redondear(viatico.RC_IVA),
                                "liqpagable": self.redondear(viatico.Liquido_pagable),
                                "liqtotalcancelar": self.redondear(viatico.totalC),
                                "ue":ue,
                                "prog":prog,
                                "act":act,
                                "proy":viatico.proy,
                                "numero":viatico.solicitante.bcontrol
                        })
                        cont=cont+1
        detalles = [(
                via['id'],
                via['NombreCompleto'],
                via['ci'],
                via['pasaje'],
                via['peaje'],
                via['importe'],
                via['rciva'],
                via['liqpagable'],
                via['liqtotalcancelar'],
                via['ue'],
                via['prog'],
                via['proy'],
                via['act'],
                via['numero']
                ) for via in preparandojson]
        cm = 29
        #cm = 23.4
        if hasheader:
            table = Table(
                [supercabecera] + [cabecera] + detalles,
                colWidths = [
                    0.9 * cm, 
                    5 * cm, 
                    1.5 * cm,  
                    1.5 * cm, 
                    1.5 * cm, 
                    1.5 * cm, 
                    1.4 * cm, 
                    2 * cm,
                    2.7 * cm,
                    1 * cm,
                    1 * cm,
                    1 * cm,
                    1 * cm,
                    2.1 * cm
                ],
                splitByRow = 1,
                repeatRows = 0
            )
        
        if style:
            if hasheader:
                table.setStyle(style)
            elif stylealt:
                table.setStyle(stylealt)
        return table
    def redondear(self,valor=None):
        leter=str(valor)
        for le in xrange(len(leter)):
                if leter[le]=='.':
                        if (le+2)==len(leter):
                                return '%s%s'%(valor,0) 
                        else:     
                                return valor
    def draw_in_table_resumen(self,index = 0, datereference = None,style = None, stylealt = None, stylevoid = None, hasheader = False):
        cabecera = [
            'RESUMEN',
            ' '
        ]
        Sumatoriapasaje=0
        Sumatoriapeaje=0
        Sumatoriaimporte=0
        Sumatoriarciva=0
        Sumatorialiqpagable=0
        Sumatoriatotalcancelar=0
        preparandojson=[]
        for viatico in datereference:                
                Sumatoriapasaje=Sumatoriapasaje+viatico.pasaje
                Sumatoriapeaje=Sumatoriapeaje+viatico.peaje
                Sumatoriaimporte=Sumatoriaimporte+viatico.Monto_pagado
                Sumatoriarciva=Sumatoriarciva+viatico.RC_IVA
                Sumatorialiqpagable=Sumatorialiqpagable+viatico.Liquido_pagable
                Sumatoriatotalcancelar=Sumatoriatotalcancelar+viatico.totalC  
            
        detalles = [(
                "DESCRIPCIÓN",
                "IMPORTE EN BS."
                )]
        VIATICO = [(
                "VIÁTICO",
                self.redondear(Sumatoriaimporte)
                )]
        PEAJES = [(
                "PEAJES",
                self.redondear(Sumatoriapeaje)
                )]
        PASAJES = [(
                "PASAJES",
                self.redondear(Sumatoriapasaje)
                )]
        TOTAL = [(
                "TOTAL",
                self.redondear(Sumatoriapasaje+Sumatoriapeaje+Sumatoriaimporte)
                )]
        RC = [(
                "Menos RC - IVA",
                self.redondear(Sumatoriarciva)
                )]
        LIQUIDO = [(
                "LIQ. PAGABLE",
                self.redondear(Sumatorialiqpagable)
                )]
        cm = 29
        #cm = 23.4
        if hasheader:
            table = Table(
                [cabecera] + detalles+VIATICO+PEAJES+PASAJES+TOTAL+RC+LIQUIDO,
                colWidths = [
                    3 * cm, 
                    3 * cm                    
                ],
                splitByRow = 1,
                repeatRows = 1
            )
        if style:
            if hasheader:
                table.setStyle(style)
            elif stylealt:
                table.setStyle(stylealt)
        if len(datereference) == 0 and stylevoid is not None:
            table.setStyle(stylevoid)
        return table
    def draw_in_table_result(self,index = 0, datereference = None,style = None, stylealt = None, stylevoid = None, hasheader = False):
        Totalsumatoriapasaje=0
        Totalsumatoriapeaje=0
        Totalsumatoriaimporte=0
        Totalsumatoriarciva=0
        Totalsumatorialiqpagable=0
        Totalsumatoriatotalcancelar=0
        for viatico in datereference:
                Totalsumatoriapasaje=Totalsumatoriapasaje+viatico.pasaje
                Totalsumatoriapeaje=Totalsumatoriapeaje+viatico.peaje
                Totalsumatoriaimporte=Totalsumatoriaimporte+viatico.Monto_pagado
                Totalsumatoriarciva=Totalsumatoriarciva+viatico.RC_IVA
                Totalsumatorialiqpagable=Totalsumatorialiqpagable+viatico.Liquido_pagable
                Totalsumatoriatotalcancelar=Totalsumatoriatotalcancelar+viatico.totalC
        detalles = [(
                "TOTAL",
                " ",
                " ",
                self.redondear(Totalsumatoriapasaje),
                self.redondear(Totalsumatoriapeaje),
                self.redondear(Totalsumatoriaimporte),
                self.redondear(Totalsumatoriarciva),
                self.redondear(Totalsumatorialiqpagable),
                self.redondear(Totalsumatoriatotalcancelar),
                " ",
                " ",
                " ",
                " ",
                " ",
                )]
        cm = 29
        #cm = 23.4
        if hasheader:
            table = Table(
                detalles,
                colWidths = [
                    0.9 * cm, 
                    5 * cm, 
                    1.5 * cm,  
                    1.5 * cm, 
                    1.5 * cm, 
                    1.5 * cm, 
                    1.4 * cm, 
                    2 * cm,
                    2.7 * cm,
                    1 * cm,
                    1 * cm,
                    1 * cm,
                    1 * cm,
                    2.1 * cm
                ],
                splitByRow = 1,
                repeatRows = 1
            )
        if style:
            if hasheader:
                table.setStyle(style)
            elif stylealt:
                table.setStyle(stylealt)
        if len(datereference) == 0 and stylevoid is not None:
            table.setStyle(stylevoid)
        return table

#FIN DE GESTION DE VIATICOS

# EN COMISION

class encomisionView(TemplateView):
        template_name = "viaticos/encomision.html"
        def isTotalhora(self,valor):
                var1='%s %s'%(valor[0],valor[1])
                var2='%s %s'%(valor[2],valor[3])
                start = datetime.strptime(var1, '%Y-%m-%d %H:%M:%S') 
                ends = datetime.strptime(var2, '%Y-%m-%d %H:%M:%S')
                diff = relativedelta(start, ends) 
                dias=(diff.days)*(-1)
                horas=(diff.hours)*(-1)
                minutos=(diff.minutes)*(-1)
                Totalhoras=int(float(horas*60)+(float(dias*24)*60)+minutos)
                return Totalhoras                         
        def get_context_data(self, **kwargs):
                context = super(encomisionView, self).get_context_data(**kwargs)
                date = datetime.now()        
                viatico=viaticodiario.objects.filter(timestamp__year=date.year)
                Totalhoras=0
                Totalrestante=0
                concluidos=[]
                en_proceso=[]
                no_realizados=[]
                meses=0
                dias=0       
                dias_list=["Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]

                if date.month<10:
                        meses=('%s%s'%(0,date.month))
                else:
                        meses=date.month
                if date.day<10:
                        dias=('%s%s'%(0,date.day))
                else:
                        dias=date.day
                fechahoy=('%s-%s-%s'%(date.year,meses,dias))
                second=0
                minute=0
                if date.minute<10:
                        minute=('%s%s'%(0,date.minute))
                else:
                        minute=date.minute
                if date.second<10:
                        second=('%s%s'%(0,date.second))
                else:
                        second=date.second

                horahoy=('%s:%s:%s'%(date.hour,minute,second)) 
                #uno CONCLUIDOS
                valor_pro=0
                error=""
                if self.request.GET.get('dias_id') != None and self.request.GET.get('dias_id') !="":
                        
                        mes_list=0
                        for d in xrange(len(dias_list)):
                                if dias_list[d] == self.request.GET['dias_id']:
                                        mes_list=d
                                        break                
                        viatic = viaticodiario.objects.filter(fecha_salida__month=(mes_list+1),fecha_salida__year=date.year)                
                        if viatic.count() == 0:
                                error=error+"No existe Viaticos con esa fecha"
                                for via in viaticodiario.objects.filter(timestamp__year=date.year).order_by('timestamp')[:20]:
                                        Totalhoras=self.isTotalhora([via.fecha_salida,via.horaSalida,via.fecha_legada,via.horallegada])
                                        Totalrestante=self.isTotalhora([via.fecha_salida,via.horaSalida,fechahoy,horahoy])
                                        if via.fecha_salida < datetime.strptime(fechahoy,"%Y-%m-%d").date() and via.fecha_legada <= datetime.strptime(fechahoy,"%Y-%m-%d").date():
                                                if Totalrestante >= Totalhoras:
                                                        concluidos.append({
                                                                'nombre':via.solicitante.nombre,
                                                                'apellidoP':via.solicitante.apaterno,
                                                                'apellidoM':via.solicitante.amaterno,
                                                                'ncontrol':via.ncontrol,
                                                                'ci':via.solicitante.ci,
                                                                'fecha_salida':via.fecha_salida,
                                                                'fecha_llegada':via.fecha_legada,
                                                                'monto':via.totalC,
                                                                'lugar':via.lugar,
                                                                'slug':via.slug,
                                                        }) 
                        else:
                                for via in viatic:                               
                                        concluidos.append({
                                                'nombre':via.solicitante.nombre,
                                                'apellidoP':via.solicitante.apaterno,
                                                'apellidoM':via.solicitante.amaterno,
                                                'ncontrol':via.ncontrol,
                                                'ci':via.solicitante.ci,
                                                'fecha_salida':via.fecha_salida,
                                                'fecha_llegada':via.fecha_legada,
                                                'monto':via.totalC,
                                                'lugar':via.lugar,
                                                'slug':via.slug,
                                        })                
                else:                        
                        for via in viaticodiario.objects.filter(timestamp__year=date.year).order_by('timestamp')[:20]:
                                Totalhoras=self.isTotalhora([via.fecha_salida,via.horaSalida,via.fecha_legada,via.horallegada])
                                Totalrestante=self.isTotalhora([via.fecha_salida,via.horaSalida,fechahoy,horahoy])
                           
                                if via.fecha_salida < datetime.strptime(fechahoy,"%Y-%m-%d").date() and via.fecha_legada <= datetime.strptime(fechahoy,"%Y-%m-%d").date():
                                        if Totalrestante >= Totalhoras:
                                                concluidos.append({
                                                        'nombre':via.solicitante.nombre,
                                                        'apellidoP':via.solicitante.apaterno,
                                                        'apellidoM':via.solicitante.amaterno,
                                                        'ncontrol':via.ncontrol,
                                                        'ci':via.solicitante.ci,
                                                        'fecha_salida':via.fecha_salida,
                                                        'fecha_llegada':via.fecha_legada,
                                                        'monto':via.totalC,
                                                        'lugar':via.lugar,
                                                        'slug':via.slug,
                                                }) 

                                        
                paginator  = Paginator(concluidos,15)
                pages = self.request.GET.get('pages')
                try:
                        viaticossconcluidos = paginator.page(pages)
                except PageNotAnInteger:
                        viaticossconcluidos = paginator.page(1)
                except EmptyPage:
                        viaticossconcluidos = paginator.page(paginator.num_pages)
                
                #dos EN PROCESO    
                for via in viatico:
                        
                        Totalhoras=self.isTotalhora([via.fecha_salida,via.horaSalida,via.fecha_legada,via.horallegada])
                        Totalrestante=self.isTotalhora([via.fecha_salida,via.horaSalida,fechahoy,horahoy])
                        
                        if Totalhoras == 0:
                                barra=0
                        else:
                                barra=int((float(Totalrestante)/float(Totalhoras))*100)
                        #datetime.datetime.strptime(deadline, "%B %d, %Y").date()
                        if via.fecha_salida >= datetime.strptime(fechahoy,"%Y-%m-%d").date() or datetime.strptime(fechahoy,"%Y-%m-%d").date() <= via.fecha_legada:
                        #if via.fecha_salida > datetime.strptime(fechahoy,"%Y-%m-%d").date() or datetime.strptime(fechahoy,"%Y-%m-%d").date() < via.fecha_legada:
                                if datetime.strptime(horahoy,'%H:%M:%S').time()<=via.horallegada or datetime.strptime(fechahoy,"%Y-%m-%d").date() <= via.fecha_legada:
                                        if Totalrestante <= Totalhoras:                                        
                                                if barra>0:         
                                                        en_proceso.append({
                                                                'nombre':via.solicitante.nombre,
                                                                'apellidoP':via.solicitante.apaterno,
                                                                'apellidoM':via.solicitante.amaterno,
                                                                'ncontrol':via.ncontrol,
                                                                'ci':via.solicitante.ci,
                                                                'fecha_salida':via.fecha_salida,
                                                                'fecha_llegada':via.fecha_legada,
                                                                'monto':via.totalC,
                                                                'lugar':via.lugar,
                                                                'slug':via.slug,
                                                                'barra':barra,
                                                        })
                

                paginator  = Paginator(en_proceso,15)
                pagess = self.request.GET.get('pag')
                try:
                        viaticoss_proceso = paginator.page(pagess)
                except PageNotAnInteger:
                        viaticoss_proceso = paginator.page(1)
                except EmptyPage:
                        viaticoss_proceso = paginator.page(paginator.num_pages)
                
                if self.request.GET.get('valor_proceso') == None:
                        valor_pro=2
                else:                
                        valor_pro=self.request.GET.get('valor_proceso')
                
                if self.request.GET.get('dias_id') != None:               
                        valor_pro=1
                #tres  NO REALIDOS     
                for via in viatico:
                        if via.fecha_salida > datetime.strptime(fechahoy,"%Y-%m-%d").date() and via.fecha_legada > datetime.strptime(fechahoy,"%Y-%m-%d").date() :
                                no_realizados.append({
                                        'nombre':via.solicitante.nombre,
                                        'apellidoP':via.solicitante.apaterno,
                                        'apellidoM':via.solicitante.amaterno,
                                        'ncontrol':via.ncontrol,
                                        'ci':via.solicitante.ci,
                                        'fecha_salida':via.fecha_salida,
                                        'fecha_llegada':via.fecha_legada,
                                        'monto':via.totalC,
                                        'lugar':via.lugar,
                                        'slug':via.slug,
                                })
                paginator  = Paginator(no_realizados,12)
                page = self.request.GET.get('paged')
                try:
                        viaticossno_realizados = paginator.page(page)
                except PageNotAnInteger:
                        viaticossno_realizados = paginator.page(1)
                except EmptyPage:
                        viaticossno_realizados = paginator.page(paginator.num_pages)
                        
                
                context['viatico_no_realizados']=viaticossno_realizados
                context['viatico_no_realizados_tama']=len(no_realizados)
                context['viaticoconcluido']=viaticossconcluidos
                context['viaticoconcluido_tama']=len(concluidos)
                context['viaticoss_proceso']=viaticoss_proceso
                context['viaticoss_proceso_tama']=len(en_proceso)
                context['valor_pro']=valor_pro
                context['dias']=dias_list
                context['busqueda_no_realizados']=self.request.GET.get('dias_id')
                context['error']=error                              
                return context


#FIN EN COMISION

# FUNCTIONES EXTRAS   
def isNumber(valor):
        if valor.isdigit() == False:
                return True
        return False
def isString(valor):
        if valor.isalpha() == True:
                return True
        return False
def isDecimal(valor):
        if valor.isdecimal() == True:
                return True
        return False
def isDouble(valor):
        numero=str(valor)
        numerouno=""
        numerodos=""
        uno=True
        dos=False
        coma=False
        punto=False
        number=False
        for n in xrange(len(numero)):
                if numero[n]==',':
                        coma=True
                        break
                if numero[n]=='.':
                        punto=True
                        break
        if coma==False and punto==False:
                number=True
        for n in xrange(len(numero)):
               
                if number:
                        numerouno=numerouno+numero[n] 
                if coma:
                        if numero[n]!=',':
                                if uno:
                                        numerouno=numerouno+numero[n]
                                if dos:
                                        numerodos=numerodos+numero[n]
                        else:
                                uno=False
                                dos=True
                if punto:
                        if numero[n]!='.':
                                if uno:
                                        numerouno=numerouno+numero[n]
                                if dos:
                                        numerodos=numerodos+numero[n]
                else:
                        uno=False
                        dos=True

        if isDecimal(numerouno):
                if isDecimal(numerodos):
                        return False
                return False
        else:
                return True
def isSolo(valor):
        numero=str(valor)
        coma=False
        punto=False
        for n in xrange(len(numero)):
                if numero[n]==',':
                        coma=True
                        break
                if numero[n]=='.':
                        punto=True
                        break
        if coma==True or punto==True:
                return False
        return True     
def isConvert(valor):
        numero=str(valor)
        numerouno=""
        numerodos=""
        uno=True
        dos=False
        coma=False
        punto=False
        number=False 
        for n in xrange(len(numero)):
                if numero[n]==',':
                        coma=True
                        break
                if numero[n]=='.':
                        punto=True
                        break

        if coma==False and punto==False:
                number=True

        for n in xrange(len(numero)):
                if number:
                        numerouno=numerouno+numero[n] 
                if coma:
                        if numero[n]!=',':
                                if uno:
                                        numerouno=numerouno+numero[n]
                                if dos:
                                        numerodos=numerodos+numero[n]
                        else:
                                uno=False
                                dos=True
                if punto:
                        if numero[n]!='.':
                                if uno:
                                        numerouno=numerouno+numero[n]
                                if dos:
                                        numerodos=numerodos+numero[n]
                        else:
                                uno=False
                                dos=True
        if number:
                return '%s.%s'%(numerouno,0)
        if isDecimal(numerouno):
                if isDecimal(numerodos):
                        return '%s.%s'%(numerouno,numerodos)
# FIN DE FUNCIONES EXTRAS

# PETICIONES AJAX
def busqueda(request):
        if request.is_ajax():
                if isNumber(request.GET['id']):
                        response=JsonResponse({'error': 500})
                else:
                        consult=empleado.objects.filter(ci=request.GET['id'])               
                        if consult.exists():
                                user=empleado.objects.filter(ci=request.GET['id'])
                                for u in user:
                                        response=JsonResponse({ 'id': u.id,
                                                'nombre':u.nombre,
                                                'paterno':u.apaterno,
                                                'materno':u.amaterno,
                                                'ci':u.ci,
                                                'cargo':u.secretaria.nombreS,
                                                'error': 200,
                                        })
                        else:
                                response=JsonResponse({'error': 403})
                return HttpResponse(response.content)
        else:
                return HttpResponse("Solo Ajax") 
def getMontos(request):
        id_tipo = request.GET['id']
        monto=Monto.objects.filter(Tipo_viatico_id=id_tipo,valido=1)
        mont=[]
        bs=""
        for m in monto:
                if m.identificacion == 1:
                        bs=" Bs."
                else:
                        bs=" $."
                mont.append({
                        "pk":m.id,
                        "Nombre":m.Nombre,
                        "Cantidad":'%s%s'%(m.Cantidad,bs),  
                                   
                })
        data_json=json.dumps(mont)                                        
        mimetype="application/json"
        return HttpResponse(data_json,mimetype)
        '''if monto:
                data=serializers.serialize('json',monto,fields=('Nombre','Cantidad'))
                return HttpResponse(data,content_type="application/json")'''

# esta parte es para ver las posiciones del ajax
def getPosicion(request):
        id_tipo = request.GET['id']
        monto=Monto.objects.filter(Tipo_viatico_id=id_tipo,valido=1)
        mont=[]
        for m in monto:              
                mont.append({
                        "pk":m.id                                  
                })
        data_json=json.dumps(mont)                                        
        mimetype="application/json"
        return HttpResponse(data_json,mimetype)
    

# FIN DE PETICIONES AJAX

# MODULO CENTRALIZADOR

class Reporte_Centralizador(Base_Excel):
        def __init__(self):
                self.begin(nombre = 'Centralizador')
	def cabecera(self,worksheet):          
                title='          Gobierno Autonomo Departamental de Potosi'
                worksheet.write_merge(1, 1, 2, 7,title.encode('utf8'),self.title_style)
                worksheet.write_merge(2, 2, 1, 8,'        Secretaria Departamental Administracion y Financiera',self.title_style2)
                worksheet.write_merge(4, 4, 2, 7,'      DETALLES  DE PASAJES - PEAJES Y VIATICOS',self.title_style3)
                worksheet.write_merge(5, 5, 4, 5,'%s - %s'%(' GESTION',self.date.year),self.title_style3)
                worksheet.write_merge(7, 7, 0, 0,'N. DE PERSONAS',self.header_style)
                worksheet.write_merge(7, 7, 1, 1,'INF. CONT.',self.header_style)
                worksheet.write_merge(7, 7, 2, 2,'C-31',self.header_style)
                worksheet.write_merge(7, 7, 3, 3,'PASAJES',self.header_style)
                worksheet.write_merge(7, 7, 4, 4,'PEAJES',self.header_style)
                worksheet.write_merge(7, 7, 5, 5,'IMPORTES',self.header_style)
                worksheet.write_merge(7, 7, 6, 6,'RC-IVA',self.header_style)
                worksheet.write_merge(7, 7, 7, 7,'LIQ. PAGABLE',self.header_style)
                worksheet.write_merge(7, 7, 8, 8,'TOTAL A CANCELAR',self.header_style)
	def tabla(self,worksheet):
                Totalsumatoriapasaje=0
		Totalsumatoriapeaje=0
                Totalsumatoriaimporte=0
                Totalsumatoriarciva=0
                Totalsumatorialiqpagable=0
                Totalsumatoriatotalcancelar=0   
                Sumatoriapasaje=0
                Sumatoriapeaje=0
                Sumatoriaimporte=0
                Sumatoriarciva=0
                Sumatorialiqpagable=0
                Sumatoriatotalcancelar=0
                numeropersonas=0
                preparandojson=[]
                viatico=viaticodiario.objects.filter(timestamp__year=self.date.year).distinct('centralizador')
                for vis in viatico:
                        ViaticoControl=viaticodiario.objects.filter(centralizador=vis.centralizador)
                        if ViaticoControl.exists():      
                                for vi in ViaticoControl:
                                        numeropersonas=numeropersonas+1
                                        Sumatoriapasaje=Sumatoriapasaje+vi.pasaje
                                        Sumatoriapeaje=Sumatoriapeaje+vi.peaje
                                        Sumatoriaimporte=Sumatoriaimporte+vi.Monto_pagado
                                        Sumatoriarciva=Sumatoriarciva+vi.RC_IVA
                                        Sumatorialiqpagable=Sumatorialiqpagable+vi.Liquido_pagable
                                        Sumatoriatotalcancelar=Sumatoriatotalcancelar+vi.totalC
                                        Totalsumatoriapasaje=Totalsumatoriapasaje+vi.pasaje
                                        Totalsumatoriapeaje=Totalsumatoriapeaje+vi.peaje
                                        Totalsumatoriaimporte=Totalsumatoriaimporte+vi.Monto_pagado
                                        Totalsumatoriarciva=Totalsumatoriarciva+vi.RC_IVA
                                        Totalsumatorialiqpagable=Totalsumatorialiqpagable+vi.Liquido_pagable
                                        Totalsumatoriatotalcancelar=Totalsumatoriatotalcancelar+vi.totalC
                                preparandojson.append({
                                        "NumeroPersonas":numeropersonas,
                                        "infcont":vis.centralizador,
                                        "cc":31,
                                        "totalpasaje": Sumatoriapasaje,
                                        "totalpeaje": Sumatoriapeaje,
                                        "totalimporte": Sumatoriaimporte,
                                        "totalrciva": Sumatoriarciva,
                                        "totalliqpagable": Sumatorialiqpagable,
                                        "totalliqtotalcancelar": Sumatoriatotalcancelar
                                })
                        Sumatoriapasaje=0
                        Sumatoriapeaje=0
                        Sumatoriaimporte=0
                        Sumatoriarciva=0
                        Sumatorialiqpagable=0
                        Sumatoriatotalcancelar=0
                        numeropersonas=0
                row_num = 7
                for via in preparandojson:
                        row_num += 1
                        row = [ via['NumeroPersonas'],
                                via['infcont'],
                                " ",
                                via['totalpasaje'],
                                via['totalpeaje'],
                                via['totalimporte'],
                                via['totalrciva'],
                                via['totalliqpagable'],
                                via['totalliqtotalcancelar']
                        ]
                        for col_num in range(len(row)):
                                if col_num == 3 or col_num == 4 or col_num == 5 or  col_num == 6 or col_num == 7 or col_num == 8:
                                        worksheet.write(row_num,col_num, row[col_num],self.redondeos_style)
                                else:
                                        worksheet.write(row_num,col_num, row[col_num],self.body_style)
                
                self.insert(worksheet,9,row_num)
                
	def get(self, request, *args, **kwargs):
                self.tama(self.worksheet)
                self.cabecera(self.worksheet)
                self.tabla(self.worksheet)
                self.workbook.save(self.response)
		return self.response
class Reporte_Centralizador_Secre(Base_Excel):
        def __init__(self):
                self.begin(nombre = 'CentralizadorSecretarias')
        def cabecera(self,worksheet,cent_id):
              
                worksheet.col(0).width = 20 * 180
                worksheet.col(0).height = 20 * 40

                tamamuygrande=[36,7,17,24,29,39]
                posiciontamamuygrande=[{"x":0,"y":8}]
                
                tamagrande=[1,4,14,19,20,30,33]
                posiciontamagrande=[{"x":2,"y":7}]

                tamapequeno=[2,3,12,18,21,32,37]
                posiciontamapequeno=[{"x":3,"y":7}]

                tamasemifgrande=[5,6,8,9,10,11,13,15,16,22,23,25,26,27,28,31,34,35,38]
                posiciontamasemifgrande=[{"x":1,"y":8}]         
                uno=True
                dos=True
                tres=True
                cuatro=True
                x=0
                y=0
                titulo=""      
                if uno:
                        for ta in tamamuygrande:
                                if int(ta) == int(cent_id):
                                        for po in posiciontamamuygrande:
                                                x=po['x']
                                                y=po['y']
                                        dos=False
                                        tres=False
                                        cuatro=False
                                        break
                if dos:
                        for ta in tamagrande:
                                if int(ta) == int(cent_id):
                                        for po in posiciontamagrande:
                                                x=po['x']
                                                y=po['y']
                                        tres=False
                                        cuatro=False
                                        break
                if tres:
                        for ta in tamapequeno:
                                if int(ta) == int(cent_id):
                                        for po in posiciontamapequeno:
                                                x=po['x']
                                                y=po['y']

                                        cuatro=False
                                        break
                if cuatro:
                        for ta in tamasemifgrande:
                                if int(ta) == int(cent_id):
                                        for po in posiciontamasemifgrande:
                                                x=po['x']
                                                y=po['y']
                                        break
                for nom in SecresubSecre.objects.filter(id=cent_id):
                        titulo=nom.descripcion.descripcion
                        break
                title='    Gobierno Autonomo Departamental de Potosi'
                worksheet.write_merge(1, 1, 2, 7,title.encode('utf8'),self.title_style)
                worksheet.write_merge(2, 2, 1, 8,'      Secretaria Departamental Administracion y Financiera',self.title_style2)
                worksheet.write_merge(4, 4, 2, 7,'DETALLES  DE PASAJES - PEAJES Y VIATICOS',self.title_style3)
                worksheet.write_merge(5, 5, 3, 5,'%s - %s'%('          GESTION',self.date.year),self.title_style3)
                worksheet.write_merge(6, 6, x, y,'   '+titulo,self.title_style3)
                worksheet.write_merge(8, 8, 0, 0,'N. DE PERSONAS',self.header_style)
                worksheet.write_merge(8, 8, 1, 1,'INF. CONT.',self.header_style)
                worksheet.write_merge(8, 8, 2, 2,'C-31',self.header_style)
                worksheet.write_merge(8, 8, 3, 3,'PASAJES',self.header_style)
                worksheet.write_merge(8, 8, 4, 4,'PEAJES',self.header_style)
                worksheet.write_merge(8, 8, 5, 5,'IMPORTES',self.header_style)
                worksheet.write_merge(8, 8, 6, 6,'RC-IVA',self.header_style)
                worksheet.write_merge(8, 8, 7, 7,'LIQ. PAGABLE',self.header_style)
                worksheet.write_merge(8, 8, 8, 8,'TOTAL A CANCELAR',self.header_style)
        def tabla(self,worksheet,cent_id):
                numeropersonas=0
                preparandojson=[]
                viatico=viaticodiario.objects.filter(timestamp__year=self.date.year).distinct('centralizador')
                for vis in viatico:
                        ViaticoControl=viaticodiario.objects.filter(centralizador=vis.centralizador,timestamp__year=self.date.year)
                        if ViaticoControl:
                                ViaticoRecorrer=SecresubSecre.objects.filter(descripcion__id=cent_id)
                                itemue=0
                                itemprog=0
                                itemact=0
                                for visss in ViaticoRecorrer:
                                        itemue=visss.ue
                                        itemprog=visss.prog
                                        itemact=visss.act
                                        break
                                pasaje=0
                                peaje=0
                                rciva=0
                                importe=0
                                liqpagable=0
                                totalcancelar=0
                                contt=0        
                                for vi in ViaticoControl:
                                        if itemue==vi.ue and itemprog==vi.prog and itemact==vi.act:
                                                pasaje=pasaje+vi.pasaje
                                                peaje=peaje+vi.peaje
                                                importe=importe+vi.Monto_pagado
                                                rciva=rciva+vi.RC_IVA
                                                liqpagable=liqpagable+vi.Liquido_pagable
                                                totalcancelar=totalcancelar+vi.totalC    
                                                contt=contt+1
                                                numeropersonas=numeropersonas+1
                                if contt>0:     
                                        preparandojson.append({
                                                "infcont":vis.centralizador,
                                                'cc':"233-34",
                                                "NumeroPersonas":numeropersonas,
                                                "pasaje": pasaje,
                                                "peaje": peaje,
                                                "importe":importe,
                                                "rciva": rciva,
                                                "liqpagable": liqpagable,
                                                "totalcancelar": totalcancelar
                                        })
                        numeropersonas=0
                        contt=0
                row_num = 8
                for via in preparandojson:
                        row_num += 1
                        row = [ via['NumeroPersonas'],
                                via['infcont'],
                                "",
                                via['pasaje'],
                                via['peaje'],
                                via['importe'],
                                via['rciva'],
                                via['liqpagable'],
                                via['totalcancelar']
                        ]
                        for col_num in range(len(row)):
                                if col_num == 3 or col_num == 4 or col_num == 5 or  col_num == 6 or col_num == 7 or col_num == 8:
                                        worksheet.write(row_num,col_num, row[col_num],self.redondeos_style)
                                else:
                                        worksheet.write(row_num,col_num, row[col_num],self.body_style)
                self.insert(worksheet,10,row_num)                
        def get(self, request, *args, **kwargs):
                cent_id =borrar(self.kwargs.get('slug'))                	                                
                self.tama(self.worksheet)
                self.cabecera(self.worksheet,cent_id)
                self.tabla(self.worksheet,cent_id)
                self.workbook.save(self.response)
		return self.response

class CentralizadorView(View):
        model=SecresubSecre.objects.all()
        varificar=False
        error=""
        context={}
        numeropersonas=0
        Totalsumatoriapasaje=0
        Totalsumatoriapeaje=0
        Totalsumatoriaimporte=0
        Totalsumatoriarciva=0
        Totalsumatorialiqpagable=0
        Totalsumatoriatotalcancelar=0
        pasaje=0
        peaje=0
        rciva=0
        importe=0
        liqpagable=0
        totalcancelar=0            
        preparandojson=[]
        date = datetime.now()
        def post(self,request,*args,**kwargs):
                self.preparandojson=[]
                area1=request.POST.get('area')                                                                        
                todos1=request.POST.get('todos') 
                
                if area1 == "..." and todos1 == "...":                        
                        self.varificar=True
                        self.error=self.error+'SELECCIONE ALGUNA PESTAÑA '+'\n'
                if len(self.error)==0:
                        self.varificar=False                        
                if self.varificar:                                                   
                        self.context={
                                'secretaria':self.model,
                                'error':self.error                              
                        }      
                        return render(request,"centralizador/centralizador.html",self.context)           
                if area1 == None and todos1 == None:                                                                
                        self.context={'secretaria':self.model}
                        return render(request,"centralizador/centralizador.html",self.context)
                else:
                        uno=True
                        dos=True
                        if area1 != '...' and todos1 != '...':
                                uno=False
                                dos=False
                                self.error="NO PUEDE SELECCIONAR LOS DOS A LA VES"
                                self.context={
                                        'secretaria':self.model,
                                        'error':self.error                              
                                }      
                      
                        if uno and area1 != '...' and todos1 == '...':                                                           
                                dos=False
                                monto_agrupacion_secre=[]                                                     
                                fecha_salida=""
                                viatico=viaticodiario.objects.filter(~Q(centralizador__isnull=True),timestamp__year=self.date.year).distinct('centralizador')
                                i=1
                                totol_personas=0
                                for vis in viatico:
                                        ViaticoControl=viaticodiario.objects.filter(centralizador=vis.centralizador,timestamp__year=self.date.year)
                                        if ViaticoControl:                                                       
                                                viaaa=get_object_or_404(SecresubSecre,descripcion__id=area1)                                                       
                                                itemue=viaaa.ue
                                                itemprog=viaaa.prog
                                                itemact=viaaa.act                                                
                                                contt=0        
                                                for vi in ViaticoControl:
                                                        if itemue==vi.ue and itemprog==vi.prog and itemact==vi.act:
                                                                self.pasaje=self.pasaje+vi.pasaje
                                                                self.peaje=self.peaje+vi.peaje
                                                                self.importe=self.importe+vi.Monto_pagado
                                                                self.rciva=self.rciva+vi.RC_IVA
                                                                self.liqpagable=self.liqpagable+vi.Liquido_pagable
                                                                self.totalcancelar=self.totalcancelar+vi.totalC    
                                                                contt=contt+1
                                                if contt>0:     
                                                        for vi in ViaticoControl:
                                                                fecha_salida=datetime.strptime(str(vi.timestamp),'%Y-%m-%d').strftime('%d/%m/%Y')  
                                                                break
                                                        for vi in ViaticoControl:
                                                                if itemue==vi.ue and itemprog==vi.prog and itemact==vi.act:
                                                                        self.numeropersonas=self.numeropersonas+1
                                                                        self.Totalsumatoriapasaje=self.Totalsumatoriapasaje+vi.pasaje
                                                                        self.Totalsumatoriapeaje=self.Totalsumatoriapeaje+vi.peaje
                                                                        self.Totalsumatoriaimporte=self.Totalsumatoriaimporte+vi.Monto_pagado
                                                                        self.Totalsumatoriarciva=self.Totalsumatoriarciva+vi.RC_IVA
                                                                        self.Totalsumatorialiqpagable=self.Totalsumatorialiqpagable+vi.Liquido_pagable
                                                                        self.Totalsumatoriatotalcancelar=self.Totalsumatoriatotalcancelar+vi.totalC    
                                                        totol_personas=totol_personas+self.numeropersonas
                                                        self.preparandojson.append({
                                                                "n":i,
                                                                "fechasalida":fecha_salida,
                                                                "infcont":vis.centralizador,
                                                                'cc':"233-34",
                                                                "NumeroPersonas":self.numeropersonas,
                                                                "pasaje":self.pasaje,
                                                                "peaje":self.peaje,
                                                                "importe":self.importe,
                                                                "rciva":self.rciva,
                                                                "liqpagable":self.liqpagable,
                                                                "totalcancelar":self.totalcancelar
                                                        })
                                                        i=i+1
                                        self.numeropersonas=0
                                        contt=0
                                sec=1           
                                self.context={
                                        'secretaria':self.model,
                                        'soloporsecretaria':sec,
                                        "presolo":self.preparandojson,
                                        'Totalsumatoriapasaje':self.Totalsumatoriapasaje,
                                        'totol_personas':totol_personas,
                                        'Totalsumatoriapeaje':self.Totalsumatoriapeaje,
                                        'Totalsumatoriaimporte':self.Totalsumatoriaimporte,
                                        'Totalsumatoriarciva':self.Totalsumatoriarciva,
                                        'Totalsumatorialiqpagable':self.Totalsumatorialiqpagable,
                                        'Totalsumatoriatotalcancelar':self.Totalsumatoriatotalcancelar,
                                        'secretaria_id':area1,
                                        'secretaria_id_url':'%s-%s'%(listaAleatorios(10),(str(area1)+letras())),
                                }                              
                        if dos and todos1 != '...' and area1 == '...' :                                                                
                                Sumatoriapasaje=0
                                Sumatoriapeaje=0
                                Sumatoriaimporte=0
                                Sumatoriarciva=0
                                Sumatorialiqpagable=0
                                Sumatoriatotalcancelar=0
                                cont=1
                                resultado=[]                
                                cantidadViaticos=0
                                #Name.objects.exclude(Q(alias__isnull=True) | Q(alias__exact=''))

                                viatico=viaticodiario.objects.filter(~Q(centralizador__isnull=True),timestamp__year=self.date.year).distinct('centralizador')
                                for vi in viatico:
                                        print('%s %s'%("CENTRALIZADOR = ",vi.centralizador))
                                for vis in viatico:
                                        if vis.centralizador !=None:
                                                ViaticoControl=viaticodiario.objects.filter(centralizador=vis.centralizador,timestamp__year=(self.date.year)).order_by('ue')                                        
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
                                                        for item in no_repetidos:
                                                                for vi in ViaticoControl:
                                                                        if item["ue"]==vi.ue and item["prog"]==vi.prog and item["act"]==vi.act:
                                                                                self.pasaje=self.pasaje+vi.pasaje
                                                                                self.peaje=self.peaje+vi.peaje
                                                                                self.importe=self.importe+vi.Monto_pagado
                                                                                self.rciva=self.rciva+vi.RC_IVA
                                                                                self.liqpagable=self.liqpagable+vi.Liquido_pagable
                                                                                self.totalcancelar=self.totalcancelar+vi.totalC
                                                                NombreSecre=SecresubSecre.objects.filter(ue=item["ue"],prog=item["prog"],act=item["act"])
                                                                Nombre=""
                                                                for secre in NombreSecre:
                                                                        Nombre=secre.descripcion.descripcion  
                                                                        break
                                                                if Nombre == "":                                
                                                                        Nombre="ADVERTENCIA NO EXISTE ESA SECRETARIA"
                                                                monto_agrupacion_secre.append({
                                                                        "secreatria":Nombre,
                                                                        "pasaje":self.pasaje,
                                                                        "peaje":self.peaje,
                                                                        "importe":self.importe,
                                                                        "rciva":self.rciva,
                                                                        "liqpagable":self.liqpagable,
                                                                        "totalcancelar":self.totalcancelar
                                                                })    
                                                                self.pasaje=0
                                                                self.peaje=0
                                                                self.rciva=0
                                                                self.importe=0
                                                                self.liqpagable=0
                                                                self.totalcancelar=0
                                                        for vi in ViaticoControl:                                                
                                                                self.numeropersonas=self.numeropersonas+1
                                                                cantidadViaticos=cantidadViaticos+1
                                                                Sumatoriapasaje=Sumatoriapasaje+vi.pasaje
                                                                Sumatoriapeaje=Sumatoriapeaje+vi.peaje
                                                                Sumatoriaimporte=Sumatoriaimporte+vi.Monto_pagado
                                                                Sumatoriarciva=Sumatoriarciva+vi.RC_IVA
                                                                Sumatorialiqpagable=Sumatorialiqpagable+vi.Liquido_pagable
                                                                Sumatoriatotalcancelar=Sumatoriatotalcancelar+vi.totalC                                                        
                                                                self.Totalsumatoriapasaje=self.Totalsumatoriapasaje+vi.pasaje
                                                                self.Totalsumatoriapeaje=self.Totalsumatoriapeaje+vi.peaje
                                                                self.Totalsumatoriaimporte=self.Totalsumatoriaimporte+vi.Monto_pagado
                                                                self.Totalsumatoriarciva=self.Totalsumatoriarciva+vi.RC_IVA
                                                                self.Totalsumatorialiqpagable=self.Totalsumatorialiqpagable+vi.Liquido_pagable
                                                                self.Totalsumatoriatotalcancelar=self.Totalsumatoriatotalcancelar+vi.totalC
                                                        fecha_salida=0
                                                        for vi in ViaticoControl:
                                                                fecha_salida=datetime.strptime(str(vi.timestamp),'%Y-%m-%d').strftime('%d/%m/%Y')  
                                                                break
                                                        total=[
                                                                {
                                                                        "totalpasaje": Sumatoriapasaje,
                                                                        "totalpeaje": Sumatoriapeaje,
                                                                        "totalimporte": Sumatoriaimporte,
                                                                        "totalrciva": Sumatoriarciva,
                                                                        "totalliqpagable": Sumatorialiqpagable,
                                                                        "totalliqtotalcancelar": Sumatoriatotalcancelar
                                                                }
                                                        ]
                                                        self.preparandojson.append({
                                                                "n":(cont+100),                                                        
                                                                "infcont":vis.centralizador,
                                                                "NumeroPersonas":self.numeropersonas,
                                                                "Fecha":fecha_salida,
                                                                "Secretarias" : monto_agrupacion_secre,
                                                                "Total":total
                                                        })
                                        Sumatoriapasaje=0
                                        Sumatoriapeaje=0
                                        Sumatoriaimporte=0
                                        Sumatoriarciva=0
                                        Sumatorialiqpagable=0
                                        Sumatoriatotalcancelar=0
                                        self.numeropersonas=0
                                        resultado=[]  
                                        cont=cont+1
                                #print(self.preparandojson)
                                paginator  = Paginator(self.preparandojson,10)
                                page = request.GET.get('page')
                                try:
                                        contacts = paginator.page(page)
                                except PageNotAnInteger:
                                        contacts = paginator.page(1)
                                except EmptyPage:
                                        contacts = paginator.page(paginator.num_pages)                                
                                self.context={
                                        'secretaria':self.model,
                                        "pre":self.preparandojson,
                                        'contacts': contacts,
                                        'contactslen':len(self.preparandojson),
                                        'cantidadviaticos':cantidadViaticos,
                                        'Totalsumatoriapasaje':self.Totalsumatoriapasaje,
                                        'Totalsumatoriapeaje':self.Totalsumatoriapeaje,
                                        'Totalsumatoriaimporte':self.Totalsumatoriaimporte,
                                        'Totalsumatoriarciva':self.Totalsumatoriarciva,
                                        'Totalsumatorialiqpagable':self.Totalsumatorialiqpagable,
                                        'Totalsumatoriatotalcancelar':self.Totalsumatoriatotalcancelar,
                                        'todos':todos1,
                                }                                                           
                        return render(request,"centralizador/centralizador.html",self.context)
        def get(self,request,*args,**kwargs): 
                '''secre=[]
                
                for s in self.model:
                        secre.append({
                                "id":'%s-%s'%(listaAleatorios(10),(str(s.id)+letras())),
                                "descripcion":s.descripcion.descripcion
                        })
                print(secre)'''
                self.context={'secretaria':self.model}
                return render(request,"centralizador/centralizador.html",self.context)
             
class BuscarSaldoView(TemplateView):
        template_name = 'centralizador/saldoclas.html'
        def get_context_data(self, **kwargs):
                context = super(BuscarSaldoView, self).get_context_data(**kwargs)
                date = datetime.now()
                secretarias=[]
                montosgastos=[]
                saldos=[]
                sumatoria=0
                for se in Secretaria.objects.all():
                        vi=viaticodiario.objects.filter(secretaria_id=se.id,fecha_salida__year=date.year)                        
                        if vi.exists():
                                secretarias.append({
                                        'nombresecre':se.nombreS,
                                        'id_secre':se.id,
                                        })
                                for v in vi:
                                        sumatoria=sumatoria+v.totalC
                                saldores=SaldosTotales.objects.filter(secretaria=se.id)
                                for s in saldores:                                        
                                        saldos.append(s.MontoDesignado)
                                montosgastos.append(sumatoria)
                        else:                                
                                secretarias.append({
                                        'nombresecre':se.nombreS,
                                        'id_secre':se.id,
                                        })
                                saldores=SaldosTotales.objects.select_related().filter(secretaria=se.id)
                                for s in saldores:
                                        saldos.append(s.MontoDesignado)
                                montosgastos.append(sumatoria)
                        sumatoria=0
                resultado=[]
                color=''
                total_actual=0
                total_progreso=0
                total_sobrante=0
                total_monto=0
                for p in xrange(len(secretarias)):
                        for suma in xrange(len(montosgastos)):
                                if suma==p:
                                        if int(((montosgastos[p])/(saldos[p]))*100) <= 60:
                                                color='#1e7e34'
                                        if int(((montosgastos[p])/(saldos[p]))*100) > 60:
                                                color='#d39e00'
                                        if int(((montosgastos[p])/(saldos[p]))*100) > 80:
                                                color='#bd2130'
                                        total_actual=total_actual+montosgastos[p]
                                        
                                        total_sobrante=total_sobrante+(saldos[p]-montosgastos[p])
                                        total_monto=total_monto+saldos[p]
                                        resultado.append({
                                                'numero':(p+1),
                                                'numero_secre':str('viaticos-')+str(secretarias[p]['id_secre']),
                                                'secre':secretarias[p]['nombresecre'],
                                                'montosobrante':(saldos[p]-montosgastos[p]),
                                                'barra':int(((montosgastos[p])/(saldos[p]))*100),
                                                'color':color,
                                                'MontoGasto':montosgastos[p],
                                                'SaldoSecre':saldos[p]
                                        })
                total_progreso=int(((total_actual)/(total_monto))*100)                
                context['SaldosPorSecre'] = resultado
                context['ano']=date.year
                context['total_actual']=total_actual
                context['total_progreso']=total_progreso
                context['total_sobrante']=total_sobrante
                context['total_monto']=total_monto
                return context
class Reporte_saldoView(BasePlatypusReport):
        total_actual=0               
        total_sobrante=0
        total_monto=0
        def __init__(self):
                self.begin(orientation = 'portrait', rightMargin = 28, leftMargin = 28, topMargin = 36, bottomMargin = 28)

        def get(self, request, *args, **kwargs):
                self.draw()
                
                self.write(onFirstPage = self.title)#, onLaterPages = self.page_number)
                return self.response

        def title(self, canvas, document):

                canvas.saveState()
                canvas.setFont('Helvetica-Bold', 14)
                archivo_imagen = settings.MEDIA_ROOT+'\images\logoo.png'
                archivo_imagen1 = settings.MEDIA_ROOT+'\images\money.png'
                        
                canvas.setFont("Helvetica-Bold", 13)
                canvas.drawCentredString(self.x_start + self.width_internal / 2, self.y_start - 25, u"GOBIERNO AUTONOMO DEPARTAMENTAL DE POTOSI")
                canvas.setFont("Helvetica-Bold", 13)
                canvas.drawCentredString(self.x_start + self.width_internal / 2, self.y_start - 45, u"Secretaria Departamental Administracion y Financiera")
        
                canvas.drawImage(archivo_imagen1, self.x_start + 470,self.y_start - 64, 55, 55, preserveAspectRatio = True)
                
                canvas.setLineWidth(1)
                canvas.line(self.x_start+135, self.y_start-55, 450, self.y_start-55)
                
                canvas.setFont("Helvetica-Bold", 12)
                canvas.drawCentredString(self.x_start + self.width_internal / 2, self.y_start - 78, u"DETALLES  DE GASTOS DE SECRETARIAS DE VIATICOS, PASAJES Y PEAJES ")
                date = datetime.now()
                year=date.year
                gestion=u'GESTION '+ str(year)
                canvas.setFont("Helvetica-Bold", 12)
                canvas.drawCentredString(self.x_start + self.width_internal / 2, self.y_start - 91, gestion)

                self.draw_left_image(canvas = canvas,
                url = archivo_imagen,
                x = self.x_start + 30, 
                y = self.y_start - 8, 
                w = 55, 
                h = 55
                )

        def draw(self):
                self.add(Spacer(1, 90))
                self.draw_table()
        def draw_table(self):
                
                date = datetime.now()
                year=date.year
                basic_style_full_doble = self.get_basic_style_full_doble()
                basic_style_body = self.get_basic_style_body()
                basic_style_full_doble_void = self.get_basic_style_full_doble_void()
                viaticos=Secretaria.objects.all()
                self.add(self.draw_in_table_top(0,viaticos,self.get_basic_style_full_doble_top(),basic_style_body, basic_style_full_doble_void, True))                
                self.add(Spacer(1,0))
                self.add(self.draw_in_table_result(0,self.get_basic_style_full_doble_button(), basic_style_body, basic_style_full_doble_void, True))
        def draw_in_table_top(self,index = 0, datereference = None, style = None,stylealt = None, stylevoid = None, hasheader = False):
                cabecera = [
                'N°',
                'SECRETARIA',
                'MONTO ACTUAL',
                'MONTO SOBRANTE',
                'MONTO ASIGNADO',
          
                ]

                date = datetime.now()
                secretarias=[]
                montosgastos=[]
                saldos=[]
                sumatoria=0
                for se in datereference:
                        vi=viaticodiario.objects.filter(secretaria_id=se.id,fecha_salida__year=date.year)                        
                        if vi.exists():
                                secretarias.append({
                                        'nombresecre':se.nombreS,
                                        'id_secre':se.id,
                                        })
                                for v in vi:
                                        sumatoria=sumatoria+v.totalC
                                saldores=SaldosTotales.objects.filter(secretaria=se.id)
                                for s in saldores:                                        
                                        saldos.append(s.MontoDesignado)
                                montosgastos.append(sumatoria)
                        else:                                
                                secretarias.append({
                                        'nombresecre':se.nombreS,
                                        'id_secre':se.id,
                                        })
                                saldores=SaldosTotales.objects.select_related().filter(secretaria=se.id)
                                for s in saldores:
                                        saldos.append(s.MontoDesignado)
                                montosgastos.append(sumatoria)
                        sumatoria=0
                resultado=[]
                color=''
                
                for p in xrange(len(secretarias)):
                        for suma in xrange(len(montosgastos)):
                                if suma==p:
                                        
                                        self.total_actual=self.total_actual+montosgastos[p]
                                        
                                        self.total_sobrante=self.total_sobrante+(saldos[p]-montosgastos[p])
                                        self.total_monto=self.total_monto+saldos[p]
                                        resultado_sobrante=0
                                        if (saldos[p]-montosgastos[p]) < 0:
                                                resultado_sobrante=u'Excedido'
                                        else:
                                                resultado_sobrante=(saldos[p]-montosgastos[p])                                        
                                        resultado.append({
                                                'numero':(p+1),
                                                'secre':secretarias[p]['nombresecre'],
                                                'montosobrante':resultado_sobrante,                                      
                                                'MontoGasto':montosgastos[p],
                                                'SaldoSecre':saldos[p]
                                        })
                               

                detalles = [(via['numero'],via['secre'],via['MontoGasto'],via['montosobrante'],via['SaldoSecre']) for via in resultado]
                cm = 29
                #cm = 23.4
                if hasheader:
                        table = Table(
                                [cabecera] + detalles,
                                colWidths = [
                                0.7 * cm, 
                                7 * cm, 
                                2.3 * cm,  
                                2.7 * cm, 
                                2.6 * cm
                                ],
                                splitByRow = 1,
                                repeatRows = 0
                        )
                
                if style:
                        if hasheader:
                                table.setStyle(style)
                        elif stylealt:
                                table.setStyle(stylealt)
                return table
      

        def draw_in_table_result(self,index = 0,style = None, stylealt = None, stylevoid = None, hasheader = False):
                
                detalles = [(
                        "TOTAL",
                        " ",
                        self.total_actual,
                        self.total_sobrante,
                        self.total_monto
                        )]
                cm = 29
                #cm = 23.4
                if hasheader:
                        table = Table(
                                detalles,
                                colWidths = [
                                0.7 * cm, 
                                7 * cm, 
                                2.3 * cm,  
                                2.7 * cm, 
                                2.6 * cm
                                ],
                                splitByRow = 1,
                                repeatRows = 1
                        )
                if style:
                        if hasheader:
                                table.setStyle(style)
                        elif stylealt:
                                table.setStyle(stylealt)                                
                        return table

def buscarSecre(request):
        if request.is_ajax():
                secre=Secretaria.objects.filter(nombreS__icontains=request.GET['secre'])
                if secre.exists():               
                        date = datetime.now()
                        secretarias=[]
                        montosgastos=[]
                        saldos=[]
                        sumatoria=0
                        for se in secre:
                                vi=viaticodiario.objects.filter(secretaria_id=se.id,fecha_salida__year=date.year)                                
                                if vi.exists():
                                        secretarias.append({
                                                'nombresecre':se.nombreS,
                                                'id_secre':se.id,
                                                })
                                        for v in vi:
                                                sumatoria=sumatoria+v.totalC
                                        saldores=SaldosTotales.objects.filter(secretaria=se.id)
                                        for s in saldores:                                                
                                                saldos.append(s.MontoDesignado)
                                        montosgastos.append(sumatoria)
                                else:                                        
                                        secretarias.append({
                                                'nombresecre':se.nombreS,
                                                'id_secre':se.id,
                                                })
                                        saldores=SaldosTotales.objects.select_related().filter(secretaria=se.id)
                                        for s in saldores:                                                
                                                saldos.append(s.MontoDesignado)
                                        montosgastos.append(sumatoria)                                        
                                sumatoria=0                        
                        results=[]
                        cont=1
                        color=''
                        for p in xrange(len(secretarias)):
                                for suma in xrange(len(montosgastos)):
                                        if suma==p:
                                                if int(((montosgastos[p])/(saldos[p]))*100) <= 60:
                                                        color='#1e7e34'
                                                if int(((montosgastos[p])/(saldos[p]))*100) > 60:
                                                        color='#d39e00'
                                                if int(((montosgastos[p])/(saldos[p]))*100) > 80:
                                                        color='#bd2130'
                                                producto_json={}
                                                producto_json['numero']=cont
                                                producto_json['numero_secre']=se.nombreS
                                                producto_json['secre']=secretarias[p]['nombresecre']
                                                producto_json['montosobrante']=(saldos[p]-montosgastos[p])
                                                producto_json['barra']=int(((montosgastos[p])/(saldos[p]))*100)
                                                producto_json['color']=color
                                                producto_json['MontoGasto']=montosgastos[p]
                                                producto_json['SaldoSecre']=saldos[p]
                                                results.append(producto_json)
                                cont=cont+1                                                  
                        data_json=json.dumps(results)
                        
                else:
                        print("No existe  con esa palabra")
                        data_json='fail'
                mimetype="application/json"
                return HttpResponse(data_json,mimetype)

# FIN DE MODULO CENTRALIZADOR

# MODULO DE BUSQUEDA

class BusquedaVia_View(BusquedaView):                
        model1=viaticodiario.objects.all()
        user=[]
        def post(self,request,*args,**kwargs):
                self.via=[]
                numerocontrol1=request.POST.get('numerocontrol')                                                        
                gestion1=request.POST.get('gestion')
                meses1=request.POST.get('meses')                  
                fecha1=request.POST.get('fecha')                
                if numerocontrol1 == "" and gestion1 == '...' and fecha1 == "" and meses1 == '...':                        
                        self.varificar=True
                        self.error=self.error+'Seleccione algun campo '+'\n'
                if len(self.error)==0:
                        self.varificar=False
                ncontrol1=numerocontrol1
                if ncontrol1 == None:
                        ncontrol1=""

                if ncontrol1 != "":
                        print(ncontrol1)                                
                        self.valid_space(ncontrol1) 
                        self.is_Number(ncontrol1)                        
                        if len(self.error) != 0:                                
                                self.varificar=True
                if self.varificar:                                                                           
                        self.context={
                                'anos':self.cargar(),
                                'meses':self.meseslist,
                                'error':self.error,
                                'ncontrol':numerocontrol1,                          
                        }      
                        return render(request,"busqueda/buscar_registro_clas.html",self.context)
                else:                        
                        uno=True
                        dos=True
                        tres=True
                        cuatro=True
                        cinco=True
                        seis=True
                        siete=True
                        ocho=True
                        if uno and gestion1!= '...' and ncontrol1 != "" and meses1== '...' and fecha1 == "" :                        
                                dos=False
                                tres=False
                                cuatro=False
                                cinco=False
                                seis=False
                                siete=False
                                ocho=False
                                viaa= viaticodiario.objects.filter(slug=('%s-%s'%(ncontrol1,gestion1)))
                                if viaa.exists():
                                        for vis in viaa:
                                                self.LlenarViatico([vis.id,vis.solicitante.nombre,vis.solicitante.apaterno,vis.solicitante.amaterno,vis.solicitante.ci,vis.Monto_pagado,vis.totalC,vis.lugar,vis.ncontrol,vis.encargado,vis.slug,vis.cod_u])                                                                                                                                                                                    
                                if len(self.via) != 0:
                                        self.context={
                                                'anos':self.cargar(),
                                                'via':self.via,                                                        
                                                'ncontrol':ncontrol1,
                                                'meses':self.meseslist,
                                        }             
                                else:
                                        self.error="NO EXISTE EL VIATICO EN ESA GESTION"
                                        self.context={
                                                'anos':self.cargar(),
                                                'via':self.via,
                                                'error':self.error,
                                                'meses':self.meseslist,
                                                'ncontrol':ncontrol1,
                                                'gestion':gestion1,
                                        }                                                 
                        if dos and   ncontrol1 != "" and meses1!= '...' and gestion1 == '...' and fecha1 == "":
                                tres=False
                                cuatro=False
                                cinco=False
                                seis=False
                                siete=False
                                ocho=False
                                
                                viaa= viaticodiario.objects.filter(ncontrol=ncontrol1)
                                if viaa.exists():
                                        for vis in viaa:
                                                for mese in xrange(len(self.mesesingles)):
                                                        if self.mesesingles[mese]==vis.timestamp.strftime('%B'):
                                                                if self.meseslist[mese] == meses1:
                                                                        self.LlenarViatico([vis.id,vis.solicitante.nombre,vis.solicitante.apaterno,vis.solicitante.amaterno,vis.solicitante.ci,vis.Monto_pagado,vis.totalC,vis.lugar,vis.ncontrol,vis.encargado,vis.slug,vis.cod_u])                                                                                                                                                                     
                                if len(self.via)==0:
                                        self.error="NO EXISTE ESE VIATICO CON ESA FECHA"
                                        self.context={
                                                'anos':self.cargar(),
                                                'via':self.via,
                                                'meses':self.meseslist,
                                                'error':self.error,
                                                'mese':meses1,
                                                'ncontrol':ncontrol1,                                                
                                        }
                                else:
                                        self.context={
                                                'anos':self.cargar(),
                                                'via':self.via,
                                                'meses':self.meseslist,
                                                'ncontrol':ncontrol1,                                                         
                                        }                                          
                        if cuatro and  gestion1!= '...' and meses1!= '...' and ncontrol1 == "" and fecha1 == "":
                                cinco=False
                                seis=False
                                siete=False
                                ocho=False                                                       
                                for vis in self.model1:
                                        for mese in xrange(len(self.mesesingles)):
                                                if self.mesesingles[mese]==vis.timestamp.strftime('%B'):
                                                        if self.meseslist[mese] == meses1 and vis.timestamp.strftime('%Y') == gestion1:
                                                                self.LlenarViatico([vis.id,vis.solicitante.nombre,vis.solicitante.apaterno,vis.solicitante.amaterno,vis.solicitante.ci,vis.Monto_pagado,vis.totalC,vis.lugar,vis.ncontrol,vis.encargado,vis.slug,vis.cod_u])                                                                                                                                                                                                
                                if len(self.via)==0:
                                        self.error="NO EXISTE ESE VIATICO CON ESA FECHA Y AÑO"
                                        self.context={
                                                'anos':self.cargar(),
                                                'via':self.via,
                                                'meses':self.meseslist,
                                                'error':self.error,
                                                'mese':meses1,
                                                'gestion':gestion1,        
                                        }
                                else:
                                        self.context={
                                                'anos':self.cargar(),
                                                'via':self.via,
                                                'meses':self.meseslist,
                                        }                                                                                          
                        if ocho==True:
                                if gestion1 != '...' and ncontrol1 == "" and fecha1 == "" and meses1 == '...' :
                                        for vis in self.model1:
                                                if vis.timestamp.strftime('%Y') == gestion1:
                                                        self.LlenarViatico([vis.id,vis.solicitante.nombre,vis.solicitante.apaterno,vis.solicitante.amaterno,vis.solicitante.ci,vis.Monto_pagado,vis.totalC,vis.lugar,vis.ncontrol,vis.encargado,vis.slug,vis.cod_u])                                                                                                                                                                                               
                                                        
                                        if len(self.via) != 0:
                                                self.context={
                                                        'anos':self.cargar(),
                                                        'via':self.via,                                                        
                                                        'ncontrol':ncontrol1,
                                                        'meses':self.meseslist,
                                                } 
                                        else:
                                                self.error='%s %s'%("NO EXISTE VIATICOS EN LA GESTION ",gestion1)
                                                self.context={
                                                        'anos':self.cargar(),                                                        
                                                        'error':self.error,
                                                        'meses':self.meseslist,
                                                        'gestion':gestion1,
                                                }                                                                
                                if ncontrol1 != "" and gestion1 == '...' and meses1 == '...' and fecha1 == "":                                                                               
                                        viaa= viaticodiario.objects.filter(ncontrol=ncontrol1)                            
                                        if viaa.exists():
                                                for vis in viaa:
                                                        self.LlenarViatico([vis.id,vis.solicitante.nombre,vis.solicitante.apaterno,vis.solicitante.amaterno,vis.solicitante.ci,vis.Monto_pagado,vis.totalC,vis.lugar,vis.ncontrol,vis.encargado,vis.slug,vis.cod_u])                                                                                                                                                  
                                        if len(self.via) != 0:
                                                self.context={
                                                        'anos':self.cargar(),
                                                        'via':self.via,                                                        
                                                        'ncontrol':ncontrol1,
                                                        'meses':self.meseslist,
                                                }
                                        else:
                                                self.error="NO EXISTE EL NUMERO DE CONTROL DE ESE VIATICO"
                                                self.context={
                                                        'anos':self.cargar(),
                                                        
                                                        'error':self.error,
                                                        'ncontrol':ncontrol1,
                                                        'meses':self.meseslist,
                                                }                                                              
                                if fecha1 != "" and gestion1 == '...' and ncontrol1 == "" and meses1 == '...':
                                        
                                        viaa=viaticodiario.objects.filter(timestamp=fecha1)
                                        if viaa.exists():
                                                for vis in viaa:
                                                        self.LlenarViatico([vis.id,vis.solicitante.nombre,vis.solicitante.apaterno,vis.solicitante.amaterno,vis.solicitante.ci,vis.Monto_pagado,vis.totalC,vis.lugar,vis.ncontrol,vis.encargado,vis.slug,vis.cod_u])                                                                                                                                                                                               
                                        if len(self.via) != 0:
                                                self.context={
                                                        'anos':self.cargar(),
                                                        'via':self.via,                                                        
                                                        'ncontrol':ncontrol1,
                                                        'meses':self.meseslist,
                                                }              
                                        else:
                                                self.error="NO EXISTE ESE VIATICO CON ESA FECHA"
                                                self.context={
                                                        'anos':self.cargar(),                                                        
                                                        'meses':self.meseslist,
                                                        'error':self.error,
                                                        'fecha':fecha1,
                                                        
                                                }                                                                                                                                                 
                                if meses1 != '...' and gestion1 == '...' and ncontrol1 == "" and fecha1 == "":
                                
                                        for vis in self.model1:
                                                for mese in xrange(len(self.mesesingles)):
                                                        if self.mesesingles[mese]==vis.timestamp.strftime('%B'):
                                                                if self.meseslist[mese] == meses1:
                                                                        self.LlenarViatico([vis.id,vis.solicitante.nombre,vis.solicitante.apaterno,vis.solicitante.amaterno,vis.solicitante.ci,vis.Monto_pagado,vis.totalC,vis.lugar,vis.ncontrol,vis.encargado,vis.slug,vis.cod_u])                                                                                                                                                  
                                        if len(self.via)==0:
                                                self.error="NO EXISTE ESE VIATICO CON ESA FECHA"
                                                self.context={
                                                        'anos':self.cargar(),                                            
                                                        'meses':self.meseslist,
                                                        'error':self.error,
                                                        'mese':meses1,        
                                                }
                                        else:
                                                self.context={
                                                        'anos':self.cargar(),
                                                        'via':self.via,
                                                        'meses':self.meseslist,
                                                        'mese':meses1,        
                                                }                                                
                        return render(request,"busqueda/buscar_registro_clas.html",self.context)

        def get(self,request,*args,**kwargs):                
                self.context={'anos':self.cargar(),'meses':self.meseslist}
                return render(request,"busqueda/buscar_registro_clas.html",self.context)               
class BusquedaEmp_View(BusquedaView):        
        def insert(self,valor):
                if valor[0].exists():
                        for emp in valor[0]:
                                viaa=viaticodiario.objects.filter(id_solicitante=emp.ci)                                      
                                for vis in viaa:
                                        self.LlenarViatico([vis.id,vis.solicitante.nombre,vis.solicitante.apaterno,vis.solicitante.amaterno,vis.solicitante.ci,vis.Monto_pagado,vis.totalC,vis.lugar,vis.ncontrol,vis.encargado,vis.slug,vis.cod_u])
                if len(self.via) != 0:
                        self.context={
                                'anos':self.cargar(),
                                'via':self.via,
                                'meses':self.meseslist,
                                'tipovalor':valor[1]
                                                    
                        }
                else:
                        self.error="No existe ninguno Viatico hacia esa Persona"
                        self.context={
                                'anos':self.cargar(),
                                'error':self.error,
                                'meses':self.meseslist,
                                'tipovalor':valor[1]
                                                               
                        }                  
        def Name_complete(self,valor):                                           
                apellidouno=""
                apellidodos=""
                uno=True
                dos=False
                empleados=""
                for i in xrange(len(valor)):
                        if valor[i] != " ":
                                if uno:
                                        apellidouno =apellidouno+valor[i]
                                if dos:
                                        apellidodos =apellidodos+valor[i]
                        else:
                                dos=True
                                uno=False                                
                if len(apellidouno) != 0 and len(apellidodos) !=0:                                                
                        empleados=empleado.objects.filter(apaterno__icontains=apellidouno.upper(),amaterno__icontains=apellidodos.upper())
                else:
                        empleados=empleado.objects.filter(apaterno__icontains=valor.upper())
                return empleados  
        def validar_apellido(self,valor):
                apellidouno=""
                apellidodos=""
                uno=True
                dos=False
                empleados=""
                for i in xrange(len(valor)):
                        if valor[i] != " ":
                                if uno:
                                        apellidouno =apellidouno+valor[i]
                                if dos:
                                        apellidodos =apellidodos+valor[i]
                        else:
                                dos=True
                                uno=False                                
                if len(apellidouno) != 0 or len(apellidodos) !=0: 
                        if apellidouno.isalpha()==True:
                                return True
                        if apellidodos.isalpha()==True:
                                return True
                        return False
        def post(self,request,*args,**kwargs):
                self.via=[]
                tipo_valor=request.POST.get('tipovalor')  
                meses1=request.POST.get('meses') 
                anos1=request.POST.get('anos') 
                fechadesde1=request.POST.get('fechadesde') 
                fechahasta1=request.POST.get('fechahasta') 
                if tipo_valor == "":                        
                        self.varificar=True
                        self.error=self.error+'Seleccione el Campo Ci-Apellido'+'\n'
                if len(self.error)==0:
                        self.varificar=False
                tipovalor1=tipo_valor
                if tipovalor1 == None:
                        tipovalor1=""

                if self.varificar:                                                   
                        self.context={
                                'anos':self.cargar(),
                                'error':self.error,
                                'meses':self.meseslist,
                                'tipovalor':tipovalor1
                        }      
                        return render(request,"busqueda/busqueda_empleado_clas.html",self.context)

                if tipovalor1 != "":
                        if (tipovalor1.strip()).isdigit()==True:                                         
                                self.valid_space(tipovalor1)
                        else:                                                                    
                                if self.validar_apellido(tipovalor1)==False:
                                        self.error=self.error+'INTRODUSCA EL APELLIDO COMPLETO '+'\n'
                                
                        if len(self.error) != 0:                                                                         
                                self.context={
                                        'anos':self.cargar(),
                                        'error':self.error,
                                        'meses':self.meseslist,
                                        'tipovalor':tipovalor1,                                                
                                }                                
                                return render(request,"busqueda/busqueda_empleado_clas.html",self.context)
                        else:                                
                                one=True
                                two=True
                                three=True
                                four=True
                                five=True                        
                                if one and tipovalor1 != "" and meses1 == "..." and anos1 == "..." and fechadesde1 == "" and fechahasta1 == "":
                                        two=False
                                        three=False
                                        four=False
                                        five=False                                                                                                           
                                        if tipovalor1.isdigit()==True:                                        
                                                empleados=empleado.objects.filter(ci=tipovalor1)
                                                self.insert([empleados,tipovalor1])   
                                        else:                                        
                                                if tipovalor1.isalpha()==True or self.validar_apellido(tipovalor1):                                                                                                                                        
                                                        emp=self.Name_complete(tipovalor1)
                                                        self.insert([emp,tipovalor1])                       
                                if two and tipovalor1 != "" and meses1 != "..." and anos1 == "..." and fechadesde1 == "" and fechahasta1 == "":                                                              
                                        three=False
                                        four=False
                                        five=False 
                                        self.error="No existe ninguno Viatico hacia esa Persona ..."              
                                        if tipovalor1.isdigit()==True:
                                                empleados=empleado.objects.filter(ci=tipovalor1)
                                                if empleados.exists():
                                                        for emp in empleados:
                                                                viaa=viaticodiario.objects.filter(id_solicitante=emp.ci)                                      
                                                                for vis in viaa:
                                                                        for mese in xrange(len(self.mesesingles)):
                                                                                if self.mesesingles[mese]==vis.timestamp.strftime('%B'):
                                                                                        if self.meseslist[mese] == meses1:
                                                                                                self.LlenarViatico([vis.id,vis.solicitante.nombre,vis.solicitante.apaterno,vis.solicitante.amaterno,vis.solicitante.ci,vis.Monto_pagado,vis.totalC,vis.lugar,vis.ncontrol,vis.encargado,vis.slug,vis.cod_u])                                          
                                                if len(self.via) != 0:
                                                        self.context={
                                                                'anos':self.cargar(),
                                                                'via':self.via,
                                                                'meses':self.meseslist,
                                                                'tipovalor':tipovalor1,
                                                        }
                                                else:                                                
                                                        self.context={
                                                                'anos':self.cargar(),
                                                                'error':self.error,
                                                                'meses':self.meseslist,
                                                                'tipovalor':tipovalor1,
                                                                'mese':meses1,
                                                        } 
                                        else:                                                                                                                                                 
                                                if tipovalor1.isalpha()==True or self.validar_apellido(tipovalor1):
                                                        emp=self.Name_complete(tipovalor1)
                                                        if emp.exists():
                                                                for emp in emp:
                                                                        viaa=viaticodiario.objects.filter(id_solicitante=emp.ci)                                      
                                                                        for vis in viaa:
                                                                                for mese in xrange(len(self.mesesingles)):
                                                                                        if self.mesesingles[mese]==vis.timestamp.strftime('%B'):
                                                                                                if self.meseslist[mese] == meses1:
                                                                                                        self.LlenarViatico([vis.id,vis.solicitante.nombre,vis.solicitante.apaterno,vis.solicitante.amaterno,vis.solicitante.ci,vis.Monto_pagado,vis.totalC,vis.lugar,vis.ncontrol,vis.encargado,vis.slug,vis.cod_u])                                          
                                                        if len(self.via) != 0:
                                                                self.context={
                                                                        'anos':self.cargar(),
                                                                        'via':self.via,
                                                                        'meses':self.meseslist,
                                                                        'tipovalor':tipovalor1,                                                                
                                                                }
                                                        else:
                                                                self.context={
                                                                        'anos':self.cargar(),
                                                                        'error':self.error,
                                                                        'meses':self.meseslist,
                                                                        'tipovalor':tipovalor1,
                                                                        'mese':meses1,
                                                                }                                           
                                if three and tipovalor1 != "" and anos1 != "..." and meses1 == "..." and fechadesde1 == "" and fechahasta1 == "":
                                        four=False
                                        five=False
                                        self.error="No existe ninguno Viatico hacia esa Persona ..."                        
                                        if tipovalor1.isdigit()==True:
                                                empleados=empleado.objects.filter(ci=tipovalor1)
                                                if empleados.exists():
                                                        for emp in empleados:
                                                                viaa=viaticodiario.objects.filter(id_solicitante=emp.ci)                                      
                                                                for vis in viaa:
                                                                        if vis.timestamp.strftime('%Y') == anos1:
                                                                                self.LlenarViatico([vis.id,vis.solicitante.nombre,vis.solicitante.apaterno,vis.solicitante.amaterno,vis.solicitante.ci,vis.Monto_pagado,vis.totalC,vis.lugar,vis.ncontrol,vis.encargado,vis.slug,vis.cod_u])                                                                  
                                                if len(self.via) != 0:
                                                        self.context={
                                                                'anos':self.cargar(),
                                                                'via':self.via,
                                                                'meses':self.meseslist,
                                                                'tipovalor':tipovalor1,                                                        
                                                        }
                                                else:
                                                        self.context={                                             
                                                                'anos':self.cargar(),
                                                                'error':self.error,
                                                                'meses':self.meseslist,
                                                                'tipovalor':tipovalor1,

                                                                'year':anos1,
                                                        }                                               
                                        else:                                        
                                                if tipovalor1.isalpha()==True or self.validar_apellido(tipovalor1):
                                                        emp=self.Name_complete(tipovalor1)
                                                        if emp.exists():
                                                                for emp in emp:
                                                                        viaa=viaticodiario.objects.filter(id_solicitante=emp.ci)                                      
                                                                        for vis in viaa:
                                                                                if vis.timestamp.strftime('%Y') == anos1:
                                                                                        self.LlenarViatico([vis.id,vis.solicitante.nombre,vis.solicitante.apaterno,vis.solicitante.amaterno,vis.solicitante.ci,vis.Monto_pagado,vis.totalC,vis.lugar,vis.ncontrol,vis.encargado,vis.slug,vis.cod_u])                                                                                          
                                                        if len(self.via) != 0:
                                                                self.context={
                                                                        'anos':self.cargar(),
                                                                        'via':self.via,
                                                                        'meses':self.meseslist,
                                                                        'tipovalor':tipovalor1,
                                                                }
                                                        else:
                                                                self.context={
                                                                        'anos':self.cargar(),
                                                                        'error':self.error,
                                                                        'meses':self.meseslist,
                                                                        'tipovalor':tipovalor1,
                                                                        'year':anos1,
                                                                }                                                                                     
                                if four and tipovalor1 != "" and fechadesde1 != "" and fechahasta1 != "" and meses1 == "..." and anos1 == "...":
                                        five=False
                                        self.error="No existe ninguno Viatico hacia esa Persona"                                
                                        fechadesde=fechadesde1
                                        fechahasta=fechahasta1
                                        if tipovalor1.isdigit()==True:  
                                                empleados=empleado.objects.filter(ci=tipovalor1)
                                                if empleados.exists():
                                                        for emp in empleados:
                                                                viaa=viaticodiario.objects.filter(
                                                                        id_solicitante=emp.ci,
                                                                        fecha_salida__gte=fechadesde,
                                                                        fecha_legada__lte=fechahasta)                                   
                                                                for vis in viaa:
                                                                        self.LlenarViatico([vis.id,vis.solicitante.nombre,vis.solicitante.apaterno,vis.solicitante.amaterno,vis.solicitante.ci,vis.Monto_pagado,vis.totalC,vis.lugar,vis.ncontrol,vis.encargado,vis.slug,vis.cod_u])                                                                                                                                                  
                                                if len(self.via) != 0:
                                                        self.context={
                                                                'anos':self.cargar(),
                                                                'via':self.via,
                                                                'meses':self.meseslist,
                                                                'tipovalor':tipovalor1,

                                                        }
                                                else:
                                                        self.context={
                                                                'anos':self.cargar(),
                                                                'error':self.error,
                                                                'meses':self.meseslist,
                                                                'tipovalor':tipovalor1,

                                                                'fechadesde':fechadesde,
                                                                'fechahasta':fechahasta,
                                                        }                                                                                
                                        else:                                        
                                                if tipovalor1.isalpha()==True or self.validar_apellido(tipovalor1):
                                                        empe=self.Name_complete(tipovalor1)
                                                        if empe.exists():
                                                                for emp in empe:
                                                                        viaa=viaticodiario.objects.filter(
                                                                                id_solicitante=emp.ci,
                                                                                fecha_salida__gte=fechadesde,
                                                                                fecha_legada__lte=fechahasta)                                   
                                                                        for vis in viaa:
                                                                                self.LlenarViatico([vis.id,vis.solicitante.nombre,vis.solicitante.apaterno,vis.solicitante.amaterno,vis.solicitante.ci,vis.Monto_pagado,vis.totalC,vis.lugar,vis.ncontrol,vis.encargado,vis.slug,vis.cod_u])                                                                                                                                                  
                                                        if len(self.via) != 0:
                                                                self.context={
                                                                        'anos':self.cargar(),
                                                                        'via':self.via,
                                                                        'meses':self.meseslist,
                                                                        'tipovalor':tipovalor1,
                                                                }
                                                        else:
                                                                self.context={
                                                                        'anos':self.cargar(),
                                                                        'error':self.error,
                                                                        'meses':self.meseslist,
                                                                        'tipovalor':tipovalor1,
                                                                        'fechadesde':fechadesde,
                                                                        'fechahasta':fechahasta,
                                                                }                                                                                             
                                if five and tipovalor1 != "" and meses1 != "..." and anos1 != "..." and fechadesde1 == "" and fechahasta1 == "":
                                        self.error="No existe ninguno Viatico hacia esa Persona ..."                                                           
                                        if tipovalor1.isdigit()==True:
                                                empleados=empleado.objects.filter(ci=tipovalor1)
                                                if empleados.exists():
                                                        for emp in empleados:
                                                                viaa=viaticodiario.objects.filter(id_solicitante=emp.ci)                                      
                                                                for vis in viaa:
                                                                        for mese in xrange(len(self.mesesingles)):
                                                                                if self.mesesingles[mese]==vis.timestamp.strftime('%B'):
                                                                                        if vis.timestamp.strftime('%Y') == anos1 and self.meseslist[mese] == meses1:
                                                                                                self.LlenarViatico([vis.id,vis.solicitante.nombre,vis.solicitante.apaterno,vis.solicitante.amaterno,vis.solicitante.ci,vis.Monto_pagado,vis.totalC,vis.lugar,vis.ncontrol,vis.encargado,vis.slug,vis.cod_u])                                                                                                                                                  
                                                if len(self.via) != 0:
                                                        self.context={
                                                                'anos':self.cargar(),
                                                                'via':self.via,
                                                                'meses':self.meseslist,
                                                                'tipovalor':tipovalor1,

                                                        }
                                                else:
                                                        self.context={
                                                                'anos':self.cargar(),
                                                                'error':self.error,
                                                                'meses':self.meseslist,
                                                                'tipovalor':tipovalor1,

                                                                'mese':meses1,
                                                                'year':anos1,
                                                        }                                        
                                        else:                                        
                                                if tipovalor1.isalpha()==True or self.validar_apellido(tipovalor1):
                                                        empe=self.Name_complete(tipovalor1)
                                                        if empe.exists():
                                                                for emp in empe:
                                                                        viaa=viaticodiario.objects.filter(id_solicitante=emp.ci)                                      
                                                                        for vis in viaa:
                                                                                for mese in xrange(len(self.mesesingles)):
                                                                                        if self.mesesingles[mese]==vis.timestamp.strftime('%B'):
                                                                                                if vis.timestamp.strftime('%Y') == anos1 and self.meseslist[mese] == meses1:
                                                                                                        self.LlenarViatico([vis.id,vis.solicitante.nombre,vis.solicitante.apaterno,vis.solicitante.amaterno,vis.solicitante.ci,vis.Monto_pagado,vis.totalC,vis.lugar,vis.ncontrol,vis.encargado,vis.slug,vis.cod_u])                                                                                                                                  
                                                        if len(self.via) != 0:
                                                                self.context={
                                                                        'anos':self.cargar(),
                                                                        'via':self.via,
                                                                        'meses':self.meseslist,
                                                                        'tipovalor':tipovalor1,
                                                                }
                                                        else:
                                                                self.context={
                                                                        'anos':self.cargar(),
                                                                        'error':self.error,
                                                                        'meses':self.meseslist,
                                                                        'tipovalor':tipovalor1,
                                                                        'mese':meses1,
                                                                        'year':anos1,
                                                                }                                                                                
                                return render(request,"busqueda/busqueda_empleado_clas.html",self.context)
                
        def get(self,request,*args,**kwargs):                                
                self.context={'anos':self.cargar(),'meses':self.meseslist}
                return render(request,"busqueda/busqueda_empleado_clas.html",self.context)
class buscar_Viaticos_View(BusquedaView):
        model=User.objects.all()  
        model1=viaticodiario.objects.all()
        
        def get(self,request,*args,**kwargs):
                context={
                                'anos':self.cargar(),
                                'meses':self.meseslist,
                                'error':self.error,
                                #'user':self.model,                        
                        }
                return render(request,"busqueda/buscar_viatico.html",context)
# FIN DE MODULO DE BUSQUEDA

# GESTION DE REPORTES
class ReportCentralizador(BasePlatypusReport):
    def __init__(self):
        self.begin(orientation = 'portrait', rightMargin = 28, leftMargin = 28, topMargin = 36, bottomMargin = 28)

    def get(self, request, *args, **kwargs):
        self.draw()
        self.write(onFirstPage = self.title)#, onLaterPages = self.page_number)
        return self.response

    def title(self, canvas, document):

        canvas.saveState()
        canvas.setFont('Helvetica-Bold', 14)
        archivo_imagen = settings.MEDIA_ROOT+'\images\logoo.png'
        archivo_imagen1 = settings.MEDIA_ROOT+'\images\money.png'
                
        canvas.setFont("Helvetica-Bold", 13)
        canvas.drawCentredString(self.x_start + self.width_internal / 2, self.y_start - 25, u"GOBIERNO AUTONOMO DEPARTAMENTAL DE POTOSI")
        canvas.setFont("Helvetica-Bold", 13)
        canvas.drawCentredString(self.x_start + self.width_internal / 2, self.y_start - 45, u"Secretaria Departamental Administracion y Financiera")
      
        canvas.drawImage(archivo_imagen1, self.x_start + 470,self.y_start - 64, 55, 55, preserveAspectRatio = True)
        
        canvas.setLineWidth(1)
        #print(self.x_start)
        #print(self.y_start)
        canvas.line(self.x_start+135, self.y_start-55, 450, self.y_start-55)
        
        canvas.setFont("Helvetica-Bold", 12)
        canvas.drawCentredString(self.x_start + self.width_internal / 2, self.y_start - 72, u"DETALLES  DE PASAJES - PEAJES Y VIATICOS")
        date = datetime.now()
        year=date.year
        gestion=u'GESTION '+ str(year)
        canvas.setFont("Helvetica-Bold", 12)
        canvas.drawCentredString(self.x_start + self.width_internal / 2, self.y_start - 87, gestion)

        self.draw_left_image(canvas = canvas,
            url = archivo_imagen,
            x = self.x_start + 30, 
            y = self.y_start - 8, 
            w = 55, 
            h = 55
        )
        #canvas.setFont('Helvetica', 8)
        #canvas.drawRightString(self.x_end, self.y_end - 10,
        #    'Página {} '.format(document.page)
        #)
        #canvas.restoreState()

    def page_number(self, canvas, document):
        canvas.saveState()
        canvas.setFont('Helvetica', 8)
        canvas.drawRightString(self.x_end, self.y_end - 10,
            'Página {} '.format(document.page)
        )
        canvas.restoreState()

    def draw(self):
        self.add(Spacer(1, 90))
        self.draw_table()
    def draw_table(self):
            
        date = datetime.now()
        year=date.year
        basic_style_full_doble = self.get_basic_style_full_doble()
        basic_style_body = self.get_basic_style_body()
        basic_style_full_doble_void = self.get_basic_style_full_doble_void()
        viaticos=viaticodiario.objects.filter(timestamp__year=year).distinct('centralizador')
        self.add(self.draw_in_table_top(0,viaticos,self.get_basic_style_full_doble_top(),basic_style_body, basic_style_full_doble_void, True))
        self.add(Spacer(1,0))
        self.add(self.draw_in_table_result(0,viaticos,self.get_basic_style_full_doble_button(), basic_style_body, basic_style_full_doble_void, True))
    def draw_in_table_top(self,index = 0, datereference = None, style = None,stylealt = None, stylevoid = None, hasheader = False):
        
        cabecera = [
            'INF. CONT.',
            'C-31',
            'N° PERSONAS',
            'PASAJES',
            'PEAJES',
            'IMPORTES',
            'RC-IVA',
            'LIQ. PAGABLE',
            'TOTAL A CANCELAR'
        ]

        preparandojson = []
        Totalsumatoriapasaje=0
        Totalsumatoriapeaje=0
        Totalsumatoriaimporte=0
        Totalsumatoriarciva=0
        Totalsumatorialiqpagable=0
        Totalsumatoriatotalcancelar=0   
        Sumatoriapasaje=0
        Sumatoriapeaje=0
        Sumatoriaimporte=0
        Sumatoriarciva=0
        Sumatorialiqpagable=0
        Sumatoriatotalcancelar=0
        numeropersonas=0
        preparandojson=[]
        for viatico in datereference:
                print(viatico.centralizador)
                ViaticoControl=viaticodiario.objects.filter(centralizador=viatico.centralizador)
                for vi in ViaticoControl:
                        numeropersonas=numeropersonas+1
                        Sumatoriapasaje=Sumatoriapasaje+vi.pasaje
                        Sumatoriapeaje=Sumatoriapeaje+vi.peaje
                        Sumatoriaimporte=Sumatoriaimporte+vi.Monto_pagado
                        Sumatoriarciva=Sumatoriarciva+vi.RC_IVA
                        Sumatorialiqpagable=Sumatorialiqpagable+vi.Liquido_pagable
                        Sumatoriatotalcancelar=Sumatoriatotalcancelar+vi.totalC

                        Totalsumatoriapasaje=Totalsumatoriapasaje+vi.pasaje
                        Totalsumatoriapeaje=Totalsumatoriapeaje+vi.peaje
                        Totalsumatoriaimporte=Totalsumatoriaimporte+vi.Monto_pagado
                        Totalsumatoriarciva=Totalsumatoriarciva+vi.RC_IVA
                        Totalsumatorialiqpagable=Totalsumatorialiqpagable+vi.Liquido_pagable
                        Totalsumatoriatotalcancelar=Totalsumatoriatotalcancelar+vi.totalC
                preparandojson.append({
                        "NumeroPersonas":numeropersonas,
                        "infcont":viatico.centralizador,
                        "cc":31,
                        "totalpasaje": Sumatoriapasaje,
                        "totalpeaje": Sumatoriapeaje,
                        "totalimporte": Sumatoriaimporte,
                        "totalrciva": Sumatoriarciva,
                        "totalliqpagable": Sumatorialiqpagable,
                        "totalliqtotalcancelar": Sumatoriatotalcancelar
                })
                                
                Sumatoriapasaje=0
                Sumatoriapeaje=0
                Sumatoriaimporte=0
                Sumatoriarciva=0
                Sumatorialiqpagable=0
                Sumatoriatotalcancelar=0
                numeropersonas=0
        detalles = [(via['infcont'],0,via['NumeroPersonas'],via['totalpasaje'],via['totalpeaje'],via['totalimporte'],via['totalrciva'],via['totalliqpagable'],via['totalliqtotalcancelar']) for via in preparandojson]
        cm = 29
        #cm = 23.4
        if hasheader:
            table = Table(
                [cabecera] + detalles,
                colWidths = [
                    1.8 * cm, 
                    1.7 * cm, 
                    2 * cm,  
                    1.7 * cm, 
                    1.7 * cm, 
                    1.7 * cm, 
                    1.4 * cm, 
                    2 * cm,
                    2.7 * cm
                ],
                splitByRow = 1,
                repeatRows = 0
            )
        
        if style:
            if hasheader:
                table.setStyle(style)
            elif stylealt:
                table.setStyle(stylealt)
        return table

    def draw_in_table_result(self,index = 0, datereference = None,style = None, stylealt = None, stylevoid = None, hasheader = False):
        Totalsumatoriapasaje=0
        Totalsumatoriapeaje=0
        Totalsumatoriaimporte=0
        Totalsumatoriarciva=0
        Totalsumatorialiqpagable=0
        Totalsumatoriatotalcancelar=0
        numero_personas=0
        for viatico in datereference:
                ViaticoControl=viaticodiario.objects.filter(centralizador=viatico.centralizador)
                for vi in ViaticoControl:
                        numero_personas=numero_personas+1
                        Totalsumatoriapasaje=Totalsumatoriapasaje+vi.pasaje
                        Totalsumatoriapeaje=Totalsumatoriapeaje+vi.peaje
                        Totalsumatoriaimporte=Totalsumatoriaimporte+vi.Monto_pagado
                        Totalsumatoriarciva=Totalsumatoriarciva+vi.RC_IVA
                        Totalsumatorialiqpagable=Totalsumatorialiqpagable+vi.Liquido_pagable
                        Totalsumatoriatotalcancelar=Totalsumatoriatotalcancelar+vi.totalC
        detalles = [(
                "TOTAL",
                " ",
                numero_personas,
                Totalsumatoriapasaje,
                Totalsumatoriapeaje,
                Totalsumatoriaimporte,
                Totalsumatoriarciva,
                Totalsumatorialiqpagable,
                Totalsumatoriatotalcancelar
                )]
        cm = 29
        #cm = 23.4
        if hasheader:
            table = Table(
                detalles,
                colWidths = [
                    1.8 * cm, 
                    1.7 * cm, 
                    2 * cm,  
                    1.7 * cm, 
                    1.7 * cm, 
                    1.7 * cm, 
                    1.4 * cm, 
                    2 * cm,
                    2.7 * cm
                ],
                splitByRow = 1,
                repeatRows = 1
            )
        if style:
            if hasheader:
                table.setStyle(style)
            elif stylealt:
                table.setStyle(stylealt)
        if len(datereference) == 0 and stylevoid is not None:
            table.setStyle(stylevoid)
        return table

    def draw_in_table(self,index = 0, datereference = None,style = None, stylealt = None, stylevoid = None, hasheader = False):
        supercabecera = [
            'Lic. Reyna Oporto Mamani',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
        ]
        cabecera = [
            'N° PERSONAS',
            'INF. CONT.',
            'C-31',
            'PASAJES',
            'PEAJES',
            'IMPORTES',
            'RC-IVA',
            'LIQ. PAGABLE',
            'TOTAL A CANCELAR'
        ]

        preparandojson = []
        Totalsumatoriapasaje=0
        Totalsumatoriapeaje=0
        Totalsumatoriaimporte=0
        Totalsumatoriarciva=0
        Totalsumatorialiqpagable=0
        Totalsumatoriatotalcancelar=0   
        Sumatoriapasaje=0
        Sumatoriapeaje=0
        Sumatoriaimporte=0
        Sumatoriarciva=0
        Sumatorialiqpagable=0
        Sumatoriatotalcancelar=0
        numeropersonas=0
        preparandojson=[]
        for viatico in datereference:
                print(viatico.centralizador)
                ViaticoControl=viaticodiario.objects.filter(centralizador=viatico.centralizador)
                for vi in ViaticoControl:
                        numeropersonas=numeropersonas+1
                        Sumatoriapasaje=Sumatoriapasaje+vi.pasaje
                        Sumatoriapeaje=Sumatoriapeaje+vi.peaje
                        Sumatoriaimporte=Sumatoriaimporte+vi.Monto_pagado
                        Sumatoriarciva=Sumatoriarciva+vi.RC_IVA
                        Sumatorialiqpagable=Sumatorialiqpagable+vi.Liquido_pagable
                        Sumatoriatotalcancelar=Sumatoriatotalcancelar+vi.totalC

                        Totalsumatoriapasaje=Totalsumatoriapasaje+vi.pasaje
                        Totalsumatoriapeaje=Totalsumatoriapeaje+vi.peaje
                        Totalsumatoriaimporte=Totalsumatoriaimporte+vi.Monto_pagado
                        Totalsumatoriarciva=Totalsumatoriarciva+vi.RC_IVA
                        Totalsumatorialiqpagable=Totalsumatorialiqpagable+vi.Liquido_pagable
                        Totalsumatoriatotalcancelar=Totalsumatoriatotalcancelar+vi.totalC
                preparandojson.append({
                        "NumeroPersonas":numeropersonas,
                        "infcont":viatico.centralizador,
                        "cc":31,
                        "totalpasaje": Sumatoriapasaje,
                        "totalpeaje": Sumatoriapeaje,
                        "totalimporte": Sumatoriaimporte,
                        "totalrciva": Sumatoriarciva,
                        "totalliqpagable": Sumatorialiqpagable,
                        "totalliqtotalcancelar": Sumatoriatotalcancelar
                })
                Sumatoriapasaje=0
                Sumatoriapeaje=0
                Sumatoriaimporte=0
                Sumatoriarciva=0
                Sumatorialiqpagable=0
                Sumatoriatotalcancelar=0
                numeropersonas=0
        detalles = [(via['NumeroPersonas'],via['infcont'],0,via['totalpasaje'],via['totalpeaje'],via['totalimporte'],via['totalrciva'],via['totalliqpagable'],via['totalliqtotalcancelar']) for via in preparandojson]
        cm = 29
        #cm = 23.4
        if hasheader:
            table = Table(
                [supercabecera] + [cabecera] + detalles,
                colWidths = [
                    2 * cm, 
                    1.7 * cm, 
                    2 * cm,  
                    1.7 * cm, 
                    1.7 * cm, 
                    1.7 * cm, 
                    1.4 * cm, 
                    2 * cm,
                    2.7 * cm
                ],
                splitByRow = 1,
                repeatRows = 1
            )
        if style:
            if hasheader:
                table.setStyle(style)
            elif stylealt:
                table.setStyle(stylealt)
        if len(datereference) == 0 and stylevoid is not None:
            table.setStyle(stylevoid)
        return table
class ListViewReport_mes(ReportsView):       
        cantidadDias=[]
        date = datetime.now()

        if  date.year %4==0  and date.year %100 !=0 or date.year % 400==0:
                cantidadDias=[31,29,31,30,31,30,31,31,30,31,30,31]
        else:
                cantidadDias=[31,28,31,30,31,30,31,31,30,31,30,31]
        sumapasaje=0
        sumapeaje=0
        sumaimporte=0
        sumarciva=0
        sumaliqpagable=0
        sumaliqtotalcancelar=0
        dias=''
        vacio=0

        model=SecresubSecre.objects.all()
        cont=1
        errorone=''
        varificar=False
        context={}
        def sum(self,vias):
                for vi in vias:
                        self.sumapasaje=self.sumapasaje+vi.pasaje
                        self.sumapeaje=self.sumapeaje+vi.peaje
                        self.sumaimporte=self.sumaimporte+vi.Monto_pagado
                        self.sumarciva=self.sumarciva+vi.RC_IVA
                        self.sumaliqpagable=self.sumaliqpagable+vi.Liquido_pagable
                        self.sumaliqtotalcancelar=self.sumaliqtotalcancelar+vi.totalC                
        def retornar_json(self,valor):
                self.preparandojson.append({   
                        "DesdeHasta":valor[0],                                                                                                                                             
                        "id":valor[1],
                        "pasaje": self.sumapasaje,
                        "peaje": self.sumapeaje,
                        "importe": self.sumaimporte,
                        "rciva": self.sumarciva,
                        "liqpagable": self.sumaliqpagable,
                        "liqtotalcancelar": self.sumaliqtotalcancelar                                                                                                                                              
                })
                self.sumapasaje=0
                self.sumapeaje=0
                self.sumaimporte=0
                self.sumarciva=0
                self.sumaliqpagable=0
                self.sumaliqtotalcancelar=0                                                        
                self.dias=''  
                self.vacio=0
        def llevar_json_fechas(self,request_valor): 
                fechahoy=self.date.month                 
                if int(request_valor)==2:
                        diastotales=(fechahoy/2)
                        if diastotales*2>=2:                                             
                                if fechahoy == diastotales*2:
                                        if self.date.day < self.cantidadDias[fechahoy-1]:
                                                diastotales=diastotales-1                                                                                                                                                                               
                                contfecha=1                                                                                
                                self.vacio=0
                                while contfecha <= (diastotales*2):
                                        vias=viaticodiario.objects.filter(timestamp__year=self.date.year,timestamp__month=contfecha)
                                        if vias.exists():
                                                self.sum(vias)
                                        else:
                                                self.vacio=self.vacio+1                                                
                                        self.dias=self.dias+' '+self.meseslist[contfecha-1]
                                        if contfecha%2!=0:
                                                self.dias = self.dias + ' - '                                                        
                                        if contfecha%2==0:
                                                if self.vacio!=2:                                                                
                                                        print(self.dias)
                                                self.retornar_json([self.dias,contfecha])                                                                             
                                        contfecha=contfecha+1    
                                self.errorone='Aun no existe viaticos para Bimestral'                 
                if int(request_valor)==4:
                        day=['Enero - Junio','Julio - Diciembre']
                        one=0                                                                                                       
                        if fechahoy > 6:   
                                if fechahoy == 12:                                        
                                        if self.date.day >= self.cantidadDias[fechahoy-1]:
                                                cont=1
                                                while cont <= 12:  
                                                        vias=viaticodiario.objects.filter(timestamp__year=self.date.year,timestamp__month=cont)
                                                        if vias.exists():                                                                          
                                                                self.sum(vias)                                                       
                                                        if  cont == 6 or  cont == 12:
                                                                self.retornar_json([day[one],cont])
                                                                one=one+1                                                                                                                                               
                                                        cont=cont+1
                                        else:
                                                cont=1
                                                while cont <= 6:  
                                                        vias=viaticodiario.objects.filter(timestamp__year=self.date.year,timestamp__month=cont)
                                                        if vias.exists():    
                                                                self.sum(vias)                                                                                                                                      
                                                        self.dias=self.dias+' '+self.meseslist[cont-1]
                                                        
                                                        cont=cont+1 
                                                self.retornar_json([day[0],cont])
                                else:                                                                     
                                        
                                        cont=1
                                        while cont <= 6:  
                                                vias=viaticodiario.objects.filter(timestamp__year=self.date.year,timestamp__month=cont)
                                                if vias.exists():   
                                                        self.sum(vias)                                                                                                                               
                                                self.dias=self.dias+' '+self.meseslist[cont-1]
                                                cont=cont+1 
                                        self.retornar_json([day[0],cont])                         
                        else:                                                                                                                                                                                                                                                                                                          
                                self.errorone='Aun no existe viaticos para Semestral'                                                                                                                                                                                        
                if int(request_valor)==3:
                        diastotales=(fechahoy/3)                                        
                        if diastotales*3>=3:                                             
                                if fechahoy == diastotales*3:
                                        if self.date.day < self.cantidadDias[(diastotales*3)-1]:
                                                diastotales=diastotales-1                                                                                                                                                                               
                                contfecha=1
                                day=['Enero - Marzo','Abril - Junio','Julio - Septiembre','Octubre - Diciembre']
                                one=0
                                while contfecha <= (diastotales*3):                                                        
                                        vias=viaticodiario.objects.filter(timestamp__year=self.date.year,timestamp__month=contfecha)
                                        if vias.exists():
                                                self.sum(vias)                                                                
                                        else:
                                                self.vacio=self.vacio+1                                                                                                        
                                        if contfecha%3==0:
                                                
                                                #if vacio!=3:                                                                
                                                #        print(dias)
                                                self.retornar_json([day[one],contfecha])                                             
                                                one=one+1                                                                                                                                                                             
                                        contfecha=contfecha+1    
                                self.errorone='Aun no existe viaticos para Trimestral'    
                if int(request_valor)==5:
                        if fechahoy == 12:
                                if self.date.day >= self.cantidadDias[11]:
                                        cont=1
                                        while cont <= 12:  
                                                vias=viaticodiario.objects.filter(timestamp__year=self.date.year,timestamp__month=cont)
                                                if vias.exists(): 
                                                        self.sum(vias)                                                                                                                                
                                                cont=cont+1
                                        self.retornar_json(["Enero - Diciembre",1])                                                                                                                                                                                                                                
                        self.errorone='Aun no existe viaticos para Anual'
        def post(self,request,*args,**kwargs):
                self.preparandojson=[]
                anos1=request.POST.get('anios')
                meses1=request.POST.get('meses')
                secretaria1=request.POST.get('secretaria')
                fechas1=request.POST.get('fechass')
                fechadesde1=request.POST.get('fechadesde')
                fechahasta1=request.POST.get('fechahasta')
                if fechas1 == 'None':
                        if fechadesde1 == '' and fechahasta1 == '':
                                self.form_valid([anos1,'SELECCIONE POR LO MENOS EL CAMPO GESTION '])
                        #self.form_valid([meses1,'SELECCIONE EL CAMPO MES '])                       
                if len(self.error)==0:
                        self.varificar=False
                if self.varificar:                                                   
                        self.context={
                                'ano':self.cargar(),
                                'meses':self.meseslist,
                                'error':self.error, 
                                'secretaria':self.model,                                                  
                                'mes':meses1,
                                'anoss':anos1,
                                'secre':secretaria1                                
                        }      
                        return render(request,"reportes/listar_por_mes_clas.html",self.context)
                else: 
                        one=True
                        two=True
                        tree=True
                        four=True
                        apell=""
                        verificar=False
                        if fechas1 != 'None' and anos1 == 'None' and meses1 == 'None' and fechadesde1 == '' and fechahasta1 == '' and secretaria1 == 'None' :
                                verificar=True
                                one = False
                                two = False  
                                tree = False                           
                                self.llevar_json_fechas(fechas1)
                                if len(self.preparandojson) == 0:
                                        self.context={
                                                'ano':self.cargar(),
                                                'meses':self.meseslist,
                                                'secretaria':self.model,                                                                                                              
                                                'error':self.errorone,
                                                'viaticoOther':self.preparandojson
                                        }
                                else:
                                        self.context={
                                                'others':True,
                                                'valorOther':fechas1,
                                                'ano':self.cargar(),
                                                'meses':self.meseslist,
                                                'secretaria':self.model,                                                                                                                            
                                                'viaticoOther':self.preparandojson
                                        } 
                        if one and anos1 != 'None' and meses1 == 'None' and fechadesde1 == '' and fechahasta1 == '' and secretaria1 == 'None' and fechas1 == 'None':
                                verificar=True
                                two=False
                                tree=False
                                four=False
                                cont=1
                       
                                for viatico in viaticodiario.objects.all():
                                        if viatico.timestamp.strftime('%Y') == anos1:    
                                                if viatico.solicitante.amaterno == None:
                                                        self.llevar_json_otros([viatico.ue,viatico.prog,viatico.act,viatico.proy,viatico.solicitante.ci,viatico.solicitante.nombre.upper(),viatico.solicitante.apaterno.upper(),apell,viatico.pasaje,viatico.peaje,viatico.Monto_pagado,viatico.RC_IVA,viatico.Liquido_pagable,viatico.totalC,viatico.solicitante.bcontrol,self.cont])                                                                
                                                else:                                                    
                                                        self.llevar_json_otros([viatico.ue,viatico.prog,viatico.act,viatico.proy,viatico.solicitante.ci,viatico.solicitante.nombre.upper(),viatico.solicitante.apaterno.upper(),viatico.solicitante.amaterno.upper(),viatico.pasaje,viatico.peaje,viatico.Monto_pagado,viatico.RC_IVA,viatico.Liquido_pagable,viatico.totalC,viatico.solicitante.bcontrol,cont])                                                                                                                                                                                                                                                                
                                                cont=cont+1
                
                                if len(self.preparandojson) == 0:
                                        self.context={
                                                'ano':self.cargar(),
                                                'meses':self.meseslist,
                                                'secretaria':self.model,                                               
                                                'anoss':anos1,                                                
                                                'error':'NO EXISTE NINGUN VIATICO CON ESA FECHA , AÑO Y SECRETARIA',
                                                'viatico':self.preparandojson
                                        }
                                else:
                                        self.context={
                                                'ano':self.cargar(),
                                                'meses':self.meseslist,
                                                'secretaria':self.model,
                                                
                                                'anoss':anos1,
                                            
                                                'tres':True,
                                                'viatico':self.preparandojson
                                        }  
                        if two and  anos1 != 'None' and meses1 != 'None' and secretaria1 != 'None' and fechadesde1 == '' and fechahasta1 == ''  and fechas1 == 'None':
                                verificar=True
                                tree=False
                                four=False
                                cont=1
                                viaRec=get_object_or_404(SecresubSecre,descripcion__id=secretaria1)
                                itemue=viaRec.ue
                                itemprog=viaRec.prog
                                itemact=viaRec.act
                                for viatico in viaticodiario.objects.all():
                                        for mese in xrange(len(self.mesesingles)):
                                                if self.mesesingles[mese]==viatico.timestamp.strftime('%B'):
                                                        if self.meseslist[mese] == meses1 and viatico.timestamp.strftime('%Y') == anos1 and itemue==viatico.ue and itemprog==viatico.prog and itemact==viatico.act:                                                        
                                                                if viatico.solicitante.amaterno == None:
                                                                        self.llevar_json_otros([viatico.ue,viatico.prog,viatico.act,viatico.proy,viatico.solicitante.ci,viatico.solicitante.nombre.upper(),viatico.solicitante.apaterno.upper(),apell,viatico.pasaje,viatico.peaje,viatico.Monto_pagado,viatico.RC_IVA,viatico.Liquido_pagable,viatico.totalC,viatico.solicitante.bcontrol,cont])                                                                                                                                                                                                                                                                
                                                                else:
                                                                        self.llevar_json_otros([viatico.ue,viatico.prog,viatico.act,viatico.proy,viatico.solicitante.ci,viatico.solicitante.nombre.upper(),viatico.solicitante.apaterno.upper(),viatico.solicitante.amaterno.upper(),viatico.pasaje,viatico.peaje,viatico.Monto_pagado,viatico.RC_IVA,viatico.Liquido_pagable,viatico.totalC,viatico.solicitante.bcontrol,cont])                                                                                                                                                                                                                                                                
                                                                cont=cont+1
                                
                                if len(self.preparandojson) == 0:
                                        self.context={
                                                'ano':self.cargar(),
                                                'meses':self.meseslist,
                                                'secretaria':self.model,
                                                'mes':meses1,
                                                'anoss':anos1,
                                                'secre':secretaria1,
                                                'error':'NO EXISTE NINGUN VIATICO CON ESA FECHA , AÑO Y SECRETARIA',
                                                'viatico':self.preparandojson
                                        }
                                else:
                                        self.context={
                                                'ano':self.cargar(),
                                                'meses':self.meseslist,
                                                'secretaria':self.model,
                                                'mes':meses1,
                                                'anoss':anos1,
                                                'secre':secretaria1,
                                                'dos':True,
                                                'viatico':self.preparandojson
                                        } 
                        if tree and meses1 != 'None' and fechadesde1 == '' and fechahasta1 == '' and  anos1 != 'None' and secretaria1 == 'None' and fechas1 == 'None':
                                verificar=True
                                four=False
                                cont=1
                                for viatico in viaticodiario.objects.all():
                                        for mese in xrange(len(self.mesesingles)):
                                                if self.mesesingles[mese]==viatico.timestamp.strftime('%B'):
                                                        if self.meseslist[mese] == meses1 and viatico.timestamp.strftime('%Y') == anos1:                                                                
                                                                if viatico.solicitante.amaterno == None:
                                                                        self.llevar_json_otros([viatico.ue,viatico.prog,viatico.act,viatico.proy,viatico.solicitante.ci,viatico.solicitante.nombre.upper(),viatico.solicitante.apaterno.upper(),apell,viatico.pasaje,viatico.peaje,viatico.Monto_pagado,viatico.RC_IVA,viatico.Liquido_pagable,viatico.totalC,viatico.solicitante.bcontrol,cont])                                                                                                                                                                                                                                                                
                                                                else:
                                                                        self.llevar_json_otros([viatico.ue,viatico.prog,viatico.act,viatico.proy,viatico.solicitante.ci,viatico.solicitante.nombre.upper(),viatico.solicitante.apaterno.upper(),viatico.solicitante.amaterno.upper(),viatico.pasaje,viatico.peaje,viatico.Monto_pagado,viatico.RC_IVA,viatico.Liquido_pagable,viatico.totalC,viatico.solicitante.bcontrol,cont])                                                                                                                                                                                                                                                                
                                                                cont=cont+1
                                if len(self.preparandojson) == 0:
                                        self.context={
                                                'ano':self.cargar(),
                                                'meses':self.meseslist,
                                                'secretaria':self.model,
                                                'mes':meses1,
                                                'anoss':anos1,
                                                'error':'NO EXISTE NINGUN VIATICO CON ESA FECHA NI AÑO',
                                                'viatico':self.preparandojson
                                        }  
                                else:
                                        self.context={
                                                'ano':self.cargar(),
                                                'meses':self.meseslist,
                                                'secretaria':self.model,
                                                'mes':meses1,
                                                'anoss':anos1,
                                                'uno':True,
                                                'viatico':self.preparandojson
                                        }                                     
                        if four and fechadesde1 != '' and fechahasta1 != '' and meses1 == 'None'  and  anos1 == 'None' and secretaria1 == 'None' and fechas1 == 'None':
                                self.error="No existe ninguno Viatico hacia esa Persona"                                
                                fechadesde=fechadesde1
                                fechahasta=fechahasta1  
                                cont=1         
                                verificar=True                                                                             
                                viaa=viaticodiario.objects.filter(                                     
                                        fecha_salida__gte=fechadesde,
                                        fecha_legada__lte=fechahasta) 
                                if viaa.exists():                                  
                                        for viatico in viaa:
                                                if viatico.solicitante.amaterno == None:
                                                        self.llevar_json_otros([viatico.ue,viatico.prog,viatico.act,viatico.proy,viatico.solicitante.ci,viatico.solicitante.nombre.upper(),viatico.solicitante.apaterno.upper(),apell,viatico.pasaje,viatico.peaje,viatico.Monto_pagado,viatico.RC_IVA,viatico.Liquido_pagable,viatico.totalC,viatico.solicitante.bcontrol,cont])                                                                                                                                                                                                                                                                
                                                else:
                                                        self.llevar_json_otros([viatico.ue,viatico.prog,viatico.act,viatico.proy,viatico.solicitante.ci,viatico.solicitante.nombre.upper(),viatico.solicitante.apaterno.upper(),viatico.solicitante.amaterno.upper(),viatico.pasaje,viatico.peaje,viatico.Monto_pagado,viatico.RC_IVA,viatico.Liquido_pagable,viatico.totalC,viatico.solicitante.bcontrol,cont])                                                                                                                                                                                                                                                                
                                                cont=cont+1
                                if len(self.preparandojson) != 0:
                                        self.context={
                                                'ano':self.cargar(),
                                                'meses':self.meseslist,
                                                'secretaria':self.model,
                                                'viatico':self.preparandojson,
                                         
                                        }
                                else:
                                        self.context={
                                                'ano':self.cargar(),
                                                'meses':self.meseslist,
                                                'secretaria':self.model,
                                                'error':self.error,
                                            
                                                'fechadesde':fechadesde,
                                                'fechahasta':fechahasta,
                                        }
                        if verificar ==False:
                                self.context={'ano':self.cargar(),'meses':self.meseslist,'secretaria':self.model} 
                        return render(request,"reportes/listar_por_mes_clas.html",self.context)
        def get(self,request,*args,**kwargs):                
                self.context={'ano':self.cargar(),'meses':self.meseslist,'secretaria':self.model} 
                return render(request,"reportes/listar_por_mes_clas.html",self.context)                                  
class ListViewReport_emp(ReportsView):        
        model=viaticodiario.objects.all()
        def post(self,request,*args,**kwargs):
                self.preparandojson=[]
                apell=""
                anos1=request.POST.get('anios')
                user_id1=request.POST.get('user_id')
                mes1=request.POST.get('mes') 
                
                #print('%s-%s'%(listaAleatorios(10),(str(anos1)+letras())))
                #print('%s-%s'%(listaAleatorios(10),(str(user_id1)+letras())))
                #print(mes1)
                self.form_valid([anos1,'SELECCIONE EL CAMPO GESTION '])
                if user_id1 == "":                        
                        self.varificar=True
                        self.error=self.error+'SELECCIONE EL CAMPO C.I. '+'\n'
                if len(self.error)==0:
                        self.varificar=False
                use=user_id1                                        
                if use == None:
                        use=""
                if self.varificar:                                                   
                        context={
                                'ano':self.cargar(),
                                'meses':self.meseslist,
                                'error':self.error,                   
                                'user_id':use,
                                'mes':mes1,
                                'anoss':anos1
                        }      
                        return render(request,"reportes/listar_por_emp_clas.html",context)
                else:                        
                        one=True
                        two=True      
                        verificar=False                    
                        if one and user_id1 != "" and  mes1 != '...' and anos1 != '...':
                                two=False                                                                                                                         
                                verificar=True
                                for viatico in self.model:
                                        for mese in xrange(len(self.mesesingles)):
                                                if self.mesesingles[mese]==viatico.timestamp.strftime('%B'):
                                                        if self.meseslist[mese] == mes1 and viatico.timestamp.strftime('%Y') == anos1 and int(user_id1)==viatico.id_solicitante:                                                                                                                                
                                                                if viatico.solicitante.amaterno == None:
                                                                        self.llevar_json_otros([viatico.ue,viatico.prog,viatico.act,viatico.proy,viatico.solicitante.ci,viatico.solicitante.nombre.upper(),viatico.solicitante.apaterno.upper(),apell,viatico.pasaje,viatico.peaje,viatico.Monto_pagado,viatico.RC_IVA,viatico.Liquido_pagable,viatico.totalC,viatico.solicitante.bcontrol,self.cont])                                                                
                                                                else:
                                                                        self.llevar_json_otros([viatico.ue,viatico.prog,viatico.act,viatico.proy,viatico.solicitante.ci,viatico.solicitante.nombre.upper(),viatico.solicitante.apaterno.upper(),viatico.solicitante.amaterno.upper(),viatico.pasaje,viatico.peaje,viatico.Monto_pagado,viatico.RC_IVA,viatico.Liquido_pagable,viatico.totalC,viatico.solicitante.bcontrol,self.cont])                                                                
                                                                self.cont=self.cont+1                                                                                         
                                if len(self.preparandojson) == 0:
                                        context={
                                                'ano':self.cargar(),
                                                'meses':self.meseslist,                                        
                                                'mes':mes1,
                                                'anoss':anos1,
                                                'user_id':user_id1,
                                                'error':'NO EXISTE NINGUN VIATICO CON ESA FECHA , AÑO Y C.I.',
                                                'viatico':self.preparandojson
                                        }
                                else:                                  
                                        context={
                                                'ano':self.cargar(),
                                                'meses':self.meseslist,                                                
                                                'mes':mes1,
                                                'anoss':anos1,
                                                'user_id':user_id1,
                                                'dos':True,
                                                'viatico':self.preparandojson
                                        }
                        if two and user_id1 != "" and  anos1 != '...' and mes1 == '...':                            
                                preparandojson=[]                              
                                verificar=True
                                for viatico in self.model:
                                        if viatico.timestamp.strftime('%Y') == anos1 and int(user_id1)==viatico.id_solicitante:                                                
                                                self.llevar_json_otros([viatico.ue,viatico.prog,viatico.act,viatico.proy,viatico.solicitante.ci,viatico.solicitante.nombre.upper(),viatico.solicitante.apaterno.upper(),viatico.solicitante.amaterno.upper(),viatico.pasaje,viatico.peaje,viatico.Monto_pagado,viatico.RC_IVA,viatico.Liquido_pagable,viatico.totalC,viatico.solicitante.bcontrol,self.cont])                                                                                                         
                                                self.cont=self.cont+1
                                if len(self.preparandojson) == 0:
                                        context={                                                
                                                'ano':self.cargar(),
                                                'meses':self.meseslist,                                                
                                                'anoss':anos1,
                                                'user_id':user_id1,
                                                'error':'NO EXISTE NINGUN VIATICO CON ESE C.I. Y GESTION',
                                                'viatico':self.preparandojson
                                        }  
                                else:                                        
                                        context={
                                                'ano':self.cargar(),
                                                'meses':self.meseslist,                                               
                                                'anoss':anos1,
                                                'anoss_url':anos1.encode('utf-8'),
                                                'user_id':user_id1,                                                
                                                'user_id_url':anos1,
                                                'uno':True,
                                                'viatico':self.preparandojson
                                        }     
                        if verificar==False:
                                context={'ano':self.cargar(),'meses':self.meseslist,'user_id':use,'mes':mes1,'anoss':anos1}                   
                        return render(request,"reportes/listar_por_emp_clas.html",context)
        def get(self,request,*args,**kwargs):                 
                context={'ano':self.cargar(),'meses':self.meseslist} 
                return render(request,"reportes/listar_por_emp_clas.html",context)
 

class ReporteViaticos(BasePlatypusReportOther):
   
    def __init__(self):
        self.begin(orientation = 'LANDSCAPE', rightMargin = 28, leftMargin = 28, topMargin = 36, bottomMargin = 28)

    def get(self, request, *args, **kwargs):
        slug =self.kwargs.get('slug')
        gestion =self.kwargs.get('slugu')
        secre =self.kwargs.get('sluguh')                       
        self.draw(slug,gestion,secre)
        self.write(onFirstPage = self.title)
        return self.response

    def title(self,canvas, document,**kwargs):
        slug =self.kwargs.get('slug')
        gestion =self.kwargs.get('slugu')
        title = 'BOLETAS REGISTRADAS'
        canvas.saveState()
        
        archivo_imagen = settings.MEDIA_ROOT+'\images\logoo.png'
        archivo_imagen1 = settings.MEDIA_ROOT+'\images\money.png'
                
        canvas.setFont("Helvetica-Bold", 11)
        canvas.drawCentredString(self.x_start + self.width_internal / 2, self.y_start - 25, u"GOBIERNO AUTONOMO DEPARTAMENTAL DE POTOSI")
        canvas.setFont("Helvetica-Bold", 11)
        canvas.drawCentredString(self.x_start + self.width_internal / 2, self.y_start - 45, u"Secretaria Departamental Administracion y Financiera")
      
        canvas.drawImage(archivo_imagen1, self.x_start + 600,self.y_start - 64, 55, 55, preserveAspectRatio = True)
        
        canvas.setLineWidth(1)
        canvas.line(self.x_start+180, self.y_start-60, 585, self.y_start-60)
        
        canvas.setFont("Helvetica-Bold", 10)
        canvas.drawCentredString(self.x_start + self.width_internal / 2, self.y_start - 72, u"DETALLE DE PASAJES Y VIÁTICOS DEL PERSONAL DEL GOBIERNO AUTÓNOMO")
        if str(slug)!="None":           
                gestion=slug.upper()+' '+u'GESTION '+ gestion
        else:
                gestion=u'GESTION '+ gestion
        canvas.setFont("Helvetica-Bold", 10)
        canvas.drawCentredString(self.x_start + self.width_internal / 2, self.y_start - 87, gestion)

        self.draw_left_image(canvas = canvas,
            url = archivo_imagen,
            x = self.x_start + 70, 
            y = self.y_start - 8, 
            w = 55, 
            h = 55
        )
    def draw(self,slug,gestion,secre):
        
        self.add(Spacer(1, 90))
        self.draw_table(slug,gestion,secre)
    def draw_table(self,slug,gestion,secre):
        basic_style_full_doble = self.get_basic_style_full_doble()
        basic_style_body = self.get_basic_style_body()
        basic_style_full_doble_void = self.get_basic_style_full_doble_void()
        viaticos=viaticodiario.objects.all()
        self.add(self.draw_in_table_top(0,viaticos,slug,gestion,secre,self.get_basic_style_full_doble_top(),basic_style_body, basic_style_full_doble_void, True))
        self.add(self.draw_in_table_result(0,viaticos,self.get_basic_style_full_doble_button(), basic_style_body, basic_style_full_doble_void, True)) 
        self.add(Spacer(1, 20))
        self.add(self.draw_in_table_resumen(0,viaticos,self.get_basic_style_full_doble_resumen(), basic_style_body, basic_style_full_doble_void, True)) 
    def draw_in_table_top(self,index = 0,datereference = None,slug= None,gestion= None,secre=None,style = None,stylealt = None, stylevoid = None, hasheader = False):        
        if secre != "None":
                ViaticoRecorrer=SecresubSecre.objects.filter(descripcion__id=secre)
                itemue=0
                itemprog=0
                itemact=0
                for visss in ViaticoRecorrer:
                        itemue=visss.ue
                        itemprog=visss.prog
                        itemact=visss.act
        
        meses=['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
        mesesingles=['January','February','March','April','May','June','July','August','September','October','November','December']
        supercabecera = [
                'N°',
                'NOMBRES Y APELLIDOS',
                'C.I.',
                'PASAJES',
                'PEAJES',
                'VIATICO',
                '',
                '',
                'TOTAL A CANCELAR',
                'CONTROL PRESUPUESTARIO',
                '',
                '',
                '',
                'N° CUENTA'
        ]
        cabecera = [
            '',
            '',
            '',
            '',
            '',
            'IMPORTES',
            'RC-IVA',
            'LIQ. PAGABLE',
            '',
            'U.E',
            'PROG',
            'PROY',
            'ACT',
            ''		
        ]
        preparandojson = []
        cont=1
        apell=""
        for viatico in datereference:
                
                for mese in xrange(len(mesesingles)):
                        if mesesingles[mese]==viatico.timestamp.strftime('%B'):
                                if secre== "None" and slug=="None" and gestion !="None":
                                        if viatico.timestamp.strftime('%Y') == gestion:
                                                ue=0
                                                prog=0
                                                act=0
                                                proy=0
                                                if viatico.ue < 10:
                                                        ue='%s%s'%(0,viatico.ue)
                                                else:
                                                        ue=viatico.ue
                                                
                                                if viatico.prog < 10:
                                                        prog='%s%s'%(0,viatico.prog)
                                                else:
                                                        prog=viatico.prog

                                                if viatico.act < 10:
                                                        act='%s%s'%(0,viatico.act)
                                                else:
                                                        act=viatico.act

                                                if viatico.proy < 10:
                                                        if viatico.proy == None:
                                                                proy=""
                                                        else:
                                                                proy='%s%s'%(0,viatico.proy)
                                                else:
                                                        proy=viatico.proy
                                                if viatico.solicitante.amaterno != None:
                                                        apell=viatico.solicitante.amaterno.upper()
                                                preparandojson.append({
                                                        "ci":viatico.solicitante.ci,
                                                        "NombreCompleto":'%s %s %s'%(viatico.solicitante.nombre.upper(),viatico.solicitante.apaterno.upper(),apell),
                                                        "id":cont,
                                                        "pasaje": self.redondear(viatico.pasaje),
                                                        "peaje": self.redondear(viatico.peaje),
                                                        "importe": self.redondear(viatico.Monto_pagado),
                                                        "rciva": self.redondear(viatico.RC_IVA),
                                                        "liqpagable": self.redondear(viatico.Liquido_pagable),
                                                        "liqtotalcancelar": self.redondear(viatico.totalC),
                                                        "ue":ue,
                                                        "prog":prog,
                                                        "act":act,
                                                        "proy":viatico.proy,
                                                        "numero":viatico.solicitante.bcontrol
                                                })
                                    
                                else:
                                        if secre == "None":
                                                if meses[mese] == slug and viatico.timestamp.strftime('%Y') == gestion:
                                                        ue=0
                                                        prog=0
                                                        act=0
                                                        proy=0
                                                        if viatico.ue < 10:
                                                                ue='%s%s'%(0,viatico.ue)
                                                        else:
                                                                ue=viatico.ue
                                                        
                                                        if viatico.prog < 10:
                                                                prog='%s%s'%(0,viatico.prog)
                                                        else:
                                                                prog=viatico.prog

                                                        if viatico.act < 10:
                                                                act='%s%s'%(0,viatico.act)
                                                        else:
                                                                act=viatico.act

                                                        if viatico.proy < 10:
                                                                proy='%s%s'%(0,viatico.proy)
                                                        else:
                                                                proy=viatico.proy
                                                
                                                        preparandojson.append({
                                                                "ci":viatico.solicitante.ci,
                                                                "NombreCompleto":'%s %s %s'%(viatico.solicitante.nombre.upper(),viatico.solicitante.apaterno.upper(),viatico.solicitante.amaterno.upper()),
                                                                "id":cont,
                                                                "pasaje": self.redondear(viatico.pasaje),
                                                                "peaje": self.redondear(viatico.peaje),
                                                                "importe": self.redondear(viatico.Monto_pagado),
                                                                "rciva": self.redondear(viatico.RC_IVA),
                                                                "liqpagable": self.redondear(viatico.Liquido_pagable),
                                                                "liqtotalcancelar": self.redondear(viatico.totalC),
                                                                "ue":ue,
                                                                "prog":prog,
                                                                "act":act,
                                                                "proy":viatico.proy,
                                                                "numero":viatico.solicitante.bcontrol
                                                        })
                                        else:
                                                if meses[mese] == slug and viatico.timestamp.strftime('%Y') == gestion and itemue==viatico.ue and itemprog==viatico.prog and itemact==viatico.act:
                                                        ue=0
                                                        prog=0
                                                        act=0
                                                        proy=0
                                                        if viatico.ue < 10:
                                                                ue='%s%s'%(0,viatico.ue)
                                                        else:
                                                                ue=viatico.ue
                                                        
                                                        if viatico.prog < 10:
                                                                prog='%s%s'%(0,viatico.prog)
                                                        else:
                                                                prog=viatico.prog

                                                        if viatico.act < 10:
                                                                act='%s%s'%(0,viatico.act)
                                                        else:
                                                                act=viatico.act

                                                        if viatico.proy < 10:
                                                                proy='%s%s'%(0,viatico.proy)
                                                        else:
                                                                proy=viatico.proy
                                                
                                                        preparandojson.append({
                                                                "ci":viatico.solicitante.ci,
                                                                "NombreCompleto":'%s %s %s'%(viatico.solicitante.nombre.upper(),viatico.solicitante.apaterno.upper(),viatico.solicitante.amaterno.upper()),
                                                                "id":cont,
                                                                "pasaje": self.redondear(viatico.pasaje),
                                                                "peaje": self.redondear(viatico.peaje),
                                                                "importe": self.redondear(viatico.Monto_pagado),
                                                                "rciva": self.redondear(viatico.RC_IVA),
                                                                "liqpagable": self.redondear(viatico.Liquido_pagable),
                                                                "liqtotalcancelar": self.redondear(viatico.totalC),
                                                                "ue":ue,
                                                                "prog":prog,
                                                                "act":act,
                                                                "proy":viatico.proy,
                                                                "numero":viatico.solicitante.bcontrol
                                                        })
                cont=cont+1
        detalles = [(
                via['id'],
                via['NombreCompleto'],
                via['ci'],
                via['pasaje'],
                via['peaje'],
                via['importe'],
                via['rciva'],
                via['liqpagable'],
                via['liqtotalcancelar'],
                via['ue'],
                via['prog'],
                via['proy'],
                via['act'],
                via['numero']
                ) for via in preparandojson]
        cm = 29
        #cm = 23.4
        if hasheader:
            table = Table(
                [supercabecera] + [cabecera] + detalles,
                colWidths = [
                    0.9 * cm, 
                    5 * cm, 
                    1.5 * cm,  
                    1.5 * cm, 
                    1.5 * cm, 
                    1.5 * cm, 
                    1.4 * cm, 
                    2 * cm,
                    2.7 * cm,
                    1 * cm,
                    1 * cm,
                    1 * cm,
                    1 * cm,
                    2.1 * cm
                ],
                splitByRow = 1,
                repeatRows = 0
            )
        
        if style:
            if hasheader:
                table.setStyle(style)
            elif stylealt:
                table.setStyle(stylealt)
        return table
    def redondear(self,valor=None):
        leter=str(valor)
        for le in xrange(len(leter)):
                if leter[le]=='.':
                        if (le+2)==len(leter):
                                return '%s%s'%(valor,0) 
                        else:     
                                return valor
    def draw_in_table_resumen(self,index = 0, datereference = None,style = None, stylealt = None, stylevoid = None, hasheader = False):
        cabecera = [
            'RESUMEN',
            ' '
        ]
        Sumatoriapasaje=0
        Sumatoriapeaje=0
        Sumatoriaimporte=0
        Sumatoriarciva=0
        Sumatorialiqpagable=0
        Sumatoriatotalcancelar=0
        preparandojson=[]
        for viatico in datereference:                
                Sumatoriapasaje=Sumatoriapasaje+viatico.pasaje
                Sumatoriapeaje=Sumatoriapeaje+viatico.peaje
                Sumatoriaimporte=Sumatoriaimporte+viatico.Monto_pagado
                Sumatoriarciva=Sumatoriarciva+viatico.RC_IVA
                Sumatorialiqpagable=Sumatorialiqpagable+viatico.Liquido_pagable
                Sumatoriatotalcancelar=Sumatoriatotalcancelar+viatico.totalC  
            
        detalles = [(
                "DESCRIPCIÓN",
                "IMPORTE EN BS."
                )]
        VIATICO = [(
                "VIÁTICO",
                self.redondear(Sumatoriaimporte)
                )]
        PEAJES = [(
                "PEAJES",
                self.redondear(Sumatoriapeaje)
                )]
        PASAJES = [(
                "PASAJES",
                self.redondear(Sumatoriapasaje)
                )]
        TOTAL = [(
                "TOTAL",
                self.redondear(Sumatoriapasaje+Sumatoriapeaje+Sumatoriaimporte)
                )]
        RC = [(
                "Menos RC - IVA",
                self.redondear(Sumatoriarciva)
                )]
        LIQUIDO = [(
                "LIQ. PAGABLE",
                self.redondear(Sumatorialiqpagable)
                )]
        cm = 29
        #cm = 23.4
        if hasheader:
            table = Table(
                [cabecera] + detalles+VIATICO+PEAJES+PASAJES+TOTAL+RC+LIQUIDO,
                colWidths = [
                    3 * cm, 
                    3 * cm                    
                ],
                splitByRow = 1,
                repeatRows = 1
            )
        if style:
            if hasheader:
                table.setStyle(style)
            elif stylealt:
                table.setStyle(stylealt)
        if len(datereference) == 0 and stylevoid is not None:
            table.setStyle(stylevoid)
        return table
    def draw_in_table_result(self,index = 0, datereference = None,style = None, stylealt = None, stylevoid = None, hasheader = False):
        Totalsumatoriapasaje=0
        Totalsumatoriapeaje=0
        Totalsumatoriaimporte=0
        Totalsumatoriarciva=0
        Totalsumatorialiqpagable=0
        Totalsumatoriatotalcancelar=0
        for viatico in datereference:
                Totalsumatoriapasaje=Totalsumatoriapasaje+viatico.pasaje
                Totalsumatoriapeaje=Totalsumatoriapeaje+viatico.peaje
                Totalsumatoriaimporte=Totalsumatoriaimporte+viatico.Monto_pagado
                Totalsumatoriarciva=Totalsumatoriarciva+viatico.RC_IVA
                Totalsumatorialiqpagable=Totalsumatorialiqpagable+viatico.Liquido_pagable
                Totalsumatoriatotalcancelar=Totalsumatoriatotalcancelar+viatico.totalC
        detalles = [(
                "TOTAL",
                " ",
                " ",
                self.redondear(Totalsumatoriapasaje),
                self.redondear(Totalsumatoriapeaje),
                self.redondear(Totalsumatoriaimporte),
                self.redondear(Totalsumatoriarciva),
                self.redondear(Totalsumatorialiqpagable),
                self.redondear(Totalsumatoriatotalcancelar),
                " ",
                " ",
                " ",
                " ",
                " ",
                )]
        cm = 29
        #cm = 23.4
        if hasheader:
            table = Table(
                detalles,
                colWidths = [
                    0.9 * cm, 
                    5 * cm, 
                    1.5 * cm,  
                    1.5 * cm, 
                    1.5 * cm, 
                    1.5 * cm, 
                    1.4 * cm, 
                    2 * cm,
                    2.7 * cm,
                    1 * cm,
                    1 * cm,
                    1 * cm,
                    1 * cm,
                    2.1 * cm
                ],
                splitByRow = 1,
                repeatRows = 1
            )
        if style:
            if hasheader:
                table.setStyle(style)
            elif stylealt:
                table.setStyle(stylealt)
        if len(datereference) == 0 and stylevoid is not None:
            table.setStyle(stylevoid)
        return table
class ReporteViaticosBiseTri(BasePlatypusReport):
   
    def __init__(self):
        self.begin(orientation = 'portrait', rightMargin = 28, leftMargin = 28, topMargin = 36, bottomMargin = 28)

    def get(self, request, *args, **kwargs):
        slug =self.kwargs.get('slug')
        self.draw(slug)
        self.write(onFirstPage = self.title)
        return self.response

    def title(self,canvas, document,**kwargs):
        slug =self.kwargs.get('slug')
        
        title = 'BOLETAS REGISTRADAS'
        canvas.saveState()
        canvas.setFont('Helvetica-Bold', 14)
        archivo_imagen = settings.MEDIA_ROOT+'\images\logoo.png'
        archivo_imagen1 = settings.MEDIA_ROOT+'\images\money.png'
                
        canvas.setFont("Helvetica-Bold", 13)
        canvas.drawCentredString(self.x_start + self.width_internal / 2, self.y_start - 25, u"GOBIERNO AUTONOMO DEPARTAMENTAL DE POTOSI")
        canvas.setFont("Helvetica-Bold", 13)
        canvas.drawCentredString(self.x_start + self.width_internal / 2, self.y_start - 45, u"Secretaria Departamental Administracion y Financiera")
      
        canvas.drawImage(archivo_imagen1, self.x_start + 470,self.y_start - 64, 55, 55, preserveAspectRatio = True)
        
        canvas.setLineWidth(1)
        #print(self.x_start)
        #print(self.y_start)
        canvas.line(self.x_start+135, self.y_start-55, 450, self.y_start-55)
        
        canvas.setFont("Helvetica-Bold", 12)
        canvas.drawCentredString(self.x_start + self.width_internal / 2, self.y_start - 72, u"DETALLES  DE PASAJES - PEAJES Y VIATICOS")
        titulo=''
        if int(slug)==2:                                     
                titulo='Reporte Bimestral'                                                      
        if int(slug)==4:                                                                                                                                                                                                                                                                                                                                                 
                titulo='Reporte Semestral'                                                                                                                                                                                        
        if int(slug)==3:
                titulo='Reporte Trimestral'    
        if int(slug)==5:
                titulo='Reporte Anual' 
     
        canvas.setFont("Helvetica-Bold", 10)
        canvas.drawCentredString(self.x_start + self.width_internal / 2, self.y_start - 87, titulo.upper())

        self.draw_left_image(canvas = canvas,
            url = archivo_imagen,
            x = self.x_start + 40, 
            y = self.y_start - 8, 
            w = 55, 
            h = 55
        )
    def draw(self,slug):
        self.add(Spacer(1, 90))
        self.draw_table(slug)
    def draw_table(self,slug):
        basic_style_full_doble = self.get_basic_style_full_doble()
        basic_style_body = self.get_basic_style_body()
        basic_style_full_doble_void = self.get_basic_style_full_doble_void()
        viaticos=viaticodiario.objects.all()
        self.add(self.draw_in_table_top(0,viaticos,slug,self.get_basic_style_full_doble_top(),basic_style_body, basic_style_full_doble_void, True))
        self.add(self.draw_in_table_result(0,viaticos,slug,self.get_basic_style_full_doble_button(), basic_style_body, basic_style_full_doble_void, True)) 
        self.add(Spacer(1, 20))        
    def draw_in_table_top(self,index = 0,datereference = None,slug= None,style = None,stylealt = None, stylevoid = None, hasheader = False):

        meses=['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
        mesesingles=['January','February','March','April','May','June','July','August','September','October','November','December']
        supercabecera = [
                'N°',
                'FECHAS',                
                'PASAJES',
                'PEAJES',
                'IMPORTES',
                'RC-IVA',
                'LIQ. PAGABLE',
                'TOTAL A CANCELAR',      
        ]
        cantidadDias=[]
        date = datetime.now()
        if  date.year %4==0  and date.year %100 !=0 or date.year % 400==0:
                cantidadDias=[31,29,31,30,31,30,31,31,30,31,30,31]
        else:
                cantidadDias=[31,28,31,30,31,30,31,31,30,31,30,31]
        errorone=''
        preparandojson=[]
        fechahoy=date.month
        via=viaticodiario.objects.filter(timestamp__year=date.year)  
        sumapasaje=0
        sumapeaje=0
        sumaimporte=0
        sumarciva=0
        sumaliqpagable=0
        sumaliqtotalcancelar=0
        dias=''
        if int(slug)==2:
                diastotales=(fechahoy/2)
                if diastotales*2>=2:                                             
                        if fechahoy == diastotales*2:
                                if date.day < cantidadDias[fechahoy-1]:
                                        diastotales=diastotales-1                                                                                                                                                                               
                        contfecha=1
                                                                        
                        vacio=0
                        while contfecha <= (diastotales*2):
                                vias=viaticodiario.objects.filter(timestamp__year=date.year,timestamp__month=contfecha)
                                if vias.exists():
                                        for vi in vias:
                                                sumapasaje=sumapasaje+vi.pasaje
                                                sumapeaje=sumapeaje+vi.peaje
                                                sumaimporte=sumaimporte+vi.Monto_pagado
                                                sumarciva=sumarciva+vi.RC_IVA
                                                sumaliqpagable=sumaliqpagable+vi.Liquido_pagable
                                                sumaliqtotalcancelar=sumaliqtotalcancelar+vi.totalC
                                else:
                                        vacio=vacio+1
                                        #print('%s %s'%("No existe con el mes de = ",meses[contfecha-1]))
                                dias=dias+' '+meses[contfecha-1]
                                if contfecha%2!=0:
                                        dias = dias + ' - '                                                        
                                if contfecha%2==0:
                                        if vacio!=2:                                                                
                                                print(dias)
                                        preparandojson.append({   
                                                "DesdeHasta":dias,                                                                                                                                             
                                                "id":contfecha,
                                                "pasaje": sumapasaje,
                                                "peaje": sumapeaje,
                                                "importe": sumaimporte,
                                                "rciva": sumarciva,
                                                "liqpagable": sumaliqpagable,
                                                "liqtotalcancelar": sumaliqtotalcancelar                                                                                                                                              
                                        })
                                        sumapasaje=0
                                        sumapeaje=0
                                        sumaimporte=0
                                        sumarciva=0
                                        sumaliqpagable=0
                                        sumaliqtotalcancelar=0                                                        
                                        dias=''  
                                        vacio=0
                                #print(meses[contfecha-1])                                                                                                                  
                                contfecha=contfecha+1    
                        errorone='Aun no existe viaticos para Bimestral'             
        if int(slug)==4:  
                #print(fechahoy)                                                              
                if fechahoy > 6:   
                        if fechahoy == 12:
                                if date.day >= cantidadDias[fechahoy-1]:
                                        cont=1
                                        while cont <= 12:  
                                                vias=viaticodiario.objects.filter(timestamp__year=date.year,timestamp__month=cont)
                                                if vias.exists():                                                                          
                                                        for viatico in vias:                                                                                                                                                                                                                
                                                                sumapasaje=sumapasaje+viatico.pasaje
                                                                sumapeaje=sumapeaje+viatico.peaje
                                                                sumaimporte=sumaimporte+viatico.Monto_pagado
                                                                sumarciva=sumarciva+viatico.RC_IVA
                                                                sumaliqpagable=sumaliqpagable+viatico.Liquido_pagable
                                                                sumaliqtotalcancelar=sumaliqtotalcancelar+viatico.totalC                                                                                                                                                                                                                                              
                                                dias=dias+' '+meses[cont-1]
                                                if  cont == 6 or  cont == 12:
                                                        preparandojson.append({   
                                                                "DesdeHasta":dias,                                                                                                                                             
                                                                "id":cont,
                                                                "pasaje": sumapasaje,
                                                                "peaje": sumapeaje,
                                                                "importe": sumaimporte,
                                                                "rciva": sumarciva,
                                                                "liqpagable": sumaliqpagable,
                                                                "liqtotalcancelar": sumaliqtotalcancelar                                                                                                                                              
                                                        })
                                                        sumapasaje=0
                                                        sumapeaje=0
                                                        sumaimporte=0
                                                        sumarciva=0
                                                        sumaliqpagable=0
                                                        sumaliqtotalcancelar=0                                                        
                                                        dias=''  
                                                        vacio=0                                                                                          
                                                cont=cont+1
                                else:
                                        cont=1
                                        while cont <= 6:  
                                                vias=viaticodiario.objects.filter(timestamp__year=date.year,timestamp__month=cont)
                                                if vias.exists():                                                                          
                                                        for viatico in vias:                                                                                                                                                                                                                
                                                                sumapasaje=sumapasaje+viatico.pasaje
                                                                sumapeaje=sumapeaje+viatico.peaje
                                                                sumaimporte=sumaimporte+viatico.Monto_pagado
                                                                sumarciva=sumarciva+viatico.RC_IVA
                                                                sumaliqpagable=sumaliqpagable+viatico.Liquido_pagable
                                                                sumaliqtotalcancelar=sumaliqtotalcancelar+viatico.totalC                                                                                                                                                                                                                                              
                                                dias=dias+' '+meses[cont-1]
                                                cont=cont+1     
                                        preparandojson.append({   
                                                "DesdeHasta":dias,                                                                                                                                             
                                                "id":cont,
                                                "pasaje": sumapasaje,
                                                "peaje": sumapeaje,
                                                "importe": sumaimporte,
                                                "rciva": sumarciva,
                                                "liqpagable": sumaliqpagable,
                                                "liqtotalcancelar": sumaliqtotalcancelar                                                                                                                                              
                                        })
                        else:                                                                     
                                
                                cont=1
                                while cont <= 6:  
                                        vias=viaticodiario.objects.filter(timestamp__year=date.year,timestamp__month=cont)
                                        if vias.exists():                                                                          
                                                for viatico in vias:                                                                                                                                                                                                                
                                                        sumapasaje=sumapasaje+viatico.pasaje
                                                        sumapeaje=sumapeaje+viatico.peaje
                                                        sumaimporte=sumaimporte+viatico.Monto_pagado
                                                        sumarciva=sumarciva+viatico.RC_IVA
                                                        sumaliqpagable=sumaliqpagable+viatico.Liquido_pagable
                                                        sumaliqtotalcancelar=sumaliqtotalcancelar+viatico.totalC                                                                                                                                                                                                                                              
                                        dias=dias+' '+meses[cont-1]
                                        cont=cont+1     
                                preparandojson.append({   
                                        "DesdeHasta":dias,                                                                                                                                             
                                        "id":cont,
                                        "pasaje": sumapasaje,
                                        "peaje": sumapeaje,
                                        "importe": sumaimporte,
                                        "rciva": sumarciva,
                                        "liqpagable": sumaliqpagable,
                                        "liqtotalcancelar": sumaliqtotalcancelar                                                                                                                                              
                                })
                else:                                                                                                                                                                                                                                                                                                          
                        errorone='Aun no existe viaticos para Semestral'                                                                                                                                                                                        
        if int(slug)==3:
                print("Trimestral")
                diastotales=(fechahoy/3)                                        
                if diastotales*3>=3:                                             
                        if fechahoy == diastotales*3:
                                if date.day < cantidadDias[(diastotales*3)-1]:
                                        diastotales=diastotales-1                                                                                                                                                                               
                        contfecha=1
                        sumapasaje=0
                        sumapeaje=0
                        sumaimporte=0
                        sumarciva=0
                        sumaliqpagable=0
                        sumaliqtotalcancelar=0         
                        vacio=0
                        day=['Enero - Marzo','Abril - Junio','Julio - Septiembre','Octubre - Diciembre']
                        one=0
                        while contfecha <= (diastotales*3):                                                        
                                vias=viaticodiario.objects.filter(timestamp__year=date.year,timestamp__month=contfecha)
                                if vias.exists():
                                        for vi in vias:
                                                sumapasaje=sumapasaje+vi.pasaje
                                                sumapeaje=sumapeaje+vi.peaje
                                                sumaimporte=sumaimporte+vi.Monto_pagado
                                                sumarciva=sumarciva+vi.RC_IVA
                                                sumaliqpagable=sumaliqpagable+vi.Liquido_pagable
                                                sumaliqtotalcancelar=sumaliqtotalcancelar+vi.totalC                                                                
                                else:
                                        vacio=vacio+1                                                                
                                
                                if contfecha%3==0:
                                        
                                        #if vacio!=3:                                                                
                                        #        print(dias)
                                        preparandojson.append({   
                                                "DesdeHasta":day[one],                                                                                                                                             
                                                "id":contfecha,
                                                "pasaje": sumapasaje,
                                                "peaje": sumapeaje,
                                                "importe": sumaimporte,
                                                "rciva": sumarciva,
                                                "liqpagable": sumaliqpagable,
                                                "liqtotalcancelar": sumaliqtotalcancelar                                                                                                                                              
                                        })
                                        sumapasaje=0
                                        sumapeaje=0
                                        sumaimporte=0
                                        sumarciva=0
                                        sumaliqpagable=0
                                        sumaliqtotalcancelar=0                                                                                                                      
                                        vacio=0
                                        one=one+1                                                                                                                                                                             
                                contfecha=contfecha+1    
                        errorone='Aun no existe viaticos para Trimestral'    
        if int(slug)==5:
                                        #print("Anual")
                                        if fechahoy == 12:
                                                if date.day >= cantidadDias[11]:
                                                        cont=1
                                                        while cont <= 12:  
                                                                vias=viaticodiario.objects.filter(timestamp__year=date.year,timestamp__month=cont)
                                                                if vias.exists():                                                                          
                                                                        for viatico in vias:                                                                                                                                                                                                                
                                                                                sumapasaje=sumapasaje+viatico.pasaje
                                                                                sumapeaje=sumapeaje+viatico.peaje
                                                                                sumaimporte=sumaimporte+viatico.Monto_pagado
                                                                                sumarciva=sumarciva+viatico.RC_IVA
                                                                                sumaliqpagable=sumaliqpagable+viatico.Liquido_pagable
                                                                                sumaliqtotalcancelar=sumaliqtotalcancelar+viatico.totalC                                                                                                                                                                                                                                              
                                                                cont=cont+1
                                                        preparandojson.append({   
                                                                "DesdeHasta":"Enero - Diciembre",                                                                                                                                             
                                                                "id":1,
                                                                "pasaje": sumapasaje,
                                                                "peaje": sumapeaje,
                                                                "importe": sumaimporte,
                                                                "rciva": sumarciva,
                                                                "liqpagable": sumaliqpagable,
                                                                "liqtotalcancelar": sumaliqtotalcancelar                                                                                                                                              
                                                        })                                                                                                                                                                                                                                 
                                        errorone='Aun no existe viaticos para Anual' 
        detalles = [(
                via['id'],
                via['DesdeHasta'],
                via['pasaje'],
                via['peaje'],
                via['importe'],
                via['rciva'],
                via['liqpagable'],
                via['liqtotalcancelar']
                ) for via in preparandojson]                         
        cm = 29
        #cm = 23.4
        if hasheader:
            table = Table(
                [supercabecera] + detalles,
                colWidths = [
                    0.9 * cm, 
                    5 * cm, 
             
                    1.5 * cm, 
                    1.5 * cm, 
                    1.5 * cm, 
                    1.4 * cm, 
                    2 * cm,
                    2.7 * cm
                ],
                splitByRow = 1,
                repeatRows = 0
            )
        
        if style:
            if hasheader:
                table.setStyle(style)
            elif stylealt:
                table.setStyle(stylealt)
        return table
    def redondear(self,valor=None):
        leter=str(valor)
        for le in xrange(len(leter)):
                if leter[le]=='.':
                        if (le+2)==len(leter):
                                return '%s%s'%(valor,0) 
                        else:     
                                return valor
    def draw_in_table_result(self,index = 0, datereference = None,slug=None,style = None, stylealt = None, stylevoid = None, hasheader = False):
        
        meses=['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
        mesesingles=['January','February','March','April','May','June','July','August','September','October','November','December']
        supercabecera = [
                'N°',
                'FECHAS',                
                'PASAJES',
                'PEAJES',
                'IMPORTES',
                'RC-IVA',
                'LIQ. PAGABLE',
                'TOTAL A CANCELAR',      
        ]
        cantidadDias=[]
        date = datetime.now()
        if  date.year %4==0  and date.year %100 !=0 or date.year % 400==0:
                cantidadDias=[31,29,31,30,31,30,31,31,30,31,30,31]
        else:
                cantidadDias=[31,28,31,30,31,30,31,31,30,31,30,31]
        errorone=''
        preparandojson=[]
        fechahoy=date.month
        via=viaticodiario.objects.filter(timestamp__year=date.year)  
        sumapasaje=0
        sumapeaje=0
        sumaimporte=0
        sumarciva=0
        sumaliqpagable=0
        sumaliqtotalcancelar=0
        dias=''
        if int(slug)==2:
                diastotales=(fechahoy/2)
                if diastotales*2>=2:                                             
                        if fechahoy == diastotales*2:
                                if date.day < cantidadDias[fechahoy-1]:
                                        diastotales=diastotales-1                                                                                                                                                                               
                        contfecha=1
                                                                        
                        vacio=0
                        while contfecha <= (diastotales*2):
                                vias=viaticodiario.objects.filter(timestamp__year=date.year,timestamp__month=contfecha)
                                if vias.exists():
                                        for vi in vias:
                                                sumapasaje=sumapasaje+vi.pasaje
                                                sumapeaje=sumapeaje+vi.peaje
                                                sumaimporte=sumaimporte+vi.Monto_pagado
                                                sumarciva=sumarciva+vi.RC_IVA
                                                sumaliqpagable=sumaliqpagable+vi.Liquido_pagable
                                                sumaliqtotalcancelar=sumaliqtotalcancelar+vi.totalC                        
                                contfecha=contfecha+1                
        if int(slug)==4:  
                #print(fechahoy)                                                              
                if fechahoy > 6:   
                        if fechahoy == 12:
                                if date.day >= cantidadDias[fechahoy-1]:
                                        cont=1
                                        while cont <= 12:  
                                                vias=viaticodiario.objects.filter(timestamp__year=date.year,timestamp__month=cont)
                                                if vias.exists():                                                                          
                                                        for viatico in vias:                                                                                                                                                                                                                
                                                                sumapasaje=sumapasaje+viatico.pasaje
                                                                sumapeaje=sumapeaje+viatico.peaje
                                                                sumaimporte=sumaimporte+viatico.Monto_pagado
                                                                sumarciva=sumarciva+viatico.RC_IVA
                                                                sumaliqpagable=sumaliqpagable+viatico.Liquido_pagable
                                                                sumaliqtotalcancelar=sumaliqtotalcancelar+viatico.totalC                                                                                                                                                                                                                                              
                                                dias=dias+' '+meses[cont-1]
                                                if  cont == 6 or  cont == 12:
                                                        preparandojson.append({   
                                                                "DesdeHasta":dias,                                                                                                                                             
                                                                "id":cont,
                                                                "pasaje": sumapasaje,
                                                                "peaje": sumapeaje,
                                                                "importe": sumaimporte,
                                                                "rciva": sumarciva,
                                                                "liqpagable": sumaliqpagable,
                                                                "liqtotalcancelar": sumaliqtotalcancelar                                                                                                                                              
                                                        })
                                                        sumapasaje=0
                                                        sumapeaje=0
                                                        sumaimporte=0
                                                        sumarciva=0
                                                        sumaliqpagable=0
                                                        sumaliqtotalcancelar=0                                                        
                                                        dias=''  
                                                        vacio=0                                                                                          
                                                cont=cont+1
                                else:
                                        cont=1
                                        while cont <= 6:  
                                                vias=viaticodiario.objects.filter(timestamp__year=date.year,timestamp__month=cont)
                                                if vias.exists():                                                                          
                                                        for viatico in vias:                                                                                                                                                                                                                
                                                                sumapasaje=sumapasaje+viatico.pasaje
                                                                sumapeaje=sumapeaje+viatico.peaje
                                                                sumaimporte=sumaimporte+viatico.Monto_pagado
                                                                sumarciva=sumarciva+viatico.RC_IVA
                                                                sumaliqpagable=sumaliqpagable+viatico.Liquido_pagable
                                                                sumaliqtotalcancelar=sumaliqtotalcancelar+viatico.totalC                                                                                                                                                                                                                                              
                                                dias=dias+' '+meses[cont-1]
                                                cont=cont+1     
                                        preparandojson.append({   
                                                "DesdeHasta":dias,                                                                                                                                             
                                                "id":cont,
                                                "pasaje": sumapasaje,
                                                "peaje": sumapeaje,
                                                "importe": sumaimporte,
                                                "rciva": sumarciva,
                                                "liqpagable": sumaliqpagable,
                                                "liqtotalcancelar": sumaliqtotalcancelar                                                                                                                                              
                                        })
                        else:                                                                     
                                
                                cont=1
                                while cont <= 6:  
                                        vias=viaticodiario.objects.filter(timestamp__year=date.year,timestamp__month=cont)
                                        if vias.exists():                                                                          
                                                for viatico in vias:                                                                                                                                                                                                                
                                                        sumapasaje=sumapasaje+viatico.pasaje
                                                        sumapeaje=sumapeaje+viatico.peaje
                                                        sumaimporte=sumaimporte+viatico.Monto_pagado
                                                        sumarciva=sumarciva+viatico.RC_IVA
                                                        sumaliqpagable=sumaliqpagable+viatico.Liquido_pagable
                                                        sumaliqtotalcancelar=sumaliqtotalcancelar+viatico.totalC                                                                                                                                                                                                                                              
                                        dias=dias+' '+meses[cont-1]
                                        cont=cont+1     
                                preparandojson.append({   
                                        "DesdeHasta":dias,                                                                                                                                             
                                        "id":cont,
                                        "pasaje": sumapasaje,
                                        "peaje": sumapeaje,
                                        "importe": sumaimporte,
                                        "rciva": sumarciva,
                                        "liqpagable": sumaliqpagable,
                                        "liqtotalcancelar": sumaliqtotalcancelar                                                                                                                                              
                                })
                else:                                                                                                                                                                                                                                                                                                          
                        errorone='Aun no existe viaticos para Semestral'                                                                                                                                                                                        
        if int(slug)==3:
                print("Trimestral")
                diastotales=(fechahoy/3)                                        
                if diastotales*3>=3:                                             
                        if fechahoy == diastotales*3:
                                if date.day < cantidadDias[(diastotales*3)-1]:
                                        diastotales=diastotales-1                                                                                                                                                                               
                        contfecha=1
                        sumapasaje=0
                        sumapeaje=0
                        sumaimporte=0
                        sumarciva=0
                        sumaliqpagable=0
                        sumaliqtotalcancelar=0         
                        vacio=0
                        day=['Enero - Marzo','Abril - Junio','Julio - Septiembre','Octubre - Diciembre']
                        one=0
                        while contfecha <= (diastotales*3):                                                        
                                vias=viaticodiario.objects.filter(timestamp__year=date.year,timestamp__month=contfecha)
                                if vias.exists():
                                        for vi in vias:
                                                sumapasaje=sumapasaje+vi.pasaje
                                                sumapeaje=sumapeaje+vi.peaje
                                                sumaimporte=sumaimporte+vi.Monto_pagado
                                                sumarciva=sumarciva+vi.RC_IVA
                                                sumaliqpagable=sumaliqpagable+vi.Liquido_pagable
                                                sumaliqtotalcancelar=sumaliqtotalcancelar+vi.totalC                                                                
                                else:
                                        vacio=vacio+1                                                                
                                
                                if contfecha%3==0:
                                        
                                        #if vacio!=3:                                                                
                                        #        print(dias)
                                        preparandojson.append({   
                                                "DesdeHasta":day[one],                                                                                                                                             
                                                "id":contfecha,
                                                "pasaje": sumapasaje,
                                                "peaje": sumapeaje,
                                                "importe": sumaimporte,
                                                "rciva": sumarciva,
                                                "liqpagable": sumaliqpagable,
                                                "liqtotalcancelar": sumaliqtotalcancelar                                                                                                                                              
                                        })
                                        sumapasaje=0
                                        sumapeaje=0
                                        sumaimporte=0
                                        sumarciva=0
                                        sumaliqpagable=0
                                        sumaliqtotalcancelar=0                                                                                                                      
                                        vacio=0
                                        one=one+1                                                                                                                                                                             
                                contfecha=contfecha+1    
                        errorone='Aun no existe viaticos para Trimestral'    
        if int(slug)==5:
                #print("Anual")
                if fechahoy == 12:
                        if date.day >= cantidadDias[11]:
                                cont=1
                                while cont <= 12:  
                                        vias=viaticodiario.objects.filter(timestamp__year=date.year,timestamp__month=cont)
                                        if vias.exists():                                                                          
                                                for viatico in vias:                                                                                                                                                                                                                
                                                        sumapasaje=sumapasaje+viatico.pasaje
                                                        sumapeaje=sumapeaje+viatico.peaje
                                                        sumaimporte=sumaimporte+viatico.Monto_pagado
                                                        sumarciva=sumarciva+viatico.RC_IVA
                                                        sumaliqpagable=sumaliqpagable+viatico.Liquido_pagable
                                                        sumaliqtotalcancelar=sumaliqtotalcancelar+viatico.totalC                                                                                                                                                                                                                                              
                                        cont=cont+1
                                preparandojson.append({   
                                        "DesdeHasta":"Enero - Diciembre",                                                                                                                                             
                                        "id":1,
                                        "pasaje": sumapasaje,
                                        "peaje": sumapeaje,
                                        "importe": sumaimporte,
                                        "rciva": sumarciva,
                                        "liqpagable": sumaliqpagable,
                                        "liqtotalcancelar": sumaliqtotalcancelar                                                                                                                                              
                                })                                                                                                                                                                                                                                 
                errorone='Aun no existe viaticos para Anual'         
        valor_pasaje=0
        valor_peaje=0
        valor_importe=0
        valor_rciva=0
        valor_liq=0
        valor_total=0
        if sumapasaje != 0:
                valor_pasaje=self.redondear(sumapasaje)
        if sumapeaje != 0:
                valor_peaje=self.redondear(sumapeaje)
        if sumaimporte != 0:
                valor_importe=self.redondear(sumaimporte)
        if sumarciva != 0:
                valor_rciva=self.redondear(sumarciva)
        if sumaliqpagable != 0:
                valor_liq=self.redondear(sumaliqpagable)
        if sumaliqtotalcancelar != 0:
                valor_total=self.redondear(sumaliqtotalcancelar)
        detalles = [(
                "TOTAL",
                "",
                valor_pasaje,
                valor_peaje,
                valor_importe,
                valor_rciva,
                valor_liq,
                valor_total
                )]
        cm = 29
        #cm = 23.4
        if hasheader:
            table = Table(
                detalles,
                colWidths = [
                    0.9 * cm, 
                    5 * cm, 
             
                    1.5 * cm, 
                    1.5 * cm, 
                    1.5 * cm, 
                    1.4 * cm, 
                    2 * cm,
                    2.7 * cm
                ],
                splitByRow = 1,
                repeatRows = 1
            )
        if style:
            if hasheader:
                table.setStyle(style)
            elif stylealt:
                table.setStyle(stylealt)
        if len(datereference) == 0 and stylevoid is not None:
            table.setStyle(stylevoid)
        return table

class ReporteViaticosEmp(BasePlatypusReportOther):
    def __init__(self):
        self.begin(orientation = 'LANDSCAPE', rightMargin = 28, leftMargin = 28, topMargin = 36, bottomMargin = 28)

    def get(self, request, *args, **kwargs):
        user_id =self.kwargs.get('slug')
        anoss =self.kwargs.get('slugu')
        
        self.draw(user_id,anoss)
        self.write(onFirstPage = self.title)
        return self.response

    def title(self,canvas, document,**kwargs):
        user_id =self.kwargs.get('slug')
        gestion =self.kwargs.get('slugu')
        title = 'BOLETAS REGISTRADAS'
        canvas.saveState()
        
        archivo_imagen = settings.MEDIA_ROOT+'\images\logoo.png'
        archivo_imagen1 = settings.MEDIA_ROOT+'\images\money.png'
                
        canvas.setFont("Helvetica-Bold", 11)
        canvas.drawCentredString(self.x_start + self.width_internal / 2, self.y_start - 25, u"GOBIERNO AUTONOMO DEPARTAMENTAL DE POTOSI")
        canvas.setFont("Helvetica-Bold", 11)
        canvas.drawCentredString(self.x_start + self.width_internal / 2, self.y_start - 45, u"Secretaria Departamental Administracion y Financiera")
      
        canvas.drawImage(archivo_imagen1, self.x_start + 600,self.y_start - 64, 55, 55, preserveAspectRatio = True)
        
        canvas.setLineWidth(1)
        canvas.line(self.x_start+180, self.y_start-60, 585, self.y_start-60)
        
        canvas.setFont("Helvetica-Bold", 10)
        canvas.drawCentredString(self.x_start + self.width_internal / 2, self.y_start - 72, u"DETALLE DE PASAJES Y VIÁTICOS DEL PERSONAL DEL GOBIERNO AUTÓNOMO")
        emp=get_object_or_404(empleado,ci=user_id)
        gestion=emp.nombre.upper()+' '+emp.apaterno.upper()+' '+emp.amaterno.upper()+' '+u'GESTION '+ gestion
        canvas.setFont("Helvetica-Bold", 10)
        canvas.drawCentredString(self.x_start + self.width_internal / 2, self.y_start - 87, gestion)

        self.draw_left_image(canvas = canvas,
            url = archivo_imagen,
            x = self.x_start + 70, 
            y = self.y_start - 8, 
            w = 55, 
            h = 55
        )
    def draw(self,user_id,anoss):
        self.add(Spacer(1, 90))
        self.draw_table(user_id,anoss)
    def draw_table(self,user_id,anoss):
        basic_style_full_doble = self.get_basic_style_full_doble()
        basic_style_body = self.get_basic_style_body()
        basic_style_full_doble_void = self.get_basic_style_full_doble_void()        
        viaticos=None        
        try:                
                viaticos=viaticodiario.objects.filter(timestamp__year=anoss,id_solicitante=user_id)
        except:
                raise Http404    
        self.add(self.draw_in_table_top(0,viaticos,user_id,anoss,self.get_basic_style_full_doble_top(),basic_style_body, basic_style_full_doble_void, True))
        self.add(self.draw_in_table_result(0,viaticos,self.get_basic_style_full_doble_button(), basic_style_body, basic_style_full_doble_void, True)) 
        self.add(Spacer(1, 20))
        self.add(self.draw_in_table_resumen(0,viaticos,self.get_basic_style_full_doble_resumen(), basic_style_body, basic_style_full_doble_void, True)) 
    def draw_in_table_top(self,index = 0,datereference = None,user_id= None,anoss= None,style = None,stylealt = None, stylevoid = None, hasheader = False):
        supercabecera = [
                'N°',
                'NOMBRES Y APELLIDOS',
                'C.I.',
                'PASAJES',
                'PEAJES',
                'VIATICO',
                '',
                '',
                'TOTAL A CANCELAR',
                'CONTROL PRESUPUESTARIO',
                '',
                '',
                '',
                'N° CUENTA'
        ]
        cabecera = [
            '',
            '',
            '',
            '',
            '',
            'IMPORTES',
            'RC-IVA',
            'LIQ. PAGABLE',
            '',
            'U.E',
            'PROG',
            'PROY',
            'ACT',
            ''		
        ]
        preparandojson = []
        cont=1
        for viatico in datereference:
                if viatico.timestamp.strftime('%Y') == anoss and int(user_id)==viatico.id_solicitante:               
                        ue=0
                        prog=0
                        act=0
                        proy=0
                        if viatico.ue < 10:
                                ue='%s%s'%(0,viatico.ue)
                        else:
                                ue=viatico.ue
                        
                        if viatico.prog < 10:
                                prog='%s%s'%(0,viatico.prog)
                        else:
                                prog=viatico.prog

                        if viatico.act < 10:
                                act='%s%s'%(0,viatico.act)
                        else:
                                act=viatico.act

                        if viatico.proy < 10:
                                proy='%s%s'%(0,viatico.proy)
                        else:
                                proy=viatico.proy
                        
                        preparandojson.append({
                                "ci":viatico.solicitante.ci,
                                "NombreCompleto":'%s %s %s'%(viatico.solicitante.nombre.upper(),viatico.solicitante.apaterno.upper(),viatico.solicitante.amaterno.upper()),
                                "id":cont,
                                "pasaje": self.redondear(viatico.pasaje),
                                "peaje": self.redondear(viatico.peaje),
                                "importe": self.redondear(viatico.Monto_pagado),
                                "rciva": self.redondear(viatico.RC_IVA),
                                "liqpagable": self.redondear(viatico.Liquido_pagable),
                                "liqtotalcancelar": self.redondear(viatico.totalC),
                                "ue":ue,
                                "prog":prog,
                                "act":act,
                                "proy":viatico.proy,
                                "numero":viatico.solicitante.bcontrol
                        })
                cont=cont+1
        detalles = [(
                via['id'],
                via['NombreCompleto'],
                via['ci'],
                via['pasaje'],
                via['peaje'],
                via['importe'],
                via['rciva'],
                via['liqpagable'],
                via['liqtotalcancelar'],
                via['ue'],
                via['prog'],
                via['proy'],
                via['act'],
                via['numero']
                ) for via in preparandojson]
        cm = 29
        #cm = 23.4
        if hasheader:
            table = Table(
                [supercabecera] + [cabecera] + detalles,
                colWidths = [
                    0.9 * cm, 
                    5 * cm, 
                    1.5 * cm,  
                    1.5 * cm, 
                    1.5 * cm, 
                    1.5 * cm, 
                    1.4 * cm, 
                    2 * cm,
                    2.7 * cm,
                    1 * cm,
                    1 * cm,
                    1 * cm,
                    1 * cm,
                    2.1 * cm
                ],
                splitByRow = 1,
                repeatRows = 0
            )
        
        if style:
            if hasheader:
                table.setStyle(style)
            elif stylealt:
                table.setStyle(stylealt)
        return table
    def redondear(self,valor=None):
        leter=str(valor)
        for le in xrange(len(leter)):
                if leter[le]=='.':
                        if (le+2)==len(leter):
                                return '%s%s'%(valor,0) 
                        else:     
                                return valor
    def draw_in_table_resumen(self,index = 0, datereference = None,style = None, stylealt = None, stylevoid = None, hasheader = False):
        cabecera = [
            'RESUMEN',
            ' '
        ]
        Sumatoriapasaje=0
        Sumatoriapeaje=0
        Sumatoriaimporte=0
        Sumatoriarciva=0
        Sumatorialiqpagable=0
        Sumatoriatotalcancelar=0
        preparandojson=[]
        for viatico in datereference:                
                Sumatoriapasaje=Sumatoriapasaje+viatico.pasaje
                Sumatoriapeaje=Sumatoriapeaje+viatico.peaje
                Sumatoriaimporte=Sumatoriaimporte+viatico.Monto_pagado
                Sumatoriarciva=Sumatoriarciva+viatico.RC_IVA
                Sumatorialiqpagable=Sumatorialiqpagable+viatico.Liquido_pagable
                Sumatoriatotalcancelar=Sumatoriatotalcancelar+viatico.totalC  
            
        detalles = [(
                "DESCRIPCIÓN",
                "IMPORTE EN BS."
                )]
        VIATICO = [(
                "VIÁTICO",
                self.redondear(Sumatoriaimporte)
                )]
        PEAJES = [(
                "PEAJES",
                self.redondear(Sumatoriapeaje)
                )]
        PASAJES = [(
                "PASAJES",
                self.redondear(Sumatoriapasaje)
                )]
        TOTAL = [(
                "TOTAL",
                self.redondear(Sumatoriapasaje+Sumatoriapeaje+Sumatoriaimporte)
                )]
        RC = [(
                "Menos RC - IVA",
                self.redondear(Sumatoriarciva)
                )]
        LIQUIDO = [(
                "LIQ. PAGABLE",
                self.redondear(Sumatorialiqpagable)
                )]
        cm = 29
        #cm = 23.4
        if hasheader:
            table = Table(
                [cabecera] + detalles+VIATICO+PEAJES+PASAJES+TOTAL+RC+LIQUIDO,
                colWidths = [
                    3 * cm, 
                    3 * cm                    
                ],
                splitByRow = 1,
                repeatRows = 1
            )
        if style:
            if hasheader:
                table.setStyle(style)
            elif stylealt:
                table.setStyle(stylealt)
        if len(datereference) == 0 and stylevoid is not None:
            table.setStyle(stylevoid)
        return table
    def draw_in_table_result(self,index = 0, datereference = None,style = None, stylealt = None, stylevoid = None, hasheader = False):
        Totalsumatoriapasaje=0
        Totalsumatoriapeaje=0
        Totalsumatoriaimporte=0
        Totalsumatoriarciva=0
        Totalsumatorialiqpagable=0
        Totalsumatoriatotalcancelar=0
        for viatico in datereference:
                Totalsumatoriapasaje=Totalsumatoriapasaje+viatico.pasaje
                Totalsumatoriapeaje=Totalsumatoriapeaje+viatico.peaje
                Totalsumatoriaimporte=Totalsumatoriaimporte+viatico.Monto_pagado
                Totalsumatoriarciva=Totalsumatoriarciva+viatico.RC_IVA
                Totalsumatorialiqpagable=Totalsumatorialiqpagable+viatico.Liquido_pagable
                Totalsumatoriatotalcancelar=Totalsumatoriatotalcancelar+viatico.totalC
        detalles = [(
                "TOTAL",
                " ",
                " ",
                self.redondear(Totalsumatoriapasaje),
                self.redondear(Totalsumatoriapeaje),
                self.redondear(Totalsumatoriaimporte),
                self.redondear(Totalsumatoriarciva),
                self.redondear(Totalsumatorialiqpagable),
                self.redondear(Totalsumatoriatotalcancelar),
                " ",
                " ",
                " ",
                " ",
                " ",
                )]
        cm = 29
        #cm = 23.4
        if hasheader:
            table = Table(
                detalles,
                colWidths = [
                    0.9 * cm, 
                    5 * cm, 
                    1.5 * cm,  
                    1.5 * cm, 
                    1.5 * cm, 
                    1.5 * cm, 
                    1.4 * cm, 
                    2 * cm,
                    2.7 * cm,
                    1 * cm,
                    1 * cm,
                    1 * cm,
                    1 * cm,
                    2.1 * cm
                ],
                splitByRow = 1,
                repeatRows = 1
            )
        if style:
            if hasheader:
                table.setStyle(style)
            elif stylealt:
                table.setStyle(stylealt)
        if len(datereference) == 0 and stylevoid is not None:
            table.setStyle(stylevoid)
        return table

class ReporteViaticosEmpTres(BasePlatypusReportOther):
    def __init__(self):
        self.begin(orientation = 'LANDSCAPE', rightMargin = 28, leftMargin = 28, topMargin = 36, bottomMargin = 28)

    def get(self, request, *args, **kwargs):
        mes =self.kwargs.get('slug')
        anoss =self.kwargs.get('slugu')
        user_id =self.kwargs.get('sluguh')
        self.draw(mes,anoss,user_id)
        self.write(onFirstPage = self.title)
        return self.response

    def title(self,canvas, document,**kwargs):
        slug =self.kwargs.get('slug')
        gestion =self.kwargs.get('slugu')
        user_id =self.kwargs.get('sluguh')
        #sluguh
        emp=get_object_or_404(empleado,ci=user_id)
        
        title = 'BOLETAS REGISTRADAS'
        canvas.saveState()
        
        archivo_imagen = settings.MEDIA_ROOT+'\images\logoo.png'
        archivo_imagen1 = settings.MEDIA_ROOT+'\images\money.png'
                
        canvas.setFont("Helvetica-Bold", 11)
        canvas.drawCentredString(self.x_start + self.width_internal / 2, self.y_start - 25, u"GOBIERNO AUTONOMO DEPARTAMENTAL DE POTOSI")
        canvas.setFont("Helvetica-Bold", 11)
        canvas.drawCentredString(self.x_start + self.width_internal / 2, self.y_start - 45, u"Secretaria Departamental Administracion y Financiera")
      
        canvas.drawImage(archivo_imagen1, self.x_start + 600,self.y_start - 64, 55, 55, preserveAspectRatio = True)
        
        canvas.setLineWidth(1)
        canvas.line(self.x_start+180, self.y_start-60, 585, self.y_start-60)
        
        canvas.setFont("Helvetica-Bold", 10)
        canvas.drawCentredString(self.x_start + self.width_internal / 2, self.y_start - 72, u"DETALLE DE PASAJES Y VIÁTICOS DEL PERSONAL DEL GOBIERNO AUTÓNOMO")
        
        gestion=emp.nombre.upper()+' '+emp.apaterno.upper()+' '+emp.amaterno.upper()+' MES DE '+slug.upper()+' '+u'GESTION '+ gestion
        canvas.setFont("Helvetica-Bold", 10)
        canvas.drawCentredString(self.x_start + self.width_internal / 2, self.y_start - 87, gestion)

        self.draw_left_image(canvas = canvas,
            url = archivo_imagen,
            x = self.x_start + 70, 
            y = self.y_start - 8, 
            w = 55, 
            h = 55
        )
    def draw(self,mes,anoss,user_id):
        self.add(Spacer(1, 90))
        self.draw_table(mes,anoss,user_id)
    def draw_table(self,mes,anoss,user_id):
        basic_style_full_doble = self.get_basic_style_full_doble()
        basic_style_body = self.get_basic_style_body()
        basic_style_full_doble_void = self.get_basic_style_full_doble_void()
        viaticos=viaticodiario.objects.all()
        self.add(self.draw_in_table_top(0,viaticos,mes,anoss,user_id,self.get_basic_style_full_doble_top(),basic_style_body, basic_style_full_doble_void, True))
        self.add(self.draw_in_table_result(0,viaticos,self.get_basic_style_full_doble_button(), basic_style_body, basic_style_full_doble_void, True)) 
        self.add(Spacer(1, 20))
        self.add(self.draw_in_table_resumen(0,viaticos,self.get_basic_style_full_doble_resumen(), basic_style_body, basic_style_full_doble_void, True)) 
    def draw_in_table_top(self,index = 0,datereference = None,mes= None,anoss= None,user_id=None,style = None,stylealt = None, stylevoid = None, hasheader = False):

        meses=['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
        mesesingles=['January','February','March','April','May','June','July','August','September','October','November','December']
        supercabecera = [
                'N°',
                'NOMBRES Y APELLIDOS',
                'C.I.',
                'PASAJES',
                'PEAJES',
                'VIATICO',
                '',
                '',
                'TOTAL A CANCELAR',
                'CONTROL PRESUPUESTARIO',
                '',
                '',
                '',
                'N° CUENTA'
        ]
        cabecera = [
            '',
            '',
            '',
            '',
            '',
            'IMPORTES',
            'RC-IVA',
            'LIQ. PAGABLE',
            '',
            'U.E',
            'PROG',
            'PROY',
            'ACT',
            ''		
        ]
        preparandojson = []
        cont=1
        for viatico in datereference:
                for mese in xrange(len(mesesingles)):
                        if mesesingles[mese]==viatico.timestamp.strftime('%B'):
                                if meses[mese] == mes and viatico.timestamp.strftime('%Y') == anoss and int(user_id)==viatico.id_solicitante:
                                      
                                        ue=0
                                        prog=0
                                        act=0
                                        proy=0
                                        if viatico.ue < 10:
                                                ue='%s%s'%(0,viatico.ue)
                                        else:
                                                ue=viatico.ue
                                        
                                        if viatico.prog < 10:
                                                prog='%s%s'%(0,viatico.prog)
                                        else:
                                                prog=viatico.prog

                                        if viatico.act < 10:
                                                act='%s%s'%(0,viatico.act)
                                        else:
                                                act=viatico.act

                                        if viatico.proy < 10:
                                                proy='%s%s'%(0,viatico.proy)
                                        else:
                                                proy=viatico.proy
                                      
                                        preparandojson.append({
                                                "ci":viatico.solicitante.ci,
                                                "NombreCompleto":'%s %s %s'%(viatico.solicitante.nombre.upper(),viatico.solicitante.apaterno.upper(),viatico.solicitante.amaterno.upper()),
                                                "id":cont,
                                                "pasaje": self.redondear(viatico.pasaje),
                                                "peaje": self.redondear(viatico.peaje),
                                                "importe": self.redondear(viatico.Monto_pagado),
                                                "rciva": self.redondear(viatico.RC_IVA),
                                                "liqpagable": self.redondear(viatico.Liquido_pagable),
                                                "liqtotalcancelar": self.redondear(viatico.totalC),
                                                "ue":ue,
                                                "prog":prog,
                                                "act":act,
                                                "proy":viatico.proy,
                                                "numero":viatico.solicitante.bcontrol
                                        })
                cont=cont+1
        detalles = [(
                via['id'],
                via['NombreCompleto'],
                via['ci'],
                via['pasaje'],
                via['peaje'],
                via['importe'],
                via['rciva'],
                via['liqpagable'],
                via['liqtotalcancelar'],
                via['ue'],
                via['prog'],
                via['proy'],
                via['act'],
                via['numero']
                ) for via in preparandojson]
        cm = 29
        #cm = 23.4
        if hasheader:
            table = Table(
                [supercabecera] + [cabecera] + detalles,
                colWidths = [
                    0.9 * cm, 
                    5 * cm, 
                    1.5 * cm,  
                    1.5 * cm, 
                    1.5 * cm, 
                    1.5 * cm, 
                    1.4 * cm, 
                    2 * cm,
                    2.7 * cm,
                    1 * cm,
                    1 * cm,
                    1 * cm,
                    1 * cm,
                    2.1 * cm
                ],
                splitByRow = 1,
                repeatRows = 0
            )
        
        if style:
            if hasheader:
                table.setStyle(style)
            elif stylealt:
                table.setStyle(stylealt)
        return table
    def redondear(self,valor=None):
        leter=str(valor)
        for le in xrange(len(leter)):
                if leter[le]=='.':
                        if (le+2)==len(leter):
                                return '%s%s'%(valor,0) 
                        else:     
                                return valor
    def draw_in_table_resumen(self,index = 0, datereference = None,style = None, stylealt = None, stylevoid = None, hasheader = False):
        cabecera = [
            'RESUMEN',
            ' '
        ]
        Sumatoriapasaje=0
        Sumatoriapeaje=0
        Sumatoriaimporte=0
        Sumatoriarciva=0
        Sumatorialiqpagable=0
        Sumatoriatotalcancelar=0
        preparandojson=[]
        for viatico in datereference:                
                Sumatoriapasaje=Sumatoriapasaje+viatico.pasaje
                Sumatoriapeaje=Sumatoriapeaje+viatico.peaje
                Sumatoriaimporte=Sumatoriaimporte+viatico.Monto_pagado
                Sumatoriarciva=Sumatoriarciva+viatico.RC_IVA
                Sumatorialiqpagable=Sumatorialiqpagable+viatico.Liquido_pagable
                Sumatoriatotalcancelar=Sumatoriatotalcancelar+viatico.totalC  
            
        detalles = [(
                "DESCRIPCIÓN",
                "IMPORTE EN BS."
                )]
        VIATICO = [(
                "VIÁTICO",
                self.redondear(Sumatoriaimporte)
                )]
        PEAJES = [(
                "PEAJES",
                self.redondear(Sumatoriapeaje)
                )]
        PASAJES = [(
                "PASAJES",
                self.redondear(Sumatoriapasaje)
                )]
        TOTAL = [(
                "TOTAL",
                self.redondear(Sumatoriapasaje+Sumatoriapeaje+Sumatoriaimporte)
                )]
        RC = [(
                "Menos RC - IVA",
                self.redondear(Sumatoriarciva)
                )]
        LIQUIDO = [(
                "LIQ. PAGABLE",
                self.redondear(Sumatorialiqpagable)
                )]
        cm = 29
        #cm = 23.4
        if hasheader:
            table = Table(
                [cabecera] + detalles+VIATICO+PEAJES+PASAJES+TOTAL+RC+LIQUIDO,
                colWidths = [
                    3 * cm, 
                    3 * cm                    
                ],
                splitByRow = 1,
                repeatRows = 1
            )
        if style:
            if hasheader:
                table.setStyle(style)
            elif stylealt:
                table.setStyle(stylealt)
        if len(datereference) == 0 and stylevoid is not None:
            table.setStyle(stylevoid)
        return table
    def draw_in_table_result(self,index = 0, datereference = None,style = None, stylealt = None, stylevoid = None, hasheader = False):
        Totalsumatoriapasaje=0
        Totalsumatoriapeaje=0
        Totalsumatoriaimporte=0
        Totalsumatoriarciva=0
        Totalsumatorialiqpagable=0
        Totalsumatoriatotalcancelar=0
        for viatico in datereference:
                Totalsumatoriapasaje=Totalsumatoriapasaje+viatico.pasaje
                Totalsumatoriapeaje=Totalsumatoriapeaje+viatico.peaje
                Totalsumatoriaimporte=Totalsumatoriaimporte+viatico.Monto_pagado
                Totalsumatoriarciva=Totalsumatoriarciva+viatico.RC_IVA
                Totalsumatorialiqpagable=Totalsumatorialiqpagable+viatico.Liquido_pagable
                Totalsumatoriatotalcancelar=Totalsumatoriatotalcancelar+viatico.totalC
        detalles = [(
                "TOTAL",
                " ",
                " ",
                self.redondear(Totalsumatoriapasaje),
                self.redondear(Totalsumatoriapeaje),
                self.redondear(Totalsumatoriaimporte),
                self.redondear(Totalsumatoriarciva),
                self.redondear(Totalsumatorialiqpagable),
                self.redondear(Totalsumatoriatotalcancelar),
                " ",
                " ",
                " ",
                " ",
                " ",
                )]
        cm = 29
        #cm = 23.4
        if hasheader:
            table = Table(
                detalles,
                colWidths = [
                    0.9 * cm, 
                    5 * cm, 
                    1.5 * cm,  
                    1.5 * cm, 
                    1.5 * cm, 
                    1.5 * cm, 
                    1.4 * cm, 
                    2 * cm,
                    2.7 * cm,
                    1 * cm,
                    1 * cm,
                    1 * cm,
                    1 * cm,
                    2.1 * cm
                ],
                splitByRow = 1,
                repeatRows = 1
            )
        if style:
            if hasheader:
                table.setStyle(style)
            elif stylealt:
                table.setStyle(stylealt)
        if len(datereference) == 0 and stylevoid is not None:
            table.setStyle(stylevoid)
        return table

# FIN GESTION DE REPORTES

def borrar(valor):
        id=valor[30:-1]
        return int(id)
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

@method_decorator(permission_required('viaticos.add_viaticodiario'),name='dispatch')
class ViaticoCreateView(CreateView):
	model = viaticodiario
	template_name = 'viaticos/viatico_modificado/register.html'
	form_class = viaticodiarioFormModificado
        second_form_class = otrosform
	success_url = reverse_lazy('viaticos:detail')

	def get_context_data(self, **kwargs):
		context = super(ViaticoCreateView, self).get_context_data(**kwargs)
                if 'nombre_completo' in context:
                        context['nombre']=kwargs['nombre_completo'][0]
                        context['apellido']=kwargs['nombre_completo'][1]
                        context['ci']=kwargs['nombre_completo'][2]
                        context['cargo']=kwargs['nombre_completo'][3]
		if 'form' not in context:
			context['form'] = self.form_class(self.request.GET)
		if 'form2' not in context:
			context['form2'] = self.second_form_class(self.request.GET)
		return context
        def get_initial(self, *args, **kwargs):
                initial = super(ViaticoCreateView, self).get_initial(**kwargs)
                initial['cambio_moneda'] =6.96                
                return initial
        def empty(self,valor):
                if valor == None:
                        return True
                return False
        def vacio(self,valor):
                if len(str(valor)) == 0:
                        return True
                return False
        def isConvert(self,valor):
                numero=str(valor)
                numerouno=""
                numerodos=""
                uno=True
                dos=False
                coma=False
                punto=False
                number=False 
                for n in xrange(len(numero)):
                        if numero[n]==',':
                                coma=True
                                break
                        if numero[n]=='.':
                                punto=True
                                break

                if coma==False and punto==False:
                        number=True

                for n in xrange(len(numero)):
                        if number:
                                numerouno=numerouno+numero[n] 
                        if coma:
                                if numero[n]!=',':
                                        if uno:
                                                numerouno=numerouno+numero[n]
                                        if dos:
                                                numerodos=numerodos+numero[n]
                                else:
                                        uno=False
                                        dos=True
                        if punto:
                                if numero[n]!='.':
                                        if uno:
                                                numerouno=numerouno+numero[n]
                                        if dos:
                                                numerodos=numerodos+numero[n]
                                else:
                                        uno=False
                                        dos=True
                if number:
                        return '%s.%s'%(numerouno,0)
                if isDecimal(numerouno):
                        if isDecimal(numerodos):
                                return '%s.%s'%(numerouno,numerodos)                              
        def llamar_ho_fec(self,valor):
                var1='%s %s'%(valor[0],valor[2])
                var2='%s %s'%(valor[1],valor[3])
                start = datetime.strptime(var1, '%Y-%m-%d %H:%M:%S') 
                ends = datetime.strptime(var2, '%Y-%m-%d %H:%M:%S')
                diff = relativedelta(start, ends) 
                dias=(diff.days)*(-1)
                horas=(diff.hours)*(-1)
                minutos=(diff.minutes)*(-1)
                diasviatico=0
                if horas < 6:
                        diasviatico='%s.%s'%(dias,0)
                else:
                        diasviatico='%s.%s'%(dias,5)
                return [dias,horas,minutos,diasviatico]

	def post(self, request, *args, **kwargs):
		self.object = self.get_object
		form = self.form_class(request.POST)
		form2 = self.second_form_class(request.POST)
                nombre_completo=[request.POST["nombre"],request.POST["apellido"],request.POST["ci"],request.POST["cargo"]]
		date = datetime.now()                
                if form.is_valid() and form2.is_valid():                        
                        viaticos = form.save(commit=False)                         
                        empleados=get_object_or_404(empleado,ci=viaticos.id_solicitante)   
                        orden_fechas=[]                        
                        otros_viajes=[]                                      
                        if viaticos.tipo_viatico_id == 3:               
                                errorfecha=[]
                                otrosviajes = form2.save(commit=False)
                                validaciones=[  otrosviajes.fecha_inicial_urbana,otrosviajes.fecha_llegada_urbana,
                                                otrosviajes.horaSalida_urbana,otrosviajes.horallegada_urbana,
                                                otrosviajes.lugar_urbana,

                                                otrosviajes.fecha_inicial_rural,otrosviajes.fecha_llegada_rural,
                                                otrosviajes.horaSalida_rural,otrosviajes.horallegada_rural,
                                                otrosviajes.lugar_rural,

                                                otrosviajes.fecha_inicial_frontera,otrosviajes.fecha_llegada_frontera,
                                                otrosviajes.horaSalida_frontera,otrosviajes.horallegada_frontera,
                                                otrosviajes.lugar_frontera,
                                                ]                            
                                i=0                                
                                vaciouno=False
                                vaciodos=False
                                vaciotres=False
                                vaciocuatro=False
                                vaciocinco=False
                                verificar=False
                                vali=[]
                                pos=0
                                n=0
                                for i in xrange(len(validaciones)):
                                        
                                        if i == 4:
                                                luga=otrosviajes.lugar_urbana
                                                print(luga)
                                                if otrosviajes.lugar_urbana==None:
                                                        vaciouno=True
                                                if str(validaciones[i-1])=="None":
                                                        vaciodos=True
                                                if str(validaciones[i-2])=="None":
                                                        vaciotres=True
                                                if str(validaciones[i-3])=="None":
                                                        vaciocuatro=True
                                                if str(validaciones[i-4])=="None":
                                                        vaciocinco=True
                                              
                                        if i == 9:
                                                
                                                if otrosviajes.lugar_rural==None:
                                                        vaciouno=True
                                                if str(validaciones[i-1])=="None":
                                                        vaciodos=True
                                                if str(validaciones[i-2])=="None":
                                                        vaciotres=True
                                                if str(validaciones[i-3])=="None":
                                                        vaciocuatro=True
                                                if str(validaciones[i-4])=="None":
                                                        vaciocinco=True
                                        if i == 14:     
                                                if otrosviajes.lugar_frontera==None:
                                                        vaciouno=True
                                                if str(validaciones[i-1])=="None":
                                                        vaciodos=True
                                                if str(validaciones[i-2])=="None":
                                                        vaciotres=True
                                                if str(validaciones[i-3])=="None":
                                                        vaciocuatro=True
                                                if str(validaciones[i-4])=="None":
                                                        vaciocinco=True
                                        if i == 4 or i==9 or i==14:
                                                if  vaciouno and vaciodos and vaciotres and vaciocuatro and vaciocinco:
                                                        vali.append({"valor":True}) 
                                                else:
                                                        vali.append({"valor":False})
                                                vaciouno=False
                                                vaciodos=False
                                                vaciotres=False
                                                vaciocuatro=False
                                                vaciocinco=False                                
                                cont=0                              
                                for m in xrange(len(vali)):                                                                           
                                        if vali[m]["valor"] == True:                                                
                                                cont=cont+1                              
                                if cont == 3:
                                        verificar=True
                                        errorfecha.append('SELECCIONE POR LO MENOS ALGUNA FECHA Y HORA DE VIAJE')                                      
                                else:
                                        pos=0
                                        n=0
                                        pala=["URBANA","RURAL","FRONTERA"]
                                        
                                        for m in xrange(len(vali)):
                                                
                                                if vali[m]["valor"]== False:
                                                        if m == 0:
                                                                n=4                                                                                                                                
                                                                if str(validaciones[n-4])=="None":
                                                                        verificar=True
                                                                        errorfecha.append('SELECCIONE FECHA DE SALIDA '+pala[m])
                                                                else:
                                                                        if int(validaciones[n-4].strftime('%Y')) != int(date.year):
                                                                                verificar=True
                                                                                errorfecha.append('LA FECHA SALIDA '+pala[m]+' TIENE QUE SER DE ESTE ANO')

                                                                if str(validaciones[n-3])=="None":
                                                                        verificar=True
                                                                        errorfecha.append('SELECCIONE FECHA DE LLEGADA '+pala[m])
                                                                else:
                                                                        
                                                                        if int(validaciones[n-3].strftime('%Y')) != int(date.year):
                                                                                verificar=True
                                                                                errorfecha.append('LA FECHA LLEGADA '+pala[m]+' TIENE QUE SER DE ESTE ANO')


                                                                if str(validaciones[n-2])=="None":
                                                                        verificar=True
                                                                        errorfecha.append('SELECCIONE HORA DE SALIDA '+pala[m])
                                                                                
                                                                if str(validaciones[n-1])=="None":
                                                                        verificar=True
                                                                        errorfecha.append('SELECCIONE HORA DE LLEGADA '+pala[m])
                                                                if otrosviajes.lugar_urbana==None:
                                                                        verificar=True
                                                                        errorfecha.append('SELECCIONE EL LUGAR '+pala[m])
                                                                
                                                                if str(validaciones[n-4])!="None" and str(validaciones[n-3])!="None":                                                                                 
                                                                        if validaciones[n-3] < validaciones[n-4]:
                                                                                verificar=True
                                                                                errorfecha.append('LA FECHA DE LLEGADA NO PUEDE SER MENOR A LA FECHA SALIDA EN '+pala[m])
                                                                
                                                                if str(validaciones[n-2]) !="None" and str(validaciones[n-1]) != "None":
                                                                        salida=validaciones[n-4]
                                                                        llegada=validaciones[n-3]
                                                                        horasalida=validaciones[n-2]
                                                                        horallegada=validaciones[n-1]                                                                                                                      
                                                                        if salida == llegada:
                                                                                if horallegada < horasalida:
                                                                                        verificar=True
                                                                                        errorfecha.append('LA HORA DE LLEGADA NO PUEDE SER MENOR A LA HORA SALIDA EN '+pala[m])
                                                        if m == 1:
                                                                n=9
                                                                if str(validaciones[n-4])=="None":
                                                                        verificar=True
                                                                        errorfecha.append('SELECCIONE FECHA DE SALIDA '+pala[m])
                                                                else:
                                                                        if int(validaciones[n-4].strftime('%Y')) != int(date.year):
                                                                                verificar=True
                                                                                errorfecha.append('LA FECHA SALIDA '+pala[m]+' TIENE QUE SER DE ESTE ANO')

                                                                if str(validaciones[n-3])=="None":
                                                                        verificar=True
                                                                        errorfecha.append('SELECCIONE FECHA DE LLEGADA '+pala[m])
                                                                else:
                                                                        
                                                                        if int(validaciones[n-3].strftime('%Y')) != int(date.year):
                                                                                verificar=True
                                                                                errorfecha.append('LA FECHA LLEGADA '+pala[m]+' TIENE QUE SER DE ESTE ANO')


                                                                if str(validaciones[n-2])=="None":
                                                                        verificar=True
                                                                        errorfecha.append('SELECCIONE HORA DE SALIDA '+pala[m])
                                                                                
                                                                if str(validaciones[n-1])=="None":
                                                                        verificar=True
                                                                        errorfecha.append('SELECCIONE HORA DE LLEGADA '+pala[m])
                                                                if otrosviajes.lugar_rural==None:
                                                                        verificar=True
                                                                        errorfecha.append('SELECCIONE EL LUGAR '+pala[m])
                                                                
                                                                if str(validaciones[n-4])!="None" and str(validaciones[n-3])!="None":                                                                                 
                                                                        if validaciones[n-3] < validaciones[n-4]:
                                                                                verificar=True
                                                                                errorfecha.append('LA FECHA DE LLEGADA NO PUEDE SER MENOR A LA FECHA SALIDA EN '+pala[m])
                                                                if str(validaciones[n-2]) !="None" and str(validaciones[n-1]) != "None":
                                                                        salida=validaciones[n-4]
                                                                        llegada=validaciones[n-3]
                                                                        horasalida=validaciones[n-2]
                                                                        horallegada=validaciones[n-1]                                                                                                                      
                                                                        if salida == llegada:
                                                                                if horallegada < horasalida:
                                                                                        verificar=True
                                                                                        errorfecha.append('LA HORA DE LLEGADA NO PUEDE SER MENOR A LA HORA SALIDA EN '+pala[m])
                                                        if m == 2:     
                                                                n=14
                                                                if str(validaciones[n-4])=="None":
                                                                        verificar=True
                                                                        errorfecha.append('SELECCIONE FECHA DE SALIDA '+pala[m])
                                                                else:
                                                                        if int(validaciones[n-4].strftime('%Y')) != int(date.year):
                                                                                verificar=True
                                                                                errorfecha.append('LA FECHA SALIDA '+pala[m]+' TIENE QUE SER DE ESTE ANO')

                                                                if str(validaciones[n-3])=="None":
                                                                        verificar=True
                                                                        errorfecha.append('SELECCIONE FECHA DE LLEGADA '+pala[m])
                                                                else:
                                                                        
                                                                        if int(validaciones[n-3].strftime('%Y')) != int(date.year):
                                                                                verificar=True
                                                                                errorfecha.append('LA FECHA LLEGADA '+pala[m]+' TIENE QUE SER DE ESTE ANO')


                                                                if str(validaciones[n-2])=="None":
                                                                        verificar=True
                                                                        errorfecha.append('SELECCIONE HORA DE SALIDA '+pala[m])
                                                                                
                                                                if str(validaciones[n-1])=="None":
                                                                        verificar=True
                                                                        errorfecha.append('SELECCIONE HORA DE LLEGADA '+pala[m])
                                                                if otrosviajes.lugar_frontera == None:
                                                                        verificar=True
                                                                        errorfecha.append('SELECCIONE EL LUGAR '+pala[m])
                                                                
                                                                if str(validaciones[n-4])!="None" and str(validaciones[n-3])!="None":                                                                                 
                                                                        if validaciones[n-3] < validaciones[n-4]:
                                                                                verificar=True
                                                                                errorfecha.append('LA FECHA DE LLEGADA NO PUEDE SER MENOR A LA FECHA SALIDA EN '+pala[m])
                                                                if str(validaciones[n-2]) !="None" and str(validaciones[n-1]) != "None":
                                                                        salida=validaciones[n-4]
                                                                        llegada=validaciones[n-3]
                                                                        horasalida=validaciones[n-2]
                                                                        horallegada=validaciones[n-1]                                                                                                                      
                                                                        if salida == llegada:
                                                                                if horallegada < horasalida:
                                                                                        verificar=True
                                                                                        errorfecha.append('LA HORA DE LLEGADA NO PUEDE SER MENOR A LA HORA SALIDA EN '+pala[m])

                                if verificar==True:                                                                                                     
                                        return self.render_to_response(self.get_context_data(form=form, form2=form2,nombre_completo=nombre_completo,errorfecha=errorfecha))
                                else:
                                        cont_rural_fronte_urb_dias=0
                                        cont_rural_fronte_urb_horas=0
                                        cont_rural_fronte_urb_minutos=0
                                                                                                
                                        tipo_others=otrosviajes.tipos_viajante
                                        mont_frontera=0
                                        valor_de_horas_fechas=[]
                                        nombre=""                                     
                                        NombreValores=["Urbana","Rural","F. Frontera"]  
                                        
                                        fecha_salida_valor=0
                                        fecha_legada_valor=0
                                        horaSalida_valor=0
                                        horallegada_valor=0
                                        for m in xrange(len(vali)): 
                                                if vali[m]["valor"]== False:
                                                        
                                                        pos=m*3
                                                        if m == 0:
                                                                n=4
                                                        if m == 1:
                                                                n=9
                                                        if m == 2:    
                                                                n=14
                                                        
                                                        fecha_salida_valor=validaciones[n-4]
                                                                                              
                                                        fecha_legada_valor=validaciones[n-3]
                                                        horaSalida_valor=validaciones[n-2]
                                                        horallegada_valor=validaciones[n-1]

                                                        orden_fechas.append({"id":m,"key":fecha_legada_valor,"key1":horallegada_valor})
                                                        orden_fechas.append({"id":m,"key":fecha_salida_valor,"key1":horaSalida_valor})                                                        
                                                        #nombre=nombre+str(validaciones[n])+"-" 
                                                        if m == 0:
                                                                nombre=nombre+otrosviajes.lugar_urbana+"-"
                                                                n=4
                                                        if m == 1:
                                                                nombre=nombre+otrosviajes.lugar_rural+"-"
                                                                n=9
                                                        if m == 2:    
                                                                nombre=nombre+otrosviajes.lugar_frontera+"-" 
                                                                n=14

                                                        va=self.llamar_ho_fec([fecha_salida_valor,fecha_legada_valor,horaSalida_valor,horallegada_valor])
                                                        
                                                        cont_rural_fronte_urb_dias=cont_rural_fronte_urb_dias+va[0]
                                                        cont_rural_fronte_urb_horas=cont_rural_fronte_urb_horas+va[1]
                                                        cont_rural_fronte_urb_minutos=cont_rural_fronte_urb_minutos+va[2]

                                                        montoss=get_object_or_404(Monto,Tipo_viatico_id=tipo_others,Nombre=NombreValores[m],valido=1)
                                                        result=0
                                                        monto=montoss.Cantidad
                                                        
                                                        i=1
                                                        cantidad_de_hora=6
                                                        if va[0] != 0:
                                                                while i <= va[0]:
                                                                        result=result+monto
                                                                        i = i + 1

                                                        if va[1]>=cantidad_de_hora:
                                                                result=result+float(monto)/2
                                                       
                                                        temporal=[]
                                                        resultado=round(result*concatenar(13),0)
                                                        temporal.append({"RC_IVA":int(resultado),
                                                                        "Liquido_pagable":result-resultado,
                                                                        "Monto_pagado":result})
                                                        
                                                        valor_de_horas_fechas.append({"posicion":m,"valor":temporal})
                                                        
                                                        otr_fech_salid=datetime.strptime(str(fecha_salida_valor),'%Y-%m-%d').date()                                                
                                                        otr_fehc_llegad=datetime.strptime(str(fecha_legada_valor),'%Y-%m-%d').date()
                                                                                                                                                  
                                                    
                                                        otros_fechav='%s al %s'%(otr_fech_salid.strftime('%d-%m'),otr_fehc_llegad.strftime('%d-%m-%Y'))
                                                        otros_calculohora='%s d, %s h, %s m '%(va[0],va[1],va[2])
                                                        otros_dias=va[3]
                                                        otros_viajes.append({                                                                
                                                                "fecha_salida":fecha_salida_valor,
                                                                "fecha_legada":fecha_legada_valor,
                                                                "horaSalida":horaSalida_valor,
                                                                "horallegada":horallegada_valor,
                                                                "lugar":validaciones[n],
                                                                "fechav":otros_fechav,
                                                                "calculohora":otros_calculohora,
                                                                "dias":otros_dias
                                                        })
                                                else:
                                                        valor_de_horas_fechas.append({"posicion":m,"valor":False})
                                                        otros_viajes.append({                                                                
                                                                "fecha_salida":"9999-09-09",
                                                                "fecha_legada":"9999-09-09",
                                                                "horaSalida":"00:00",
                                                                "horallegada":"00:00",
                                                                "lugar":"(null)",
                                                                "fechav":"(null)",
                                                                "calculohora":"(null)",
                                                                "dias":"0"
                                                        })                                                                                                                            
                                        for cal in xrange(len(valor_de_horas_fechas)):
                                                if valor_de_horas_fechas[cal]["valor"]!= False:                                                        
                                                        for mo in valor_de_horas_fechas[cal]["valor"]: 
                                                                                                                  
                                                                mont_frontera=float(mont_frontera)+float(mo["Monto_pagado"])
                                     
                                        result=mont_frontera                                                                       
                                        tipo_viaticoss=""
                                        id_tipo=0
                                        tipo_monto=""                                        
                                        tipo_viaticoss=Monto.objects.filter(Tipo_viatico_id=viaticos.tipo_viatico_id)
                                        for tis in tipo_viaticoss:
                                                id_tipo=tis.id
                                        tipo_monto=get_object_or_404(Monto,id=id_tipo)                                                                                            
                                        
                                        viaticos.monto=tipo_monto

                                        resultado=round(float(self.isConvert(result))*0.13,2)
                                        viaticos.Monto_pagado=float(self.isConvert(result))
                                        viaticos.RC_IVA=int(resultado)
                                        viaticos.Liquido_pagable=float(self.isConvert(result))-float(self.isConvert(viaticos.RC_IVA))
                                        pasaje=0
                                        peaje=0
                                        Extra=0
                                        if self.vacio(viaticos.pasaje):                                                
                                                viaticos.pasaje=pasaje

                                        if self.vacio(viaticos.peaje):                                                
                                                viaticos.peaje=peaje

                                        if self.vacio(viaticos.Extra):                                                
                                                viaticos.Extra=Extra
                                                        
                                        viaticos.totalC=viaticos.Liquido_pagable+float(self.isConvert(viaticos.pasaje))+float(self.isConvert(viaticos.peaje))+float(self.isConvert(viaticos.Extra))

                                        nombre_oficial=""
                                        for pa in xrange(len(nombre)):
                                                if pa == (len(nombre)-1):
                                                        if nombre[pa] != "-":
                                                                nombre_oficial=nombre_oficial+nombre[pa]
                                                else:        
                                                        nombre_oficial=nombre_oficial+nombre[pa]                                      
                                        viaticos.lugar=nombre_oficial 
                                        fecha1=0
                                        fecha2=0
                                        var_dias=0
                                        var_horas=0
                                        var_minutos=0
                                        var_fecha_Salida=0
                                        var_fecha_llegada=0
                                        var_hora_salida=0
                                        var_hora_llegada=0
                                        dias_sumando=0
                                        
                                        sorted_date = sorted(orden_fechas, key=lambda x: (datetime.strptime(str(x['key']), '%Y-%m-%d').date(),x['id'],x['key1']))                                                           
                                        fecha1=sorted_date[0]["key"]
                                        fecha2=sorted_date[len(sorted_date)-1]["key"]
                                        if cont_rural_fronte_urb_horas > 0 and cont_rural_fronte_urb_minutos >= 0:
                                                if cont_rural_fronte_urb_horas < 24:
                                                        var_dias=cont_rural_fronte_urb_dias
                                                        var_horas=cont_rural_fronte_urb_horas
                                                        var_minutos=cont_rural_fronte_urb_minutos
                                                else:
                                                        while cont_rural_fronte_urb_horas >= 24:                                                        
                                                                cont_rural_fronte_urb_dias=cont_rural_fronte_urb_dias+1
                                                                cont_rural_fronte_urb_horas=cont_rural_fronte_urb_horas-24
                                                        var_dias=cont_rural_fronte_urb_dias
                                                        var_horas=cont_rural_fronte_urb_horas
                                                        var_minutos=cont_rural_fronte_urb_minutos
                                        else:
                                                var_dias=cont_rural_fronte_urb_dias
                                                var_horas=cont_rural_fronte_urb_horas
                                                var_minutos=cont_rural_fronte_urb_minutos
                                        for otros in xrange(len(otros_viajes)):
                                                dias_sumando=dias_sumando+float(self.isConvert(otros_viajes[otros]["dias"]))

                                        var_fecha_Salida=fecha1
                                        var_fecha_llegada=fecha2                        
                                        var_hora_salida=sorted_date[0]["key1"]
                                        var_hora_llegada=sorted_date[len(sorted_date)-1]["key1"]

                                        viaticos.dias=dias_sumando 
                                        var_dia=str(dias_sumando)
                                        for di in xrange(len(var_dia)):
                                                if var_dia[di] ==".":
                                                        numero=int(var_dia[di+1])                                                
                                                        if numero == 0:
                                                                var_horas=random.randint(1, 5)
                                                        else:
                                                                var_horas=random.randint(7, 22)   
                                                        break                               
                                        viaticos.calculohora='%s d, %s h, %s m '%(var_dias,var_horas,var_minutos)
                                                                               
                                        if vali[0]["valor"]== False:                                                                                        
                                                otrosviajes.fechav_urbana=otros_viajes[0]["fechav"]
                                                otrosviajes.calculohora_urbana=otros_viajes[0]["calculohora"]
                                                otrosviajes.dias_urbana=otros_viajes[0]["dias"]

                                        if vali[1]["valor"]== False:                                              
                                                otrosviajes.fechav_rural=otros_viajes[1]["fechav"]
                                                otrosviajes.calculohora_rural=otros_viajes[1]["calculohora"]
                                                otrosviajes.dias_rural=otros_viajes[1]["dias"]                                     
                                        
                                        if vali[2]["valor"]== False:                                                
                                                otrosviajes.fechav_frontera=otros_viajes[2]["fechav"]
                                                otrosviajes.calculohora_frontera=otros_viajes[2]["calculohora"]
                                                otrosviajes.dias_frontera=otros_viajes[2]["dias"]                                        
                                        
                                        fech_salid=datetime.strptime(str(var_fecha_Salida),'%Y-%m-%d').date()                                                
                                        
                                        fehc_llegad=datetime.strptime(str(var_fecha_llegada),'%Y-%m-%d').date()
                                                                        
                                        viaticos.fecha_salida=fech_salid
                                        viaticos.fecha_legada=fehc_llegad
                                        viaticos.horaSalida=datetime.strptime(str(var_hora_salida),'%H:%M:%S').time()
                                        viaticos.horallegada=datetime.strptime(str(var_hora_llegada),'%H:%M:%S').time()
                                        
                                        viaticos.fechav='%s al %s'%(fech_salid.strftime('%d-%m'),fehc_llegad.strftime('%d-%m-%Y'))
                                        otrosviajes.slug_viaticos='%s-%s'%(viaticos.ncontrol,date.year)
                                        otrosviajes.save()
                        if viaticos.tipo_viatico_id == 1 or viaticos.tipo_viatico_id == 2:                                                     
                                var1='%s %s'%(viaticos.fecha_salida,viaticos.horaSalida)
                                var2='%s %s'%(viaticos.fecha_legada,viaticos.horallegada)                                                              
                                start = datetime.strptime(var1, '%Y-%m-%d %H:%M:%S') 
                                ends = datetime.strptime(var2, '%Y-%m-%d %H:%M:%S')
                                diff = relativedelta(start, ends) 
                                dias=(diff.days)*(-1)
                                horas=(diff.hours)*(-1)
                                minutos=(diff.minutes)*(-1)
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        
                                diastotales=[]
                                
                                dias_totales = ((start - ends).days)*(-1)
                                dias_totales = (ends - start).days
                                for days in range(dias_totales + 1): 
                                        fecha = start + relativedelta(days=days)
                                        nuevo=fecha.strftime('%A')
                                        diastotales.append(nuevo)
                                
                                longitud = len(diastotales)
                                contdias=0
                                conthoras=horas
                                contminutos=minutos
                                j=0
                                while j<dias:
                                        contdias=contdias+24
                                        j=j+1
                                conthoras=conthoras+contdias
                                totalhoras=0
                                totalminutos=0
                                cont=conthoras
                                uno=True
                                dos=True
                                tres=True
                                cuantas_vueltas=0
                                if viaticos.tipo_viatico_id == 2:                                         
                                        if viaticos.resolucion == False:                                                                  
                                                for i in xrange(len(diastotales)):
                                                        if uno:
                                                                if diastotales[i] == "Monday" or diastotales[i] == "Tuesday" or diastotales[i] ==  "Wednesday" or diastotales[i] == "Thursday" or diastotales[i] == "Friday":
                                                                        dos=False
                                                                        tres=False                                                   
                                                                        if diastotales[i] == "Friday" and i < longitud:
                                                                                print("si hay sabado")

                                                                                if (i+1) < longitud:
                                                                                        print("si hay domingo")
                                                                                        if diastotales[i+1] == "Saturday":
                                                                                                if (i+2) < longitud:     
                                                                                                        if diastotales[i+2] == "Sunday":
                                                                                                                if (i+3) < longitud:
                                                                                                                        if diastotales[i+3] == "Monday":
                                                                                                                                cuantas_vueltas=cuantas_vueltas+1
                                                                                                                                print("si hay lunes")
                                                                                                                                # poner la hora desde el viernes hasta las 23
                                                                                                                                # luego poner desde las 00:00 del lunes hasta la hora q es 
                                                                                                                        
                                                                                                                                menoshoras=viaticos.horallegada
                                                                                                                                totalhoras=(cont-48)
                                                                                                                                cont=cont-48
                                                                                                                                totalminutos=contminutos
                                                                                                                                #print('%s horas, %s minutos'%(cont,totalminutos))
                                                                                                                else:
                                                                                                                        print("si hay domingo")
                                                                                                                        menoshoras=viaticos.horallegada
                                                                                                                        totalhoras=(conthoras-menoshoras.hour)-24
                                                                                                                        totalminutos=contminutos-menoshoras.minute
                                                                                                                        #print('%s horas, %s minutos'%(totalhoras,totalminutos))                   
                                                                                                else:
                                                                                                        print("si hay sabado")
                                                                                                        
                                                                                                        menoshoras=viaticos.horallegada
                                                                                                        totalhoras=conthoras-menoshoras.hour
                                                                                                        totalminutos=contminutos-menoshoras.minute
                                                                                                        #print('%s horas, %s minutos'%(totalhoras,totalminutos))                                                                                                       
                                                        if dos:
                                                                if i==0 and (i) < longitud and diastotales[i] == "Saturday" and (i+1) < longitud and  diastotales[i+1] == "Sunday":
                                                                        uno=False
                                                                        tres=False
                                                                        if (i+2) < longitud:
                                                                                if diastotales[i+2] == "Monday":
                                                                                        if (i+3) < longitud:
                                                                                                if diastotales[i+3] == "Tuesday":
                                                                                                        if (i+4) < longitud:
                                                                                                                if diastotales[i+4] == "Wednesday":
                                                                                                                        if (i+5) < longitud:
                                                                                                                                if diastotales[i+5] == "Thursday":
                                                                                                                                        if (i+6) < longitud:
                                                                                                                                                if diastotales[i+6] == "Friday":
                                                                                                                                                        print("si hay viernes")
                                                                                                                                                        #menoshoras=viatico.horallegada
                                                                                                                                                        #datetime.strptime(str(horaSalida+':00'),'%H:%M:%S').time()
                                                                                                                                                       
                                                                                                                                                        menoshorassalida=viaticos.horaSalida
                                                                                                                                                        totalhoras=(cont-24-(24-menoshorassalida.hour))
                                                                                                                                                        totalminutos=contminutos-menoshorassalida.minute
                                                                                                                                                        print('%s horas, %s minutos'%(cont,totalminutos))        
                                                                                                                                        else:
                                                                                                                                                print("si hay jueves")
                                                                                                                                                #menoshoras=viatico.horallegada
                                                                                                                                                menoshorassalida=viaticos.horaSalida
                                                                                                                                                totalhoras=(cont-24-(24-menoshorassalida.hour))
                                                                                                                                                totalminutos=contminutos-menoshorassalida.minute
                                                                                                                                                print('%s horas, %s minutos'%(cont,totalminutos))
                                                                                                                        else:
                                                                                                                                print("si hay miercoles")
                                                                                                                                #menoshoras=viatico.horallegada
                                                                                                                                menoshorassalida=viaticos.horaSalida
                                                                                                                                totalhoras=(cont-24-(24-menoshorassalida.hour))
                                                                                                                                totalminutos=contminutos-menoshorassalida.minute
                                                                                                                                print('%s horas, %s minutos'%(cont,totalminutos))
                                                                                                        else:
                                                                                                                print("si hay martes")
                                                                                                                #menoshoras=viatico.horallegada
                                                                                                                menoshorassalida=viaticos.horaSalida
                                                                                                                totalhoras=(cont-24-(24-menoshorassalida.hour))
                                                                                                                totalminutos=contminutos-menoshorassalida.minute
                                                                                                                print('%s horas, %s minutos'%(cont,totalminutos))
                                                                                        else:
                                                                                                print("si hay lunes")
                                                                                                #menoshoras=viatico.horallegada
                                                                                                menoshorassalida=viaticos.horaSalida
                                                                                                totalhoras=(cont-24-(24-menoshorassalida.hour))
                                                                                                totalminutos=contminutos-menoshorassalida.minute
                                                                                                print('%s horas, %s minutos'%(cont,totalminutos))
                                                                                                                
                                                                        else:
                                                                                print("si hay sabado")
                                                                                #print('%s horas, %s minutos'%(totalhoras,totalminutos))
                                                        if tres:
                                                                if i==0 and (i) < longitud and diastotales[i] == "Sunday":
                                                                        uno=False
                                                                        dos=False
                                                                        if (i+1) < longitud:
                                                                                if diastotales[i+1] == "Monday":
                                                                                        if (i+2) < longitud:
                                                                                                if diastotales[i+2] == "Tuesday":
                                                                                                        if (i+3) < longitud:
                                                                                                                if diastotales[i+3] == "Wednesday":
                                                                                                                        if (i+4) < longitud:
                                                                                                                                if diastotales[i+4] == "Thursday":
                                                                                                                                        if (i+5) < longitud:
                                                                                                                                                if diastotales[i+5] == "Friday":
                                                                                                                                                        if (i+6) < longitud:
                                                                                                                                                                if diastotales[i+6] == "Saturday":
                                                                                                                                                                        
                                                                                                                                                                        menoshoras=viaticos.horallegada
                                                                                                                                                                        menoshorassalida=viaticos.horaSalida
                                                                                                                                                                        totalhoras=(cont-(24-menoshorassalida.hour)-menoshoras.hour)
                                                                                                                                                                        totalminutos=contminutos-menoshorassalida.minute-menoshoras.minute
                                                                                                                                                                #print('%s horas, %s minutos'%(cont,totalminutos))
                                                                                                                                        else:
                                                                                                                                                print("si hay domingo")
                                                                                                                                                menoshorassalida=viaticos.horaSalida
                                                                                                                                                totalhoras=(cont-(24-menoshorassalida.hour))
                                                                                                                                                totalminutos=contminutos-menoshorassalida.minute
                                                                                                                        else:
                                                                                                                                print("si hay domingo")
                                                                                                                                menoshorassalida=viaticos.horaSalida
                                                                                                                                totalhoras=(cont-(24-menoshorassalida.hour))
                                                                                                                                totalminutos=contminutos-menoshorassalida.minute
                                                                                                        else:
                                                                                                                print("si hay domingo")
                                                                                                                menoshorassalida=viaticos.horaSalida
                                                                                                                totalhoras=(cont-(24-menoshorassalida.hour))
                                                                                                                totalminutos=contminutos-menoshorassalida.minute
                                                                                                
                                                                                        else:
                                                                                                print("si hay domingo")
                                                                                                
                                                                                                menoshorassalida=viaticos.horaSalida
                                                                                                totalhoras=(cont-(24-menoshorassalida.hour))
                                                                                                totalminutos=contminutos-menoshorassalida.minute
                                                                                                #print('%s horas, %s minutos'%(totalhoras,totalminutos))
                                                                                                                       
                                contadordias=0
                                contadorhoras=0
                                contadorminutos=0
                                if totalhoras > 0 and totalminutos >= 0:
                                        if totalhoras < 24:
                                                contadordias=0
                                                contadorhoras=totalhoras
                                                contadorminutos=totalminutos
                                        else:
                                                while totalhoras >= 24:
                                                      
                                                        contadordias=contadordias+1
                                                        totalhoras=totalhoras-24
                                                contadorhoras=totalhoras
                                                contadorminutos=totalminutos
                                else:
                                        contadordias=dias
                                        contadorhoras=horas
                                        contadorminutos=contminutos
                                restando=0
                                if viaticos.tipo_viatico_id == 2: 
                                        if viaticos.resolucion == False:
                                                if viaticos.tipo_viatico_id == 2:
                                                        if cuantas_vueltas !=0:
                                                                date_only=viaticos.horaSalida                                                        
                                                                restando=contadorhoras-date_only.hour
                                                                                                                       
                                                                contadorhoras=restando
                                
                                Mont=get_object_or_404(Monto,id=request.POST['monto'])

                                
                                diasviatico=""
                                if contadorhoras < 6:
                                        diasviatico='%s.%s'%(contadordias,0)
                                else:
                                        diasviatico='%s.%s'%(contadordias,5)
                                Montos_request=get_object_or_404(Monto,id=viaticos.monto_id)
                                if Montos_request.identificacion == 2:
                                        viaticos.dias=viaticos.cantidad_dias_fuera_pais                                             
                                        viaticos.calculohora='%s d, %s h, %s m '%(viaticos.cantidad_dias_fuera_pais,0,0)
                                else:
                                        viaticos.dias=diasviatico                                                                                    
                                        viaticos.calculohora='%s d, %s h, %s m '%(contadordias,contadorhoras,contadorminutos)
                                                                                              
                                if Montos_request.identificacion == 1:
                                        result=0
                                        monto=Montos_request.Cantidad
                                        i=1
                                        cantidad_de_hora=6
                                        #if dias != 0:
                                        if contadordias != 0:
                                                while i <= contadordias:
                                                        result=result+monto
                                                        i = i + 1
                                        if contadorhoras>=cantidad_de_hora:
                                                result=result+float(monto)/2
                                        resultado=round(result*concatenar(13),0)
                                        viaticos.RC_IVA=int(resultado)
                                        viaticos.Liquido_pagable=result-resultado
                                        viaticos.Monto_pagado=result
                                        viaticos.cambio_moneda=0  
                                        
                                        pasaje=0
                                        peaje=0
                                        Extra=0
                                
                                        if self.vacio(viaticos.pasaje):                                                
                                                viaticos.pasaje=pasaje

                                        if self.vacio(viaticos.peaje):                                                
                                                viaticos.peaje=peaje

                                        if self.vacio(viaticos.Extra):                                                
                                                viaticos.Extra=Extra
                                                
                                        viaticos.totalC=viaticos.Liquido_pagable+float(self.isConvert(viaticos.pasaje))+float(self.isConvert(viaticos.peaje))+float(self.isConvert(viaticos.Extra))
                                        
                                        
                                else:
                                        if Montos_request.identificacion == 2:
                                                result=0
                                                monto=Montos_request.Cantidad
                                
                                                cambiomoneda=viaticos.cambio_moneda
                                                dias_afuera=viaticos.cantidad_dias_fuera_pais
                                                
                                                moneda_cambio=monto*float(self.isConvert(cambiomoneda))
                                                resultado_cambio=0
                                                j=0
                                                while j < int(dias_afuera):
                                                        resultado_cambio=resultado_cambio+moneda_cambio
                                                        j=j+1                         
                                                resultado=round(resultado_cambio*concatenar(13),0)                                                                                                                                                                        
                                                viaticos.RC_IVA=int(resultado)
                                                viaticos.Liquido_pagable=resultado_cambio-resultado
                                                viaticos.Monto_pagado=resultado_cambio
                                                pasaje=0
                                                peaje=0
                                                Extra=0
                                        
                                                if self.vacio(viaticos.pasaje):                                                
                                                        viaticos.pasaje=pasaje

                                                if self.vacio(viaticos.peaje):                                                
                                                        viaticos.peaje=peaje

                                                if self.vacio(viaticos.Extra):                                                
                                                        viaticos.Extra=Extra
                                                        
                                                viaticos.totalC=viaticos.Liquido_pagable+float(self.isConvert(viaticos.pasaje))+float(self.isConvert(viaticos.peaje))+float(self.isConvert(viaticos.Extra))
                                                                                                                                                                                        
                                
                                viaticos.fechav='%s al %s'%(viaticos.fecha_salida.strftime('%d-%m'),viaticos.fecha_legada.strftime('%d-%m-%Y'))
                        
                        viaticos.solicitante=empleados  

                        usuario=get_object_or_404(User,id=request.user.id)

                        viaticos.encargado='%s%s'%(usuario.username.capitalize(),' ')
                        viaticos.cod_u=usuario.id  

                        secretarias=get_object_or_404(Secretaria,id=empleados.secretaria_id)
                        viaticos.secretaria=secretarias
                                
                        viaticos.timestamp=datetime.strptime(('%s-%s-%s'%(date.year,date.month,date.day)), '%Y-%m-%d')                       
                        viaticos.save()		
			return HttpResponseRedirect(self.get_success_url())
		else:
			return self.render_to_response(self.get_context_data(form=form, form2=form2,nombre_completo=nombre_completo))

def handler404(request, *args, **argv):
    response = render_to_response('404.html', {},context_instance=RequestContext(request))
    response.status_code = 404
    return response
def handler500(request, *args, **argv):
    response = render_to_response('500.html', {},context_instance=RequestContext(request))
    response.status_code = 500
    return response

def home(request):
        template="home.html"
        return render(request,template,{})