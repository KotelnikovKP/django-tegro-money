from django.contrib import admin

from django_tegro_money.models import *


class TegroMoneyOrderAdmin(admin.ModelAdmin):
    list_display = ['shop_id', 'order_id', 'payment_id', 'date_created', 'date_payed', 'payment_system',
                    'currency', 'currency_id', 'amount', 'fee', 'status', 'test_order']
    list_display_links = tuple()
    search_fields = ('shop_id', 'order_id', 'payment_id', 'date_created', 'date_payed', 'payment_system',
                     'currency', 'currency_id', 'amount', 'fee', 'status', 'test_order')
    fields = ('shop_id', 'order_id', 'payment_id', 'date_created', 'date_payed', 'payment_system',
              'currency', 'currency_id', 'amount', 'fee', 'status', 'test_order')
    list_filter = ('shop_id', 'order_id', 'payment_id', 'date_created', 'date_payed', 'payment_system',
                   'currency', 'currency_id', 'amount', 'fee', 'status', 'test_order')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(TegroMoneyOrder, TegroMoneyOrderAdmin)


class TegroMoneyOrderFieldsAdmin(admin.ModelAdmin):
    list_display = ['order', 'field_name', 'field_value']
    list_display_links = tuple()
    search_fields = ('order', 'field_name', 'field_value')
    fields = ('order', 'field_name', 'field_value')
    list_filter = ('order', 'field_name', 'field_value')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(TegroMoneyOrderFields, TegroMoneyOrderFieldsAdmin)


class TegroMoneyOrderReceiptAdmin(admin.ModelAdmin):
    list_display = ['order', 'name', 'count', 'price']
    list_display_links = tuple()
    search_fields = ('order', 'name', 'count', 'price')
    fields = ('order', 'name', 'count', 'price')
    list_filter = ('order', 'name', 'count', 'price')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(TegroMoneyOrderReceipt, TegroMoneyOrderReceiptAdmin)

