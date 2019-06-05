from django import forms
import datetime
from .models import viaticodiario,OtrosViajes,SecresubSecre
from .validators import validate_ncontrol
STATUS_CHOICES = (
    (False, "Anular"),
    (True, "Valido"),
)
no_ue=[]
no_prog=[]
no_act=[]
no_proy=[]

for item in SecresubSecre.objects.filter(gestion=2018).order_by('ue').values_list("ue",flat = True).distinct():                
    valor=""
    if item < 10:
        valor='%s%s'%(0,item)
    else:
        valor=item
    no_ue.append((item,valor))
for item in SecresubSecre.objects.filter(gestion=2018).order_by('prog').values_list("prog",flat = True).distinct():                
    valor=""
    if item < 10:
        valor='%s%s'%(0,item)
    else:
        valor=item
    no_prog.append((item,valor))
for item in SecresubSecre.objects.filter(gestion=2018).order_by('act').values_list("act",flat = True).distinct():                
    valor=""
    if item < 10:
        valor='%s%s'%(0,item)
    else:
        valor=item
    no_act.append((item,valor))
for item in SecresubSecre.objects.filter(gestion=2018).order_by('proy').values_list("proy",flat = True).distinct():                
    valor=""
    if item < 10:
        valor='%s%s'%(0,item)
    else:
        valor=item
    no_proy.append((item,valor))


#UE_CHOICES = ((name,name) for name in SecresubSecre.objects.filter(gestion=2018).order_by('ue').values_list("ue",flat = True).distinct())

