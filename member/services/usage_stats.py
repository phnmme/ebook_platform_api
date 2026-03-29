from datetime import datetime

from django.db.models import Count
from django.db.models.functions import TruncDate, TruncMonth
from django.utils import timezone

from member.models import UsageHistory


def _parse_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def _base_queryset(user_id=None, start=None, end=None):
    qs = UsageHistory.objects.all()
    if user_id:
        qs = qs.filter(user_id=user_id)

    start_date = _parse_date(start)
    end_date = _parse_date(end)

    if start_date:
        qs = qs.filter(timestamp__date__gte=start_date)
    if end_date:
        qs = qs.filter(timestamp__date__lte=end_date)

    return qs, start_date, end_date


def get_last_login(user_id=None):
    qs = UsageHistory.objects.filter(action="login")
    if user_id:
        qs = qs.filter(user_id=user_id)
    record = qs.order_by("-timestamp").first()
    return record.timestamp if record else None


def get_frequency(user_id=None, start=None, end=None):
    qs, start_date, end_date = _base_queryset(user_id=user_id, start=start, end=end)
    total = qs.filter(action="login").count()

    return {
        "total": total,
        "start": start_date.isoformat() if start_date else None,
        "end": end_date.isoformat() if end_date else None,
    }


def get_daily_frequency(user_id=None, start=None, end=None):
    qs, start_date, end_date = _base_queryset(user_id=user_id, start=start, end=end)
    rows = (
        qs.filter(action="login")
        .annotate(day=TruncDate("timestamp"))
        .values("day")
        .annotate(count=Count("id"))
        .order_by("day")
    )
    data = [{"date": r["day"].isoformat(), "count": r["count"]} for r in rows]

    return {
        "start": start_date.isoformat() if start_date else None,
        "end": end_date.isoformat() if end_date else None,
        "data": data,
    }


def get_monthly_frequency(user_id=None, start=None, end=None):
    qs, start_date, end_date = _base_queryset(user_id=user_id, start=start, end=end)
    rows = (
        qs.filter(action="login")
        .annotate(month=TruncMonth("timestamp"))
        .values("month")
        .annotate(count=Count("id"))
        .order_by("month")
    )
    data = [{"month": r["month"].date().isoformat()[:7], "count": r["count"]} for r in rows]

    return {
        "start": start_date.isoformat() if start_date else None,
        "end": end_date.isoformat() if end_date else None,
        "data": data,
    }
