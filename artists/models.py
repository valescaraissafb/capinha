from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator


class Artista(models.Model):
    """
    Modelo de Artista - Especialização do usuário.
    Define um usuário como criador de conteúdo.
    """
    STATUS_APROVACAO = [
        ('pendente', 'Pendente Aprovação'),
        ('aprovado', 'Aprovado'),
        ('bloqueado', 'Bloqueado'),
    ]
    
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='perfil_artista'
    )

    nome_artistico = models.CharField(max_length=150)
    biografia = models.TextField(blank=True)
    instagram = models.URLField(blank=True)
    portfolio_url = models.URLField(blank=True)
    
    # Status
    ativo = models.BooleanField(default=True)
    status_aprovacao = models.CharField(
        max_length=20, 
        choices=STATUS_APROVACAO, 
        default='pendente',
        help_text="Status de aprovação da plataforma"
    )
    
    # Métricas
    total_vendas = models.PositiveIntegerField(
        default=0, 
        validators=[MinValueValidator(0)],
        help_text="Total de itens vendidos"
    )
    total_pedidos = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Total de pedidos processados"
    )
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=5.00,
        validators=[MinValueValidator(0), MinValueValidator(5)],
        help_text="Avaliação média (0-5)"
    )
    total_avaliacoes = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )
    
    criado_em = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Artista"
        verbose_name_plural = "Artistas"
        ordering = ['-total_vendas']

    def __str__(self):
        return self.nome_artistico

    def pode_vender(self):
        """Verifica se artista está ativo e aprovado"""
        return self.ativo and self.status_aprovacao == 'aprovado'


class ContaBancariaArtista(models.Model):
    """
    Dados bancários para pagamento de artistas.
    """
    artista = models.OneToOneField(
        Artista,
        on_delete=models.CASCADE,
        related_name='conta_bancaria'
    )

    banco = models.CharField(max_length=100)
    agencia = models.CharField(max_length=20)
    conta = models.CharField(max_length=30)
    tipo_conta = models.CharField(
        max_length=20,
        choices=[
            ('corrente', 'Corrente'),
            ('poupanca', 'Poupança')
        ]
    )
    
    criado_em = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Conta Bancária do Artista"
        verbose_name_plural = "Contas Bancárias dos Artistas"

    def __str__(self):
        return f'{self.artista.nome_artistico} - {self.banco}'
