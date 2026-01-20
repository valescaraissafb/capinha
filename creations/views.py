from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .models import Colecao, Arte, Personalizacao
from .serializers import (
    ColecaoSerializer,
    ColecaoDetailSerializer,
    ArteSerializer,
    PersonalizacaoSerializer
)


# ============================================================================
# HTML VIEWS (Templates)
# ============================================================================

def colecao_list_view(request):
    """Exibe lista de coleções ativas."""
    colecoes = Colecao.objects.filter(ativa=True)
    
    # Busca
    busca = request.GET.get('busca', '')
    if busca:
        colecoes = colecoes.filter(
            Q(nome__icontains=busca) | Q(descricao__icontains=busca)
        )
    
    # Filtro por artista
    artista_id = request.GET.get('artista', '')
    if artista_id:
        colecoes = colecoes.filter(artista_id=artista_id)
    
    artistas = [c.artista for c in Colecao.objects.filter(ativa=True)]
    artistas = list(dict.fromkeys(artistas))  # Remove duplicatas
    
    return render(request, 'creations/colecao_list.html', {
        'colecoes': colecoes.prefetch_related('artes'),
        'busca': busca,
        'artistas': artistas,
        'artista_selecionado': artista_id,
    })


def colecao_detail_view(request, pk):
    """Exibe detalhes de uma coleção com suas artes."""
    colecao = get_object_or_404(Colecao, pk=pk, ativa=True)
    artes = colecao.artes.filter(ativa=True) # type: ignore
    
    return render(request, 'creations/colecao_detail.html', {
        'colecao': colecao,
        'artes': artes,
    })


def arte_list_view(request):
    """Exibe lista de artes ativas."""
    artes = Arte.objects.filter(ativa=True).select_related('artista', 'colecao')
    
    # Busca
    busca = request.GET.get('busca', '')
    if busca:
        artes = artes.filter(
            Q(nome__icontains=busca) | Q(descricao__icontains=busca)
        )
    
    # Filtro por coleção
    colecao_id = request.GET.get('colecao', '')
    if colecao_id:
        artes = artes.filter(colecao_id=colecao_id)
    
    # Filtro por artista
    artista_id = request.GET.get('artista', '')
    if artista_id:
        artes = artes.filter(artista_id=artista_id)
    
    colecoes = Colecao.objects.filter(ativa=True)
    artistas = [a.artista for a in Arte.objects.filter(ativa=True)]
    artistas = list(dict.fromkeys(artistas))
    
    return render(request, 'creations/arte_list.html', {
        'artes': artes,
        'busca': busca,
        'colecoes': colecoes,
        'colecao_selecionada': colecao_id,
        'artistas': artistas,
        'artista_selecionado': artista_id,
    })


def arte_detail_view(request, pk):
    """Exibe detalhes de uma arte com suas personalizações."""
    arte = get_object_or_404(Arte, pk=pk, ativa=True)
    personalizacoes = arte.personalizacoes.all() # type: ignore
    
    return render(request, 'creations/arte_detail.html', {
        'arte': arte,
        'personalizacoes': personalizacoes,
    })


def personalizacao_list_view(request):
    """Exibe lista de personalizações do usuário autenticado."""
    if not request.user.is_authenticated:
        return render(request, 'creations/personalizacao_list.html', {
            'personalizacoes': [],
            'artes': [],
        })
    
    # Se é artista, mostra personalizações de suas artes
    if hasattr(request.user, 'artista'):
        personalizacoes = Personalizacao.objects.filter(
            arte__artista=request.user.artista
        ).select_related('arte', 'arte__artista')
    else:
        personalizacoes = Personalizacao.objects.none()
    
    # Busca
    busca = request.GET.get('busca', '')
    if busca:
        personalizacoes = personalizacoes.filter(texto__icontains=busca)
    
    # Filtro por arte
    arte_id = request.GET.get('arte', '')
    if arte_id:
        personalizacoes = personalizacoes.filter(arte_id=arte_id)
    
    artes = Arte.objects.filter(artista=request.user.artista) if hasattr(request.user, 'artista') else []
    
    return render(request, 'creations/personalizacao_list.html', {
        'personalizacoes': personalizacoes,
        'artes': artes,
        'busca': busca,
        'arte_selecionada': arte_id,
    })


# ============================================================================
# API VIEWSETS (REST)
# ============================================================================


