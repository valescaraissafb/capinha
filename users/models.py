from django.db import models

# -----------------------------
# TABELA: TipoUsuario
# Ex: cliente, artista, admin
# -----------------------------
class Tipouser(models.Model):
    nome = models.CharField(max_length=20)

    def __str__(self):
        return self.nome

class user(models.Model):
    nome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    senha = models.CharField(max_length=255)
    status = models.BooleanField(default=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)


    tipo_usuario = models.ForeignKey(
        Tipouser,
        on_delete=models.PROTECT
    )

    def __str__(self):
        return self.nome_usuario
    
class userTelefone(models.Model):
    usuario = models.ForeignKey(user,
        on_delete=models.CASCADE,
        related_name='telefones'
    )
    numero_telefone = models.CharField(max_length=20)
    tipo_telefone = models.CharField(max_length=20)  # celular, fixo, whatsapp

    def __str__(self):
        return f"{self.numero_telefone} - {self.usuario.nome_usuario}"