from django.shortcuts import render
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from .models import Availability, Category
from .forms import UserSkillsForm
from .models import UserSkill


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

@login_required
def my_skills(request):

    current_user_skills = UserSkill.objects.filter(
        user=request.user
    )

    selected_skills = [
        user_skill.skill
        for user_skill in current_user_skills
    ]

    if request.method == "POST":

        form = UserSkillsForm(request.POST)

        if form.is_valid():

            selected_skills = form.cleaned_data["skills"]

            UserSkill.objects.filter(
                user=request.user
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

            return redirect(
                "exchange:my_skills"
            )

    else:

        form = UserSkillsForm(
            initial={
                "skills": selected_skills,
            }
        )

    context = {
        "form": form,
    }

    return render(
        request,
        "exchange/my_skills.html",
        context,
    )