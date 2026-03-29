# แยก view admin ออกมา
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Count
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import AdminUserSerializer
from .permissions import IsAdminRole
from django.utils.timezone import now
from datetime import timedelta
from .models import SystemUser, UsageHistory
from .views import get_monthly_frequency , get_daily_frequency



# GET ALL USERS + SEARCH + FILTER
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminRole])
def admin_get_users(request):
    role = request.GET.get('role')
    fullname = request.GET.get('fullname')

    users = SystemUser.objects.all()

    if role:
        users = users.filter(role=role)

    if fullname:
        users = users.filter(fullname__icontains=fullname)

    serializer = AdminUserSerializer(users, many=True)
    return Response(serializer.data)


# GET USER DETAIL
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminRole])
def admin_get_user(request, user_id):
    try:
        user = SystemUser.objects.get(userid=user_id)
        serializer = AdminUserSerializer(user)
        return Response(serializer.data)
    except SystemUser.DoesNotExist:
        return Response({"error": "User not found"}, status=404)


# UPDATE USER
@api_view(['PATCH'])
@permission_classes([IsAuthenticated, IsAdminRole])
def admin_update_user(request, user_id):
    try:
        user = SystemUser.objects.get(userid=user_id)
        serializer = AdminUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    except SystemUser.DoesNotExist:
        return Response({"error": "User not found"}, status=404)


# DELETE USER
@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAdminRole])
def admin_delete_user(request, user_id):
    try:
        user = SystemUser.objects.get(userid=user_id)
        user.delete()
        return Response({"message": "deleted"})
    except SystemUser.DoesNotExist:
        return Response({"error": "User not found"}, status=404)
    

# DASHBOARD SUMMARY
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminRole])
def dashboard_summary(request):
    total_users = SystemUser.objects.count()
    authors = SystemUser.objects.filter(role='author').count()
    users = SystemUser.objects.filter(role='user').count()
    admins = SystemUser.objects.filter(role='admin').count()

    # เดือนปัจจุบัน
    today = now()
    start_month = today.replace(day=1)

    total_logins = UsageHistory.objects.filter(
        action='login',
        timestamp__gte=start_month
    ).count()

    avg_login = total_logins / total_users if total_users > 0 else 0

    return Response({
        "total_users": total_users,
        "authors": authors,
        "users": users,
        "admins": admins,
        "avg_login_per_user": round(avg_login, 2)
    })

#DASHBOARD GRAPH (MONTHLY)
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminRole])
def dashboard_monthly(request):
    data = get_monthly_frequency()
    return Response(data)

#DASHBOARD GRAPH (DAILY)
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminRole])
def dashboard_daily(request):
    data = get_daily_frequency()
    return Response(data)

#SORT USER,AUTHOR FROM FREQUENCY
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminRole])
def top_users_by_frequency(request):
    role = request.GET.get('role')

    qs = UsageHistory.objects.filter(action='login')

    if role:
        qs = qs.filter(user__role=role)

    data = (
        qs.values(
            'user__userid',  
            'user__email',
            'user__fullname',
            'user__role'
        )
        .annotate(login_count=Count('id'))
        .order_by('-login_count')
    )

    return Response(list(data))