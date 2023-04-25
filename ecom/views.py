from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from .pagination import DefaultPagination
from .serializers import *
from django.db.models.aggregates import Count
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import *
from rest_framework.authentication import *
from .permissions import *
from rest_framework_simplejwt.authentication import *
from django.core.paginator import Paginator

# Create your views here.
class CustomerViewSet(ModelViewSet):
    serializer_class = CustomerSerializer
    queryset = Customer.objects.all()

class AddressViewSet(ModelViewSet):
    serializer_class = AddressSerializer
    queryset = Address.objects.all()

    def create(self, request, *args, **kwargs):
        (customer, created) = Customer.objects.get_or_create(user=request.user)
        request.data['customer'] = customer.id
        serializer = AddressSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # Validate the serializer data
        serializer.save()  # Save the serializer data
        return Response(serializer.data, status=201)

class ProductViewSet(ModelViewSet):
    serializer_class = ProductSerializer
    pagination_class = DefaultPagination
    permission_classes = [IsAdminOrReadOnly]
    
    def get_queryset(self):
        queryset = Product.objects.all()
        search_query = self.request.query_params.get('q', None)
        if search_query is not None:
            queryset = queryset.filter(title__icontains=search_query)
        return queryset

    # def list(self, request, *args, **kwargs):
    #     serializer = self.serializer_class(self.get_queryset(), many=True, context={'cart_id': 0})
    #     return Response(serializer.data)

class CollectionViewSet(ModelViewSet):
    serializer_class = CollectionSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = DefaultPagination

    def get_queryset(self):
        queryset = Collection.objects.annotate(products_count=Count('products')).prefetch_related('products').all()
        return queryset

class CollectionImageViewSet(ModelViewSet):
    serializer_class = CollectionImageSerializer
    
    def get_queryset(self):
        queryset = CollectionImage.objects.filter(collection_id=self.kwargs['collection_pk']).select_related('collection')
        return queryset

class CartViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'delete']
    serializer_class = CartSerializer
    queryset = Cart.objects.prefetch_related('items__product').all()

    def create(self, request, *args, **kwargs):
        user = request.user
        if not Cart.objects.filter(user=user).exists():
            cart = Cart.objects.create(user=user)
        cart = Cart.objects.get(user=user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

class CartItemViewSet(ModelViewSet):
    http_method_names = ['get', 'patch', 'delete', 'post']
    
    def get_queryset(self):
        cart_id = self.kwargs['cart_pk']
        return CartItem.objects.filter(cart_id=cart_id).select_related('product')

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return UpdateCartItemSerialzer
        elif self.request.method == 'POST':
            return AddCartItemSerializer
        return CartItemSerializer
    
    def get_serializer_context(self):
        return {'cart_id': self.kwargs['cart_pk']}

class ProductImageViewSet(ModelViewSet):
    serializer_class = ProductImageSerializer
    permission_classes = [IsAdminOrReadOnly]
    
    def get_queryset(self):
        return ProductImage.objects.filter(product_id=self.kwargs['product_pk']).select_related('product')

    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}

class OrderViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']
 
    def create(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(
            data=request.data,
            context={'user_id': self.request.user.id})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateOrderSerializer
        elif self.request.method == 'PATCH':
            return UpdateOrderSerializer
        return OrderSerializer

    def get_queryset(self):
        
        return Order.objects.all()

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Cart, CartItem

@api_view(['POST'])
def transfer_cart_data(request):
    # Retrieve cart data from local storage
    cart_data = request.data.get('cart')  # Assuming the cart data is sent as JSON in the request body
    user_id = request.data.get('user_id')
    print('$$$$$$$$$$$$$$$$$$$$$$$$$', cart_data)
    # Check if cart data is available
    if cart_data:
        cart = None
        if Cart.objects.filter(user_id=user_id).exists():
            cart = Cart.objects.get(user_id=user_id)
        else:
            cart = Cart.objects.create(user_id=user_id)
        for item in cart_data:
            if CartItem.objects.filter(cart=cart, product_id=item['product_id']).exists():
                # If product already exists in cart, update the quantity
                cart_item = CartItem.objects.get(cart=cart, product_id=item['product_id'])
                cart_item.quantity += item['quantity']
                cart_item.save()
            else:
                # If product doesn't exist in cart, create a new cart item
                cart_item = CartItem.objects.create(cart=cart, product_id=item['product_id'], quantity=item['quantity'])
        
        return Response({'message': 'Cart data transferred to database successfully.'})
    else:
        return Response({'message': 'No cart data found.'}, status=400)
