from django import forms
from app.viaticos.models import SecresubSecre,DescripcionSecre,Monto,Tipo_viatico
from datetime import datetime
date = datetime.now()
gestion_lis=(
    ("", "Seleccione"),
    ("" + str(date.year-1) + "", "" + str(date.year-1) + ""),
    ("" + str(date.year) + "", "" + str(date.year) + ""),
    ("" + str(date.year+1) + "", "" + str(date.year+1) + ""),
)

class SecretariasForm(forms.ModelForm):
    gestion=forms.ChoiceField(choices=gestion_lis,widget=forms.Select(attrs={'class': 'form-control'}))
    class Meta:  
        model=SecresubSecre
        fields =[
            "ue",
            "prog",
            "proy",
            "act",
            "gestion",
        ]
        labels={
            "ue":"ue",
            "prog":"prog",
            "proy":"proy",
            "act":"act",
            "gestion":"gestion",
        }
        widgets = {
            "ue":forms.NumberInput(attrs={'class':'input form-control','autocomplete':'off'}),
            "prog":forms.NumberInput(attrs={'class':'input form-control','autocomplete':'off'}),
            "proy":forms.NumberInput(attrs={'class':'input form-control','autocomplete':'off'}),
            "act":forms.NumberInput(attrs={'class':'input form-control','autocomplete':'off'}), 
        }
class DescripcionForm(forms.ModelForm):
    class Meta: 
        model=DescripcionSecre
        fields =[
            "descripcion",
        ]
        labels={
            "descripcion":"descripcion",
        }
        widgets = {

            "descripcion":forms.Textarea(attrs={'class':'input form-control'}),
            
        }

identificacion_lis=(
    ("", "Seleccione.."),
    ("1", "Dentro del Pais"),
    ("2", "Fuera del pais"),
)

class MontoForm(forms.ModelForm):
    identificacion=forms.ChoiceField(choices=identificacion_lis,widget=forms.Select(attrs={'class': 'form-control'}))
    class Meta:  
        model=Monto
        fields =[
            "Nombre",
            "Cantidad",
            "identificacion", 
            "Tipo_viatico",           
        ]
        labels={
            "Nombre":"Nombre",
            "Cantidad":"Cantidad",
            "identificacion":"identificacion",  
            "Tipo_viatico":"Tipo_viatico",          
        }
        widgets = {
            "Nombre":forms.TextInput(attrs={'class':'input form-control','autocomplete':'off'}),
            "Cantidad":forms.NumberInput(attrs={'class':'input form-control','autocomplete':'off'}),
            "identificacion":forms.NumberInput(attrs={'class':'input form-control','autocomplete':'off'}), 
            "Tipo_viatico":forms.Select(attrs={'class':'input form-control'}),
        }

class TipoForm(forms.ModelForm):
    class Meta: 
        model=Tipo_viatico
        fields =[
            "Tipo_Viajante",
        ]
        labels={
            "Tipo_Viajante":"Tipo_Viajante",
        }
        widgets = {

            "Tipo_Viajante":forms.TextInput(attrs={'class':'input form-control'}),
            
        }