class ColecaoViewSet(ModelViewSet):
    """
    ViewSet para gerenciar coleções de artes.
    
    As coleções organizam as artes por artista.
    Apenas artistas autenticados podem criar/editar suas coleções.
    """
    serializer_class = ColecaoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['ativa', 'artista']
    search_fields = ['nome', 'descricao', 'artista__nome_artistico']
    ordering_fields = ['nome', 'criado_em']
    ordering = ['-criado_em']

    def get_queryset(self):
        """
        Retorna coleções ativas.
        Superar pode ver todas, artista vê apenas suas coleções.
        """
        qs = Colecao.objects.filter(ativa=True)
        
        if not self.request.user.is_superuser:
            if hasattr(self.request.user, 'artista'):
                qs = qs.filter(artista=self.request.user.artista) # type: ignore
        
        return qs

    def get_serializer_class(self):
        """Usa serializer detalhado para retrieve."""
        if self.action == 'retrieve':
            return ColecaoDetailSerializer
        return ColecaoSerializer

    def perform_create(self, serializer):
        """Associa a coleção ao artista autenticado."""
        artista = self.request.user.artista if hasattr(self.request.user, 'artista') else None # type: ignore
        serializer.save(artista=artista)

    def perform_update(self, serializer):
        """Verifica permissão antes de atualizar."""
        obj = self.get_object()
        if obj.artista != self.request.user.artista and not self.request.user.is_superuser:
            return Response(
                {'erro': 'Você só pode editar suas próprias coleções'},
                status=403
            )
        serializer.save()

    def perform_destroy(self, instance):
        """Verifica permissão antes de deletar."""
        if instance.artista != self.request.user.artista and not self.request.user.is_superuser: # type: ignore
            return Response(
                {'erro': 'Você só pode deletar suas próprias coleções'},
                status=403
            )
        instance.delete()

    @action(detail=False, methods=['get'])
    def minhas_colecoes(self, request):
        """Retorna as coleções do artista autenticado."""
        if hasattr(request.user, 'artista'):
            colecoes = Colecao.objects.filter(
                artista=request.user.artista,
                ativa=True
            )
            serializer = self.get_serializer(colecoes, many=True)
            return Response(serializer.data)
        return Response({'erro': 'Usuário não é artista'}, status=400)

    @action(detail=True, methods=['get'])
    def artes(self, request, pk=None):
        """Lista todas as artes de uma coleção."""
        colecao = self.get_object()
        artes = colecao.artes.filter(ativa=True)
        serializer = ArteSerializer(artes, many=True)
        return Response(serializer.data)


class ArteViewSet(ModelViewSet):
    """
    ViewSet para gerenciar artes criadas por artistas.
    
    As artes são o produto visual criado pelos artistas
    e podem ser agrupadas em coleções.
    Apenas o artista criador e superusuários podem editar.
    """
    serializer_class = ArteSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['ativa', 'artista', 'colecao']
    search_fields = ['nome', 'descricao', 'artista__nome_artistico', 'colecao__nome']
    ordering_fields = ['nome', 'criado_em']
    ordering = ['-criado_em']

    def get_queryset(self):
        """
        Retorna artes ativas.
        Superusuário vê todas, artista vê apenas suas artes.
        """
        qs = Arte.objects.filter(ativa=True)
        
        if not self.request.user.is_superuser:
            if hasattr(self.request.user, 'artista'):
                qs = qs.filter(artista=self.request.user.artista) # type: ignore
        
        return qs

    def perform_create(self, serializer):
        """Associa a arte ao artista autenticado."""
        artista = self.request.user.artista if hasattr(self.request.user, 'artista') else None # type: ignore
        serializer.save(artista=artista)

    def perform_update(self, serializer):
        """Verifica permissão antes de atualizar."""
        obj = self.get_object()
        if obj.artista != self.request.user.artista and not self.request.user.is_superuser:
            return Response(
                {'erro': 'Você só pode editar suas próprias artes'},
                status=403
            )
        serializer.save()

    def perform_destroy(self, instance):
        """Verifica permissão antes de deletar."""
        if instance.artista != self.request.user.artista and not self.request.user.is_superuser: # type: ignore
            return Response(
                {'erro': 'Você só pode deletar suas próprias artes'},
                status=403
            )
        instance.delete()

    @action(detail=False, methods=['get'])
    def minhas_artes(self, request):
        """Retorna as artes do artista autenticado."""
        if hasattr(request.user, 'artista'):
            artes = Arte.objects.filter(
                artista=request.user.artista,
                ativa=True
            )
            page = self.paginate_queryset(artes)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(artes, many=True)
            return Response(serializer.data)
        return Response({'erro': 'Usuário não é artista'}, status=400)

    @action(detail=False, methods=['get'])
    def por_colecao(self, request):
        """Lista artes filtradas por coleção específica."""
        colecao_id = request.query_params.get('colecao_id')
        if colecao_id:
            artes = self.get_queryset().filter(colecao_id=colecao_id)
            page = self.paginate_queryset(artes)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(artes, many=True)
            return Response(serializer.data)
        return Response({'erro': 'colecao_id é obrigatório'}, status=400)

    @action(detail=False, methods=['get'])
    def por_artista(self, request):
        """Lista artes de um artista específico (público)."""
        artista_id = request.query_params.get('artista_id')
        if artista_id:
            artes = Arte.objects.filter(
                artista_id=artista_id,
                ativa=True
            )
            page = self.paginate_queryset(artes)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(artes, many=True)
            return Response(serializer.data)
        return Response({'erro': 'artista_id é obrigatório'}, status=400)

    @action(detail=False, methods=['get'])
    def ultimas(self, request):
        """Retorna as artes criadas mais recentemente."""
        limite = request.query_params.get('limite', 10)
        artes = self.get_queryset()[:int(limite)]
        serializer = self.get_serializer(artes, many=True)
        return Response(serializer.data)


