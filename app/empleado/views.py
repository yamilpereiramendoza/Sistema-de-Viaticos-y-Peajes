# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from .models import Secretaria,empleado
from django.core import serializers
from django.http import HttpResponse,JsonResponse
from datetime import datetime,date
from django.contrib import messages
from .forms import EmpleadoForm
from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import View,TemplateView,DetailView,DeleteView,CreateView
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect,HttpResponse
'''def staff_required(login_url=None):
    return user_passes_test(lambda u: u.is_staff, login_url=login_url)


@staff_required(login_url="../admin")'''



# Create your views here.
def create(request):
    if request.method == "POST":
        nombre=request.POST['nombre']
        apellido='%s %s'%(request.POST['apellidoP'],request.POST['apellidoM'])
        fecharegistro=request.POST['fecharegistro']
        user=User.objects.create_user(username=request.POST['username'],password=request.POST['password'])    
        user.first_name=nombre
        user.last_name=apellido
        user.date_joined=fecharegistro
        user.is_staff=False
        user.is_active=True
        user.is_superuser=False
        user.save()
        return redirect('empleados:list_user')
    return render(request,"usuarios/create.html",{})
def busquedaUsuario(request):
        if request.is_ajax():
            if request.GET['id'].isdigit() == False:                
                response=JsonResponse({'error': 500})
            else:             
                consult=empleado.objects.filter(ci=request.GET['id'])
                if consult.exists():
                        user=empleado.objects.get(ci=request.GET['id'])
                        response=JsonResponse({
                                'id': user.id,
                                'nombre':user.nombre,
                                'paterno':user.apaterno,
                                'materno':user.amaterno,
                                'fecha':user.fechaReg,                                   
                                'error': 200,
                        })                
                else:
                        response=JsonResponse({'error': 403})
            return HttpResponse(response.content)
        else:
                return HttpResponse("Solo Ajax") 

def list_user(request):
    usuario=User.objects.filter(is_superuser=False)
    context={
        'usuario':usuario
    }
    return render(request,"usuarios/list_user.html",context)    

def getSecretarias(request):
    id_secre = int(request.GET['id'])
    secre=Secretaria.objects.filter(numeroS=id_secre)    
    if secre:
        data=serializers.serialize('json',secre,fields=('nombreS'))
        return HttpResponse(data,content_type="application/json")

'''class CreateEmpleados(CreateView):
    model = empleado
    template_name = 'admin/Tipo_de_Viaje.html'
    form_class = EmpleadoForm
    success_url = reverse_lazy('administrador:registro_montos')
    
    def get_context_data(self, **kwargs):
        context = super(CreateEmpleados, self).get_context_data(**kwargs)
        if 'form' not in context:
            context['form'] = self.form_class(self.request.GET)        
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object
        form = self.form_class(request.POST)
        if form.is_valid():
            secre = form.save(commit=False)
            secre.valido=1
            secre.save()
            messages.success(request, 'Se creo correctamente el Monto')
            return HttpResponseRedirect(self.get_success_url())            
        else:
            return self.render_to_response(self.get_context_data(form=form))'''

def create_empleado(request):
    if request.method == "POST":
        form=EmpleadoForm(request.POST or None)
        if form.is_valid():
            empleado = form.save(commit=False)
            usuario=get_object_or_404(User,id=request.user.id)
            empleado.cod_usu=usuario.id
            date = datetime.now()
            empleado.fechaReg=datetime.strptime(('%s/%s/%s'%(date.day,date.month,date.year)), '%d/%m/%Y')
            empleado.save()
            messages.success(request, 'Se creo correctamente el Empleado')
            return redirect('empleados:create_empleado')
        else:
            messages.success(request, 'Se no creo el Empleado')
    else:
        form=EmpleadoForm()
    context={
        'form':form,
    }
    return render(request,"empleado/register.html",context)
def dar_de_alta_usuario(request,cent_id):
    user = User.objects.get(id=cent_id)
    user.is_active =True
    user.save()
    #print(cent_id)
    return redirect('empleados:list_user')
def dar_de_baja_usuario(request,cent_id):
    user = User.objects.get(id=cent_id)
    user.is_active =False
    user.save()
    print(cent_id)
    return redirect('empleados:list_user')

def saveuser(request):
    if request.method == "POST":
        form=EmpleadoForm(request.POST or None)
        #print(form)
        if form.is_valid():
            emple = form.save(commit=False)
            nuevoempleado=empleado.objects.filter(ci=emple.ci)
            for obj in nuevoempleado:
                obj.nombre =emple.nombre
                obj.apaterno =emple.apaterno
                obj.amaterno =emple.amaterno
                obj.ci =emple.ci
                obj.bcontrol=emple.bcontrol
                obj.ue=emple.ue
                obj.secretaria=emple.secretaria
                obj.save()
            messages.success(request, 'Se Actualizo correctamente el Empleado')
            return redirect('empleados:update_empleado')
    return render(request,"empleado/editar_empleado.html",{})
    #return HttpResponse("hola")}
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST or None)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Cambio su Contrseña!')
            return redirect('accounts:change_password')
            #return redirect('change_password')
        else:
            messages.error(request, 'Error al realizar el cambio de contraseña')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'empleado/change_password.html', {'form': form})
    #return render(request,"empleado/changepassword.html",{})
def list_empleados(request):
    emplead=empleado.objects.all().order_by('-fechaReg')
    paginator = Paginator(emplead, 25)
    page = request.GET.get('page')
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:        
        contacts = paginator.page(1)
    except EmptyPage:        
        contacts = paginator.page(paginator.num_pages)
    context={
        'usuario':contacts,
    }
    return render(request,"empleado/list_empleados.html",context)
def update_empleado(request):
    if request.method == "GET":
        if 'user_id' in request.GET  :
            if request.GET['user_id']:
                buscar=empleado.objects.filter(ci=request.GET['user_id'])
                if buscar.exists():
                    empleados=get_object_or_404(empleado,ci=request.GET['user_id'])
                    return render(request,"empleado/saveuser.html",{'form':empleados})
                else:
                    error="No existe el Empleado con ese C.I."
                    return render(request,"empleado/editar_empleado.html",{'error':error})
    return render(request,"empleado/editar_empleado.html",{})