from django.conf.urls import url
from . import views
from .views import Validar,CreaTipoViajante,listTipoView,DeleteSecretariasView,UpdateSecretariaView,CrearSecretarias,listSecreView,BuscarCostoView,CreaMontos,DeleteMontosView,DeleteTipoView,UpdateTipoView,UpdateMontoView,Invalidar

from django.contrib.auth.decorators import login_required,permission_required
urlpatterns = [
    url(r'^registro_montos/$',login_required(BuscarCostoView.as_view()),name='registro_montos'),
    url(r'^crear_Secretarias/$',login_required(CrearSecretarias.as_view()), name="crear_secretarias_modal"),
    url(r'^update_Secretarias/(?P<pk>\d+)/$',login_required(UpdateSecretariaView.as_view()), name="update_secretarias_modal"),
    url(r'^delete_Secretarias/(?P<pk>\d+)/$',login_required(DeleteSecretariasView.as_view()),name='delete_Secretarias'),
    url(r'^list_secre/$',login_required(listSecreView.as_view()),name='list_secre'),
    
    url(r'^Listar_tipo/$',login_required(listTipoView.as_view()),name='crear_tipo'),
    url(r'^crear_tipo/$',login_required(CreaTipoViajante.as_view()),name='crear_tipoviajante'),
    url(r'^update_tipo/(?P<pk>\d+)/$',login_required(UpdateTipoView.as_view()),name='update_tipo'),    
    url(r'^eliminar_tipo/(?P<pk>\d+)/$',login_required(DeleteTipoView.as_view()),name='eliminar_tipo'),
    
    url(r'^crear_tipo_monto/$',login_required(CreaMontos.as_view()),name='crear_tipo_monto'),
    url(r'^list_monto/$',login_required(BuscarCostoView.as_view()),name='list_monto'),
    url(r'^eliminar_monto/(?P<pk>\d+)/$',login_required(DeleteMontosView.as_view()),name='eliminar_monto'),
    url(r'^update_monto/(?P<pk>\d+)/$',login_required(UpdateMontoView.as_view()),name='update_monto'),
    url(r'^invalidar_monto/(?P<pk>\d+)/$',login_required(Invalidar.as_view()),name='invalidar_monto'),
    url(r'^validar_monto/(?P<pk>\d+)/$',login_required(Validar.as_view()),name='validar_monto'),



    
]