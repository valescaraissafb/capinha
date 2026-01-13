from django.db import models


class Impressora(models.Model):
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
    
    nome = models.CharField(max_length=200)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ativo')
    localizacao = models.CharField(max_length=200, blank=True, null=True)
    fabricante = models.CharField(max_length=200, blank=True, null=True)
    modelo = models.CharField(max_length=200, blank=True, null=True)
    data_aquisicao = models.DateField(blank=True, null=True)
    data_ultima_manutencao = models.DateField(blank=True, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Impressora'
        verbose_name_plural = 'Impressoras'
        ordering = ['nome']
    
    def __str__(self):
        return f"{self.nome} ({self.get_tipo_display()})"
