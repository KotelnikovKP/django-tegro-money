from django.conf import settings


TEGRO_MONEY_SHOP_ID = getattr(settings, 'TEGRO_MONEY_SHOP_ID', '')
TEGRO_MONEY_SECRET_KEY = getattr(settings, 'TEGRO_MONEY_SECRET_KEY', '')
TEGRO_MONEY_API_KEY = getattr(settings, 'TEGRO_MONEY_API_KEY', '')
