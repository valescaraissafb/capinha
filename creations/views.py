from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Colecao, Arte, Personalizacao
from .serializers import (
    ColecaoSerializer,
    ColecaoDetailSerializer,
    ArteSerializer,
    PersonalizacaoSerializer
)


class ColecaoViewSet(ModelViewSet):
    queryset = Colecao.objects.filter(ativa=True)
    serializer_class = ColecaoSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ColecaoDetailSerializer
        return ColecaoSerializer

    def perform_create(self, serializer):
        serializer.save(artista=self.request.user.artista)

    @action(detail=True, methods=['get'])
    def artes(self, request, pk=None):
        """Lista todas as artes de uma coleção"""
        colecao = self.get_object()
        artes = colecao.artes.filter(ativa=True)
        serializer = ArteSerializer(artes, many=True)
        return Response(serializer.data)


class ArteViewSet(ModelViewSet):
    queryset = Arte.objects.filter(ativa=True)
    serializer_class = ArteSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(artista=self.request.user.artista)

    @action(detail=False, methods=['get'])
    def por_colecao(self, request):
        """Lista artes filtradas por coleção"""
        colecao_id = request.query_params.get('colecao_id')
        if colecao_id:
            artes = Arte.objects.filter(
                colecao_id=colecao_id,
                ativa=True
            )
            serializer = self.get_serializer(artes, many=True)
            return Response(serializer.data)
        return Response({'erro': 'colecao_id é obrigatório'}, status=400)

    @action(detail=False, methods=['get'])
    def do_artista(self, request):
        """Lista artes do artista autenticado"""
        artes = Arte.objects.filter(
            artista=request.user.artista,
            ativa=True
        )
        serializer = self.get_serializer(artes, many=True)
        return Response(serializer.data)


class PersonalizacaoViewSet(ModelViewSet):
    queryset = Personalizacao.objects.all()
    serializer_class = PersonalizacaoSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def por_arte(self, request):
        """Lista personalizações filtradas por arte"""
        arte_id = request.query_params.get('arte_id')
        if arte_id:
            personalizacoes = Personalizacao.objects.filter(arte_id=arte_id)
            serializer = self.get_serializer(personalizacoes, many=True)
            return Response(serializer.data)
        return Response({'erro': 'arte_id é obrigatório'}, status=400)
