from django.views.generic import TemplateView, ListView
from django.db.models import Sum, Count
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from .models import (
    Recompensa, UsuarioRecompensa, Pontos, Nivel, Badge, Ranking
)
from .serializers import RecompensaSerializer, UsuarioRecompensaSerializer


class RecompensaViewSet(viewsets.ModelViewSet):
    queryset = Recompensa.objects.all()
    serializer_class = RecompensaSerializer


class UsuarioRecompensaViewSet(viewsets.ModelViewSet):
    queryset = UsuarioRecompensa.objects.all()
    serializer_class = UsuarioRecompensaSerializer
    
    @action(detail=False, methods=['get'])
    def por_usuario(self, request):
        usuario_id = request.query_params.get('usuario_id')
        if not usuario_id:
            return Response({'erro': 'usuario_id é obrigatório'}, status=status.HTTP_400_BAD_REQUEST)
        
        recompensas = UsuarioRecompensa.objects.filter(usuario_id=usuario_id)
        serializer = self.get_serializer(recompensas, many=True)
        return Response(serializer.data)


# ===== VIEWS BASEADAS EM CLASSE PARA TEMPLATES =====

class GamificationDashboardView(TemplateView):
    """Dashboard de gamificação do usuário"""
    template_name = 'gamification/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.request.user

        # Pontos do usuário
        try:
            pontos = Pontos.objects.get(usuario=usuario)
        except Pontos.DoesNotExist:
            pontos = Pontos.objects.create(usuario=usuario)

        # Badges desbloqueados
        badges = UsuarioRecompensa.objects.filter(usuario=usuario).select_related('badge')

        # Nível do usuário
        nivel = None
        niveis = Nivel.objects.all().order_by('numero')
        for n in niveis:
            if pontos.saldo >= n.pontos_minimos:
                nivel = n

        # Ranking
        ranking = Ranking.objects.filter(
            usuario=usuario,
            tipo='usuarios'
        ).first()

        # Estatísticas
        stats = {
            'pontos_saldo': pontos.saldo,
            'pontos_total': pontos.total_acumulado,
            'badges_desbloqueados': badges.count(),
            'nivel_atual': nivel,
            'posicao_ranking': ranking.posicao if ranking else 'N/A',
        }

        context.update({
            'stats': stats,
            'badges': badges,
            'nivel': nivel,
            'niveis': niveis,
            'ranking': ranking,
        })

        return context


class BadgesListView(ListView):
    """Lista de todos os badges disponíveis"""
    model = Badge
    template_name = 'gamification/badges_list.html'
    context_object_name = 'badges'
    paginate_by = 12

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.request.user
        
        # Badges desbloqueados por este usuário
        desbloqueados = UsuarioRecompensa.objects.filter(
            usuario=usuario
        ).values_list('badge_id', flat=True)
        
        context['badges_desbloqueados'] = desbloqueados
        return context


class RankingListView(ListView):
    """Ranking de usuários"""
    model = Ranking
    template_name = 'gamification/ranking_list.html'
    context_object_name = 'ranking'
    paginate_by = 20

    def get_queryset(self):
        return Ranking.objects.filter(tipo='usuarios').order_by('posicao')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Posição do usuário atual
        posicao_usuario = Ranking.objects.filter(
            usuario=self.request.user,
            tipo='usuarios'
        ).first()
        context['posicao_usuario'] = posicao_usuario
        return context