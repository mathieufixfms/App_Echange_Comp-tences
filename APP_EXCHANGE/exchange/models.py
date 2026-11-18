from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Category(models.Model):
    """
    A category used to group skills.
    """

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="nom",
    )

    class Meta:
        verbose_name = "catégorie"
        verbose_name_plural = "catégories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Skill(models.Model):
    """
    A skill that users can offer or request.
    """

    name = models.CharField(
        max_length=150,
        unique=True,
        verbose_name="nom",
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="skills",
        verbose_name="catégorie",
    )

    description = models.TextField(
        blank=True,
        verbose_name="description",
    )

    class Meta:
        verbose_name = "compétence"
        verbose_name_plural = "compétences"
        ordering = ["category__name", "name"]

    def __str__(self):
        return f"{self.name} ({self.category.name})"


class UserSkill(models.Model):
    """
    A skill owned and offered by a user.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_skills",
        verbose_name="utilisateur",
    )

    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name="user_skills",
        verbose_name="compétence",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="date d’ajout",
    )

    class Meta:
        verbose_name = "compétence d’un utilisateur"
        verbose_name_plural = "compétences des utilisateurs"
        ordering = ["user__username", "skill__name"]

        constraints = [
            models.UniqueConstraint(
                fields=["user", "skill"],
                name="unique_user_skill",
            )
        ]

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.skill.name}"


class Availability(models.Model):
    """
    A full day during which a user is available to offer a skill.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="availabilities",
        verbose_name="utilisateur",
    )

    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name="availabilities",
        verbose_name="compétence proposée",
    )

    date = models.DateField(
        verbose_name="journée disponible",
    )

    is_booked = models.BooleanField(
        default=False,
        verbose_name="créneau réservé",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="date de création",
    )

    class Meta:
        verbose_name = "disponibilité"
        verbose_name_plural = "disponibilités"
        ordering = ["date", "skill__name"]

        constraints = [
            models.UniqueConstraint(
                fields=["user", "skill", "date"],
                name="unique_user_skill_availability",
            )
        ]

    def clean(self):
        """
        Check that the user owns the skill they want to offer.
        """

        if self.user_id and self.skill_id:
            owns_skill = UserSkill.objects.filter(
                user=self.user,
                skill=self.skill,
            ).exists()

            if not owns_skill:
                raise ValidationError(
                    {
                        "skill": (
                            "Vous ne pouvez proposer que les compétences "
                            "que vous avez déclarées."
                        )
                    }
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def is_past(self):
        return self.date < timezone.localdate()

    def __str__(self):
        user_name = self.user.get_full_name() or self.user.username

        return (
            f"{user_name} - {self.skill.name} - "
            f"{self.date.strftime('%d/%m/%Y')}"
        )


class HelpRequest(models.Model):
    """
    A request created by a user who needs help with an activity.
    """

    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="help_requests_created",
        verbose_name="demandeur",
    )

    skill = models.ForeignKey(
        Skill,
        on_delete=models.PROTECT,
        related_name="help_requests",
        verbose_name="compétence recherchée",
    )

    activity = models.TextField(
        verbose_name="activité à réaliser",
        help_text="Décrivez librement l’activité pour laquelle vous avez besoin d’aide.",
    )

    date = models.DateField(
        verbose_name="journée souhaitée",
    )

    helper = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="help_requests_accepted",
        null=True,
        blank=True,
        verbose_name="aidant",
    )

    availability = models.OneToOneField(
        Availability,
        on_delete=models.SET_NULL,
        related_name="help_request",
        null=True,
        blank=True,
        verbose_name="disponibilité utilisée",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="date de création",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="dernière modification",
    )

    class Meta:
        verbose_name = "demande d’aide"
        verbose_name_plural = "demandes d’aide"
        ordering = ["date", "skill__name"]

    @property
    def is_assigned(self):
        return self.helper is not None

    @property
    def is_past(self):
        return self.date < timezone.localdate()

    def clean(self):
        errors = {}

        if self.requester_id and self.skill_id:
            requester_owns_skill = UserSkill.objects.filter(
                user=self.requester,
                skill=self.skill,
            ).exists()

            if requester_owns_skill:
                errors["skill"] = (
                    "Vous devez sélectionner une compétence "
                    "que vous ne possédez pas."
                )

        if self.helper_id and self.requester_id:
            if self.helper == self.requester:
                errors["helper"] = (
                    "Le demandeur ne peut pas être son propre aidant."
                )

        if self.helper_id and self.skill_id:
            helper_owns_skill = UserSkill.objects.filter(
                user=self.helper,
                skill=self.skill,
            ).exists()

            if not helper_owns_skill:
                errors["helper"] = (
                    "L’aidant sélectionné ne possède pas "
                    "la compétence recherchée."
                )

        if self.availability_id:
            if self.helper_id and self.availability.user_id != self.helper_id:
                errors["availability"] = (
                    "Cette disponibilité n’appartient pas à l’aidant sélectionné."
                )

            if self.skill_id and self.availability.skill_id != self.skill_id:
                errors["availability"] = (
                    "La compétence de la disponibilité ne correspond pas "
                    "à la compétence recherchée."
                )

            if self.date and self.availability.date != self.date:
                errors["availability"] = (
                    "La date de disponibilité ne correspond pas "
                    "à la date de la demande."
                )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        requester_name = (
            self.requester.get_full_name()
            or self.requester.username
        )

        return (
            f"{requester_name} - {self.skill.name} - "
            f"{self.date.strftime('%d/%m/%Y')}"
        )
