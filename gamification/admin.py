from django.contrib import admin
from .models import Pontos, Nivel, Badge, Ranking, UsuarioRecompensa, Recompensa


@admin.register(Pontos)
class PontosAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'saldo', 'total_acumulado']
    search_fields = ['usuario__nome', 'usuario__email']
    readonly_fields = ['total_acumulado', 'criado_em', 'atualizado_em']
    fieldsets = (
        ('Usuário', {
            'fields': ('usuario',)
        }),
        ('Pontos', {
            'fields': ('saldo', 'total_acumulado')
        }),
        ('Datas', {
            'fields': ('criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Nivel)
class NivelAdmin(admin.ModelAdmin):
    list_display = ['numero', 'nome', 'pontos_minimos']
    search_fields = ['nome']
    ordering = ['numero']
    fieldsets = (
        ('Informações', {
            'fields': ('numero', 'nome', 'descricao')
        }),
        ('Requisitos', {
            'fields': ('pontos_minimos',)
        }),
        ('Benefícios', {
            'fields': ('beneficios',)
        }),
    )


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ['nome', 'categoria', 'pontos_recompensa']
    search_fields = ['nome', 'descricao']
    list_filter = ['categoria']
    fieldsets = (
        ('Informações', {
            'fields': ('nome', 'descricao', 'icone')
        }),
        ('Classificação', {
            'fields': ('categoria',)
        }),
        ('Recompensa', {
            'fields': ('pontos_recompensa',)
        }),
    )


@admin.register(Ranking)
class RankingAdmin(admin.ModelAdmin):
    list_display = ['tipo', 'posicao', 'usuario', 'pontos']
    search_fields = ['usuario__nome', 'usuario__email']
    list_filter = ['tipo', 'mes']
    readonly_fields = ['atualizado_em']
    ordering = ['tipo', 'posicao']


@admin.register(UsuarioRecompensa)
class UsuarioRecompensaAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'badge', 'data_desbloqueio']
    search_fields = ['usuario__nome', 'badge__nome']
    list_filter = ['badge', 'data_desbloqueio']
    readonly_fields = ['data_desbloqueio']


@admin.register(Recompensa)
class RecompensaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'tipo', 'descricao']
    search_fields = ['nome', 'tipo']
    list_filter = ['tipo']
