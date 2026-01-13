from decimal import Decimal
from django.db import transaction
from .models import Pedido, ItemPedido
from django.db import models


class PedidoService:
    """Serviço de orquestração de pedidos"""

    @staticmethod
    def criar_pedido(usuario):
        """Cria um novo pedido no status 'criado'"""
        pedido = Pedido.objects.create(
            usuario=usuario,
            status_pedido='criado',
            valor_total=Decimal('0.00')
        )
        return pedido

    @staticmethod
    @transaction.atomic
    def adicionar_item(pedido, produto, personalizacao, quantidade, preco_unitario):
        """
        Adiciona um item ao pedido e recalcula o valor total
        
        Regra: Apenas pedidos em status 'criado' podem receber itens
        """
        if pedido.status_pedido != 'criado':
            raise ValueError(f"Pedido não pode ser alterado. Status atual: {pedido.status_pedido}")

        subtotal = Decimal(str(quantidade)) * Decimal(str(preco_unitario))
        
        item = ItemPedido.objects.create(
            pedido=pedido,
            produto=produto,
            personalizacao=personalizacao,
            quantidade=quantidade,
            preco_unitario=preco_unitario,
            subtotal=subtotal
        )
        
        # Recalcula valor total do pedido
        PedidoService.recalcular_valor_total(pedido)
        
        return item

    @staticmethod
    def recalcular_valor_total(pedido):
        """Recalcula o valor_total do pedido somando subtotais dos itens"""
        valor_total = ItemPedido.objects.filter(pedido=pedido).aggregate(
            total=models.Sum('subtotal')
        )['total'] or Decimal('0.00')
        
        pedido.valor_total = valor_total
        pedido.save(update_fields=['valor_total'])
        return pedido

    @staticmethod
    @transaction.atomic
    def atualizar_item(item, quantidade=None, preco_unitario=None):
        """
        Atualiza quantidade e/ou preço de um item
        
        Regra: Apenas itens de pedidos em status 'criado' podem ser alterados
        """
        if item.pedido.status_pedido != 'criado':
            raise ValueError(f"Item não pode ser alterado. Pedido em status: {item.pedido.status_pedido}")

        if quantidade is not None:
            item.quantidade = quantidade
        if preco_unitario is not None:
            item.preco_unitario = preco_unitario

        item.subtotal = Decimal(str(item.quantidade)) * Decimal(str(item.preco_unitario))
        item.save()

        # Recalcula valor total do pedido
        PedidoService.recalcular_valor_total(item.pedido)

        return item

    @staticmethod
    @transaction.atomic
    def remover_item(item):
        """
        Remove um item do pedido
        
        Regra: Apenas itens de pedidos em status 'criado' podem ser removidos
        """
        if item.pedido.status_pedido != 'criado':
            raise ValueError(f"Item não pode ser removido. Pedido em status: {item.pedido.status_pedido}")

        pedido = item.pedido
        item.delete()

        # Recalcula valor total
        PedidoService.recalcular_valor_total(pedido)

        return pedido

    @staticmethod
    def validar_pedido(pedido):
        """Valida se o pedido tem itens e está pronto para pagamento"""
        if not pedido.itens.exists():
            raise ValueError("Pedido não pode ser pago sem itens.")
        
        if pedido.valor_total <= 0:
            raise ValueError("Pedido com valor inválido.")
        
        return True

    @staticmethod
    @transaction.atomic
    def confirmar_pagamento(pedido, forma_pagamento, status_pagamento='confirmado'):
        """
        Confirma o pagamento e muda o status para 'pago'
        
        Regra: Apenas pedidos em status 'criado' podem ser pagos
        """
        if pedido.status_pedido != 'criado':
            raise ValueError(f"Pedido não pode ser pago. Status atual: {pedido.status_pedido}")

        PedidoService.validar_pedido(pedido)

        pedido.forma_pagamento = forma_pagamento
        pedido.status_pagamento = status_pagamento
        pedido.status_pedido = 'pago'
        pedido.save()

        return pedido

    @staticmethod
    def enviar_para_producao(pedido):
        """Muda o status do pedido para 'em_producao'"""
        if pedido.status_pedido != 'pago':
            raise ValueError(f"Apenas pedidos pagos podem ir para produção. Status: {pedido.status_pedido}")

        pedido.status_pedido = 'em_producao'
        pedido.save()

        return pedido

    @staticmethod
    def finalizar_pedido(pedido):
        """Muda o status do pedido para 'finalizado'"""
        if pedido.status_pedido != 'em_producao':
            raise ValueError(f"Pedido não está em produção. Status: {pedido.status_pedido}")

        pedido.status_pedido = 'finalizado'
        pedido.save()

        return pedido

    @staticmethod
    @transaction.atomic
    def cancelar_pedido(pedido):
        """Cancela o pedido (apenas se estiver em 'criado')"""
        if pedido.status_pedido != 'criado':
            raise ValueError(f"Apenas pedidos em 'criado' podem ser cancelados. Status: {pedido.status_pedido}")

        pedido.status_pedido = 'cancelado'
        pedido.save()

        return pedido

