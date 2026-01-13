from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone


class Pedido(models.Model):
    STATUS_CHOICES = [
        ('criado', 'Criado'),
        ('pago', 'Pago'),
        ('em_producao', 'Em Produção'),
        ('finalizado', 'Finalizado'),
        ('cancelado', 'Cancelado'),
    ]
    
    FORMA_PAGAMENTO_CHOICES = [
        ('cartao_credito', 'Cartão de Crédito'),
        ('cartao_debito', 'Cartão de Débito'),
        ('pix', 'PIX'),
        ('boleto', 'Boleto'),
    ]
    
    id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey('users.User', on_delete=models.PROTECT, related_name='pedidos')
    status_pedido = models.CharField(max_length=20, choices=STATUS_CHOICES, default='criado')
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    data_pedido = models.DateTimeField(auto_now_add=True)
    forma_pagamento = models.CharField(max_length=20, choices=FORMA_PAGAMENTO_CHOICES, null=True, blank=True)
    status_pagamento = models.CharField(max_length=20, null=True, blank=True)
    impressora = models.ForeignKey('printing.Impressora', on_delete=models.SET_NULL, null=True, blank=True, related_name='pedidos')
    
    class Meta:
        ordering = ['-data_pedido']
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
    
    def __str__(self):
        return f"Pedido #{self.id} - {self.usuario} - {self.status_pedido}"


class ItemPedido(models.Model):
    id = models.AutoField(primary_key=True)
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey('products.Produto', on_delete=models.PROTECT, related_name='itens_pedido')
    personalizacao = models.ForeignKey('creations.Personalizacao', on_delete=models.PROTECT, related_name='itens_pedido')
    quantidade = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    
    class Meta:
        verbose_name = 'Item do Pedido'
        verbose_name_plural = 'Itens do Pedido'
    
    def __str__(self):
        return f"Item #{self.id} - Pedido #{self.pedido.id}"
