from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Pedido, ItemPedido
from .serializers import (
    PedidoListSerializer, PedidoDetailSerializer, PedidoStatusUpdateSerializer,
    PedidoCreateSerializer,
    ItemPedidoSerializer, ItemPedidoCreateUpdateSerializer
)
from .services import PedidoService


class PedidoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar Pedidos.
    
    Endpoints:
    - GET /orders/ → Lista pedidos do usuário
    - POST /orders/ → Cria novo pedido
    - GET /orders/{id}/ → Detalhes do pedido
    - PATCH /orders/{id}/status/ → Atualiza status
    - POST /orders/{id}/items/ → Adiciona item
    - PATCH /orders/{id}/marcar-impresso/ → Marca como impresso
    - PATCH /orders/{id}/marcar-enviado/ → Marca como enviado
    - PATCH /orders/{id}/finalizar/ → Finaliza pedido
    """
    permission_classes = [IsAuthenticated]
    queryset = Pedido.objects.all()

    def get_queryset(self):
        return Pedido.objects.filter(usuario=self.request.user).order_by('-data_pedido')

    def get_serializer_class(self):
        if self.action == 'list':
            return PedidoListSerializer
        if self.action == 'create':
            return PedidoCreateSerializer
        return PedidoDetailSerializer

    def create(self, request, *args, **kwargs):
        """Cria um novo pedido"""
        serializer = PedidoCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        pedido = serializer.save()
        
        response_serializer = PedidoDetailSerializer(pedido, context={'request': request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['patch'], url_path='status')
    def status(self, request, pk=None):
        """Atualiza o status do pedido com validação de fluxo"""
        pedido = get_object_or_404(Pedido, pk=pk, usuario=request.user)
        serializer = PedidoStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        novo_status = serializer.validated_data['status_pedido']

        try:
            if novo_status == 'pago':
                forma = request.data.get('forma_pagamento')
                if not forma:
                    return Response(
                        {'detail': 'forma_pagamento é obrigatória para status "pago".'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                pedido = PedidoService.confirmar_pagamento(
                    pedido, 
                    forma_pagamento=forma, 
                    status_pagamento=request.data.get('status_pagamento', 'confirmado')
                )
            elif novo_status == 'em_producao':
                pedido = PedidoService.enviar_para_producao(pedido)
            elif novo_status == 'impresso':
                pedido = PedidoService.marcar_como_impresso(pedido)
            elif novo_status == 'enviado':
                pedido = PedidoService.marcar_como_enviado(pedido)
            elif novo_status == 'concluido':
                pedido = PedidoService.finalizar_pedido(pedido)
            elif novo_status == 'cancelado':
                pedido = PedidoService.cancelar_pedido(pedido)
            else:
                return Response(
                    {'detail': 'Status não suportado.'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(PedidoDetailSerializer(pedido, context={'request': request}).data)

    @action(detail=True, methods=['patch'], url_path='marcar-impresso')
    def marcar_impresso(self, request, pk=None):
        """Marca o pedido como impresso"""
        pedido = get_object_or_404(Pedido, pk=pk, usuario=request.user)
        
        try:
            pedido = PedidoService.marcar_como_impresso(pedido)
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(PedidoDetailSerializer(pedido, context={'request': request}).data)

    @action(detail=True, methods=['patch'], url_path='marcar-enviado')
    def marcar_enviado(self, request, pk=None):
        """Marca o pedido como enviado"""
        pedido = get_object_or_404(Pedido, pk=pk, usuario=request.user)
        
        try:
            pedido = PedidoService.marcar_como_enviado(pedido)
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(PedidoDetailSerializer(pedido, context={'request': request}).data)

    @action(detail=True, methods=['patch'], url_path='finalizar')
    def finalizar(self, request, pk=None):
        """Finaliza o pedido (marca como concluído)"""
        pedido = get_object_or_404(Pedido, pk=pk, usuario=request.user)
        
        try:
            pedido = PedidoService.finalizar_pedido(pedido)
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(PedidoDetailSerializer(pedido, context={'request': request}).data)

    @action(detail=True, methods=['post'], url_path='items')
    def add_item(self, request, pk=None):
        """Adiciona um item ao pedido"""
        pedido = get_object_or_404(Pedido, pk=pk, usuario=request.user)
        serializer = ItemPedidoCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            item = PedidoService.adicionar_item(
                pedido,
                data['produto'],
                data['personalizacao'],
                data['quantidade'],
                data['preco_unitario']
            )
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            ItemPedidoSerializer(item, context={'request': request}).data, 
            status=status.HTTP_201_CREATED
        )


class ItemPedidoViewSet(mixins.UpdateModelMixin,
                       mixins.DestroyModelMixin,
                       viewsets.GenericViewSet):
    """ViewSet para gerenciar Itens de Pedido"""
    permission_classes = [IsAuthenticated]
    queryset = ItemPedido.objects.all()
    serializer_class = ItemPedidoSerializer

    def get_object(self):
        obj = get_object_or_404(ItemPedido, pk=self.kwargs['pk'], pedido__usuario=self.request.user)
        return obj

    def update(self, request, *args, **kwargs):
        """Atualiza quantidade e/ou preço de um item"""
        item = self.get_object()
        serializer = ItemPedidoCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            item = PedidoService.atualizar_item(
                item,
                quantidade=data.get('quantidade'),
                preco_unitario=data.get('preco_unitario')
            )
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(ItemPedidoSerializer(item, context={'request': request}).data)

    def destroy(self, request, *args, **kwargs):
        """Remove um item do pedido"""
        item = self.get_object()
        try:
            PedidoService.remover_item(item)
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)


# ===== VIEWS BASEADAS EM CLASSE PARA TEMPLATES =====

class PedidoListView(ListView):
    """Lista todos os pedidos do usuário logado"""
    model = Pedido
    template_name = 'orders/pedido_list.html'
    context_object_name = 'pedidos'
    paginate_by = 10

    def get_queryset(self):
        # Se usuário não está autenticado, retornar queryset vazio
        if not self.request.user.is_authenticated:
            return Pedido.objects.none()
        return Pedido.objects.filter(usuario=self.request.user).order_by('-data_pedido')


class PedidoDetailView(DetailView):
    """Detalhes de um pedido específico"""
    model = Pedido
    template_name = 'orders/pedido_detail.html'
    context_object_name = 'pedido'

    def get_queryset(self):
        # Se usuário não está autenticado, retornar queryset vazio
        if not self.request.user.is_authenticated:
            return Pedido.objects.none()
        return Pedido.objects.filter(usuario=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['itens'] = self.object.itens.all()
        return context
