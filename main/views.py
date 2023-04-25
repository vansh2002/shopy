from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import *
from .models import *
from .serializers import *

# Create your views here.
class UserViewSet(ModelViewSet):
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return RegisterSerializer
        return UserSerializer