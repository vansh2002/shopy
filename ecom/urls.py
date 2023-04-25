from django.urls import path
from rest_framework_nested import routers
from .views import *

router = routers.DefaultRouter()
router.register('products', ProductViewSet, basename='products')
router.register('collections', CollectionViewSet, basename='collections')
router.register('carts', CartViewSet)
router.register('orders', OrderViewSet, basename='orders')
router.register('customers', CustomerViewSet)
router.register('address', AddressViewSet)

products_router = routers.NestedDefaultRouter(router, 'products', lookup='product')
products_router.register('images', ProductImageViewSet, basename='product-images')

collections_router = routers.NestedDefaultRouter(router, 'collections', lookup='collection')
collections_router.register('images', CollectionImageViewSet, basename='collection-images')

carts_router = routers.NestedDefaultRouter(router, 'carts', lookup='cart')
carts_router.register('items', CartItemViewSet, basename='cart-items')

urlpatterns = [
    path('transfer-cart-data/', transfer_cart_data, name='transfer_cart_data'),

] + router.urls + carts_router.urls + products_router.urls + collections_router.urls