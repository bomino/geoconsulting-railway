# Guide d'administration — GeoConsulting SARLU

Documentation complete pour l'administration du site GeoConsulting SARLU.

---

## Sommaire

1. [Vue d'ensemble](#1-vue-densemble)
2. [Gestion des utilisateurs](#2-gestion-des-utilisateurs)
3. [Gestion des projets](#3-gestion-des-projets)
4. [Gestion des articles](#4-gestion-des-articles)
5. [FAQ](#5-faq)
6. [Equipe](#6-equipe)
7. [Contacts & CRM](#7-contacts--crm)
8. [Portail client](#8-portail-client)
9. [Chatbot IA](#9-chatbot-ia)
10. [Journal d'audit](#10-journal-daudit)
11. [Parametres du site](#11-parametres-du-site)
12. [Maintenance & commandes](#12-maintenance--commandes)

---

## 1. Vue d'ensemble

Le panneau d'administration est accessible a `/admin/`. Seuls les utilisateurs avec le statut **staff** peuvent y acceder.

La barre laterale est organisee en **4 sections** :

| Section | Contenu |
|---------|---------|
| Gestion du site | Tableau de bord, utilisateurs, equipe, departements, divisions, parametres, ce guide |
| Contenu | Projets, articles, FAQ |
| Relations clients | Contacts, portail client, modeles email, regles d'attribution |
| Systeme | Journal d'audit |

---

## 2. Gestion des utilisateurs

**Accessible via** : Gestion du site -> Utilisateurs

### Trois roles disponibles

- **Admin** : `is_staff=True` + groupe "admins" — acces complet au panneau d'administration
- **Client** : groupe "clients" — acces au portail client uniquement
- **Invite** : aucun groupe — acces au site public uniquement

### Creer un utilisateur

Via **Gestion du site -> Utilisateurs -> Ajouter**. Renseigner email, nom, prenom et mot de passe. Le profil (telephone, avatar) est cree automatiquement.

### Changer le role

Selectionner les utilisateurs dans la liste, puis utiliser les actions groupees :

- **Assigner le role client** — ajoute au groupe "clients", retire de "admins"
- **Assigner le role admin** — ajoute au groupe "admins", active `is_staff`
- **Assigner le role invite** — retire de tous les groupes, desactive `is_staff`

### Suppression douce

Les utilisateurs ne sont **jamais supprimes definitivement**. L'action "Suppression douce" desactive le compte (`is_active=False`, `is_deleted=True`). Pour restaurer un utilisateur, utiliser l'action "Restaurer les utilisateurs selectionnes".

> **Note** : La liste affiche tous les utilisateurs, y compris les supprimes (colonne "Supprime"). Filtrer par "Est supprime : Oui/Non" pour les retrouver.

---

## 3. Gestion des projets

**Accessible via** : Contenu -> Projets

Chaque projet represente une reference de chantier de GeoConsulting.

### Champs principaux

| Champ | Description |
|-------|-------------|
| Titre | Nom du projet (max 255 caracteres) |
| Slug | Genere automatiquement a partir du titre (URL-friendly) |
| Categorie | Routes, Batiments, Hydraulique, Amenagement, Etudes |
| Statut | En cours, Termine, En attente |
| Description | Resume court du projet |
| Contenu | Description detaillee (supporte le format Markdown) |
| Localisation | Lieu du chantier |
| Nom du client | Maitre d'ouvrage |
| Annee | Annee de realisation |
| Image | Photo principale du projet |
| Publie | Visible sur le site public si coche |

### Publication

Un projet non publie n'apparait pas sur le site public. Utiliser la case "Publie" ou les actions groupees "Publier / Depublier les projets selectionnes".

### Documents joints

En bas du formulaire de projet, un onglet "Documents" permet d'ajouter des fichiers (PDF, DOCX, XLSX, max 50 Mo). Ces documents sont accessibles aux clients via le portail client.

> **Cache automatique** : La page publique des projets est mise en cache pendant 60 secondes. Apres avoir modifie un projet, le cache est automatiquement vide.

---

## 4. Gestion des articles

**Accessible via** : Contenu -> Articles

Les articles apparaissent sur la page `/actualites/`.

### Workflow de publication

1. Creer l'article avec titre, extrait, contenu (Markdown), image et categorie
2. Le slug est genere automatiquement a partir du titre
3. Cocher "Publie" — la date de publication est automatiquement definie
4. Pour depublier, decocher "Publie" — la date de publication est effacee

> **Markdown** : Le champ "Contenu" supporte la syntaxe Markdown : `**gras**`, `*italique*`, `# Titres`, listes, liens, etc. Le rendu est visible sur le site public.

---

## 5. FAQ

**Accessible via** : Contenu -> FAQ

Les FAQ sont affichees sur `/faq/`, groupees par categorie.

### Categories

- **General** — questions generales sur GeoConsulting
- **Services** — informations sur les prestations
- **Projets** — questions sur les references de chantier
- **Clients** — portail client, acces, suivi
- **Contact** — coordonnees, demandes de devis

### Ordre d'affichage

Le champ "Ordre" est editable directement dans la liste. Les FAQ sont triees par categorie puis par ordre croissant. La case "Publie" controle la visibilite sur le site public.

---

## 6. Equipe, departements et divisions

Les membres apparaissent dans l'organigramme sur `/a-propos/`.

### Departements

**Accessible via** : Gestion du site -> Departements

Les departements structurent l'organigramme. Chaque departement a un nom, un slug (genere automatiquement), un ordre d'affichage et un statut de publication.

| Champ | Description |
|-------|-------------|
| Nom | Nom du departement (unique) |
| Slug | Identifiant URL, genere automatiquement a partir du nom |
| Ordre | Position dans l'organigramme (0 = premier) |
| Direction | Si coche, le departement est affiche en haut de l'organigramme (un seul autorise) |
| Publie | Visible sur le site public si coche |

> **Regle** : Un seul departement peut etre marque comme "Direction". Tenter d'en marquer un deuxieme provoquera une erreur de validation.

### Divisions

**Accessible via** : Gestion du site -> Divisions

Les divisions subdivisent un departement. Elles apparaissent comme sous-blocs dans l'organigramme.

| Champ | Description |
|-------|-------------|
| Nom | Nom de la division (unique par departement) |
| Slug | Identifiant URL, genere automatiquement |
| Departement | Departement parent (selection avec recherche) |
| Ordre | Position dans le departement (0 = premier) |
| Publie | Visible sur le site public si coche |

### Membres de l'equipe

**Accessible via** : Gestion du site -> Equipe

Chaque membre est rattache a un departement (obligatoire) et optionnellement a une division.

| Champ | Description |
|-------|-------------|
| Departement | Departement du membre (selection avec recherche) |
| Division | Division du membre, optionnelle (selection avec recherche) |
| Role | Intitule du poste (texte libre) |

> **Validation** : La division selectionnee doit appartenir au departement selectionne. Un message d'erreur s'affiche en cas d'incoherence.

> **Protection** : Il est impossible de supprimer un departement qui contient des membres. Reassigner les membres avant de supprimer le departement.

### Photo

La photo est automatiquement redimensionnee a 100x100 pixels lors de l'enregistrement. Formats acceptes : JPEG, PNG.

### Ordre d'affichage

Le champ "Ordre" est editable dans la liste pour les departements, divisions et membres. Les membres sont tries par departement, puis par division, puis par ordre, puis par nom.

---

## 7. Contacts & CRM

### Pipeline des contacts

```
En attente  ->  En cours  ->  Resolu
```

1. Un visiteur remplit le formulaire sur `/contact/`
2. Le contact est cree avec le statut "En attente"
3. Les regles d'attribution automatique s'appliquent (si configurees)
4. Tous les administrateurs recoivent un email de notification
5. Gerer le contact via les actions groupees ou en modifiant le statut individuellement

### Onglets de la liste

En haut de la liste des contacts, trois onglets indiquent le nombre de contacts par statut : En attente, En cours, Resolus.

### Actions groupees

- **Marquer comme lu**
- **Marquer en cours**
- **Marquer resolu**
- **Archiver**
- **Exporter en CSV** — telecharge un fichier CSV avec nom, email, telephone, sujet, message, statut et date

### Regles d'attribution automatique

**Accessible via** : Relations clients -> Regles d'attribution

Chaque regle contient :

- **Mots-cles** — liste de termes a rechercher dans le sujet et le message du contact
- **Utilisateur assigne** — le membre du staff qui recevra le contact
- **Priorite** — les regles de priorite superieure sont evaluees en premier
- **Active** — seules les regles actives sont prises en compte

**Exemple** : Regle avec mots-cles = ["route", "chaussee"], utilisateur = Moussa, priorite = 10. Un contact avec le sujet "Etude de route nationale" sera automatiquement attribue a Moussa.

### Modeles email

**Accessible via** : Relations clients -> Modeles email

Creer des modeles reutilisables pour les communications clients (devis, renseignements, informations generales).

### Protection anti-spam

Le formulaire de contact inclut un champ invisible (honeypot). Les soumissions de robots qui remplissent ce champ sont silencieusement ignorees.

---

## 8. Portail client

Le portail client (`/portail/`) permet aux clients de suivre leurs projets, telecharger des documents et communiquer avec l'equipe.

### Donner acces a un client

1. Creer le compte utilisateur et lui assigner le role "Client" (voir section 2)
2. Aller dans **Relations clients -> Portail client**
3. Cliquer "Ajouter" et selectionner l'utilisateur, le projet et le niveau d'acces

### Niveaux d'acces

| Niveau | Permissions |
|--------|-------------|
| Consultation (view) | Voir le projet et telecharger les documents |
| Commentaire (comment) | Consultation + envoyer des messages |
| Edition (edit) | Acces complet au projet |

### Ce que voit le client

- **Tableau de bord** — liste des projets auxquels il a acces
- **Detail du projet** — informations + liste des documents telechargables
- **Messages** — boite de reception, envoi de messages au staff ou aux autres clients partageant un projet

### Notifications automatiques

- Un email est envoye au client lorsqu'un projet lui est attribue
- Un email est envoye a tous les clients d'un projet lorsqu'un nouveau document est ajoute

> **Documents securises** : Les documents sont stockes sur Cloudflare R2. Les liens de telechargement sont signes et temporaires (securite).

---

## 9. Chatbot IA

Un assistant IA est disponible sur le site public. Il utilise l'API OpenAI (modele GPT-4o-mini) avec un prompt systeme en francais, enrichi des statistiques de l'entreprise.

### Fonctionnement

- Les visiteurs envoient un message via l'interface de chat
- La reponse est diffusee en temps reel (streaming SSE)
- L'historique de conversation est conserve cote client (navigateur)

### Protections

| Protection | Detail |
|------------|--------|
| Limitation de debit | 20 requetes par IP toutes les 5 minutes |
| Disjoncteur | Apres 5 erreurs consecutives d'OpenAI, le chatbot est desactive pendant 5 minutes |
| Taille du message | Maximum 2 000 caracteres par message |
| Historique | Maximum 50 messages dans l'historique |

### Configuration

La variable d'environnement `OPENAI_API_KEY` dans le fichier `.env` active le chatbot. Si elle est vide, le chatbot est desactive. Aucune interface d'administration n'est necessaire.

---

## 10. Journal d'audit

**Accessible via** : Systeme -> Journal d'audit

Chaque creation, modification ou suppression est automatiquement enregistree.

### Entites suivies

Projets, Articles, Contacts, Acces client (ClientProject), Messages, Modeles email, Regles d'attribution.

### Informations capturees

- **Date et heure** de l'action
- **Utilisateur** qui a effectue l'action (ou anonyme)
- **Action** : creation, modification, suppression
- **Type et ID de l'entite** concernee
- **Adresse IP** et **User-Agent** du navigateur

> **Lecture seule** : Le journal d'audit est en lecture seule. Il est impossible d'ajouter, modifier ou supprimer des entrees manuellement.

---

## 11. Parametres du site

**Accessible via** : Gestion du site -> Parametres du site

### Parametres existants

| Cle | Utilisation |
|-----|-------------|
| `organigramme_image` | Image de l'organigramme affichee sur la page A propos |
| `politique_qualite_image` | Image de la politique qualite ISO 9001 affichee sur la page A propos |

Pour mettre a jour une image, cliquer sur la cle concernee et telecharger une nouvelle image. La cle est en lecture seule (impossible de creer de nouveaux parametres depuis l'interface).

---

## 12. Maintenance & commandes

Commandes disponibles via le terminal du serveur.

### Commandes

| Commande | Description |
|----------|-------------|
| `python manage.py seed_content` | Initialise le contenu : images, articles, FAQ, equipe, parametres du site. Idempotent. Option : `--dry-run` |
| `python manage.py seed_projects` | Initialise les 63 projets de reference. Idempotent. Option : `--dry-run` |
| `python scripts/seed_admin.py` | Cree les groupes (clients, admins), les cles SiteSetting et les 5 FAQ initiales |
| `python manage.py migrate` | Applique les migrations de base de donnees |
| `python manage.py collectstatic` | Collecte les fichiers statiques pour la production |
| `python manage.py createsuperuser` | Cree un nouveau compte superutilisateur |
| `npm run build:css` | Compile le CSS Tailwind pour la production |

### Variables d'environnement

| Variable | Requis | Description |
|----------|--------|-------------|
| `DJANGO_SECRET_KEY` | Oui | Cle secrete Django (generee aleatoirement) |
| `DATABASE_URL` | Oui | URL de connexion PostgreSQL |
| `DJANGO_ALLOWED_HOSTS` | Non | Domaines autorises (separes par virgule) |
| `OPENAI_API_KEY` | Non | Cle API OpenAI (vide = chatbot desactive) |
| `DEFAULT_FROM_EMAIL` | Non | Adresse d'expediteur des emails (defaut : info@mygeoconsulting.com) |
