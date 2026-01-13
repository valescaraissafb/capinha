from django.db import models


class Produto(models.Model):
    CATEGORIA_CHOICES = [
        ('capinha', 'Capinha'),
        ('case', 'Case'),
        ('protetor', 'Protetor de Tela'),
        ('acessorio', 'Acessório'),
    ]
    
    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True, null=True)
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES, default='capinha')
    preco_base = models.DecimalField(max_digits=10, decimal_places=2)
    estoque = models.PositiveIntegerField(default=0)
    ativo = models.BooleanField(default=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'
        ordering = ['nome']
    
    def __str__(self):
        return self.nome
