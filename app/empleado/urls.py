   # sistema de registro nuevos usuarios
from django.conf.urls import url
from . import views
from django.contrib.auth.decorators import login_required
urlpatterns = [    
    url(r'^create_empleado/$',login_required(views.create_empleado),name="create_empleado"),
    url(r'^saveuser/$',login_required(views.saveuser),name="saveuser"),
    url(r'^change_password/$',login_required(views.change_password),name="changepassword"),
    url(r'^list_empleados/$',login_required(views.list_empleados),name="list_empleados"),
    
    url(r'^update_empleado/$',login_required(views.update_empleado),name="update_empleado"),
    url(r'^buscar_secretarias/$',login_required(views.getSecretarias)),

    url(r'^create/$',login_required(views.create),name="create"),
    url(r'^busquedaUsuario/$',login_required(views.busquedaUsuario),name='busquedaUsuario'),
    url(r'^list_user/$',login_required(views.list_user),name="list_user"),
    url(r'^dar_de_baja_usuario/(?P<cent_id>\d+)/$',login_required(views.dar_de_baja_usuario),name="dar_de_baja_usuario"),
    url(r'^dar_de_alta_usuario/(?P<cent_id>\d+)/$',login_required(views.dar_de_alta_usuario),name="dar_de_alta_usuario"),

]