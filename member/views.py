import calendar
from datetime import timedelta
from django.utils import timezone

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
from .models import SystemUser, UsageHistory
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
            "user": {
                "id": user.userid,       
                "email": user.email,
                "fullname": user.fullname,
                "role": user.role
            }
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


from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    user = request.user

    if request.method == 'GET':
        # คืนค่าข้อมูลโปรไฟล์
        return Response({
            "id": getattr(user, "pk", getattr(user, "userid", None)),
            "email": getattr(user, "email", ""),
            "fullname": getattr(user, "fullname", ""),
            "phone": getattr(user, "phone", ""),
            "role": getattr(user, "role", ""),
            "expertise": getattr(user, "expertise", ""),
            "date_joined": user.date_joined,
            "last_login": user.last_login,
        })

    elif request.method == 'PUT':
        # อัปเดตข้อมูลโปรไฟล์
        data = request.data
        email = data.get("email")
        phone = data.get("phone")
        expertise = data.get("expertise")

        if email:
            user.email = email.strip()
        if phone:
            user.phone = phone.strip()
        if user.role == 'author' and expertise is not None:
            user.expertise = expertise.strip()

        user.save()

        return Response({
            "success": True,
            "user": {
                "id": getattr(user, "pk", getattr(user, "userid", None)),
                "email": user.email,
                "fullname": user.fullname,
                "phone": user.phone,
                "role": user.role,
                "expertise": user.expertise,
                "date_joined": user.date_joined,
                "last_login": user.last_login,
            }
        }, status=status.HTTP_200_OK)


# =========================================
# Dashboard Stats 
# =========================================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    now = timezone.localtime(timezone.now())

    total_users = SystemUser.objects.filter(role='user').count()
    total_authors = SystemUser.objects.filter(role='author').count()
    total_admins = SystemUser.objects.filter(role='admin').count()
    active_users = SystemUser.objects.filter(is_active=True).count()

    new_users_today = SystemUser.objects.filter(date_joined__date=now.date()).count()

    week_start = now - timedelta(days=now.weekday())
    new_users_this_week = SystemUser.objects.filter(date_joined__gte=week_start).count()

    new_users_this_month = SystemUser.objects.filter(
        date_joined__year=now.year,
        date_joined__month=now.month
    ).count()

    data = {
        'total_users': total_users,
        'total_authors': total_authors,
        'total_admins': total_admins,
        'active_users': active_users,
        'new_users_today': new_users_today,
        'new_users_this_week': new_users_this_week,
        'new_users_this_month': new_users_this_month,
    }
    return Response(data)


# =========================================
# Chart Weekly — จำนวน Users & Authors ต่อวัน
# =========================================
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def chart_weekly(request):
    now = timezone.localtime(timezone.now())
    week_start = now - timedelta(days=now.weekday())
    labels = []
    users_data = []
    authors_data = []

    for i in range(7):
        day_start = (week_start + timedelta(days=i)).replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        labels.append(day_start.strftime("%a"))

        users_count = SystemUser.objects.filter(role="user", date_joined__gte=day_start, date_joined__lt=day_end).count()
        authors_count = SystemUser.objects.filter(role="author", date_joined__gte=day_start, date_joined__lt=day_end).count()

        users_data.append(users_count)
        authors_data.append(authors_count)

    data = [{"label": labels[i], "users": users_data[i], "authors": authors_data[i]} for i in range(7)]
    return Response(data)


# =========================================
# Chart Monthly — จำนวน Users & Authors ต่อเดือน
# =========================================
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def chart_monthly(request):
    now = timezone.localtime(timezone.now())
    labels = []
    users_data = []
    authors_data = []

    for month in range(1, 13):
        month_start = now.replace(month=month, day=1, hour=0, minute=0, second=0, microsecond=0)
        last_day = calendar.monthrange(month_start.year, month_start.month)[1]
        month_end = month_start.replace(day=last_day, hour=23, minute=59, second=59)

        labels.append(month_start.strftime("%b"))

        users_count = SystemUser.objects.filter(
            role="user",
            date_joined__gte=month_start,
            date_joined__lte=month_end
        ).count()

        authors_count = SystemUser.objects.filter(
            role="author",
            date_joined__gte=month_start,
            date_joined__lte=month_end
        ).count()

        users_data.append(users_count)
        authors_data.append(authors_count)

    data = [{"label": labels[i], "users": users_data[i], "authors": authors_data[i]} for i in range(12)]
    return Response(data)
