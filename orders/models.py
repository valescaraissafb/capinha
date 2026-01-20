from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal

class Pedido(models.Model):
    """
    Modelo central de Pedido - O coração transacional do sistema.
    Gerencia todo o fluxo de compra: da criação até a entrega.
    
    Liga todos os outros apps:
    - users: Quem fez o pedido
    - artists: Quem vai produzir
    - products: O que foi comprado
    - creations: Personalizações
    - printing: Impressora usada
    - payments: Status de pagamento
    """
    
    STATUS_CHOICES = [
        ('criado', 'Criado'),
        ('pago', 'Pago'),
        ('em_producao', 'Em Produção'),
        ('impresso', 'Impresso'),
        ('enviado', 'Enviado'),
        ('concluido', 'Concluído'),
        ('cancelado', 'Cancelado'),
    ]
    
    FORMA_PAGAMENTO_CHOICES = [
        ('cartao_credito', 'Cartão de Crédito'),
        ('cartao_debito', 'Cartão de Débito'),
        ('pix', 'PIX'),
        ('boleto', 'Boleto'),
    ]
    
    # Identificadores
    id = models.AutoField(primary_key=True)
    
    # Quem está comprando
    usuario = models.ForeignKey('users.user', on_delete=models.PROTECT, related_name='pedidos')
    
    # Quem vai produzir (artista)
    artista = models.ForeignKey('artists.Artista', on_delete=models.PROTECT, related_name='pedidos_para_produzir', null=True, blank=True)
    
    # Status e controle
    status_pedido = models.CharField(max_length=20, choices=STATUS_CHOICES, default='criado')
    
    # Valores monetários
    valor_total = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'), 
        validators=[MinValueValidator(0)]
    )
    
    # Datas
    data_pedido = models.DateTimeField(auto_now_add=True)
    data_pagamento = models.DateTimeField(null=True, blank=True)
    data_producao = models.DateTimeField(null=True, blank=True)
    data_impressao = models.DateTimeField(null=True, blank=True)
    data_envio = models.DateTimeField(null=True, blank=True)
    data_conclusao = models.DateTimeField(null=True, blank=True)
    
    # Pagamento
    forma_pagamento = models.CharField(max_length=20, choices=FORMA_PAGAMENTO_CHOICES, null=True, blank=True)
    status_pagamento = models.CharField(max_length=20, null=True, blank=True)
    
    # Produção
    impressora = models.ForeignKey('printing.Impressora', on_delete=models.SET_NULL, null=True, blank=True, related_name='pedidos')
    
    class Meta:
        ordering = ['-data_pedido']
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
    
    def __str__(self):
        return f"Pedido #{self.id} - {self.usuario.nome} - {self.status_pedido}"
    
    def pode_adicionar_itens(self):
        """Apenas pedidos em 'criado' podem receber itens"""
        return self.status_pedido == 'criado'
    
    def pode_mudar_status(self, novo_status):
        """Valida transição de status"""
        fluxo_valido = {
            'criado': ['pago', 'cancelado'],
            'pago': ['em_producao', 'cancelado'],
            'em_producao': ['impresso'],
            'impresso': ['enviado'],
            'enviado': ['concluido'],
            'concluido': [],
            'cancelado': [],
        }
        return novo_status in fluxo_valido.get(self.status_pedido, [])



class ItemPedido(models.Model):
    """
    Representa um item dentro do pedido.
    Um pedido pode ter múltiplos itens (produtos com personalizações diferentes).
    """
    id = models.AutoField(primary_key=True)
    
    # Relação com pedido
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='itens')
    
    # O que está sendo comprado
    produto = models.ForeignKey('products.Produto', on_delete=models.PROTECT, related_name='itens_pedido')
    personalizacao = models.ForeignKey('creations.Personalizacao', on_delete=models.PROTECT, related_name='itens_pedido')
    
    # Quantidade e preços
    quantidade = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    
    # Datas
    criado_em = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Item do Pedido'
        verbose_name_plural = 'Itens do Pedido'
        ordering = ['criado_em']
    
    def __str__(self):
        return f"Item #{self.id} - {self.produto.nome} x{self.quantidade}"
