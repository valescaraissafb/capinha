from rest_framework import serializers
from .models import Pedido, ItemPedido


class ItemPedidoSerializer(serializers.ModelSerializer):
    """Serializer para exibição detalhada de um item do pedido"""
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
            'criado_em',
            'atualizado_em',
        ]
        read_only_fields = ['id', 'subtotal', 'criado_em', 'atualizado_em']

    def validate_quantidade(self, value):
        if value < 1:
            raise serializers.ValidationError("Quantidade deve ser maior que 0.")
        return value

    def validate_preco_unitario(self, value):
        if value < 0:
            raise serializers.ValidationError("Preço não pode ser negativo.")
        return value


class ItemPedidoCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer para criar/atualizar itens do pedido"""
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
    """Serializer para listagem de pedidos"""
    usuario_nome = serializers.CharField(source='usuario.nome', read_only=True)
    usuario_email = serializers.CharField(source='usuario.email', read_only=True)
    artista_nome = serializers.CharField(source='artista.nome_artistico', read_only=True)
    quantidade_itens = serializers.SerializerMethodField()

    class Meta:
        model = Pedido
        fields = [
            'id',
            'usuario',
            'usuario_nome',
            'usuario_email',
            'artista',
            'artista_nome',
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
    """Serializer para detalhes completos de um pedido"""
    itens = ItemPedidoSerializer(many=True, read_only=True)
    usuario_nome = serializers.CharField(source='usuario.nome', read_only=True)
    usuario_email = serializers.CharField(source='usuario.email', read_only=True)
    artista_nome = serializers.CharField(source='artista.nome_artistico', read_only=True)
    artista_biografia = serializers.CharField(source='artista.biografia', read_only=True)
    impressora_nome = serializers.CharField(source='impressora.nome', read_only=True, allow_null=True)

    class Meta:
        model = Pedido
        fields = [
            'id',
            'usuario',
            'usuario_nome',
            'usuario_email',
            'artista',
            'artista_nome',
            'artista_biografia',
            'status_pedido',
            'valor_total',
            'data_pedido',
            'data_pagamento',
            'data_producao',
            'data_impressao',
            'data_envio',
            'data_conclusao',
            'forma_pagamento',
            'status_pagamento',
            'impressora',
            'impressora_nome',
            'itens',
        ]
        read_only_fields = ['id', 'data_pedido', 'valor_total', 'status_pedido', 
                           'data_pagamento', 'data_producao', 'data_impressao', 
                           'data_envio', 'data_conclusao']


class PedidoCreateSerializer(serializers.ModelSerializer):
    """Serializer para criar um novo pedido"""
    class Meta:
        model = Pedido
        fields = ['usuario', 'artista']

    def create(self, validated_data):
        from .services import PedidoService
        usuario = validated_data['usuario']
        artista = validated_data['artista']
        
        pedido = PedidoService.criar_pedido(usuario, artista)
        return pedido


class PedidoStatusUpdateSerializer(serializers.ModelSerializer):
    """Serializer para atualizar status de um pedido"""
    class Meta:
        model = Pedido
        fields = ['status_pedido']

    def validate_status_pedido(self, value):
        STATUS_VALIDOS = ['criado', 'pago', 'em_producao', 'impresso', 'enviado', 'concluido', 'cancelado']
        if value not in STATUS_VALIDOS:
            raise serializers.ValidationError(f"Status inválido. Opções: {STATUS_VALIDOS}")
        return value