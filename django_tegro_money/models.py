from django.db import models
from django.db.models import Index


class TegroMoneyOrder(models.Model):
    """
        Orders
    """
    shop_id = models.CharField(max_length=50, verbose_name='Shop identifier', null=True, blank=True)
    order_id = models.IntegerField(verbose_name='Tegro money order identifier', null=True, blank=True)
    payment_id = models.CharField(max_length=50, verbose_name='Shop order identifier', null=True, blank=True)
    date_created = models.DateTimeField(verbose_name='Order time created', null=True, blank=True)
    date_payed = models.DateTimeField(verbose_name='Order time payed', null=True, blank=True)
    payment_system = models.IntegerField(verbose_name='Payment system identifier', null=True, blank=True)
    currency = models.CharField(max_length=10, verbose_name='Currency', null=True, blank=True)
    currency_id = models.IntegerField(verbose_name='Currency identifier', null=True, blank=True)
    amount = models.DecimalField(max_digits=19, decimal_places=8, verbose_name='Amount', null=True, blank=True)
    fee = models.DecimalField(max_digits=19, decimal_places=8, verbose_name='Fee', null=True, blank=True)
    status = models.IntegerField(verbose_name='Order status', null=True, blank=True, default=-1)
    test_order = models.IntegerField(verbose_name='Test order flag', null=True, blank=True, default=0)

    def __str__(self):
        return self.payment_id

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['shop_id', 'date_created']
        indexes = (
            Index(fields=['shop_id', 'date_created'], name='order_created'),
            Index(fields=['shop_id', 'order_id'], name='order_order_id'),
            Index(fields=['shop_id', 'payment_id'], name='order_payment_id'),
            Index(fields=['shop_id', 'status', 'date_created'], name='order_status_created'),
        )


class TegroMoneyOrderFields(models.Model):
    """
        Order buyer details
    """
    order = models.ForeignKey('TegroMoneyOrder', on_delete=models.PROTECT, verbose_name='Order')
    field_name = models.CharField(max_length=50, verbose_name='Field name', null=True, blank=True)
    field_value = models.CharField(max_length=50, verbose_name='Field value', null=True, blank=True)

    class Meta:
        verbose_name = 'Order buyer details'
        verbose_name_plural = 'Order buyer details'
        ordering = ['order']


class TegroMoneyOrderReceipt(models.Model):
    """
        Order shopping cart data
    """
    order = models.ForeignKey('TegroMoneyOrder', on_delete=models.PROTECT, verbose_name='Order')
    name = models.CharField(max_length=50, verbose_name='Item name', null=True, blank=True)
    count = models.DecimalField(max_digits=19, decimal_places=8, verbose_name='Item count', null=True, blank=True)
    price = models.DecimalField(max_digits=19, decimal_places=8, verbose_name='Item price', null=True, blank=True)

    class Meta:
        verbose_name = 'Order shopping cart data'
        verbose_name_plural = 'Order shopping cart data'
        ordering = ['order']
