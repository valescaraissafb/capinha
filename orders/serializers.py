from rest_framework import serializers
from .models import Pedido, ItemPedido


class ItemPedidoSerializer(serializers.ModelSerializer):
    produto_nome = serializers.CharField(source='produto.nome', read_only=True)
    personalizacao_descricao = serializers.CharField(source='personalizacao.descricao', read_only=True)

    class Meta:
        model = ItemPedido
        fields = [
            'id',
            'produto',
            'produto_nome',
            'personalizacao',
            'personalizacao_descricao',
            'quantidade',
            'preco_unitario',
            'subtotal',
        ]
        read_only_fields = ['id', 'subtotal']

    def validate_quantidade(self, value):
        if value < 1:
            raise serializers.ValidationError("Quantidade deve ser maior que 0.")
        return value

    def validate_preco_unitario(self, value):
        if value < 0:
            raise serializers.ValidationError("Preço não pode ser negativo.")
        return value


class ItemPedidoCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemPedido
        fields = ['produto', 'personalizacao', 'quantidade', 'preco_unitario']

    def validate(self, data):
        produto = data.get('produto')
        personalizacao = data.get('personalizacao')
        
        if not produto or not personalizacao:
            raise serializers.ValidationError(
                "Produto e personalização são obrigatórios."
            )
        return data


class PedidoListSerializer(serializers.ModelSerializer):
    usuario_nome = serializers.CharField(source='usuario.nome', read_only=True)
    quantidade_itens = serializers.SerializerMethodField()

    class Meta:
        model = Pedido
        fields = [
            'id',
            'usuario',
            'usuario_nome',
            'status_pedido',
            'valor_total',
            'data_pedido',
            'forma_pagamento',
            'status_pagamento',
            'quantidade_itens',
        ]
        read_only_fields = ['id', 'data_pedido', 'valor_total']

    def get_quantidade_itens(self, obj):
        return obj.itens.count()


class PedidoDetailSerializer(serializers.ModelSerializer):
    itens = ItemPedidoSerializer(many=True, read_only=True)
    usuario_nome = serializers.CharField(source='usuario.nome', read_only=True)
    usuario_email = serializers.CharField(source='usuario.email', read_only=True)

    class Meta:
        model = Pedido
        fields = [
            'id',
            'usuario',
            'usuario_nome',
            'usuario_email',
            'status_pedido',
            'valor_total',
            'data_pedido',
            'forma_pagamento',
            'status_pagamento',
            'impressora',
            'itens',
        ]
        read_only_fields = ['id', 'data_pedido', 'valor_total', 'status_pedido']


class PedidoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pedido
        fields = ['usuario']

    def create(self, validated_data):
        return Pedido.objects.create(
            usuario=validated_data['usuario'],
            status_pedido='criado',
            valor_total=0
        )


class PedidoStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pedido
        fields = ['status_pedido']

    def validate_status_pedido(self, value):
        STATUS_VALIDOS = ['criado', 'pago', 'em_producao', 'finalizado', 'cancelado']
        if value not in STATUS_VALIDOS:
            raise serializers.ValidationError(f"Status inválido. Opções: {STATUS_VALIDOS}")
        return value