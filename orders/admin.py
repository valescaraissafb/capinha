from django.contrib import admin
from .models import Pedido, ItemPedido

# Register your models here.
@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'status_pedido', 'valor_total', 'data_criacao')
    list_filter = ('status_pedido', 'data_criacao')
    search_fields = ('usuario__username',)

@admin.register(ItemPedido)
class ItemPedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'pedido', 'produto', 'quantidade', 'preco_unitario', 'subtotal')
    search_fields = ('pedido__id', 'produto__nome')
    list_filter = ('produto',)