class PersonalizacaoViewSet(ModelViewSet):
    """
    ViewSet para gerenciar personalizações de artes.
    
    Personalização é o resultado visual quando aplica:
    - Texto (nome, frase, número)
    - Cor
    - Fonte
    
    Essas personalizações são referenciadas pelos pedidos.
    """
    serializer_class = PersonalizacaoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['arte', 'arte__artista', 'arte__colecao']
    search_fields = ['texto', 'arte__nome']
    ordering_fields = ['criado_em']
    ordering = ['-criado_em']

    def get_queryset(self):
        """
        Retorna personalizações.
        Superusuário vê todas, artista vê apenas de suas artes.
        """
        qs = Personalizacao.objects.all()
        
        if not self.request.user.is_superuser:
            if hasattr(self.request.user, 'artista'):
                qs = qs.filter(arte__artista=self.request.user.artista) # type: ignore
        
        return qs

    def perform_create(self, serializer):
        """Cria uma personalização para uma arte."""
        serializer.save()

    def perform_update(self, serializer):
        """Verifica permissão antes de atualizar."""
        obj = self.get_object()
        if obj.arte.artista != self.request.user.artista and not self.request.user.is_superuser:
            return Response(
                {'erro': 'Você só pode editar personalizações de suas próprias artes'},
                status=403
            )
        serializer.save()

    def perform_destroy(self, instance):
        """Verifica permissão antes de deletar."""
        if instance.arte.artista != self.request.user.artista and not self.request.user.is_superuser: # type: ignore
            return Response(
                {'erro': 'Você só pode deletar personalizações de suas próprias artes'},
                status=403
            )
        instance.delete()

    @action(detail=False, methods=['get'])
    def por_arte(self, request):
        """Lista personalizações filtradas por arte específica."""
        arte_id = request.query_params.get('arte_id')
        if arte_id:
            personalizacoes = self.get_queryset().filter(arte_id=arte_id)
            page = self.paginate_queryset(personalizacoes)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(personalizacoes, many=True)
            return Response(serializer.data)
        return Response({'erro': 'arte_id é obrigatório'}, status=400)

    @action(detail=False, methods=['get'])
    def por_colecao(self, request):
        """Lista personalizações de uma coleção."""
        colecao_id = request.query_params.get('colecao_id')
        if colecao_id:
            personalizacoes = self.get_queryset().filter(arte__colecao_id=colecao_id)
            page = self.paginate_queryset(personalizacoes)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(personalizacoes, many=True)
            return Response(serializer.data)
        return Response({'erro': 'colecao_id é obrigatório'}, status=400)

    @action(detail=False, methods=['get'])
    def minhas_personalizacoes(self, request):
        """Retorna personalizações das artes do artista autenticado."""
        if hasattr(request.user, 'artista'):
            personalizacoes = self.get_queryset().filter(arte__artista=request.user.artista)
            page = self.paginate_queryset(personalizacoes)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(personalizacoes, many=True)
            return Response(serializer.data)
        return Response({'erro': 'Usuário não é artista'}, status=400)
