"""
URL configuration for shop_ease_api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.http import JsonResponse
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="ShopEase",
        default_version='v1',
        description="Modern e-commerce system seamlessly manages products, wishlists, carts, and orders, with a user-friendly interface."
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


def health_check(request):
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path('', health_check, name='health_check'),

    # Swagger documentation routes
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0),
         name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger',
         cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc',
         cache_timeout=0), name='schema-redoc'),

    # Admin (commented out but available if needed)
    # path('admin/', admin.site.urls),

    # API versioned routes
    path('api/v1/', include('users.urls', namespace='users')),
    path('api/v1/', include('categories.urls', namespace='categories')),
    path('api/v1/', include('products.urls', namespace='products')),
    path('api/v1/', include('reviews.urls', namespace='reviews')),
    path('api/v1/', include('cart.urls', namespace='cart')),
    path('api/v1/', include('wishlist.urls', namespace='wishlist')),
    path('api/v1/', include('orders.urls', namespace='orders')),
    path('api/v1/', include('offers.urls', namespace='offers')),
    path('api/v1/', include('payments.urls', namespace='payments')),
    path('api/v1/', include('notifications.urls', namespace='notifications')),
]
