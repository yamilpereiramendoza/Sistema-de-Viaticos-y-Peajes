from django.conf.urls import url
from . import views

from .views import ViaticoCreateView,ViativoUpdateView,encomisionView,DetailViaticoView,Reporte_saldoView,buscar_Viaticos_View,Reporte_Excel_ViaView,ReportCentralizador,ReporteViaticos,ReporteViaticosEmpTres,ReporteViaticosEmp,ReporteViaticosBiseTri,ListViewReport_emp,ReporteViatico,ListViewReport_mes,BusquedaEmp_View,BusquedaVia_View,CentralizadorView,Reporte_Centralizador,Reporte_Centralizador_Secre,ViaticoDeleteView,BuscarSaldoView,ViaticoListView,Reporte_Excel_Via_Todo_View
from django.contrib.auth.decorators import login_required


urlpatterns = [
    
    url(r'^$',login_required(ViaticoListView.as_view()),name='detail'),
    # fin de sistema de registro de usuarios

    url(r'^editar/(?P<slug>[\w-]+)/$',login_required(ViativoUpdateView.as_view()),name='modiviaticoclass'),
    
    url(r'^buscarviaticos/$',login_required(BusquedaVia_View.as_view()),name="buscar_registro"),
    url(r'^buscarservidorpublico/$',login_required(BusquedaEmp_View.as_view()),name="buscarr_empleado"),

    url(r'^borrar/(?P<slug>[\w-]+)/$',login_required(ViaticoDeleteView.as_view()),name='borrarviatico'),
    url(r'^detalle/(?P<slug>[-\w]+)/$',login_required(DetailViaticoView.as_view()),name="detalle_viatico"),

    url(r'^excelviatico/$',login_required(Reporte_Excel_ViaView.as_view()),name='excel'),
    url(r'^exceltodoviatico/$',login_required(Reporte_Excel_Via_Todo_View.as_view()),name='exceltodo'),
    
   #centralizador    
    url(r'^centralizador/$',login_required(CentralizadorView.as_view()),name='centralizador'), 

    url(r'^centralizadorexcel/$',login_required(Reporte_Centralizador.as_view()),name='centralizadorexcel'),
    url(r'^centralizadorsecretarias/(?P<slug>[-\w]+)/$',login_required(Reporte_Centralizador_Secre.as_view()),name='centralizadorsecretarias'),
    
    url(r'^centralizadorpdf/$',login_required(ReportCentralizador.as_view()),name='centralizadorpdf'),
    url(r'^saldosecretaria/$',login_required(BuscarSaldoView.as_view()),name='buscar_saldo'),
    url(r'^reportesaldocentralizador/$',login_required(Reporte_saldoView.as_view()),name='Reporte_saldoView'),
    url(r'^buscarSecre/$',login_required(views.buscarSecre),name='buscarSecre'),
    #viaticos

    url(r'^buscar_lugares/$',login_required(views.buscar_paices)),
    
    url(r'^comision/$',login_required(encomisionView.as_view()),name='encomision'), 
    
    url(r'^buscar_montos/$',login_required(views.getMontos)),
    url(r'^buscarusuario/$',login_required(views.busqueda),name='buscaruser'),
    url(r'^reporteviatico/$',login_required(ReporteViatico.as_view()),name='ReporteViatico'),

    #reportes viaticos

    url(r'^reporteviaticos/$',login_required(ListViewReport_mes.as_view()),name='reportes_mesClases'),
    url(r'^reporteservidorpublico/$',login_required(ListViewReport_emp.as_view()),name='reporte_empClases'),

    url(r'^listareporteviaticos/(?P<slug>[-\w]+)/(?P<slugu>[-\w]+)/(?P<sluguh>[-\w]+)/$',login_required(ReporteViaticos.as_view()),name='ReporteViaticospdf'),
    url(r'^ReporteViaticosBiseTri/(?P<slug>[-\w]+)/$',login_required(ReporteViaticosBiseTri.as_view()),name='ReporteViaticosBiseTri'),
    

    url(r'^ReporteViaticosEmp/(?P<slug>[-\w]+)/(?P<slugu>[-\w]+)/$',login_required(ReporteViaticosEmp.as_view()),name='ReporteViaticosEmppdf'),
    url(r'^ReporteViaticosEmpTres/(?P<slug>[-\w]+)/(?P<slugu>[-\w]+)/(?P<sluguh>[-\w]+)/$',login_required(ReporteViaticosEmpTres.as_view()),name='ReporteViaticosEmpTrespdf'),
    # admin
    url(r'^registroviatico/$',login_required(ViaticoCreateView.as_view()),name='SolicitudCreate'),
    
    url(r'^buscar_posicion/$',login_required(views.getPosicion)),
    
]
handler404 = 'viaticos.views.handler404'
handler500 = 'viaticos.views.handler500'
