from django.contrib import admin
from .models import Pedido, ItemPedido


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    """Admin para gerenciar Pedidos"""
    list_display = ('id', 'usuario', 'artista', 'status_pedido', 'valor_total', 'data_pedido')
    list_filter = ('status_pedido', 'data_pedido', 'artista')
    search_fields = ('usuario__nome', 'usuario__email', 'artista__nome_artistico')
    readonly_fields = ('id', 'data_pedido', 'data_pagamento', 'data_producao', 'data_impressao', 'data_envio', 'data_conclusao')
    
    fieldsets = (
        ('Informações do Pedido', {
            'fields': ('id', 'usuario', 'artista', 'status_pedido', 'valor_total')
        }),
        ('Datas', {
            'fields': ('data_pedido', 'data_pagamento', 'data_producao', 'data_impressao', 'data_envio', 'data_conclusao'),
            'classes': ('collapse',)
        }),
        ('Pagamento', {
            'fields': ('forma_pagamento', 'status_pagamento'),
            'classes': ('collapse',)
        }),
        ('Produção', {
            'fields': ('impressora',),
            'classes': ('collapse',)
        }),
    )


@admin.register(ItemPedido)
class ItemPedidoAdmin(admin.ModelAdmin):
    """Admin para gerenciar Itens de Pedido"""
    list_display = ('id', 'pedido', 'produto', 'quantidade', 'preco_unitario', 'subtotal')
    search_fields = ('pedido__id', 'produto__nome')
    list_filter = ('produto', 'criado_em')
    readonly_fields = ('subtotal', 'criado_em', 'atualizado_em')