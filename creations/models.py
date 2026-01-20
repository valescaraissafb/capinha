# pyright: reportRedeclaration=false
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
    imagem_destaque = models.ImageField(
        upload_to='colecoes/',
        blank=True,
        null=True
    )
    ativa = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-criado_em']
        indexes = [
            models.Index(fields=['artista', 'ativa']),
            models.Index(fields=['criado_em']),
        ]

    def __str__(self):
        return f'{self.nome} ({self.artista.nome_artistico})'

    @property
    def total_artes(self):
        return self.artes.filter(ativa=True).count() # type: ignore

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
    atualizado_em = models.DateTimeField(auto_now=True)

    class Metadata:
        ordering = ['-criado_em']
        indexes = [
            models.Index(fields=['artista', 'ativa']),
            models.Index(fields=['colecao', 'ativa']),
            models.Index(fields=['criado_em']),
        ]

    def __str__(self):
        return f'{self.nome} - {self.artista.nome_artistico}'

    @property
    def total_personalizacoes(self):
        return self.personalizacoes.count() # type: ignore
    
    
class Personalizacao(models.Model):
    """
    Personalização de um produto.
    Define como o produto vai ficar (visual + preço extra).
    """
    arte = models.ForeignKey(  # type: ignore
        Arte,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='personalizacoes'
    )
    produto = models.ForeignKey(
        'products.Produto',
        on_delete=models.PROTECT,
        related_name='personalizacoes',
        null=True,
        blank=True,
        help_text="Produto que esta personalização se aplica"
    )
    texto = models.CharField(max_length=255, blank=True)
    fonte = models.CharField(max_length=100, blank=True)
    cor = models.CharField(max_length=50, blank=True)
    preco_extra = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0  # type: ignore
    )

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-criado_em']
        verbose_name = "Personalização"
        verbose_name_plural = "Personalizações"

    def __str__(self):
        return f'Personalização #{self.id}' # type: ignore