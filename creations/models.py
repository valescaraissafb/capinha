from django.db import models
from artists.models import Artista


class Colecao(models.Model):
    artista = models.ForeignKey(
        Artista,
        on_delete=models.CASCADE,
        related_name='colecoes'
    )
    nome = models.CharField(max_length=150)
    descricao = models.TextField(blank=True)
    ativa = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Coleção'
        verbose_name_plural = 'Coleções'
        ordering = ['-criado_em']

    def __str__(self):
        return self.nome


class Arte(models.Model):
    artista = models.ForeignKey(
        Artista,
        on_delete=models.CASCADE,
        related_name='artes'
    )
    colecao = models.ForeignKey(
        Colecao,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='artes'
    )
    nome = models.CharField(max_length=150)
    arquivo = models.ImageField(upload_to='artes/')
    descricao = models.TextField(blank=True)
    ativa = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Arte'
        verbose_name_plural = 'Artes'
        ordering = ['-criado_em']

    def __str__(self):
        return self.nome


class Personalizacao(models.Model):
    arte = models.ForeignKey(
        Arte,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='personalizacoes'
    )
    texto = models.CharField(max_length=255, blank=True)
    fonte = models.CharField(max_length=100, blank=True)
    cor = models.CharField(max_length=50, blank=True)
    preco_extra = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Personalização'
        verbose_name_plural = 'Personalizações'
        ordering = ['-criado_em']

    def __str__(self):
        return f'Personalização #{self.id}'