class viaticodiarioFormModificado(forms.ModelForm): 
    pasaje = forms.CharField(required=False,label="Pasaje",widget=forms.TextInput(attrs={'class': 'input form-control'}))
    peaje = forms.CharField(required=False,label="Peaje",widget=forms.TextInput(attrs={'class': 'input form-control'}))
    Extra = forms.CharField(required=False,label="Extra",widget=forms.TextInput(attrs={'class': 'input form-control'}))
    ue = forms.ChoiceField(choices=no_ue, label="U.E.",widget=forms.Select(attrs={'class':'input form-control'}))
    prog = forms.ChoiceField(choices=no_prog, label="PROG.",widget=forms.Select(attrs={'class':'input form-control'}))
    proy = forms.ChoiceField(choices=no_proy, label="PROY.",widget=forms.Select(attrs={'class':'input form-control'}))
    act = forms.ChoiceField(choices=no_act, label="ACT.",widget=forms.Select(attrs={'class':'input form-control'}))
    resolucion = forms.ChoiceField(choices=STATUS_CHOICES, label="Resolucion O Aprobacion:",widget=forms.Select(attrs={'class':'input form-control'}))
    fecha_salida= forms.DateField(required=False, label="Fecha Salida.",widget=forms.DateInput(attrs={'class':'input form-control','type':"date"}))
    fecha_legada= forms.DateField(required=False,label="Fecha Llegada.", widget=forms.DateInput(attrs={'class':'input form-control','type':"date"}))
    horaSalida=forms.TimeField(required=False,label="Hora Salida.",widget=forms.TimeInput(attrs={'class':'input form-control','type':"time"}))
    horallegada=forms.TimeField(required=False,label="Hora Llegada.",widget=forms.TimeInput(attrs={'class':'input form-control','type':"time"}))
    cantidad_dias_fuera_pais = forms.IntegerField(initial=0,label="Dias",min_value=0,widget=forms.NumberInput(attrs={'class': 'input form-control'}))
    ncontrol=forms.CharField(required=False,label="N. De control",widget=forms.TextInput(attrs={'class': 'input form-control'}))
    centralizador=forms.IntegerField(required=False,min_value=0,label="N. De centralizador",widget=forms.NumberInput(attrs={'class': 'input form-control'}))
    lugar = forms.CharField(required=False,label="Lugar",widget=forms.TextInput(attrs={'class': 'input form-control'}))
    class Meta:
        model=viaticodiario
        fields =[
            "id_solicitante",
            "pasaje",
            "peaje",
            "Extra",
            "ue",
            "prog",
            "act",
            "proy",
            "fecha_salida",
            "fecha_legada",
            "horaSalida",
            "horallegada",
            "lugar",
            "ncontrol",
            "obs",
            "monto",
            "tipo_viatico",
            "centralizador",
            "cantidad_dias_fuera_pais",
            "resolucion",
            "cambio_moneda",
        ]
        labels={
            "id_solicitante":'Solicitante',
            "obs":'Observaciones.',
            "monto":'Monto',
            "tipo_viatico":'Tipo Viatico',
            "cambio_moneda":"Bs a $",
        }
        widgets = {
            "id_solicitante":forms.TextInput(attrs={'class':'input form-control'}),            
            "obs":forms.Textarea(attrs={'class':'input form-control','style': 'height: 70px !important; resize: vertical !important;'}),
            "monto":forms.Select(attrs={'class':'monto input form-control'}),
            "tipo_viatico":forms.Select(attrs={'class':'monto input form-control'}),            
            "cambio_moneda":forms.TextInput(attrs={'class':'input form-control'}),
        }
    def buscarComa(self,valor):
        numero=str(valor)
        coma=False   
        for n in xrange(len(numero)):
            if numero[n]==',':
                coma=True
                break
        if coma==True:
            return True
        return False
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

        if self.isNumber(numerouno):
            if self.isNumber(numerodos):
                return False
            return False
        else:
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
        if self.isNumber(numerouno):
            if self.isNumber(numerodos):
                return '%s.%s'%(numerouno,numerodos)                              
    def isDecimal(self,valor):
        if valor.isdecimal() == True:
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
          
    def clean_ncontrol(self):
        date = datetime.date.today()
        ncontrol = self.cleaned_data.get('ncontrol')
        slugcontrol=u'%s-%s'%(ncontrol,date.year)
        numerocontrol = viaticodiario.objects.filter(slug=slugcontrol).exists()
        
        if ncontrol == None:
            raise  forms.ValidationError("Introdusca a un Numero de Control")
        else:            
            if ncontrol<=0:
                raise  forms.ValidationError("El Numero de Control tiene que ser Mayor a 0")
        if str(ncontrol).isdigit():
            if numerocontrol:
                raise  forms.ValidationError("El Numero de Control ya existe")
        else:            
            raise  forms.ValidationError("El Numero de Control tiene que ser Numero Entero")
        
        return ncontrol
    def clean_id_solicitante(self):
        id_solicitante = self.cleaned_data.get('id_solicitante')
        if id_solicitante == None:
            raise  forms.ValidationError("Introdusca a un Empleado")
        return id_solicitante
    def clean_centralizador(self):
        centralizador = self.cleaned_data.get('centralizador')
        if centralizador == None:
            raise  forms.ValidationError("Introdusca a un Numero de Centralizador")
        elif centralizador<=0:
            raise  forms.ValidationError("El Numero de Centralizador tiene que ser Mayor a 0")
        return centralizador
    def clean_tipo_viatico(self):
        tipo_viatico = self.cleaned_data.get('tipo_viatico')
        if tipo_viatico == None:
            raise  forms.ValidationError("Seleccione Tipo de Viatico")
        return tipo_viatico

    def clean(self):
        cleaned_data = super(viaticodiarioFormModificado, self).clean()
        tipo_viatico = cleaned_data.get('tipo_viatico')
        pasaje = self.cleaned_data.get('pasaje')
        peaje = self.cleaned_data.get('peaje')
        Extra = self.cleaned_data.get('Extra')            
        if str(pasaje) != "":            
            if self.isSolo(pasaje)== False: 
                if self.isDouble(self.isConvert(pasaje)):
                    msg = "El Pasaje tiene que ser Numero Entero o Float"
                    self.add_error('pasaje', msg)
                elif self.buscarComa(pasaje):
                    msg = "Introdusca un Pasaje con ( . )"
                    self.add_error('pasaje', msg)
            else:                
                if self.isNumber(pasaje): 
                    msg = "El Pasaje tiene que ser Numero Entero o Float"
                    self.add_error('pasaje', msg)
        if str(peaje) != "":            
            if self.isSolo(peaje)== False: 
                if self.isDouble(self.isConvert(peaje)):
                    msg = "El Peaje tiene que ser Numero Entero o Float"
                    self.add_error('peaje', msg)
                elif self.buscarComa(peaje):
                    msg = "Introdusca un Peaje con ( . )"
                    self.add_error('peaje', msg)
            else:                
                if self.isNumber(peaje): 
                    msg = "El Peaje tiene que ser Numero Entero o Float"
                    self.add_error('peaje', msg)
        if str(Extra) != "":            
            if self.isSolo(Extra)== False: 
                if self.isDouble(self.isConvert(Extra)):
                    msg = "El Extra tiene que ser Numero Entero o Float"
                    self.add_error('Extra', msg)
                elif self.buscarComa(Extra):
                    msg = "Introdusca un Extra con ( . )"
                    self.add_error('Extra', msg)
            else:                
                if self.isNumber(Extra): 
                    msg = "El Extra tiene que ser Numero Entero o Float"
                    self.add_error('Extra', msg)
                
        if len(str(tipo_viatico)) == 16 or len(str(tipo_viatico)) == 10:
            fecha_salida = cleaned_data.get('fecha_salida')
            fecha_legada = cleaned_data.get('fecha_legada')
            horaSalida = cleaned_data.get('horaSalida')
            horallegada = cleaned_data.get('horallegada')
            monto = self.cleaned_data.get('monto')
            lugar = self.cleaned_data.get('lugar')
            if lugar == "":
                msg = "Introdusca un Lugar"
                self.add_error('lugar', msg)
                
            varable=str(monto)            
            if varable[-3:].find("$.") == 1:
                cantidad_dias_fuera_pais = cleaned_data.get('cantidad_dias_fuera_pais')
                cambio_moneda = cleaned_data.get('cambio_moneda')
                if cantidad_dias_fuera_pais == 0:
                    msg = "Introdusca una Cantidad de Dias"
                    self.add_error('cantidad_dias_fuera_pais', msg)
                if cambio_moneda<=0:
                    msg = "El Cambio de Moneda tiene que ser Mayor a 0"
                    self.add_error('cambio_moneda', msg)                    

            if  horaSalida == None and horallegada == None:
                msg = "Introdusca una Hora de llegada y una Hora Salida"
                self.add_error('fecha_legada', msg)
            else:
                if horaSalida == None:
                    msg = "Introdusca una Hora de Salida"
                    self.add_error('horaSalida', msg)                
                if horallegada == None:
                    msg = "Introdusca una Hora de llegada"
                    self.add_error('horallegada', msg)
                    
            if  fecha_salida != None and fecha_legada != None:
                if  fecha_salida == fecha_legada:
                    if horallegada<horaSalida:
                        msg = "Hora de llegada no puede ser menor a la Hora de salida"
                        self.add_error('horallegada', msg)
                date = datetime.date.today()

                if int(fecha_salida.strftime('%Y')) != int(date.year):
                    msg = "La Fecha de Salida tiene que tener ser de "+ str(date.year)
                    self.add_error('fecha_salida', msg)   
                
                if int(fecha_legada.strftime('%Y')) != int(date.year):
                    msg = "La Fecha de Llegada tiene que tener ser de "+ str(date.year)
                    self.add_error('fecha_legada', msg)


            if  fecha_salida == None and fecha_legada == None:
                msg = "Introdusca una Fecha de llegada y una Fecha Salida"
                self.add_error('fecha_legada', msg)
            else:
                if fecha_salida == None:
                    msg = "Introdusca una Fecha de Salida"
                    self.add_error('fecha_salida', msg)
                else:
                    if fecha_legada == None:
                        msg = "Introdusca una Fecha de llegada"
                        self.add_error('fecha_legada', msg)
                    else:
                        if fecha_salida>fecha_legada:
                            if fecha_legada<fecha_salida:                                
                                msg = "Fecha de llegada no puede ser menor a la fecha de salida"
                                self.add_error('fecha_legada', msg)
                            else:
                                msg = "Fecha de Salida no puede ser mayor a la fecha de llegada"
                                self.add_error('fecha_salida', msg)
        return cleaned_data
