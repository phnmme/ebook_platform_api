from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from django.contrib.auth import authenticate
from .serializers import RegisterSerializer, UsageHistorySerializer
from .permissions import IsAdminRole
from .services.usage_stats import (
    get_last_login,
    get_frequency,
    get_daily_frequency,
    get_monthly_frequency,
)
from .models import UsageHistory
from django.contrib.auth.signals import user_logged_in 


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        email = attrs.get("email") or attrs.get("username")
        password = attrs.get("password")

        user = authenticate(
            request=self.context.get("request"),
            username=email,
            password=password,
        )

        if not user or not user.is_active:
            raise AuthenticationFailed("No active account found with the given credentials")
        
        #สั่งให้บันทึกประวัติ Login
        request = self.context.get("request")
        user_logged_in.send(sender=user.__class__, request=request, user=user)

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


def _get_user_id(request):
    user_id = request.query_params.get("user_id")
    if user_id is None or user_id == "":
        return None, None
    try:
        return int(user_id), None
    except ValueError:
        return None, "user_id must be an integer"


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsAdminRole])
def usage_history(request):
    user_id, error = _get_user_id(request)
    if error:
        return Response({"error": error}, status=400)

    qs = UsageHistory.objects.all()
    if user_id:
        qs = qs.filter(user_id=user_id)

    serializer = UsageHistorySerializer(qs, many=True)
    return Response({"data": serializer.data})


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsAdminRole])
def usage_last_login(request):
    user_id, error = _get_user_id(request)
    if error:
        return Response({"error": error}, status=400)

    last_login = get_last_login(user_id=user_id)
    return Response({"timestamp": last_login.isoformat() if last_login else None})


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsAdminRole])
def usage_frequency(request):
    user_id, error = _get_user_id(request)
    if error:
        return Response({"error": error}, status=400)

    start = request.query_params.get("start")
    end = request.query_params.get("end")
    data = get_frequency(user_id=user_id, start=start, end=end)
    return Response(data)


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsAdminRole])
def usage_daily_frequency(request):
    user_id, error = _get_user_id(request)
    if error:
        return Response({"error": error}, status=400)

    start = request.query_params.get("start")
    end = request.query_params.get("end")
    data = get_daily_frequency(user_id=user_id, start=start, end=end)
    return Response(data)


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsAdminRole])
def usage_monthly_frequency(request):
    user_id, error = _get_user_id(request)
    if error:
        return Response({"error": error}, status=400)

    start = request.query_params.get("start")
    end = request.query_params.get("end")
    data = get_monthly_frequency(user_id=user_id, start=start, end=end)
    return Response(data)
