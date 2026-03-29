# แยก view admin ออกมา
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import SystemUser
from .serializers import AdminUserSerializer
from .permissions import IsAdminRole


# GET ALL USERS + SEARCH + FILTER
@api_view(['GET'])
@permission_classes([IsAdminRole])
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
@permission_classes([IsAdminRole])
def admin_get_user(request, user_id):
    try:
        user = SystemUser.objects.get(userid=user_id)
        serializer = AdminUserSerializer(user)
        return Response(serializer.data)
    except SystemUser.DoesNotExist:
        return Response({"error": "User not found"}, status=404)


# UPDATE USER
@api_view(['PATCH'])
@permission_classes([IsAdminRole])
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
@permission_classes([IsAdminRole])
def admin_delete_user(request, user_id):
    try:
        user = SystemUser.objects.get(userid=user_id)
        user.delete()
        return Response({"message": "deleted"})
    except SystemUser.DoesNotExist:
        return Response({"error": "User not found"}, status=404)
    

# DASHBOARD
@api_view(['GET'])
@permission_classes([IsAdminRole])
def dashboard_summary(request):
    total_users = SystemUser.objects.count()
    authors = SystemUser.objects.filter(role='author').count()
    users = SystemUser.objects.filter(role='user').count()

    return Response({
        "total_users": total_users,
        "authors": authors,
        "users": users,
    })