from django.contrib import admin
from django.urls import path
from member.views import (
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

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/register/', register_user),
    path('api/reset-password/', reset_password),

    path('api/login/', EmailTokenObtainPairView.as_view()),
    path('api/token/refresh/', TokenRefreshView.as_view()),

    path('admin/usage/history', usage_history),
    path('admin/usage/last-login', usage_last_login),
    path('admin/usage/frequency', usage_frequency),
    path('admin/usage/daily-frequency', usage_daily_frequency),
    path('admin/usage/monthly-frequency', usage_monthly_frequency),
]
