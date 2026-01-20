from django.db import models
from django.core.validators import MinValueValidator


class Impressora(models.Model):
    """
    Equipamento de impressão/produção.
    """
    TIPO_CHOICES = [
        ('uv', 'Impressora UV'),
        ('sublimacao', 'Sublimação'),
        ('serigrafia', 'Serigrafia'),
        ('digital', 'Digital'),
    ]
    STATUS_CHOICES = [
        ('ativo', 'Ativo'),
        ('inativo', 'Inativo'),
        ('manutencao', 'Em Manutenção'),
    ]
    nome = models.CharField(max_length=50)
    tipo = models.CharField(max_length=50, choices=TIPO_CHOICES)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='ativo')
    localizacao = models.CharField(max_length=50, blank=True, null=True)
    fabricante = models.CharField(max_length=50, blank=True, null=True)
    modelo = models.CharField(max_length=50, blank=True, null=True)
    data_aquisicao = models.DateField(blank=True, null=True)
    data_ultima_manutencao = models.DateField(blank=True, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Impressora'
        verbose_name_plural = 'Impressoras'
        ordering = ['nome']
    
    def __str__(self):
        return f"{self.nome} ({self.get_tipo_display()})"


class FilaImpressao(models.Model):
    """
    Fila de impressão - Gerencia a ordem de produção.
    """
    STATUS_CHOICES = [
        ('aguardando', 'Aguardando'),
        ('imprimindo', 'Imprimindo'),
        ('concluido', 'Concluído'),
        ('erro', 'Erro'),
        ('cancelado', 'Cancelado'),
    ]
    
    pedido = models.OneToOneField(
        'orders.Pedido',
        on_delete=models.CASCADE,
        related_name='fila_impressao'
    )
    impressora = models.ForeignKey(
        Impressora,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='filas'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='aguardando'
    )
    prioridade = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Ordem de prioridade na fila (menor = mais prioritário)"
    )
    
    criado_em = models.DateTimeField(auto_now_add=True)
    iniciado_em = models.DateTimeField(null=True, blank=True)
    concluido_em = models.DateTimeField(null=True, blank=True)
    
    observacoes = models.TextField(blank=True, help_text="Notas sobre a impressão")
    
    class Meta:
        verbose_name = "Fila de Impressão"
        verbose_name_plural = "Filas de Impressão"
        ordering = ['-prioridade', 'criado_em']
        indexes = [
            models.Index(fields=['status', 'prioridade']),
            models.Index(fields=['criado_em']),
        ]
    
    def __str__(self):
        return f"Fila #{self.id} - Pedido #{self.pedido.id} - {self.get_status_display()}"
