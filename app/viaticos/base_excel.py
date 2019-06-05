from django.http import HttpResponse
from django.views.generic import View
import xlwt
from xlwt import Workbook
from xlwt import Font
from xlwt import XFStyle
from xlwt import Borders
from datetime import datetime,date
from app.empleado.models import Secretaria
from django.shortcuts import get_object_or_404
class Base_Excel(View):
    date = datetime.now()
    def Upper(self,valor):
        if valor != None:
            return valor.upper()
        return ""
    def control_presupuesto(self,valor):
        pala=""
        if valor < 10:
            pala="0"+str(valor) 
        else:
            pala=valor
        return pala
    def begin(self,nombre=None,header=9,result=8):

        name=nombre+str(self.date.year)

        self.response = HttpResponse(content_type='application/ms-excel')
        self.response['Content-Disposition'] = 'attachment; filename='+str(name)+'.xls'
        self.workbook = xlwt.Workbook()
        self.worksheet = self.workbook.add_sheet(str(nombre))

        alignment = xlwt.Alignment()
        alignment.horz = xlwt.Alignment.HORZ_CENTER
        alignment.vert = xlwt.Alignment.VERT_CENTER

        header_font = Font()
        body_font = Font()
        title_font=Font()
        title_font2=Font()
        title_font3=Font()
        resultado_font=Font()
        redondeos_font=Font()
        persona_font=Font()

        title_font.name='Vivaldi'
        title_font.italic=True
        title_font.bold = True
        title_font.height = 20 * 14

        title_font2.name='Vivaldi'
        title_font2.italic=True
        title_font2.bold = True
        title_font2.height = 20 * 16

        title_font3.name='Arial'
        title_font3.italic=True
        title_font3.bold = True
        title_font3.height = 20 * 11

        header_font.name = 'Arial Narrow'
        header_font.height = 20 * header
        header_font.bold = True

        resultado_font.name = 'Arial Narrow'
        resultado_font.height = 20 * result
      

        body_font.name = 'Arial'
        
        body_font.italic = False


        redondeos_font.name = 'Arial'
        redondeos_font.height = 20 * 9


        persona_font.name = 'Arial'
        persona_font.height = 20 * 10
        
        self.title_style = XFStyle() 
        self.title_style.font = title_font
        self.title_style2 = XFStyle() 
        self.title_style2.font = title_font2
        self.title_style3 = XFStyle() 
        self.title_style3.font = title_font3

        self.header_style = XFStyle() 
        self.header_style.font = header_font

        borders = Borders()
        borders.left = 1
        borders.right = 1
        borders.top = 1
        borders.bottom = 1

        self.header_style.borders = borders
        self.header_style.alignment=alignment

        self.body_style = XFStyle()
        self.body_style.font = body_font
        self.body_style.borders=borders
        self.body_style.alignment=alignment

        self.result_style=XFStyle()
        self.result_style.font=resultado_font
        self.result_style.borders=borders
    
        self.redondeos_style=XFStyle()
        self.redondeos_style.font=redondeos_font
        self.redondeos_style.borders=borders
        self.redondeos_style.alignment=alignment
        self.redondeos_style.num_format_str = '#,###0.00'
        
        self.persona_style=XFStyle()
        self.persona_style.font=persona_font
        self.persona_style.borders=borders
        self.persona_style.alignment=alignment
    def buscarSecre(self,valor):                
                se=get_object_or_404(Secretaria,numeroS=valor)
                return se.nombreS
    def tama(self,worksheet):
        self.worksheet.col(0).width = 8 * 410
        self.worksheet.col(1).width = 8 * 280
        self.worksheet.col(2).width = 8 * 300
        self.worksheet.col(3).width = 8 * 270
        self.worksheet.col(4).width = 8 * 270
        self.worksheet.col(5).width = 8 * 350
        self.worksheet.col(6).width = 8 * 250
        self.worksheet.col(7).width = 8 * 450
        self.worksheet.col(8).width = 8 * 550                
    def insert(self,worksheet,tama=0,row_num=0):

        fila=row_num+1
        posicion=row_num+3
        
        inicio_num=tama


        self.worksheet.write_merge(row_num+1,row_num+1,0,2,"TOTAL",self.header_style)
        self.worksheet.write_merge(row_num+1,row_num+1,3,3,xlwt.Formula('SUM(D%s:D%s)'%(inicio_num,fila)),self.redondeos_style)
        self.worksheet.write_merge(row_num+1,row_num+1,4,4,xlwt.Formula('SUM(E%s:E%s)'%(inicio_num,fila)),self.redondeos_style)
        self.worksheet.write_merge(row_num+1,row_num+1,5,5,xlwt.Formula('SUM(F%s:F%s)'%(inicio_num,fila)),self.redondeos_style)
        self.worksheet.write_merge(row_num+1,row_num+1,6,6,xlwt.Formula('SUM(G%s:G%s)'%(inicio_num,fila)),self.redondeos_style)
        self.worksheet.write_merge(row_num+1,row_num+1,7,7,xlwt.Formula('SUM(H%s:H%s)'%(inicio_num,fila)),self.redondeos_style)
        self.worksheet.write_merge(row_num+1,row_num+1,8,8,xlwt.Formula('SUM(I%s:I%s)'%(inicio_num,fila)),self.redondeos_style)

        columna=row_num+2
        columns_result=['DESCRIPCION',"CANTIDAD","PEAJES","PASAJES","IMPORTE","Menos RC-IVA","LIQ. PAGABLE","TOTAL A CANCELAR"]    

        for col_num in range(len(columns_result)):
                columna =columna+1
                if col_num == 0:
                        self.worksheet.write_merge(columna,columna,3,4,columns_result[col_num],self.header_style)
                else:
                        self.worksheet.write_merge(columna,columna,3,4,columns_result[col_num],self.result_style)

        self.worksheet.write_merge(posicion,posicion,5,6,'IMPORTES EN BS.',self.header_style)
        self.worksheet.write_merge(posicion+1,posicion+1,5,6,xlwt.Formula('SUM(A%s:A%s)'%(inicio_num,fila)),self.persona_style)
        self.worksheet.write_merge(posicion+2,posicion+2,5,6,xlwt.Formula('SUM(D%s:D%s)'%(inicio_num,fila)),self.redondeos_style)
        self.worksheet.write_merge(posicion+3,posicion+3,5,6,xlwt.Formula('SUM(E%s:E%s)'%(inicio_num,fila)),self.redondeos_style)
        self.worksheet.write_merge(posicion+4,posicion+4,5,6,xlwt.Formula('SUM(F%s:F%s)'%(inicio_num,fila)),self.redondeos_style)
        self.worksheet.write_merge(posicion+5,posicion+5,5,6,xlwt.Formula('SUM(G%s:G%s)'%(inicio_num,fila)),self.redondeos_style)
        self.worksheet.write_merge(posicion+6,posicion+6,5,6,xlwt.Formula('F%s-F%s'%(row_num+8,row_num+9)),self.redondeos_style)
        self.worksheet.write_merge(posicion+7,posicion+7,5,6,xlwt.Formula('F%s+F%s+F%s'%(row_num+6,row_num+7,row_num+10)),self.redondeos_style)



       
     
        

