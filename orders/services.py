from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from .models import Pedido, ItemPedido
from django.db import models


class PedidoService:
    """
    Serviço de orquestração de pedidos - O coração transacional do sistema.
    
    Responsabilidades:
    1. Criar e gerenciar pedidos
    2. Controlar fluxo de status
    3. Calcular valores
    4. Validar transações
    5. Ligar todos os apps (users, artists, products, creations, printing, payments)
    """

    @staticmethod
    def criar_pedido(usuario, artista):
        """
        Cria um novo pedido no status 'criado'.
        
        Um pedido sempre precisa de:
        - Um usuário (quem está comprando)
        - Um artista (quem vai produzir)
        """
        if not artista.ativo:
            raise ValueError("Artista selecionado não está ativo.")
        
        pedido = Pedido.objects.create(
            usuario=usuario,
            artista=artista,
            status_pedido='criado',
            valor_total=Decimal('0.00')
        )
        return pedido

    @staticmethod
    @transaction.atomic
    def adicionar_item(pedido, produto, personalizacao, quantidade, preco_unitario):
        """
        Adiciona um item ao pedido e recalcula o valor total.
        
        Regra: Apenas pedidos em status 'criado' podem receber itens
        """
        if not pedido.pode_adicionar_itens():
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
        Atualiza quantidade e/ou preço de um item.
        
        Regra: Apenas itens de pedidos em status 'criado' podem ser alterados
        """
        if not item.pedido.pode_adicionar_itens():
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
        Remove um item do pedido.
        
        Regra: Apenas itens de pedidos em status 'criado' podem ser removidos
        """
        if not item.pedido.pode_adicionar_itens():
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
        Confirma o pagamento e muda o status para 'pago'.
        
        Fluxo: CRIADO → PAGO
        Regra: Apenas pedidos em status 'criado' podem ser pagos
        """
        if not pedido.pode_mudar_status('pago'):
            raise ValueError(f"Pedido não pode ser pago. Status atual: {pedido.status_pedido}")

        PedidoService.validar_pedido(pedido)

        pedido.forma_pagamento = forma_pagamento
        pedido.status_pagamento = status_pagamento
        pedido.status_pedido = 'pago'
        pedido.data_pagamento = timezone.now()
        pedido.save()

        return pedido

    @staticmethod
    @transaction.atomic
    def enviar_para_producao(pedido):
        """
        Muda o status do pedido para 'em_producao'.
        
        Fluxo: PAGO → EM PRODUÇÃO
        """
        if not pedido.pode_mudar_status('em_producao'):
            raise ValueError(f"Apenas pedidos pagos podem ir para produção. Status: {pedido.status_pedido}")

        pedido.status_pedido = 'em_producao'
        pedido.data_producao = timezone.now()
        pedido.save()

        return pedido

    @staticmethod
    @transaction.atomic
    def marcar_como_impresso(pedido, impressora=None):
        """
        Muda o status do pedido para 'impresso'.
        
        Fluxo: EM PRODUÇÃO → IMPRESSO
        """
        if not pedido.pode_mudar_status('impresso'):
            raise ValueError(f"Pedido não está em produção. Status: {pedido.status_pedido}")

        pedido.status_pedido = 'impresso'
        pedido.data_impressao = timezone.now()
        
        if impressora:
            pedido.impressora = impressora
            
        pedido.save()

        return pedido

    @staticmethod
    @transaction.atomic
    def marcar_como_enviado(pedido):
        """
        Muda o status do pedido para 'enviado'.
        
        Fluxo: IMPRESSO → ENVIADO
        """
        if not pedido.pode_mudar_status('enviado'):
            raise ValueError(f"Pedido ainda não foi impresso. Status: {pedido.status_pedido}")

        pedido.status_pedido = 'enviado'
        pedido.data_envio = timezone.now()
        pedido.save()

        return pedido

    @staticmethod
    @transaction.atomic
    def finalizar_pedido(pedido):
        """
        Muda o status do pedido para 'concluido'.
        
        Fluxo: ENVIADO → CONCLUÍDO
        """
        if not pedido.pode_mudar_status('concluido'):
            raise ValueError(f"Pedido ainda não foi enviado. Status: {pedido.status_pedido}")

        pedido.status_pedido = 'concluido'
        pedido.data_conclusao = timezone.now()
        pedido.save()

        return pedido

    @staticmethod
    @transaction.atomic
    def cancelar_pedido(pedido):
        """
        Cancela o pedido.
        
        Regra: Apenas pedidos em 'criado' ou 'pago' podem ser cancelados
        """
        if not pedido.pode_mudar_status('cancelado'):
            raise ValueError(f"Pedido não pode ser cancelado. Status: {pedido.status_pedido}")

        pedido.status_pedido = 'cancelado'
        pedido.save()

        return pedido

