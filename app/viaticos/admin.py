# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from . import models
# Register your models here.

admin.site.register(models.Monto)
admin.site.register(models.Tipo_viatico)
admin.site.register(models.viaticodiario)
admin.site.register(models.SecresubSecre)