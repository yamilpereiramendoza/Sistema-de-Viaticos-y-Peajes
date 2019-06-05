from django import forms
from .models import empleado
from app.empleado.models import Secretaria
class EmpleadoForm(forms.ModelForm):
    ue = forms.ModelChoiceField(queryset=Secretaria.objects.values_list('id',flat=True),widget=forms.Select(attrs={'class': 'form-control'}))
    class Meta:
        model=empleado
        fields =[
            "nombre",
            "apaterno",
            "amaterno",
            "ci",
            #"fechaReg",
            "bcontrol",
            "ue",
            "secretaria",
        ]
        labels={
            "nombre":'Nombre',
            "apaterno":'Apellido Paterno',
            "amaterno":'Apellido Materno',
            "ci":"Cedula de identidad",
            #"fechaReg":'',
            "bcontrol":'N control',
            "ue":'Unidad Ejecutora',
            "secretaria":'Secretaria',
        }
        widgets = {
            "nombre":forms.TextInput(attrs={'class':'input form-control'}),
            "apaterno":forms.TextInput(attrs={'class':'input form-control'}),
            "amaterno":forms.TextInput(attrs={'class':'input form-control'}),
            "ci":forms.TextInput(attrs={'class':'input form-control'}),
            "bcontrol":forms.TextInput(attrs={'class':'input form-control'}),
            "ue":forms.Select(attrs={'class':'monto input form-control'}),
            "secretaria":forms.Select(attrs={'class':'monto input form-control'}),
        }
