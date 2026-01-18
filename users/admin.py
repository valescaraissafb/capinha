from django.contrib import admin
from .models import user, userTelefone, Tipouser


@admin.register(Tipouser)
class TipouserAdmin(admin.ModelAdmin):
    list_display = ['id', 'nome']
    search_fields = ['nome']

@admin.register(user)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'nome','senha', 'is_active', 'is_staff')
    list_filter = ('is_active', 'is_staff', 'tipo_usuario')
    search_fields = ('email', 'nome')



@admin.register(userTelefone)
class UserTelefoneAdmin(admin.ModelAdmin):
    list_display = ['id', 'usuario', 'numero_telefone', 'tipo_telefone']
    list_filter = ['tipo_telefone', 'usuario']
    search_fields = ['usuario__nome', 'numero_telefone']
    
    fieldsets = (
        ('Informações', {'fields': ('usuario', 'numero_telefone', 'tipo_telefone')}),
    )
