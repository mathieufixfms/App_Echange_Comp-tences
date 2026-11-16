from django.db import models
from django.contrib.auth.models import User


class Categorie(models.Model):
    nom = models.CharField(max_length=100)

    def __str__(self):
        return self.nom


class Competence(models.Model):
    nom = models.CharField(max_length=150)
    categorie = models.ForeignKey(
        Categorie,
        on_delete=models.CASCADE,
        related_name="competences"
    )

    utilisateurs = models.ManyToManyField(
        User,
        related_name="competences",
        blank=True
    )

    def __str__(self):
        return self.nom


class Disponibilite(models.Model):
    utilisateur = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="disponibilites"
    )

    competence = models.ForeignKey(
        Competence,
        on_delete=models.CASCADE
    )

    date = models.DateField()

    demandeur = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="aides_reservees"
    )

    activite = models.TextField(blank=True)

    def __str__(self):
        return f"{self.utilisateur} - {self.competence} - {self.date}"


class DemandeAide(models.Model):
    utilisateur = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="demandes_aide"
    )

    competence = models.ForeignKey(
        Competence,
        on_delete=models.CASCADE
    )

    activite = models.TextField()

    date = models.DateField()

    aidant = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="aides_acceptees"
    )

    def __str__(self):
        return f"{self.activite} - {self.date}"