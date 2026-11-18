from django.shortcuts import render
from django.utils import timezone

from .models import Availability, Category


def index(request):
    categories = Category.objects.prefetch_related("skills").all()

    upcoming_availabilities = (
        Availability.objects
        .filter(
            date__gte=timezone.localdate(),
            is_booked=False,
        )
        .select_related("skill", "skill__category")
        .order_by("date")[:10]
    )

    context = {
        "categories": categories,
        "upcoming_availabilities": upcoming_availabilities,
    }

    return render(
        request,
        "exchange/index.html",
        context,
    )