from django.contrib import admin
from django.urls import path
from member.views import (
    chart_monthly,
    chart_weekly,
    dashboard_stats,
    profile_view,
    register_user,
    reset_password,
    EmailTokenObtainPairView,
    usage_history,
    usage_last_login,
    usage_frequency,
    usage_daily_frequency,
    usage_monthly_frequency,
)
from rest_framework_simplejwt.views import TokenRefreshView
from member.views_admin import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/register/', register_user),
    path('api/reset-password/', reset_password),

    path("api/dashboard-stats/", dashboard_stats),
    path("api/chart-weekly/", chart_weekly),
    path("api/chart-monthly/", chart_monthly),


    path('api/login/', EmailTokenObtainPairView.as_view()),
    path('api/token/refresh/', TokenRefreshView.as_view()),
    
    path('api/profile', profile_view),

    path('api/admin/users/', admin_get_users),      # ส่ง role มาแยกประเภทได้ ?role=author , search ตามชื่อได้ ?fullname=picky , search ตามเลข userid ได้ *api/admin/users/2/
    path('api/admin/users/<int:user_id>/', admin_get_user),
    path('api/admin/users/<int:user_id>/update/', admin_update_user),
    path('api/admin/users/<int:user_id>/delete/', admin_delete_user),
    path('api/admin/dashboard/summary/', dashboard_summary),
    path('api/admin/dashboard/monthly/', dashboard_monthly),
    path('api/admin/dashboard/daily/', dashboard_daily),
    path('api/admin/top-users/', top_users_by_frequency),   #ส่ง role มาแยกประเภทได้ ?role=author

    path('admin/usage/history', usage_history),
    path('admin/usage/last-login', usage_last_login),
    path('admin/usage/frequency', usage_frequency),
    path('admin/usage/daily-frequency', usage_daily_frequency),
    path('admin/usage/monthly-frequency', usage_monthly_frequency),
]
