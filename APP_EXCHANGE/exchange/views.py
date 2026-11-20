from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone
from django.urls import reverse
from django.core.paginator import Paginator
from django.contrib import messages

from .forms import AvailabilityForm, UserSkillsForm, HelpRequestForm
from .models import Availability, Category, UserSkill, HelpRequest


def index(request):
	"""
	Public index page.

	Displays:
	- upcoming help offers
	- upcoming help requests
	- all items sorted by date
	- skill categories
	"""
	
	today = timezone.localdate()
	
	# Skill categories
	categories = (
		Category.objects
		.prefetch_related("skills")
		.all()
		.order_by("name")
	)
	
	# Only future and unbooked help offers
	availabilities = (
		Availability.objects
		.filter(
			date__gte=today,
			is_booked=False,
		)
		.select_related(
			"user",
			"skill",
			"skill__category",
		)
		.order_by(
			"date",
			"skill__name",
		)
	)
	
	# Pagination: 6 help offers per page
	paginator = Paginator(
		availabilities,
		3,
	)
	
	page_number = request.GET.get("page")
	
	page_obj = paginator.get_page(
		page_number
	)
	
	context = {
		"categories": categories,
		"page_obj": page_obj,
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


@login_required
def my_help_requests(request):
	categories = (
		Category.objects
		.all()
		.order_by("name")
	)
	
	if request.method == "POST":
		
		category_id = request.POST.get("category")
	
	else:
		
		category_id = request.GET.get("category")
	
	selected_category = None
	
	if category_id:
		selected_category = (
			Category.objects
			.filter(id=category_id)
			.first()
		)
	
	if request.method == "POST":
		
		form = HelpRequestForm(
			request.POST,
			user=request.user,
			category=selected_category,
		)
		
		if form.is_valid():
			help_request = form.save(
				commit=False
			)
			
			help_request.requester = request.user
			
			help_request.save()
			
			redirect_url = reverse(
				"exchange:my_help_requests"
			)
			
			return redirect(
				f"{redirect_url}"
				f"?category={selected_category.id}"
			)
	
	
	elif selected_category:
		
		form = HelpRequestForm(
			user=request.user,
			category=selected_category,
		)
	
	
	else:
		
		form = None
	
	help_requests = (
		HelpRequest.objects
		.filter(
			requester=request.user,
			date__gte=timezone.localdate(),
		)
		.select_related(
			"skill",
			"skill__category",
			"helper",
		)
		.order_by(
			"date",
			"skill__name",
		)
	)
	
	context = {
		"categories": categories,
		"selected_category": selected_category,
		"form": form,
		"help_requests": help_requests,
	}
	
	return render(
		request,
		"exchange/my_help_requests.html",
		context,
	)
@login_required
def other_help_requests(request):
    """
    Display help requests from other users when the requested
    skill is owned by the connected user.
    """

    today = timezone.localdate()

    # Skills owned by the connected user
    user_skill_ids = (
        UserSkill.objects
        .filter(user=request.user)
        .values_list(
            "skill_id",
            flat=True,
        )
    )

    # Help requests matching the connected user's skills
    help_requests = (
        HelpRequest.objects
        .filter(
            date__gte=today,
            helper__isnull=True,
            skill_id__in=user_skill_ids,
        )
        .exclude(
            requester=request.user
        )
        .select_related(
            "requester",
            "skill",
            "skill__category",
        )
        .order_by(
            "date",
            "skill__category__name",
            "skill__name",
        )
    )

    # 3 requests per page
    paginator = Paginator(
        help_requests,
        3,
    )

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
    }

    return render(
        request,
        "exchange/other_help_requests.html",
        context,
    )

@login_required
def accept_help_request(request, pk):

    if request.method != "POST":
        return redirect("exchange:other_help_requests")

    help_request = get_object_or_404(
        HelpRequest,
        pk=pk,
        helper__isnull=True
    )

    # Impossible d'accepter sa propre demande
    if help_request.requester == request.user:
        messages.error(
            request,
            "Vous ne pouvez pas accepter votre propre demande."
        )

        return redirect(
            "exchange:other_help_requests"
        )

    # Vérifier que l'utilisateur possède bien
    # la compétence demandée
    has_skill = UserSkill.objects.filter(
        user=request.user,
        skill=help_request.skill
    ).exists()

    if not has_skill:
        messages.error(
            request,
            "Vous ne possédez pas la compétence demandée."
        )

        return redirect(
            "exchange:other_help_requests"
        )

    # Attribution de la demande
    help_request.helper = request.user

    help_request.save(
        update_fields=["helper"]
    )

    messages.success(
        request,
        "La demande d'aide vous a été attribuée."
    )

    return redirect(
        "exchange:other_help_requests"
    )