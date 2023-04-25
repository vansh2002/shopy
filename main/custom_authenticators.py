from rest_framework_simplejwt.authentication import JWTAuthentication

class CustomAuthentication(JWTAuthentication):
    def authenticate(self, request):
        if request.method == 'GET':
            return None
        return super().authenticate(request)