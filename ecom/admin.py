from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Cart)
admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(Collection)
admin.site.register(CollectionImage)