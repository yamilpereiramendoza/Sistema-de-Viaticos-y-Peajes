from django.views.generic import View
class base_View(View):
    anos=[]
    meseslist=['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
    mesesingles=['January','February','March','April','May','June','July','August','September','October','November','December']
    error=''
    def cargar(self):
        self.anos=[]
        i=2002
        while i <= 2050:
                self.anos.append({'ano':i}) 
                i=i+1
        return self.anos
class ReportsView(base_View):
    preparandojson=[]
    varificar=False
    cont=1
    
    def form_valid(self,valor):
        if valor[0] == 'None':
            self.varificar=True
            self.error=self.error+valor[1]+' \n' 
    def llevar_json_otros(self,viatico):                       
        ue=0
        prog=0
        act=0
        proy=0
        if viatico[0] < 10:
                ue='%s%s'%(0,viatico[0])
        else:
                ue=viatico[0]
        if viatico[1] < 10:
                prog='%s%s'%(0,viatico[1])
        else:
                prog=viatico[1]
        if viatico[2] < 10:
                act='%s%s'%(0,viatico[2])
        else:
                act=viatico[2]
                
        if viatico[3] < 10:
                if viatico[3] == None:
                        proy=""
                else:
                        proy='%s%s'%(0,viatico[3])
        else:
                proy=viatico[3]
        
        self.preparandojson.append({
                "ci":viatico[4],
                "NombreCompleto":'%s %s %s'%(viatico[5],viatico[6],viatico[7]),
                "id":viatico[15],
                "pasaje": viatico[8],
                "peaje": viatico[9],
                "importe": viatico[10],
                "rciva": viatico[11],
                "liqpagable": viatico[12],
                "liqtotalcancelar": viatico[13],
                "ue":ue,
                "prog":prog,
                "act":act,
                "proy":proy,
                "numero":viatico[14]
        })
class BusquedaView(base_View):
    context={}
    via=[]
    def LlenarViatico(self,valor):
        self.via.append({
                'id':valor[0],
                'nombre':valor[1],
                'apaterno':valor[2],
                'amaterno':valor[3],
                'ci':valor[4],
                'Monto_pagado':valor[5],
                'totalC':valor[6],
                'lugar':valor[7],
                'ncontrol':valor[8],
                'encargado':valor[9],
                'slug':valor[10],
                'cod_u':valor[11],
        }) 
    def valid_space(self,valor):
        ver_espacio=str(valor)
        for i in xrange(len(ver_espacio)):
            if ver_espacio[i] == " ":
                self.error=self.error+'EXISTEN ESPACIOS EN BLANCO '+'\n'           
    def is_Number(self,valor):
        if valor.isdigit() == False:
            self.error=self.error+'INTRODUSCA SOLO NUMEROS '+'\n'
    def apellido_valor(self,valor):
        apellidouno=""
        apellidodos=""
        uno=True
        dos=False
        tres=False
        for i in xrange(len(valor)):            
            if i == (len(valor)-1) and valor[(len(valor)-1)] == " ":
                tres=True
                break
            if valor[i] != " ":
                if uno:
                        apellidouno =apellidouno+valor[i]
                if dos:
                        apellidodos =apellidodos+valor[i]
            else:
                dos=True
                uno=False
        if tres:
            self.error=self.error+'EXISTEN ESPACIOS EN BLANCO '+'\n'
        if len(apellidouno) != 0 and len(apellidodos) !=0:
            
            if apellidouno.isalpha() == False and apellidodos.isalpha() == False:
                self.error=self.error+'INTRODUSCA SOLO LETRAS, NADA DE NUMEROS '+'\n'
    def is_String(self,valor):
        if valor.isalpha() == False:
            self.error=self.error+'INTRODUSCA SOLO LETRAS '+'\n'
      