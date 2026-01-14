from rest_framework import serializers
from .models import Colecao, Arte, Personalizacao


class ColecaoSerializer(serializers.ModelSerializer):
    artista_nome = serializers.CharField(source='artista.nome', read_only=True)
    total_artes = serializers.SerializerMethodField()

    class Meta:
        model = Colecao
        fields = [
            'id',
            'artista',
            'artista_nome',
            'nome',
            'descricao',
            'ativa',
            'criado_em',
            'total_artes'
        ]
        read_only_fields = ['id', 'criado_em']

    def get_total_artes(self, obj):
        return obj.artes.count()


class ArteSerializer(serializers.ModelSerializer):
    artista_nome = serializers.CharField(source='artista.nome', read_only=True)
    colecao_nome = serializers.CharField(source='colecao.nome', read_only=True)

    class Meta:
        model = Arte
        fields = [
            'id',
            'artista',
            'artista_nome',
            'colecao',
            'colecao_nome',
            'nome',
            'arquivo',
            'descricao',
            'ativa',
            'criado_em'
        ]
        read_only_fields = ['id', 'criado_em']


class PersonalizacaoSerializer(serializers.ModelSerializer):
    arte_nome = serializers.CharField(source='arte.nome', read_only=True)

    class Meta:
        model = Personalizacao
        fields = [
            'id',
            'arte',
            'arte_nome',
            'texto',
            'fonte',
            'cor',
            'preco_extra',
            'criado_em'
        ]
        read_only_fields = ['id', 'criado_em']


class ColecaoDetailSerializer(ColecaoSerializer):
    """Serializer detalhado da Coleção com suas Artes"""
    artes = ArteSerializer(many=True, read_only=True)

    class Meta(ColecaoSerializer.Meta):
        fields = ColecaoSerializer.Meta.fields + ['artes']