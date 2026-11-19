from django import forms
from django.utils import timezone

from .models import Category, Availability, Skill


class UserSkillsForm(forms.Form):
	
    category = forms.ModelChoiceField(
        queryset=Category.objects.all().order_by("name"),
        required=True,
        label="Catégorie",
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )

    skills = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.none(),
        required=False,
        label="Compétences",
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(
        self,
        *args,
        category=None,
        selected_skills=None,
        **kwargs
    ):
        super().__init__(*args, **kwargs)

        if category:
            self.fields["skills"].queryset = (
                Skill.objects
                .filter(category=category)
                .order_by("name")
            )

        if selected_skills is not None:
            self.fields["skills"].initial = selected_skills

class AvailabilityForm(forms.ModelForm):
    """
    Form used by a connected user to create
    an availability for one of their skills.
    """

    class Meta:
        model = Availability

        fields = [
            "date",
            "skill",
        ]

        widgets = {
            "date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                }
            ),

            "skill": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
        }

        labels = {
            "date": "Journée disponible",
            "skill": "Compétence proposée",
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.user = user

        # Only display skills owned by the connected user.
        if user is not None:
            self.fields["skill"].queryset = (
                Skill.objects
                .filter(
                    user_skills__user=user
                )
                .select_related("category")
                .order_by(
                    "category__name",
                    "name",
                )
                .distinct()
            )

        else:
            self.fields["skill"].queryset = (
                Skill.objects.none()
            )

    def clean_date(self):
        """
        Prevent the user from creating
        an availability in the past.
        """

        date = self.cleaned_data["date"]

        if date < timezone.localdate():
            raise forms.ValidationError(
                "Vous ne pouvez pas sélectionner une date passée."
            )

        return date

    def clean(self):
        """
        Prevent the same user from creating
        the same availability twice.
        """

        cleaned_data = super().clean()

        date = cleaned_data.get("date")
        skill = cleaned_data.get("skill")

        if self.user and date and skill:

            already_exists = (
                Availability.objects
                .filter(
                    user=self.user,
                    date=date,
                    skill=skill,
                )
                .exists()
            )

            if already_exists:
                raise forms.ValidationError(
                    "Vous avez déjà proposé cette compétence "
                    "pour cette journée."
                )

        return cleaned_data