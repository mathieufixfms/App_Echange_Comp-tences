from django import forms

from .models import Skill

class UserSkillsForm(forms.Form):

    skills = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Mes compétences",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["skills"].queryset = (
            Skill.objects
            .select_related("category")
            .order_by("category__name", "name")
        )