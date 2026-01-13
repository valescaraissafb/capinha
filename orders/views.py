from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Pedido, ItemPedido
from .serializers import (
    PedidoListSerializer, PedidoDetailSerializer, PedidoStatusUpdateSerializer,
    ItemPedidoSerializer, ItemPedidoCreateUpdateSerializer
)
from .services import PedidoService


class PedidoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Pedido.objects.all()

    def get_queryset(self):
        return Pedido.objects.filter(usuario=self.request.user).order_by('-data_pedido')

    def get_serializer_class(self):
        if self.action == 'list':
            return PedidoListSerializer
        if self.action in ['retrieve', 'create', 'status']:
            return PedidoDetailSerializer
        return PedidoDetailSerializer

    def create(self, request, *args, **kwargs):
        pedido = PedidoService.criar_pedido(request.user)
        serializer = PedidoDetailSerializer(pedido, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['patch'], url_path='status')
    def status(self, request, pk=None):
        pedido = get_object_or_404(Pedido, pk=pk, usuario=request.user)
        serializer = PedidoStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        novo_status = serializer.validated_data['status_pedido']

        try:
            if novo_status == 'pago':
                forma = request.data.get('forma_pagamento')
                if not forma:
                    return Response({'detail': 'forma_pagamento é obrigatória para status "pago".'}, status=status.HTTP_400_BAD_REQUEST)
                pedido = PedidoService.confirmar_pagamento(pedido, forma_pagamento=forma, status_pagamento=request.data.get('status_pagamento', 'confirmado'))
            elif novo_status == 'em_producao':
                pedido = PedidoService.enviar_para_producao(pedido)
            elif novo_status == 'finalizado':
                pedido = PedidoService.finalizar_pedido(pedido)
            elif novo_status == 'cancelado':
                pedido = PedidoService.cancelar_pedido(pedido)
            elif novo_status == 'criado':
                pedido.status_pedido = 'criado'
                pedido.save(update_fields=['status_pedido'])
            else:
                return Response({'detail': 'Status não suportado.'}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(PedidoDetailSerializer(pedido, context={'request': request}).data)

    @action(detail=True, methods=['post'], url_path='items')
    def add_item(self, request, pk=None):
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

        return Response(ItemPedidoSerializer(item, context={'request': request}).data, status=status.HTTP_201_CREATED)


class ItemPedidoViewSet(mixins.UpdateModelMixin,
                       mixins.DestroyModelMixin,
                       viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    queryset = ItemPedido.objects.all()
    serializer_class = ItemPedidoSerializer

    def get_object(self):
        obj = get_object_or_404(ItemPedido, pk=self.kwargs['pk'], pedido__usuario=self.request.user)
        return obj

    def update(self, request, *args, **kwargs):
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
        item = self.get_object()
        try:
            PedidoService.remover_item(item)
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)
