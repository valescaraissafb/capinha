from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'amount', 'method', 'status', 'created_at', 'paid_at')
    list_filter = ('status', 'method', 'created_at', 'paid_at')
    search_fields = ('reference_id',)
    readonly_fields = ('created_at', 'paid_at')
    
    fieldsets = (
        ('Informações do Pagamento', {
            'fields': ('amount', 'method', 'reference_id')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Datas', {
            'fields': ('created_at', 'paid_at')
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Edição
            return self.readonly_fields + ('amount', 'method')
        return self.readonly_fields
