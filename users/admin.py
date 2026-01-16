from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import user


@admin.register(user)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Informações Adicionais', {
            'fields': ('telefone', 'endereco', 'cidade', 'estado', 'cep', 'data_criacao')
        }),
    )
    
    list_display = ['username', 'email', 'first_name', 'last_name', 'telefone', 'cidade', 'is_active', 'data_criacao']
    list_filter = ['is_active', 'is_staff', 'cidade', 'data_criacao']
    search_fields = ['username', 'email', 'telefone', 'cidade']
    readonly_fields = ['data_criacao']
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informações Pessoais', {'fields': ('first_name', 'last_name', 'email')}),
        ('Contato', {'fields': ('telefone', 'endereco', 'cidade', 'estado', 'cep')}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Datas', {'fields': ('last_login', 'data_criacao')}),
    )
