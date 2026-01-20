from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator


class Pontos(models.Model):
    """
    Sistema de Pontos - Gamificação do usuário.
    Rastreia pontos acumulados por usuários e artistas.
    """
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='pontos'
    )
    saldo = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    total_acumulado = models.PositiveIntegerField(default=0)
    
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Pontos"
        verbose_name_plural = "Pontos"

    def __str__(self):
        return f"Pontos - {self.usuario.nome} ({self.saldo})"


class Nivel(models.Model):
    """
    Níveis de Usuário - Define hierarquia e conquistas.
    """
    NIVEL_CHOICES = [
        (1, 'Bronze'),
        (2, 'Prata'),
        (3, 'Ouro'),
        (4, 'Platina'),
        (5, 'Diamante'),
    ]
    
    numero = models.PositiveIntegerField(choices=NIVEL_CHOICES, unique=True)
    nome = models.CharField(max_length=50)
    descricao = models.TextField(blank=True)
    pontos_minimos = models.PositiveIntegerField(
        help_text="Pontos mínimos necessários para alcançar este nível"
    )
    beneficios = models.TextField(blank=True, help_text="Benefícios do nível")
    
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Nível"
        verbose_name_plural = "Níveis"
        ordering = ['numero']

    def __str__(self):
        return f"Nível {self.numero} - {self.nome}"


class Badge(models.Model):
    """
    Badges/Medalhas - Conquistas desbloqueáveis.
    """
    CATEGORIA_CHOICES = [
        ('compras', 'Compras'),
        ('criacao', 'Criação'),
        ('pagamento', 'Pagamento'),
        ('participacao', 'Participação'),
        ('performance', 'Performance'),
    ]
    
    nome = models.CharField(max_length=100)
    descricao = models.TextField()
    icone = models.ImageField(upload_to='badges/', blank=True, null=True)
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES)
    pontos_recompensa = models.PositiveIntegerField(default=10)
    
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Badge"
        verbose_name_plural = "Badges"

    def __str__(self):
        return self.nome


class Ranking(models.Model):
    """
    Ranking de Usuários e Artistas.
    Atualizado baseado em pontos, vendas ou performance.
    """
    TIPO_RANKING = [
        ('usuarios', 'Usuários'),
        ('artistas', 'Artistas'),
    ]
    
    tipo = models.CharField(max_length=20, choices=TIPO_RANKING)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='rankings'
    )
    posicao = models.PositiveIntegerField()
    pontos = models.PositiveIntegerField(default=0)
    
    mes = models.CharField(max_length=7, blank=True, help_text="YYYY-MM para rankings mensais")
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Ranking"
        verbose_name_plural = "Rankings"
        ordering = ['tipo', 'posicao']
        unique_together = ('tipo', 'usuario', 'mes')

    def __str__(self):
        return f"Ranking {self.tipo} - {self.usuario.nome} (#{self.posicao})"


class UsuarioRecompensa(models.Model):
    """
    Recompensas desbloqueadas por usuário.
    """
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recompensas_desbloqueadas'
    )
    badge = models.ForeignKey(
        Badge,
        on_delete=models.CASCADE,
        related_name='usuarios',
        null=True,
        blank=True
    )
    data_desbloqueio = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        verbose_name = "Recompensa do Usuário"
        verbose_name_plural = "Recompensas do Usuário"
        unique_together = ('usuario', 'badge')

    def __str__(self):
        return f"{self.usuario.nome} - {self.badge.nome}"


class Recompensa(models.Model):
    """
    Recompensas genéricas do sistema (LEGADO - considerar deprecar).
    """
    nome = models.CharField(max_length=100)
    descricao = models.TextField()
    tipo = models.CharField(max_length=50)

    def __str__(self):
        return self.nome
