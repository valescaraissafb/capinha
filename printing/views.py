from django.views.generic import ListView, DetailView
from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Impressora, FilaImpressao
from .serializers import ImpressoraListSerializer, ImpressoraDetailSerializer, ImpressoraCreateUpdateSerializer


class ImpressoraViewSet(viewsets.ModelViewSet):
    queryset = Impressora.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update' or self.action == 'partial_update':
            return ImpressoraCreateUpdateSerializer
        elif self.action == 'retrieve':
            return ImpressoraDetailSerializer
        return ImpressoraListSerializer
    
    @action(detail=False, methods=['get'])
    def ativas(self, request):
        """Retorna apenas impressoras ativas"""
        impressoras = self.queryset.filter(status='ativo')
        serializer = ImpressoraListSerializer(impressoras, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def marcar_manutencao(self, request):
        """Marca impressora como em manutenção"""
        impressora = self.get_object()
        impressora.status = 'manutencao'
        impressora.save()
        serializer = ImpressoraDetailSerializer(impressora)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def ativar(self, request):
        """Ativa impressora"""
        impressora = self.get_object()
        impressora.status = 'ativo'
        impressora.save()
        serializer = ImpressoraDetailSerializer(impressora)
        return Response(serializer.data)


# ===== VIEWS BASEADAS EM CLASSE PARA TEMPLATES =====

class ImpressoraListView(ListView):
    """Lista de todas as impressoras"""
    model = Impressora
    template_name = 'printing/impressora_list.html'
    context_object_name = 'impressoras'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Estatísticas
        context['total_ativas'] = Impressora.objects.filter(status='ativo').count()
        context['total_manutencao'] = Impressora.objects.filter(status='manutencao').count()
        context['total_inativas'] = Impressora.objects.filter(status='inativo').count()
        return context


class ImpressoraDetailView(DetailView):
    """Detalhes de uma impressora"""
    model = Impressora
    template_name = 'printing/impressora_detail.html'
    context_object_name = 'impressora'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Filas relacionadas
        context['filas'] = FilaImpressao.objects.filter(
            impressora=self.object
        ).order_by('-prioridade', 'criado_em')
        return context


class FilaImpressaoListView(ListView):
    """Lista de fila de impressão"""
    model = FilaImpressao
    template_name = 'printing/fila_lista.html'
    context_object_name = 'fila'
    paginate_by = 20

    def get_queryset(self):
        # Status para mostrar
        return FilaImpressao.objects.filter(
            ~Q(status='concluido')
        ).order_by('-prioridade', 'criado_em')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Estatísticas da fila
        context['aguardando'] = FilaImpressao.objects.filter(status='aguardando').count()
        context['imprimindo'] = FilaImpressao.objects.filter(status='imprimindo').count()
        context['erro'] = FilaImpressao.objects.filter(status='erro').count()
        return context