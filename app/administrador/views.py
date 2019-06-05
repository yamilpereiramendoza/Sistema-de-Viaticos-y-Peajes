# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.views.generic import TemplateView,CreateView,DeleteView,UpdateView,View
from app.viaticos.models import Monto,SecresubSecre,DescripcionSecre,Tipo_viatico
from django.shortcuts import render,redirect,get_object_or_404
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import permission_required
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect,HttpResponse
from .forms import SecretariasForm,DescripcionForm,MontoForm,TipoForm

# Create your views here.
#permission_required('administrador.add_monto')
@method_decorator(permission_required('viaticos.add_secresubsecre'),name='dispatch')
@method_decorator(permission_required('viaticos.add_descripcionsecre'),name='dispatch')
class CrearSecretarias(CreateView):
    model = SecresubSecre
    model2 = DescripcionSecre
    template_name = 'admin/templates/crear_secretarias.html'
    form_class = SecretariasForm
    second_form_class = DescripcionForm
    success_url = reverse_lazy('administrador:list_secre')

    def get_context_data(self, **kwargs):
        context = super(CrearSecretarias, self).get_context_data(**kwargs)
        if 'form' not in context:
            context['form'] = self.form_class(self.request.GET)
        if 'form2' not in context:
            context['form2'] = self.second_form_class(self.request.GET)    

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object
        form = self.form_class(request.POST)
        form2 = self.second_form_class(request.POST)
        if form.is_valid() and form2.is_valid():
            secre = form.save(commit=False)
            secre.descripcion = form2.save()
            secre.save()
            messages.success(request, 'Se creo correctamente')
            return HttpResponseRedirect(self.get_success_url())
            
        else:
            return self.render_to_response(self.get_context_data(form=form,form2=form2))
@method_decorator(permission_required('viaticos.change_secresubsecre'),name='dispatch')
@method_decorator(permission_required('viaticos.change_descripcionsecre'),name='dispatch')
class UpdateSecretariaView(UpdateView):
    model = SecresubSecre
    second_model = DescripcionSecre
    template_name = 'admin/templates/crear_secretarias.html'
    form_class = SecretariasForm
    second_form_class = DescripcionForm
    success_url = reverse_lazy('administrador:list_secre')

    def get_context_data(self, **kwargs):
        context = super(UpdateSecretariaView, self).get_context_data(**kwargs)
        pk = self.kwargs.get('pk', 0)
        secre = self.model.objects.get(id=pk)
        descriSecre = self.second_model.objects.get(id=secre.descripcion_id)
        if 'form' not in context:
            context['form'] = self.form_class()
        if 'form2' not in context:
            context['form2'] = self.second_form_class(instance=descriSecre)
        context['id'] = pk
        context['update']=True
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object
        pk = kwargs['pk']
   
        secre = self.model.objects.get(id=pk)
        descriSecre = self.second_model.objects.get(id=secre.descripcion_id)
        form = self.form_class(request.POST, instance=secre)
        form2 = self.second_form_class(request.POST, instance=descriSecre)
        if form.is_valid() and form2.is_valid():
            messages.success(request, 'Se actualizo correctamente la Secretaria')
            form.save()
            form2.save()
            return HttpResponseRedirect(self.get_success_url())
        else:
			return HttpResponseRedirect(self.get_success_url())
@method_decorator(permission_required('viaticos.delete_secresubsecre'),name='dispatch')
@method_decorator(permission_required('viaticos.delete_descripcionsecre'),name='dispatch')
class DeleteSecretariasView(DeleteView):
    model=SecresubSecre
    template_name = 'admin/templates/secresubsecre_confirm_delete.html'
    
    def delete(self, request, *args, **kwargs):     
        messages.success(request, 'Se elimino correctamente la Secretaria')
        tipo=get_object_or_404(self.model, id=self.kwargs.get("pk"))
        tipo.delete()
        return redirect('administrador:list_secre')
class listSecreView(TemplateView):
    template_name = 'admin/list_secre.html'
    model=SecresubSecre
    def get_context_data(self, **kwargs):
        context = super(listSecreView, self).get_context_data(**kwargs)                
        secreta=self.model.objects.all()
        context['secre']=secreta
        return context

@method_decorator(permission_required('viaticos.change_monto'),name='dispatch')
class UpdateMontoView(UpdateView):
    form_class = MontoForm
    model = Monto
    template_name = 'admin/templates/crear_montos.html'
    success_url = reverse_lazy('administrador:list_monto')
    
    def get_context_data(self, **kwargs):
        context = super(UpdateMontoView, self).get_context_data(**kwargs)
        pk = self.kwargs.get('pk', 0)
        tipo = self.model.objects.get(id=pk)
        if 'form' not in context:
            context['form'] = self.form_class(instance=tipo)
        context['id'] = pk
        context['update'] = True
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object
        id_solicitud = kwargs['pk']
        solicitud = self.model.objects.get(id=id_solicitud)
        form = self.form_class(request.POST, instance=solicitud)
        if form.is_valid():
            messages.success(request, 'Se actualizo correctamente el Monto')
            form.save()
            return HttpResponseRedirect(self.get_success_url())
        else:
            return HttpResponseRedirect(self.get_success_url())
