import jwt
from django.conf import settings
from django.http import HttpResponse


class AdminRoleCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the route is one of the 'admin' routes
        if request.path.startswith('/api/admin/'):
            # Extract token from the authorization header
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return HttpResponse("Unauthorized", status=401)

            token = auth_header.split(' ')[1]

            try:
                decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                user_id = decoded_token.get('user_id')
            except jwt.ExpiredSignatureError:
                return HttpResponse("Token has expired", status=401)
            except jwt.InvalidTokenError:
                return HttpResponse("Invalid token", status=401)

            # Check user role from the database
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT role FROM users WHERE id = %s", [user_id])
                result = cursor.fetchone()
                if not result or result[0] != 1:
                    return HttpResponse("Forbidden: Admin access required", status=403)

        return self.get_response(request)
