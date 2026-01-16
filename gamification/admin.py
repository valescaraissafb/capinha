from django.contrib import admin
from .models import Recompensa, UsuarioRecompensa


@admin.register(Recompensa)
class RecompensaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'tipo', 'descricao']
    search_fields = ['nome', 'tipo']
    list_filter = ['tipo']


@admin.register(UsuarioRecompensa)
class UsuarioRecompensaAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'recompensa', 'data_recompensa']
    search_fields = ['usuario__username', 'recompensa__nome']
    list_filter = ['data_recompensa', 'recompensa']
    readonly_fields = ['data_recompensa']
