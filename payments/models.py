from django.db import models
from django.conf import settings


class Payment(models.Model):
    """
    Modelo de Pagamento - Vinculado a um Pedido.
    Registra e rastreia todos os pagamentos do sistema.
    """

    PAYMENT_METHODS = [
        ("pix", "Pix"),
        ("credit_card", "Cartão de Crédito"),
        ("debit_card", "Cartão de Débito"),
        ("boleto", "Boleto"),
    ]

    PAYMENT_STATUS = [
        ("pending", "Pendente"),
        ("paid", "Pago"),
        ("canceled", "Cancelado"),
        ("refunded", "Reembolsado"),
        ("failed", "Falhou"),
    ]

    # Relações críticas
    pedido = models.OneToOneField(
        'orders.Pedido',
        on_delete=models.CASCADE,
        related_name='pagamento',
        null=True,
        blank=True,
        help_text="Pedido associado a este pagamento"
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='pagamentos',
        null=True,
        blank=True,
        help_text="Usuário que realizou o pagamento"
    )

    # Informações de pagamento
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    status = models.CharField(
        max_length=20, choices=PAYMENT_STATUS, default="pending"
    )
    reference_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Rastreamento temporal
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Pagamento"
        verbose_name_plural = "Pagamentos"
        ordering = ['-created_at']

    def __str__(self):
        return f"Pagamento #{self.id} - {self.get_status_display()}"
