from rest_framework import serializers
from .models import Tipouser, user, userTelefone

class TipouserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tipouser
        fields = [
            'id',
            'nome',
        ]

class userSerializer(serializers.ModelSerializer):
    tipo_usuario = TipouserSerializer(read_only=True)

    class Meta:
        model = user
        fields = [
            'id',
            'nome',
            'email',
            'status',
            'data_cadastro',
            'tipo_usuario',
        ]

class UserListSerializer(serializers.ModelSerializer):
    #Serializer para listagem de usuários#
    class Meta:
        model = user
        fields = [
            'id',
            'nome',
            'email',
            'status',
        ]

class UserDetailSerializer(serializers.ModelSerializer):
    #Serializer para detalhes completos do usuário#
    tipo_usuario = TipouserSerializer(read_only=True)
    telefones = serializers.SerializerMethodField()

    class Meta:
        model = user
        fields = [
            'id',
            'nome',
            'email',
            'status',
            'data_cadastro',
            'tipo_usuario',
            'telefones',
        ]

    def get_telefones(self, obj):
        telefones = obj.telefones.all()
        return UserTelefoneSerializer(telefones, many=True).data

class UserCreateSerializer(serializers.ModelSerializer):
    #Serializer para criar novo usuário#
    class Meta:
        model = user
        fields = [
            'nome',
            'email',
            'status',
            'tipo_usuario',
        ]

class UserTelefoneSerializer(serializers.ModelSerializer):
    usuario = userSerializer(read_only=True)

    class Meta:
        model = userTelefone
        fields = [
            'id',
            'usuario',
            'numero_telefone',
            'tipo_telefone',
        ]