VIAJANTE = (
    (2, "Servidor Publico"),
    (1, "Gobernador"),
)

class otrosform(forms.ModelForm):
    tipos_viajante=forms.ChoiceField(choices=VIAJANTE, label="Tipo Viajante",widget=forms.Select(attrs={'class':'input form-control'}))
    fecha_inicial_frontera= forms.DateField(required=False,label="Fecha Inicial Frontera", widget=forms.DateInput(attrs={'class':'input form-control','type':"date"}))
    fecha_llegada_frontera= forms.DateField(required=False,label="Fecha Llegada Frontera", widget=forms.DateInput(attrs={'class':'input form-control','type':"date"}))
    fecha_inicial_urbana= forms.DateField(required=False,label="Fecha Inicial Urbana", widget=forms.DateInput(attrs={'class':'input form-control','type':"date"}))
    fecha_llegada_urbana= forms.DateField(required=False,label="Fecha Llegada Urbana", widget=forms.DateInput(attrs={'class':'input form-control','type':"date"}))
    fecha_inicial_rural= forms.DateField(required=False,label="Fecha Inicial Rural", widget=forms.DateInput(attrs={'class':'input form-control','type':"date"}))
    fecha_llegada_rural= forms.DateField(required=False,label="Fecha Llegada Rural", widget=forms.DateInput(attrs={'class':'input form-control','type':"date"}))
    horaSalida_frontera= forms.TimeField(required=False,label="Hora Salida Frontera",widget=forms.TimeInput(attrs={'class':'input form-control','type':"time"}))
    horallegada_frontera= forms.TimeField(required=False,label="Hora Llegada Frontera",widget=forms.TimeInput(attrs={'class':'input form-control','type':"time"}))
    horaSalida_urbana= forms.TimeField(required=False,label="Hora Salida Urbana",widget=forms.TimeInput(attrs={'class':'input form-control','type':"time"}))
    horallegada_urbana= forms.TimeField(required=False,label="Hora Llegada Urbana",widget=forms.TimeInput(attrs={'class':'input form-control','type':"time"}))
    horaSalida_rural= forms.TimeField(required=False,label="Hora Salida Rural",widget=forms.TimeInput(attrs={'class':'input form-control','type':"time"}))
    horallegada_rural= forms.TimeField(required=False,label="Hora Llegada Rural",widget=forms.TimeInput(attrs={'class':'input form-control','type':"time"}))
    class Meta:
        model=OtrosViajes
        fields =[
            "fecha_inicial_frontera",
            "fecha_llegada_frontera",
            "fecha_inicial_urbana",
            "fecha_llegada_urbana",
            "fecha_inicial_rural",
            "fecha_llegada_rural",
            "horaSalida_frontera",
            "horallegada_frontera",
            "horaSalida_urbana",
            "horallegada_urbana",
            "horaSalida_rural",
            "horallegada_rural",
            "lugar_frontera",
            "lugar_urbana",
            "lugar_rural",
            "tipos_viajante",
        ]
        labels={
            "lugar_frontera":"Lugar Frontera",
            "lugar_urbana":"Lugar Urbana",
            "lugar_rural":"Lugar Rural",
            
        }
        widgets = {
            
            "lugar_frontera":forms.TextInput(attrs={'class':'input form-control',"onkeyup": "fAgrega();"}),
            "lugar_urbana":forms.TextInput(attrs={'class':'input form-control',"onkeyup": "fAgrega();"}),
            "lugar_rural":forms.TextInput(attrs={'class':'input form-control',"onkeyup": "fAgrega();"}),
        }