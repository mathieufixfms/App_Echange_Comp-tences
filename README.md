
# Plateforme d'Échange de Compétences (Django)

Application Web collaborative permettant aux membres d'une communauté d'échanger leurs compétences autour de créneaux d'entraide planifiés.

## 📋 Table des matières
- [Contexte & Objectifs](#-contexte--objectifs)
- [Stack Technique](#-stack-technique)
- [Installation et Démarrage](#-installation-et-démarrage)
- [Spécifications Fonctionnelles](#-spécifications-fonctionnelles)
- [Conception & Architecture UML](#-conception--architecture-uml)
- [Structure du Projet](#-structure-du-projet)

---

## 🎯 Contexte & Objectifs

L'application met en relation des utilisateurs ayant besoin d'aide sur une activité ponctuelle avec d'autres membres possédant la compétence requise. 
- **Visibilité publique maîtrisée :** Les visiteurs non connectés peuvent consulter le catalogue des compétences et le planning des prochaines sessions d'entraide de manière strictement anonyme.
- **Mise en relation ciblée :** Les utilisateurs authentifiés déclarent leurs compétences, publient leurs besoins et répondent aux demandes correspondant à leur savoir-faire. Une fois un créneau validé, les coordonnées (prénom, nom, email) sont partagées pour convenir des modalités de rencontre.

---

## 🛠 Stack Technique

- **Framework Backend :** Django `5.2.12`
- **Langage :** Python `3.12+`
- **Base de données :** SQLite3 (configuration par défaut)
- **Administration :** Django Admin (gestion des utilisateurs autorisés et du catalogue des compétences)
- **Modélisation :** PlantUML

---

## 🚀 Installation et Démarrage

### 1. Cloner le dépôt et créer l'environnement virtuel
```bash
git clone <https://github.com/mathieufixfms/App_Echange_Comp-tences>
cd <nom-du-dossier>

python -m venv venv
# Sous Windows :
venv\Scripts\activate
```

### 2. Installer les dépendances
```bash
pip install Django==5.2.12
```

### 3. Appliquer les migrations et créer un administrateur
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 4. Lancer le serveur de développement
```bash
python manage.py runserver
```
- **Application principale :** `http://127.0.0`
- **Interface d'administration :** `http://127.0.0admin/` *(pour saisir les compétences et créer les comptes utilisateurs autorisés)*.

---

## 📌 Spécifications Fonctionnelles

### 1. Rôle : Visiteur (non authentifié)
- **Catalogue des compétences (`Skill`) :** Consultation de la liste complète des compétences proposées par la plateforme.
- **Planning public (`Request`) :** Affichage chronologique des prochains créneaux d'aide (date, heure, compétence, activité) **sans aucune mention nominative** des participants.
- **Authentification :** Accès au formulaire de connexion (pas d'inscription libre).

### 2. Rôle : Utilisateur connecté (`User`)
- **Gestion du profil :** Sélection et mise à jour des compétences possédées parmi le catalogue global.
- **Publication d'une demande d'aide (`DEMAND`) :** Création d'un créneau futur avec description libre de l'activité, restreint aux compétences que l'utilisateur **ne possède pas**.
- **Consultation des demandes compatibles :** Affichage des demandes ouvertes (`OPEN`) d'autres membres correspondant aux compétences possédées par l'utilisateur connecté (avec affichage du prénom, nom et email du demandeur).
- **Acceptation d'un créneau :** Engagement sur une demande compatible. Le créneau passe au statut `ACCEPTED`, disparaît des listes publiques/ouvertes et met en relation les deux membres via leurs adresses de courriel.
- **[Optionnel] Offres de disponibilité (`OFFER`) :** Publication de plages horaires libres pour aider la communauté, et possibilité pour un autre membre de réserver l'un de ces créneaux pour une activité et une compétence manquante.

### 3. Rôle : Administrateur
- **Back-office Django Admin :** Création des comptes utilisateurs autorisés et alimentation du référentiel des compétences (`Skill`).

---

## 📐 Conception & Architecture UML

Les diagrammes de conception (Cas d'utilisation, Classes et Séquence) sont disponibles dans le dossier `/docs/uml/` au format **PlantUML** (`.puml`).

### Modèle de données principal (`models.py`)
- **`User` (Django Auth) :** Utilisateur de la plateforme (`first_name`, `last_name`, `email`). Relié en `ManyToMany` aux compétences qu'il possède.
- **`Skill` :** Référentiel des compétences (`name`, `description`).
- **`Request` :** Représente un créneau d'entraide (`start_time`, `end_time`, `slot_type` [`DEMAND`/`OFFER`], `activity`, `status` [`OPEN`/`ACCEPTED`/`COMPLETED`/`CANCELED`], `requester`, `helper`, `skill`).

---

## 📂 Structure du Projet

```text
├── config/                 # Configuration principale du projet Django
├── core/                   # Application métier (modèles, vues, formulaires, templates)
│   ├── migrations/
│   ├── templates/
│   ├── admin.py            # Enregistrement de Skill et Request dans Django Admin
│   ├── models.py           # Définition des classes Skill et Request
│   ├── urls.py
│   └── views.py
├── docs/
│   └── uml/                # Fichiers sources PlantUML (.puml)
├── db.sqlite3              # Base de données SQLite
├── manage.py
└── README.md
```
