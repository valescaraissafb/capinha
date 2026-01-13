from django.db import models


class Personalizacao(models.Model):
    TIPO_CHOICES = [
        ('foto', 'Foto'),
        ('texto', 'Texto'),
        ('design', 'Design'),
        ('combinada', 'Combinada'),
    ]
    
    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True, null=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='design')
    arquivo = models.ImageField(upload_to='personalizacoes/', blank=True, null=True)
    preco_adicional = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    data_criacao = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Personalização'
        verbose_name_plural = 'Personalizações'
        ordering = ['nome']
    
    def __str__(self):
        return self.nome
