from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import *
from django.db import transaction

class ProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'unit_price', 'inventory', 'collection']

class SimpleProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title']

class ProductImageSerializer(ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'product']

class CollectionSerializer(ModelSerializer):
    products_count = serializers.IntegerField(read_only=True)
    products = ProductSerializer(many=True)

    class Meta:
        model = Collection
        fields = ['id', 'title', 'products_count', 'products']

class CollectionImageSerializer(ModelSerializer):
    class Meta:
        model = CollectionImage
        fields = ['id', 'image', 'collection']

class CartItemSerializer(ModelSerializer):
    total_price = serializers.SerializerMethodField(method_name='get_total_price')
    product = SimpleProductSerializer(read_only=True)

    def get_total_price(self, cart_item:CartItem):
        return cart_item.quantity*cart_item.product.unit_price

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'total_price']

class CartSerializer(ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    total_price = serializers.SerializerMethodField(method_name='get_total_price')
    items = CartItemSerializer(many=True, read_only=True)

    def get_total_price(self, cart : Cart):
        total = 0
        for item in cart.items.all():
            total += item.quantity * item.product.unit_price
        return total

    class Meta:
        model = Cart
        fields = ['id', 'created_at', 'items', 'total_price']

class UpdateCartItemSerialzer(ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']

class AddCartItemSerializer(ModelSerializer):
    product_id = serializers.IntegerField()

    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError(
                'No product with the given ID was found.')
        return value

    def save(self, **kwargs):
        cart_id = self.context['cart_id']
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']
        try:
            cart_item = CartItem.objects.get(cart_id=cart_id, product_id=product_id)
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item
        except:
            cart_item = CartItem.objects.create(cart_id=cart_id, **self.validated_data)
            self.instance = cart_item
        return self.instance

    class Meta:
        model = CartItem
        fields = ['id', 'product_id', 'quantity']



class CustomerSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Customer
        fields = ['id', 'user_id', 'phone', 'birth_date', 'membership']

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'street', 'city', 'customer']
    

class OrderItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'unit_price', 'quantity']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    address = AddressSerializer()

    class Meta:
        model = Order
        fields = ['id', 'customer', 'placed_at', 'payment_status', 'items', 'address']

class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['payment_status']

class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()
    address_id = serializers.IntegerField()

    def validate_cart_id(self, cart_id):
        if not Cart.objects.filter(pk=cart_id).exists():
            raise serializers.ValidationError(
                'No cart with the given ID was found.')
        if CartItem.objects.filter(cart_id=cart_id).count() == 0:
            raise serializers.ValidationError('The cart is empty.')
        return cart_id

    def save(self, **kwargs):
        with transaction.atomic():
            cart_id = self.validated_data['cart_id']
            address_id = self.validated_data['address_id']
            (customer, created) = Customer.objects.get_or_create(
                user_id=self.context['user_id'])
            order = Order.objects.create(customer=customer, address_id=address_id)

            cart_items = CartItem.objects \
                .select_related('product') \
                .filter(cart_id=cart_id)
            order_items = [
                OrderItem(
                    order=order,
                    product=item.product,
                    unit_price=item.product.unit_price,
                    quantity=item.quantity
                ) for item in cart_items
            ]
            OrderItem.objects.bulk_create(order_items)

            Cart.objects.filter(pk=cart_id).delete()
            print("#############", order)
            print("@@@@@@@@@@@@@", order_items)
            return order


            