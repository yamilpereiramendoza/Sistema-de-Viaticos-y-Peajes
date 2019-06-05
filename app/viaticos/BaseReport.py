#-*- coding: utf-8 -*-  
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import *

# Reports
from django.conf import settings
from io import BytesIO

import os

from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import landscape
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Table, Image
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.graphics import shapes, renderPDF, renderPM
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.widgets.markers import makeMarker

from datetime import datetime

class Cadena:
    def __init__(self):
        pass

    def list_to_lines(self, alist, startline = '', endline = '', isfinal = True):
        result = ""
        for a in alist:
            result += startline + a + endline + '\n'
        if isfinal and len(result) > 2:
            result = result[0:-2]
        return result

    def simpledict_to_list(self, dict, key = ''):
        lista = []
        for d in dict:
            lista.append(d[key])
        print(str(lista))
        return lista

class BasePlatypusReport(View):
    media_path = settings.MEDIA_ROOT
    #media_path = settings.MEDIA_RAIZ
    temporal_files = []
    Cadena = Cadena()
    def begin(self, orientation = 'portrait', rightMargin = 48, leftMargin = 72, topMargin = 48, bottomMargin = 48):
        if orientation.upper() == 'PORTRAIT':
            self.response = HttpResponse(content_type = 'application/pdf')
            self.buffer = BytesIO()
            self.doc = SimpleDocTemplate(
                self.buffer,
                pagesize = letter,
                rightMargin = rightMargin,
                leftMargin = leftMargin,
                topMargin = topMargin,
                bottomMargin = bottomMargin,
                showBoundary = False
            )
            self.width, self.height = letter
        else:
            self.response = HttpResponse(content_type = 'application/pdf')
            self.buffer = BytesIO()
            self.doc = SimpleDocTemplate(
                self.buffer,
                pagesize = landscape(letter),
                rightMargin = rightMargin,
                leftMargin = leftMargin,
                topMargin = topMargin,
                bottomMargin = bottomMargin,
                showBoundary = False
            )
            self.width, self.height = landscape(letter)

        self.width_internal = self.width - leftMargin - rightMargin
        self.y_start = self.height - topMargin
        self.x_start = leftMargin
        self.x_end = self.width - rightMargin
        self.y_end = 0 + bottomMargin
        self.flowables = []

    def add(self, element):
        self.flowables.append(element)
    
    def write(self, onFirstPage = None, onLaterPages = None):
        if onFirstPage and onLaterPages:
            self.doc.build(self.flowables, onFirstPage = onFirstPage, onLaterPages = onLaterPages)
        elif onFirstPage:
            self.doc.build(self.flowables, onFirstPage = onFirstPage)
        elif onLaterPages:
            self.doc.build(self.flowables, onLaterPages = onLaterPages)
        else:
            self.doc.build(self.flowables)
        self.response.write(self.buffer.getvalue())
        self.buffer.close()

        self.delete_temporal_files()
        return self.response
    def delete_temporal_files(self):
        for tmp in self.temporal_files:
            try:
                os.remove(tmp)
            except:
                pass

    def add_temporal_file(self, element):
        self.temporal_files.append(element)

    def draw_left_image(self, canvas, url, x, y, w, h, x_padding = 0, y_padding = 0, title = ''):
        try:
            canvas.drawImage(url, x + x_padding, y - h - y_padding, w, h, preserveAspectRatio = True)
        except:
            canvas.roundRect(x + x_padding, y - y_padding - h, w, h, 0, stroke = 1, fill = 0)
            canvas.line(x + x_padding, y - y_padding + h - h, x + x_padding + w, y - y_padding - h)
            canvas.line(x + x_padding, y - y_padding - h, x + x_padding + w, y - y_padding + h - h)

    def draw_right_image(self, canvas, url, x, y, w, h, x_padding = 0, y_padding = 0, title = ''):
        try:
            canvas.drawImage(url, x + x_padding, y - h - y_padding, w, h, preserveAspectRatio = True)
        except:
            canvas.roundRect(x + x_padding, y - y_padding - h, w, h, 0, stroke = 1, fill = 0)
            canvas.line(x + x_padding, y - y_padding + h - h, x + x_padding + w, y - y_padding - h)
            canvas.line(x + x_padding, y - y_padding - h, x + x_padding + w, y - y_padding + h - h)

    def get_basic_style_full(self, size_title = 9, size_body = 9):
        estilo_completo = TableStyle(
            [
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('TEXTCOLOR',(0, 0),(-1, 0),colors.white),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('BACKGROUND', (0, 0),(-1, 0), HexColor('#8B0000')),
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                ('ALIGN', (0, 0 ), (-1, -1), 'CENTER'),
            ]
        )
        return estilo_completo
    def get_basic_style_body(self, size_body = 9):
        estilo_cuerpo = TableStyle(
            [
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                ('ALIGN', (0, 0 ), (-1, -1), 'CENTER'),
            ]
        )
        return estilo_cuerpo
    def get_basic_style_full_doble_button(self, size_title = 9, size_body = 9):
        estilo_completo = TableStyle(
            [
                ('FONTSIZE', (0, 0), (-1, -1), 7),
                ('TEXTCOLOR',(0, 1),(-1, 0),colors.white),  # esto nos sirve para el color del texto arriba
                #('ALIGN', (0, 0), (-1, 0), 'LEFT'),
                ('BACKGROUND', (0, 0),(-1, 0), colors.white),
                ('SPAN', (0, 0),(1, 0)),
                #('BACKGROUND', (0, 1),(-1, 0), HexColor('#2A3F54')),
                
                ('BOX', (0, 0), (-1, -1), 1, colors.black), # caja los laterales
                ('INNERGRID', (0, 0), (-1, -1), 1, colors.black), # caja los medios
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2), # padding-top
                ('ALIGN', (0, 0 ), (-1, -1), 'LEFT'),
            ]
        )
        return estilo_completo
    def get_basic_style_full_doble_top(self, size_title = 9, size_body = 9):
        estilo_completo = TableStyle(
            [
                ('FONTSIZE', (0, 0), (-1, -1), 7),
                ('TEXTCOLOR',(0, 0),(-1, 0),colors.white),  # esto nos sirve para el color del texto arriba
                #('ALIGN', (0, 0), (-1, 0), 'LEFT'),
                ('BACKGROUND', (0, 0),(-1, 0), HexColor('#2A3F54')),
                #('SPAN', (0, 0),(-1, 0)),
                #('ALIGN', (0, 2 ), (1, 2), 'RIGHT'),
                ('BACKGROUND', (0, 1),(-1, 0), HexColor('#2A3F54')),
                ('BOX', (0, 0), (-1, -1), 1, colors.black), # caja los laterales
                ('INNERGRID', (0, 0), (-1, -1), 1, colors.black), # caja los medios
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2), # padding-top
                ('ALIGN', (0, 0 ), (-1, -1), 'LEFT'),
            ]
        )
        return estilo_completo
    # ESTA PARTE ES PARA EL DE ARRIBA TITULO
    def get_basic_style_full_doble(self, size_title = 9, size_body = 9):
        estilo_completo = TableStyle(
            [
                ('FONTSIZE', (0, 0), (-1, -1), 7),
                ('TEXTCOLOR',(0, 0),(-1, 1),colors.white),
                ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
                ('BACKGROUND', (0, 0),(-1, 0), HexColor('#2A3F54')),
                ('SPAN', (0, 0),(-1, 0)),
                ('BACKGROUND', (0, 1),(-1, 1), HexColor('#2A3F54')),
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                ('ALIGN', (0, 0 ), (-1, -1), 'LEFT'),
            ]
        )
        return estilo_completo

    def get_basic_style_full_doble_void(self, size_title = 9, size_body = 9):
        estilo_completo = TableStyle(
            [
                ('FONTSIZE', (0, 0), (-1, -1), 7),
                ('TEXTCOLOR',(0, 0),(-1, 1),colors.white),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('BACKGROUND', (0, 0),(-1, 0), HexColor('#2A3F54')),
                ('SPAN', (0, 0),(-1, 0)),
                ('BACKGROUND', (0, 1),(-1, 1), HexColor('#2A3F54')),
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                ('ALIGN', (0, 0 ), (-1, -1), 'CENTER'),
                ('SPAN', (0, 2), (-1, -1)),
            ]
        )
        return estilo_completo
    
