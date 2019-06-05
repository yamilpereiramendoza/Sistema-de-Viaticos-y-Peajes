
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

def validate_ncontrol(value):    
    if isinstance(value, str):
        print("es entero")
        return value
    raise ValidationError(_('El Numero de Control tiene que ser Numero Entero'))
        