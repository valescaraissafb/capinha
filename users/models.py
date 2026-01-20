from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

# -----------------------------
# TABELA: TipoUsuario
# Ex: cliente, artista, admin
# -----------------------------
class Tipouser(models.Model):
    nome = models.CharField(max_length=20)

    def __str__(self):
        return self.nome


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email obrigatório')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class user(AbstractBaseUser, PermissionsMixin):
    nome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    senha = models.CharField(max_length=128)
    documento = models.CharField(
        max_length=20, 
        blank=True, 
        null=True,
        help_text="CPF ou CNPJ do usuário"
    )

    tipo_usuario = models.ForeignKey(
        Tipouser, 
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    data_cadastro = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nome']

    def __str__(self):
        return self.email


class userTelefone(models.Model):
    usuario = models.ForeignKey(
        user,
        on_delete=models.CASCADE,
        related_name='telefones'
    )
    numero_telefone = models.CharField(max_length=20)
    tipo_telefone = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.numero_telefone} - {self.usuario.email}"