class BasePlatypusReportOther(View):
    media_path = settings.MEDIA_ROOT
    #media_path = settings.MEDIA_RAIZ
    temporal_files = []
    Cadena = Cadena()
    def begin(self, orientation = 'portrait', rightMargin = 48, leftMargin = 72, topMargin = 48, bottomMargin = 48):
        if orientation.upper() == 'PORTRAIT':
            self.response = HttpResponse(content_type = 'application/pdf')
            self.buffer = BytesIO()
            self.doc = SimpleDocTemplate(
                self.buffer,
                pagesize = letter,
                rightMargin = rightMargin,
                leftMargin = leftMargin,
                topMargin = topMargin,
                bottomMargin = bottomMargin,
                showBoundary = False
            )
            self.width, self.height = letter
        else:
            self.response = HttpResponse(content_type = 'application/pdf')
            self.buffer = BytesIO()
            self.doc = SimpleDocTemplate(
                self.buffer,
                pagesize = landscape(letter),
                rightMargin = rightMargin,
                leftMargin = leftMargin,
                topMargin = topMargin,
                bottomMargin = bottomMargin,
                showBoundary = False
            )
            self.width, self.height = landscape(letter)

        self.width_internal = self.width - leftMargin - rightMargin
        self.y_start = self.height - topMargin
        self.x_start = leftMargin
        self.x_end = self.width - rightMargin
        self.y_end = 0 + bottomMargin
        self.flowables = []

    def add(self, element):
        self.flowables.append(element)
    
    def write(self, onFirstPage = None, onLaterPages = None):
        if onFirstPage and onLaterPages:
            self.doc.build(self.flowables, onFirstPage = onFirstPage, onLaterPages = onLaterPages)
        elif onFirstPage:
            self.doc.build(self.flowables, onFirstPage = onFirstPage)
        elif onLaterPages:
            self.doc.build(self.flowables, onLaterPages = onLaterPages)
        else:
            self.doc.build(self.flowables)
        self.response.write(self.buffer.getvalue())
        self.buffer.close()

        self.delete_temporal_files()
        return self.response



    def delete_temporal_files(self):
        for tmp in self.temporal_files:
            try:
                os.remove(tmp)
            except:
                pass

    def add_temporal_file(self, element):
        self.temporal_files.append(element)

    def draw_left_image(self, canvas, url, x, y, w, h, x_padding = 0, y_padding = 0, title = ''):
        try:
            canvas.drawImage(url, x + x_padding, y - h - y_padding, w, h, preserveAspectRatio = True)
        except:
            canvas.roundRect(x + x_padding, y - y_padding - h, w, h, 0, stroke = 1, fill = 0)
            canvas.line(x + x_padding, y - y_padding + h - h, x + x_padding + w, y - y_padding - h)
            canvas.line(x + x_padding, y - y_padding - h, x + x_padding + w, y - y_padding + h - h)

    def draw_right_image(self, canvas, url, x, y, w, h, x_padding = 0, y_padding = 0, title = ''):
        try:
            canvas.drawImage(url, x + x_padding, y - h - y_padding, w, h, preserveAspectRatio = True)
        except:
            canvas.roundRect(x + x_padding, y - y_padding - h, w, h, 0, stroke = 1, fill = 0)
            canvas.line(x + x_padding, y - y_padding + h - h, x + x_padding + w, y - y_padding - h)
            canvas.line(x + x_padding, y - y_padding - h, x + x_padding + w, y - y_padding + h - h)

    def get_basic_style_full(self, size_title = 9, size_body = 9):
        estilo_completo = TableStyle(
            [
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('TEXTCOLOR',(0, 0),(-1, 0),colors.white),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('BACKGROUND', (0, 0),(-1, 0), HexColor('#8B0000')),
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                ('ALIGN', (0, 0 ), (-1, -1), 'CENTER'),
            ]
        )
        return estilo_completo
    def get_basic_style_body(self, size_body = 9):
        estilo_cuerpo = TableStyle(
            [
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                ('ALIGN', (0, 0 ), (-1, -1), 'CENTER'),
            ]
        )
        return estilo_cuerpo
    def get_basic_style_full_doble_top(self, size_title = 9, size_body = 9):
        estilo_completo = TableStyle(
            [               
                ('FONTSIZE', (0, 0), (-1, -1), 7),
                ('TEXTCOLOR',(0, 0),(-1, 1),colors.white),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('BACKGROUND', (0, 0),(-1, 0), HexColor('#2A3F54')),
                ('SPAN', (0, 0),(0, 1)),
                ('VALIGN',(0,0),(0, 1),'MIDDLE'),
                ('SPAN', (1, 0),(1, 1)),
                ('VALIGN',(1,0),(1, 1),'MIDDLE'),
                ('SPAN', (2, 0),(2, 1)),
                ('VALIGN',(2,0),(2, 1),'MIDDLE'),
                ('SPAN', (3, 0),(3, 1)),
                ('VALIGN',(3,0),(3, 1),'MIDDLE'),
                ('SPAN', (4, 0),(4, 1)),
                ('VALIGN',(4,0),(4, 1),'MIDDLE'),
                ('SPAN', (5, 0),(7, 0)),
                ('SPAN', (8, 0),(8, 1)),
                ('VALIGN',(8,0),(8, 1),'MIDDLE'),
                ('SPAN', (9, 0),(12, 0)),
                ('SPAN', (13, 0),(13, 1)),
                ('VALIGN',(13,0),(13, 1),'MIDDLE'),

                ('ALIGN', (1, 2), (1, -1), 'LEFT'),    

                ('BACKGROUND', (0, 1),(-1, 1), HexColor('#2A3F54')),
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                
                ('ALIGN', (0, 2), (0, -1), 'CENTER'),
                ('ALIGN', (2, 2), (2, -1), 'CENTER'),
                ('ALIGN', (3, 2), (3, -1), 'CENTER'),
                ('ALIGN', (4, 2), (4, -1), 'CENTER'),
                ('ALIGN', (5, 2), (5, -1), 'CENTER'),
                ('ALIGN', (6, 2), (6, -1), 'CENTER'),
                ('ALIGN', (7, 2), (7, -1), 'CENTER'),
                ('ALIGN', (8, 2), (8, -1), 'CENTER'),
                ('ALIGN', (9, 2), (9, -1), 'CENTER'),
                ('ALIGN', (10, 2), (10, -1), 'CENTER'),
                ('ALIGN', (11, 2), (11, -1), 'CENTER'),
                ('ALIGN', (12, 2), (12, -1), 'CENTER'),
                ('ALIGN', (13, 2), (13, -1), 'CENTER'),
            ]
        )
        return estilo_completo
    def get_basic_style_full_doble_button(self, size_title = 9, size_body = 9):
        estilo_completo = TableStyle(
            [
                ('FONTSIZE', (0, 0), (-1, -1), 7),
                ('TEXTCOLOR',(0, 1),(-1, 0),colors.white),  # esto nos sirve para el color del texto arriba
                #('ALIGN', (0, 0), (-1, 0), 'LEFT'),
                ('BACKGROUND', (0, 0),(-1, 0), colors.white),
                ('SPAN', (0, 0),(2, 0)),
                ('SPAN', (9, 0),(13, 0)),
                #('BACKGROUND', (0, 1),(-1, 0), HexColor('#2A3F54')),
                
                ('BOX', (0, 0), (-1, -1), 1, colors.black), # caja los laterales
                ('INNERGRID', (0, 0), (-1, -1), 1, colors.black), # caja los medios
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2), # padding-top
                ('ALIGN', (3, 0 ), (8, 0), 'CENTER'),
            ]
        )
        return estilo_completo
    def get_basic_style_full_doble_resumen(self, size_title = 9, size_body = 9):
        estilo_completo = TableStyle(
            [
                ('FONTSIZE', (0, 0), (-1, -1), 7),
                ('TEXTCOLOR',(0, 1),(-1, 0),colors.white),  # esto nos sirve para el color del texto arriba
                #('ALIGN', (0, 0), (-1, 0), 'LEFT'),
                ('BACKGROUND', (0, 0),(-1, 0), colors.white),
                ('SPAN', (0, 0),(1, 0)),
                ('FONTSIZE', (0, 0), (1, 0), 9),
                ('ALIGN', (0, 0 ), (1, 0), 'CENTER'),
                #('BACKGROUND', (0, 1),(-1, 0), HexColor('#2A3F54')),
                ('ALIGN', (0, 1 ), (1, 1), 'CENTER'),
               
                ('FONTSIZE', (0, 1), (1, 1), 9),
                ('FONT', (0,1), (1, 1), 'Courier'),

                ('ALIGN', (0, 2 ), (1, 2), 'RIGHT'),
                ('ALIGN', (0, 3 ), (1, 3), 'RIGHT'),
                ('ALIGN', (0, 4 ), (1, 4), 'RIGHT'),
                ('ALIGN', (0, 5 ), (1, 5), 'RIGHT'),
                ('FONTSIZE', (0, 5), (0, 5), 9),
                ('ALIGN', (0, 6 ), (1, 6), 'RIGHT'),
                ('ALIGN', (0, 7 ), (1, 7), 'RIGHT'),
                ('FONTSIZE', (0, 7), (0, 7), 9),
                ('BOX', (0, 0), (-1, -1), 1, colors.black), # caja los laterales
                ('INNERGRID', (0, 0), (-1, -1), 1, colors.black), # caja los medios
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2), # padding-top
                #('ALIGN', (3, 0 ), (8, 0), 'CENTER'),
            ]
        )
        return estilo_completo
    def get_basic_style_full_doble(self, size_title = 9, size_body = 9):
        estilo_completo = TableStyle(
            [
                ('FONTSIZE', (0, 0), (-1, -1), 7),
                ('TEXTCOLOR',(0, 0),(-1, 1),colors.white),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('BACKGROUND', (0, 0),(-1, 0), HexColor('#2A3F54')),
                ('SPAN', (0, 0),(-1, 0)),
                ('BACKGROUND', (0, 1),(-1, 1), HexColor('#2A3F54')),
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                ('ALIGN', (0, 0 ), (-1, -1), 'CENTER'),
            ]
        )
        return estilo_completo

    def get_basic_style_full_doble_void(self, size_title = 9, size_body = 9):
        estilo_completo = TableStyle(
            [
                ('FONTSIZE', (0, 0), (-1, -1), 7),
                ('TEXTCOLOR',(0, 0),(-1, 1),colors.white),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('BACKGROUND', (0, 0),(-1, 0), HexColor('#2A3F54')),
                ('SPAN', (0, 0),(-1, 0)),
                ('BACKGROUND', (0, 1),(-1, 1), HexColor('#2A3F54')),
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                ('ALIGN', (0, 0 ), (-1, -1), 'CENTER'),
                ('SPAN', (0, 2), (-1, -1)),
            ]
        )
        return estilo_completo
    

