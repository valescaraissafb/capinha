from django.contrib import admin
from django.utils.html import format_html
from .models import Colecao, Arte, Personalizacao


@admin.register(Colecao)
class ColecaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'artista_link', 'total_artes', 'ativa', 'criado_em')
    list_filter = ('ativa', 'artista', 'criado_em')
    search_fields = ('nome', 'descricao', 'artista__nome_artistico')
    readonly_fields = ('total_artes_display', 'criado_em')
    date_hierarchy = 'criado_em'

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('artista', 'nome', 'descricao')
        }),
        ('Status', {
            'fields': ('ativa',)
        }),
        ('Estatísticas', {
            'fields': ('total_artes_display',),
            'classes': ('collapse',)
        }),
        ('Datas', {
            'fields': ('criado_em',),
            'classes': ('collapse',)
        }),
    )

    def artista_link(self, obj):
        return obj.artista.nome_artistico if obj.artista else "-"
    artista_link.short_description = 'Artista'

    def total_artes_display(self, obj):
        return obj.artes.count()
    total_artes_display.short_description = 'Total de Artes'

    def total_artes(self, obj):
        return obj.artes.count()
    total_artes.short_description = '🎨 Artes'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Se não é admin, mostrar apenas coleções do artista
        if not request.user.is_superuser:
            if hasattr(request.user, 'artista'):
                qs = qs.filter(artista=request.user.artista) # type: ignore
        return qs


@admin.register(Arte)
class ArteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'artista_link', 'colecao_link', 'preview_imagem', 'ativa', 'criado_em')
    list_filter = ('ativa', 'artista', 'colecao', 'criado_em')
    search_fields = ('nome', 'descricao', 'artista__nome_artistico', 'colecao__nome')
    readonly_fields = ('preview_imagem_grande', 'criado_em')
    date_hierarchy = 'criado_em'

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('artista', 'colecao', 'nome', 'descricao')
        }),
        ('Imagem', {
            'fields': ('arquivo', 'preview_imagem_grande')
        }),
        ('Status', {
            'fields': ('ativa',)
        }),
        ('Datas', {
            'fields': ('criado_em',),
            'classes': ('collapse',)
        }),
    )

    def artista_link(self, obj):
        return obj.artista.nome_artistico if obj.artista else "-"
    artista_link.short_description = 'Artista'

    def colecao_link(self, obj):
        if obj.colecao:
            return format_html(
                '<span style="background: #e3f2fd; padding: 5px 10px; border-radius: 3px;">{}</span>',
                obj.colecao.nome
            )
        return "-"
    colecao_link.short_description = 'Coleção'

    def preview_imagem(self, obj):
        if obj.arquivo:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 3px;" />',
                obj.arquivo.url
            )
        return "Sem imagem"
    preview_imagem.short_description = '🖼️'

    def preview_imagem_grande(self, obj):
        if obj.arquivo:
            return format_html(
                '<img src="{}" width="300" style="max-width: 100%; border-radius: 5px;" />',
                obj.arquivo.url
            )
        return "Sem imagem"
    preview_imagem_grande.short_description = 'Pré-visualização'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Se não é admin, mostrar apenas artes do artista
        if not request.user.is_superuser:
            if hasattr(request.user, 'artista'):
                qs = qs.filter(artista=request.user.artista) # type: ignore
        return qs


@admin.register(Personalizacao)
class PersonalizacaoAdmin(admin.ModelAdmin):
    list_display = ('id', 'arte_link', 'exibir_texto', 'exibir_cor', 'preco_extra', 'criado_em')
    list_filter = ('arte__artista', 'arte__colecao', 'criado_em')
    search_fields = ('arte__nome', 'texto')
    readonly_fields = ('cor_preview', 'criado_em', 'resumo_personalizacao')
    date_hierarchy = 'criado_em'

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('arte', 'resumo_personalizacao')
        }),
        ('Personalização', {
            'fields': ('texto', 'fonte', 'cor', 'cor_preview')
        }),
        ('Preço', {
            'fields': ('preco_extra',),
            'description': 'Preço adicional desta personalização'
        }),
        ('Datas', {
            'fields': ('criado_em',),
            'classes': ('collapse',)
        }),
    )

    def arte_link(self, obj):
        if obj.arte:
            return format_html(
                '<span style="background: #f3e5f5; padding: 5px 10px; border-radius: 3px;">{}</span>',
                obj.arte.nome
            )
        return "-"
    arte_link.short_description = 'Arte'

    def exibir_texto(self, obj):
        if obj.texto:
            return obj.texto[:50] + '...' if len(obj.texto) > 50 else obj.texto
        return "-"
    exibir_texto.short_description = 'Texto'

    def exibir_cor(self, obj):
        if obj.cor:
            return format_html(
                '<div style="display: inline-block; width: 20px; height: 20px; '
                'background-color: {}; border: 1px solid #ccc; border-radius: 3px;" '
                'title="{}"></div> {}',
                obj.cor, obj.cor, obj.cor
            )
        return "-"
    exibir_cor.short_description = 'Cor'

    def cor_preview(self, obj):
        if obj.cor:
            return format_html(
                '<div style="width: 100px; height: 100px; background-color: {}; '
                'border: 1px solid #ccc; border-radius: 5px;"></div>',
                obj.cor
            )
        return "Nenhuma cor selecionada"
    cor_preview.short_description = 'Pré-visualização de Cor'

    def resumo_personalizacao(self, obj):
        resumo = []
        if obj.texto:
            resumo.append(f"📝 Texto: {obj.texto}")
        if obj.fonte:
            resumo.append(f"🔤 Fonte: {obj.fonte}")
        if obj.cor:
            resumo.append(f"🎨 Cor: {obj.cor}")
        if resumo:
            return '\n'.join(resumo)
        return "Nenhuma personalização"
    resumo_personalizacao.short_description = 'Resumo'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Se não é admin, mostrar apenas personalizações de artes do artista
        if not request.user.is_superuser:
            if hasattr(request.user, 'artista'):
                qs = qs.filter(arte__artista=request.user.artista) # type: ignore
        return qs
