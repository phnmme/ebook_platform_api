from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from django.contrib.auth import authenticate
from .serializers import RegisterSerializer


# Custom JWT — บังคับใช้ email ผ่าน EmailAuthBackend
class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        email = attrs.get("email") or attrs.get("username")
        password = attrs.get("password")

        user = authenticate(
            request=self.context.get("request"),
            username=email,  # EmailAuthBackend รับ username เป็น email
            password=password,
        )

        if not user or not user.is_active:
            raise AuthenticationFailed("No active account found with the given credentials")

        refresh = self.get_token(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }


class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer


@api_view(['POST'])
def register_user(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "registered"}, status=201)
    return Response(serializer.errors, status=400)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reset_password(request):
    new_password = request.data.get("new_password")
    if not new_password:
        return Response({"error": "กรุณาระบุ new_password"}, status=400)

    request.user.set_password(new_password)
    request.user.save()
    return Response({"message": "password changed"})