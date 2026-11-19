from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone
from django.urls import reverse

from .forms import AvailabilityForm, UserSkillsForm
from .models import Availability, Category, UserSkill


def index(request):
    """
    Public index page.

    Displays:
    - available skill categories
    - upcoming anonymous availabilities
    """

    categories = (
        Category.objects
        .prefetch_related("skills")
        .all()
    )

    upcoming_availabilities = (
        Availability.objects
        .filter(
            date__gte=timezone.localdate(),
            is_booked=False,
        )
        .select_related(
			"user",
            "skill",
            "skill__category",
        )
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

@login_required
def my_skills(request):

    # Retrieve only categories in which the connected user
    # already owns at least one skill.
    categories = (
        Category.objects
        .filter(
            skills__user_skills__user=request.user
        )
        .distinct()
        .order_by("name")
    )

    category_id = (
        request.POST.get("category")
        if request.method == "POST"
        else request.GET.get("category")
    )

    selected_category = None

    if category_id:
        selected_category = (
            categories
            .filter(id=category_id)
            .first()
        )

    if request.method == "POST":

        current_skill_ids = (
            UserSkill.objects
            .filter(
                user=request.user,
                skill__category=selected_category,
            )
            .values_list(
                "skill_id",
                flat=True,
            )
        )

        form = UserSkillsForm(
            request.POST,
            category=selected_category,
            selected_skills=current_skill_ids,
        )

        if form.is_valid():

            selected_skills = form.cleaned_data["skills"]

            UserSkill.objects.filter(
                user=request.user,
                skill__category=selected_category,
            ).delete()

            UserSkill.objects.bulk_create(
                [
                    UserSkill(
                        user=request.user,
                        skill=skill,
                    )
                    for skill in selected_skills
                ]
            )

            redirect_url = reverse(
                "exchange:my_skills"
            )

            return redirect(
                f"{redirect_url}"
                f"?category={selected_category.id}"
            )

    elif selected_category:

        current_skill_ids = (
            UserSkill.objects
            .filter(
                user=request.user,
                skill__category=selected_category,
            )
            .values_list(
                "skill_id",
                flat=True,
            )
        )

        form = UserSkillsForm(
            category=selected_category,
            selected_skills=current_skill_ids,
            initial={
                "category": selected_category,
                "skills": current_skill_ids,
            },
        )

    else:
        form = UserSkillsForm()

    context = {
        "form": form,
        "categories": categories,
        "selected_category": selected_category,
    }

    return render(
        request,
        "exchange/my_skills.html",
        context,
    )

@login_required
def my_availabilities(request):
    """
    Allows a connected user to create
    and display their upcoming availabilities.
    """

    if request.method == "POST":

        form = AvailabilityForm(
            request.POST,
            user=request.user,
        )

        if form.is_valid():

            availability = form.save(
                commit=False
            )

            availability.user = request.user

            availability.save()

            return redirect(
                "exchange:my_availabilities"
            )

    else:

        form = AvailabilityForm(
            user=request.user
        )

    availabilities = (
        Availability.objects
        .filter(
            user=request.user,
            date__gte=timezone.localdate(),
        )
        .select_related(
            "skill",
            "skill__category",
        )
        .order_by(
            "date",
            "skill__name",
        )
    )

    context = {
        "form": form,
        "availabilities": availabilities,
    }

    return render(
        request,
        "exchange/my_availabilities.html",
        context,
    )