@method_decorator(permission_required('viaticos.add_monto'),name='dispatch')
class CreaMontos(CreateView):
    model = Monto
    template_name = 'admin/templates/crear_montos.html'
    form_class = MontoForm
    success_url = reverse_lazy('administrador:list_monto')
    
    def get_context_data(self, **kwargs):
        context = super(CreaMontos, self).get_context_data(**kwargs)
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
            return self.render_to_response(self.get_context_data(form=form))
@method_decorator(permission_required('viaticos.Ver_list_monto'),name='dispatch')
class BuscarCostoView(TemplateView):
    template_name = 'admin/list_mont.html'
    model=Monto
    
    def get_context_data(self, **kwargs):
        context = super(BuscarCostoView, self).get_context_data(**kwargs)                
        mon=self.model.objects.all()
        context['mon']=mon
        return context
@method_decorator(permission_required('viaticos.delete_monto'),name='dispatch')
class DeleteMontosView(DeleteView):
    model=Monto
    template_name = 'admin/templates/monto_confirm_delete.html'
    def delete(self, request, *args, **kwargs):     
        messages.success(request, 'Se elimino correctamente el Monto')
        mont=get_object_or_404(self.model, id=self.kwargs.get("pk"))
        mont.delete()
        return redirect('administrador:list_monto')
class Invalidar(View):
    model=Monto
    def cargarDatos(self):
        return self.model.objects.all()    
    def get(self,request,*args,**kwargs):
        Montos=self.model.objects.filter(id=self.kwargs.get("pk"))                
        for mon in Montos:            
            mon.valido=0
            mon.save()    
        messages.success(request, 'Se Inavilito correctamente el Monto')                           
        context={
            'mon':self.cargarDatos(),
        }                                                           
        return render(request,"admin/list_mont.html",context)
class Validar(View):
    model=Monto
    def cargarDatos(self):
        return self.model.objects.all()    
    def get(self,request,*args,**kwargs):
        Montos=self.model.objects.filter(id=self.kwargs.get("pk"))                
        for mon in Montos:            
            mon.valido=1
            mon.save()    
        messages.success(request, 'Se Volvio a validar correctamente el Monto')                           
        context={
            'mon':self.cargarDatos(),
        }                                                           
        return render(request,"admin/list_mont.html",context)

@method_decorator(permission_required('viaticos.add_tipo_viatico'),name='dispatch')
class CreaTipoViajante(CreateView):
    model = Tipo_viatico
    template_name = 'admin/templates/crear_tipo_viajante.html'
    form_class = TipoForm
    success_url = reverse_lazy('administrador:crear_tipo')
    def get_context_data(self, **kwargs):
        context = super(CreaTipoViajante, self).get_context_data(**kwargs)
        if 'form' not in context:
            context['form'] = self.form_class(self.request.GET)              
        return context
    def post(self, request, *args, **kwargs):
        self.object = self.get_object
        form = self.form_class(request.POST)
        if form.is_valid():
            secre = form.save(commit=False)
            secre.save()
            messages.success(request, 'Se creo correctamente el Tipo Viajante')
            return HttpResponseRedirect(self.get_success_url())            
        else:
            return self.render_to_response(self.get_context_data(form=form))
@method_decorator(permission_required('viaticos.Ver_list_tipo_viatico'),name='dispatch')
class listTipoView(TemplateView):
    template_name = 'admin/registro_tipo.html'
    model=Tipo_viatico
    def get_context_data(self, **kwargs):
        context = super(listTipoView, self).get_context_data(**kwargs)                
        secreta=self.model.objects.all()
        context['tipo']=secreta
        return context
@method_decorator(permission_required('viaticos.change_tipo_viatico'),name='dispatch')
class UpdateTipoView(UpdateView):
    form_class = TipoForm
    model = Tipo_viatico
    template_name = 'admin/templates/crear_tipo_viajante.html'
    success_url = reverse_lazy('administrador:crear_tipo')
    def get_context_data(self, **kwargs):
        context = super(UpdateTipoView, self).get_context_data(**kwargs)
        pk = self.kwargs.get('pk', 0)
        tipo = self.model.objects.get(id=pk)
        if 'form' not in context:
            context['form'] = self.form_class(instance=tipo)
        context['id'] = pk
        context['update']=True
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object
        id_solicitud = kwargs['pk']
        solicitud = self.model.objects.get(id=id_solicitud)
        form = self.form_class(request.POST, instance=solicitud)
        if form.is_valid():
            messages.success(request, 'Se actualizo correctamente el Tipo Viajante')
            form.save()
            return HttpResponseRedirect(self.get_success_url())
        else:
            return HttpResponseRedirect(self.get_success_url())
@method_decorator(permission_required('viaticos.delete_tipo_viatico'),name='dispatch')
class DeleteTipoView(DeleteView):
    model=Tipo_viatico
    template_name = 'admin/templates/tipo_viatico_confirm_delete.html'
    
    def delete(self, request, *args, **kwargs):     
        messages.success(request, 'Se elimino correctamente el Tipo Viajante')
        tipo=get_object_or_404(self.model, id=self.kwargs.get("pk"))
        tipo.delete()
        return redirect('administrador:crear_tipo')




