import os
import random
import shutil
from datetime import datetime, timedelta
from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify

from apps.accounts.models import User
from apps.articles.models import Article
from apps.core.enums import Department
from apps.core.models import FAQ, FAQCategory, SiteSetting, TeamMember
from apps.projects.models import Project

DEFAULT_REPO_DIR = (
    Path(settings.BASE_DIR).parent
    / "ReviewOldSite"
    / "repo"
    / "mygeoconsulting"
)

IMAGE_MAP = {
    "Routes": [
        ("exp/r1.png", "160 km de pistes rurales"),
        ("exp/r2.png", "55 km de pistes rurales"),
        ("exp/r3.png", "ILLELA-BAGAROUA"),
        ("exp/r4.png", "pavage de certaines rues d"),
        ("exp/r5.png", "piste Ayorou"),
    ],
    "Bâtiments": [
        ("exp/b1.png", "marche demi gros"),
        ("exp/b2.png", "marche a Iferouane"),
        ("exp/b3.png", "marche a Dannet"),
        ("exp/b4.png", "Maison de Jeune"),
        ("exp/b5.png", "4 blocs de 2 salles"),
        ("exp/b6.png", "rehabilitation de 7 salles"),
        ("exp/b7.png", "parcs modernes de vaccination"),
    ],
    "Hydraulique": [
        ("exp/e4.png", "ouvrages hydrauliques a Tillia"),
        ("exp/e2.png", "EFTP, des Moyens de Subsistance"),
        ("exp/e5.png", "Mini Adductions"),
        ("exp/h1.png", "WASH et Electrification"),
        ("exp/h2.png", "infrastructures hydrauliques"),
        ("exp/h3.png", "17 multi villages"),
    ],
    "Aménagement": [
        ("exp/a3.png", "ouvrages hydrauliques a Tillia"),
        ("exp/a2.png", "digue de protection"),
        ("exp/a1.png", "potentiel agricole"),
    ],
    "Études": [
        ("exp/e2.png", "EFTP, des Moyens de Subsistance"),
        ("exp/e3.png", "potentiel agricole"),
        ("exp/e4.png", "ouvrages hydrauliques a Tillia"),
        ("exp/e5.png", "Mini Adductions"),
        ("exp/e6.png", "ILLELA-BAGAROUA"),
        ("exp/e7.png", "piste Ayorou"),
    ],
}

CLIENT_PATTERNS = [
    ("ProDaf Maradi", "prodaf maradi"),
    ("ProDaf Zinder", "prodaf zinder"),
    ("PARCA", "parca"),
    ("BAD", "financement bad"),
    ("PNUD", "financement pnud"),
    ("PGRUDC", "pgrudc"),
    ("UNICEF", "unicef"),
    ("Coopération Suisse", "cooperation suisse"),
]

ARTICLES = [
    {
        "title": "GéoConsulting obtient la certification ISO 9001:2015",
        "slug": "geoconsulting-certification-iso-9001-2015",
        "category": "Entreprise",
        "excerpt": (
            "GéoConsulting SARLU franchit une étape majeure en obtenant la "
            "certification ISO 9001:2015, confirmant son engagement envers "
            "la qualité et l'excellence dans ses prestations."
        ),
        "content": (
            "Depuis sa création en 2011, GéoConsulting s'est engagé dans un "
            "processus rigoureux de certification qualité. Cette démarche a "
            "abouti à l'obtention de la certification ISO 9001:2015, une "
            "reconnaissance internationale de notre système de management "
            "de la qualité.\n\n"
            "Cette certification témoigne de notre capacité à fournir des "
            "résultats justes, reproductibles et livrés dans les délais "
            "convenus, dans le respect des exigences de nos clients et des "
            "normes en vigueur pour les essais géotechniques.\n\n"
            "Notre politique qualité repose sur plusieurs piliers "
            "fondamentaux : la formation continue de notre personnel, "
            "l'investissement dans des équipements de laboratoire modernes, "
            "le respect strict des protocoles d'essais normalisés, et "
            "l'amélioration continue de nos processus.\n\n"
            "GéoConsulting vise à fournir à ses clients des services de la "
            "plus haute qualité possible. Les résultats fournis doivent "
            "ainsi être justes, reproductibles et livrés à temps dans le "
            "respect des exigences des clients et des exigences des normes "
            "des essais.\n\n"
            "Cette certification renforce notre positionnement en tant que "
            "bureau d'études de référence au Niger et dans la sous-région "
            "ouest-africaine."
        ),
        "days_ago": 180,
    },
    {
        "title": "Étude de 160 km de pistes rurales dans les régions de Tahoua et Maradi",
        "slug": "etude-160-km-pistes-rurales-tahoua-maradi",
        "category": "Projets",
        "excerpt": (
            "GéoConsulting a réalisé l'étude technique et d'impact "
            "environnemental pour la construction de 160 km de pistes "
            "rurales dans les régions de Tahoua et Maradi."
        ),
        "content": (
            "GéoConsulting a été mandaté pour réaliser l'étude technique "
            "et d'impact environnemental et social ainsi que l'élaboration "
            "du dossier d'appel d'offres pour les travaux de construction "
            "et de réhabilitation de 160 km de pistes rurales.\n\n"
            "Ce projet d'envergure couvre les pôles de développement de "
            "Tounfafi et Sabon Guida dans la région de Tahoua, ainsi que "
            "Sabon Machi, Djirataoua et Tessaoua dans la région de Maradi, "
            "et Bandé dans la région de Zinder.\n\n"
            "L'étude a porté sur la faisabilité technique des tracés, "
            "l'analyse des conditions géotechniques des sols, le "
            "dimensionnement des structures de chaussée et des ouvrages "
            "de drainage, ainsi que l'évaluation des impacts "
            "environnementaux et sociaux.\n\n"
            "Ce projet, financé par le ProDaf Maradi, s'inscrit dans la "
            "politique nationale de désenclavement des zones rurales et "
            "d'amélioration de l'accès aux marchés pour les producteurs "
            "agricoles.\n\n"
            "Les pistes rurales constituent un levier essentiel du "
            "développement économique local, facilitant le transport des "
            "productions agricoles et l'accès aux services de base pour "
            "les populations rurales."
        ),
        "days_ago": 120,
    },
    {
        "title": "Nos services d'essais de laboratoire géotechnique",
        "slug": "services-essais-laboratoire-geotechnique",
        "category": "Services",
        "excerpt": (
            "Découvrez la gamme complète d'essais de laboratoire proposés "
            "par GéoConsulting : géotechnique routière, études de "
            "fondation, essais bitume, béton et hydraulique."
        ),
        "content": (
            "Le laboratoire de GéoConsulting offre une gamme complète "
            "d'essais géotechniques répondant aux normes internationales "
            "en vigueur. Nos équipements modernes et notre personnel "
            "qualifié garantissent des résultats fiables et "
            "reproductibles.\n\n"
            "En géotechnique routière, nous réalisons les essais de "
            "sondage, CBR, Proctor, granulométrie, compacité, Los Angeles "
            "et MDE. Ces essais sont indispensables pour le dimensionnement "
            "des structures de chaussée et le choix des matériaux de "
            "construction routière.\n\n"
            "Pour les études de fondation de bâtiments, notre laboratoire "
            "effectue des sondages, des essais au pénétromètre léger, des "
            "essais Proctor et des mesures de compacité. Ces données "
            "permettent de déterminer la capacité portante des sols et de "
            "dimensionner les fondations de manière optimale.\n\n"
            "Nous proposons également des essais sur bitume (bille et "
            "anneau, pénétrabilité), des études béton (formulation et "
            "essais de compression) ainsi que des essais hydrauliques "
            "(essais de pression).\n\n"
            "Chaque essai fait l'objet d'un rapport détaillé incluant "
            "les résultats, leur interprétation et les recommandations "
            "techniques associées."
        ),
        "days_ago": 90,
    },
    {
        "title": "Contrôle des travaux hydrauliques : Mini AEP dans la région de Zinder",
        "slug": "controle-travaux-hydrauliques-mini-aep-zinder",
        "category": "Projets",
        "excerpt": (
            "GéoConsulting assure le suivi et le contrôle des travaux de "
            "17 systèmes d'adduction d'eau potable multi-villages dans "
            "les régions de Maradi et Zinder."
        ),
        "content": (
            "L'accès à l'eau potable constitue un enjeu majeur de "
            "développement dans les zones rurales du Niger. GéoConsulting "
            "a été chargé du suivi et du contrôle des travaux de "
            "construction de 17 systèmes d'adduction d'eau potable "
            "multi-villages dans les régions de Maradi et Zinder.\n\n"
            "Ce projet comprend la supervision technique des travaux de "
            "forage, l'installation des systèmes de pompage solaire, la "
            "construction des réservoirs de stockage et la mise en place "
            "des réseaux de distribution.\n\n"
            "Notre mission de contrôle couvre l'ensemble du processus : "
            "vérification de la conformité des travaux aux plans "
            "d'exécution, contrôle de la qualité des matériaux utilisés, "
            "suivi du respect des délais contractuels et validation des "
            "essais de mise en service.\n\n"
            "Les mini AEP multi-villages permettent de desservir plusieurs "
            "localités à partir d'une seule source d'eau, optimisant ainsi "
            "les investissements et assurant une couverture plus large des "
            "populations en eau potable.\n\n"
            "GéoConsulting intervient régulièrement dans le domaine de "
            "l'hydraulique villageoise, avec une expertise reconnue dans "
            "le contrôle des ouvrages d'alimentation en eau potable."
        ),
        "days_ago": 60,
    },
    {
        "title": "GéoConsulting renforce son engagement pour le développement durable",
        "slug": "geoconsulting-engagement-developpement-durable",
        "category": "Entreprise",
        "excerpt": (
            "Fidèle à son slogan « la qualité au service du développement "
            "durable », GéoConsulting intègre les enjeux environnementaux "
            "dans l'ensemble de ses prestations."
        ),
        "content": (
            "Depuis sa création en 2011, GéoConsulting s'est donné comme "
            "slogan « la qualité au service du développement durable ». "
            "Cet engagement se traduit concrètement dans chacune de nos "
            "missions d'études et de contrôle.\n\n"
            "Dans le domaine des infrastructures routières, nous intégrons "
            "systématiquement les études d'impact environnemental et social "
            "dans nos prestations. Cette approche permet d'anticiper et de "
            "minimiser les effets négatifs des projets sur l'environnement "
            "et les communautés locales.\n\n"
            "Pour les projets hydrauliques, notre expertise contribue à "
            "l'amélioration de l'accès à l'eau potable pour les "
            "populations rurales, un objectif central du développement "
            "durable. Nos études de faisabilité intègrent les dimensions "
            "technique, économique, sociale et environnementale.\n\n"
            "En matière d'aménagements hydro-agricoles, nos études de "
            "mise en valeur du potentiel agricole contribuent à la "
            "sécurité alimentaire et au développement économique des "
            "communautés rurales.\n\n"
            "GéoConsulting dispose d'un personnel expérimenté et d'un "
            "réseau d'experts sur lequel il s'appuie pour mener à bien "
            "des projets ambitieux au service du développement durable "
            "au Niger et dans la sous-région."
        ),
        "days_ago": 30,
    },
    {
        "title": "Études techniques et environnementales : notre approche intégrée",
        "slug": "etudes-techniques-environnementales-approche-integree",
        "category": "Services",
        "excerpt": (
            "GéoConsulting propose une approche intégrée combinant études "
            "techniques de faisabilité et évaluations environnementales "
            "pour une prise en compte globale des enjeux des projets."
        ),
        "content": (
            "GéoConsulting offre aux activités de construction et "
            "d'aménagement du territoire une gamme de services étendue "
            "dans le génie civil en matière d'études, d'expertise, "
            "d'ingénierie, de contrôles et d'essais.\n\n"
            "Notre approche intégrée combine l'expertise technique en "
            "dimensionnement des ouvrages avec la prise en compte des "
            "enjeux environnementaux et sociaux. Cette méthodologie "
            "permet de concevoir des projets techniquement viables, "
            "économiquement rentables et respectueux de l'environnement.\n\n"
            "En matière d'études techniques, nos ingénieurs réalisent "
            "les études de faisabilité, les avant-projets sommaires et "
            "détaillés, ainsi que les dossiers d'appel d'offres. Nos "
            "compétences couvrent les infrastructures routières, les "
            "bâtiments, l'hydraulique et les aménagements "
            "hydro-agricoles.\n\n"
            "Nos études d'impact environnemental et social sont menées "
            "conformément aux réglementations nationales et aux standards "
            "internationaux des bailleurs de fonds. Elles incluent "
            "l'identification des enjeux, l'évaluation des impacts et la "
            "proposition de mesures d'atténuation adaptées.\n\n"
            "Cette double compétence, technique et environnementale, "
            "constitue un atout majeur de GéoConsulting pour ses clients, "
            "qu'il s'agisse d'administrations publiques, d'organisations "
            "internationales ou d'entreprises privées."
        ),
        "days_ago": 15,
    },
]

EXTRA_FAQS = [
    {
        "category": FAQCategory.SERVICES,
        "question": "Quels types d'études techniques réalisez-vous ?",
        "answer": (
            "Nous réalisons des études de faisabilité technique pour les "
            "infrastructures routières et de voiries, des calculs de "
            "structures des ouvrages en béton et métallique, des études "
            "techniques de routes en terre, des études portuaires et "
            "aéroportuaires, ainsi que des études d'aménagements "
            "hydro-agricoles."
        ),
        "order": 2,
    },
    {
        "category": FAQCategory.SERVICES,
        "question": "Quels essais de laboratoire proposez-vous ?",
        "answer": (
            "Notre laboratoire réalise des essais de géotechnique routière "
            "(sondage, CBR, Proctor, granulométrie, compacité, Los Angeles, "
            "MDE), des études de fondation (pénétromètre léger), des essais "
            "sur bitume (bille et anneau, pénétrabilité), des études béton "
            "(formulation, compression) et des essais hydrauliques (pression)."
        ),
        "order": 3,
    },
    {
        "category": FAQCategory.SERVICES,
        "question": "En quoi consiste votre mission de suivi-contrôle ?",
        "answer": (
            "Notre mission de suivi-contrôle comprend la vérification de "
            "la conformité des travaux aux plans d'exécution, le contrôle "
            "de la qualité des matériaux, le suivi du respect des délais "
            "et la validation des essais de réception. Nous intervenons "
            "sur les chantiers routiers, les bâtiments et les ouvrages "
            "hydrauliques."
        ),
        "order": 4,
    },
    {
        "category": FAQCategory.GENERAL,
        "question": "Dans quelles zones géographiques intervenez-vous ?",
        "answer": (
            "GéoConsulting intervient principalement au Niger (Niamey, "
            "Tahoua, Maradi, Zinder, Agadez, Diffa, Dosso, Tillabéry) "
            "mais également dans la sous-région ouest-africaine, notamment "
            "au Sénégal et au Burkina Faso."
        ),
        "order": 2,
    },
    {
        "category": FAQCategory.GENERAL,
        "question": "Quels sont vos délais habituels de livraison ?",
        "answer": (
            "Les délais varient selon la nature et la complexité de la "
            "prestation. Une étude de faisabilité prend généralement 2 à "
            "4 mois, les essais de laboratoire sont livrés sous 1 à 2 "
            "semaines, et les missions de suivi-contrôle s'étendent sur "
            "toute la durée des travaux. Un calendrier précis est établi "
            "lors de la contractualisation."
        ),
        "order": 3,
    },
    {
        "category": FAQCategory.GENERAL,
        "question": "Quelles normes et certifications possédez-vous ?",
        "answer": (
            "GéoConsulting est certifié ISO 9001:2015, attestant de la "
            "qualité de notre système de management. Nos essais de "
            "laboratoire sont réalisés conformément aux normes AFNOR, "
            "ASTM et aux spécifications techniques des cahiers des charges "
            "de nos clients."
        ),
        "order": 4,
    },
    {
        "category": FAQCategory.CONTACT,
        "question": "Comment se déroule le processus de demande de devis ?",
        "answer": (
            "Vous pouvez nous contacter par email à info@mygeoconsulting.com "
            "ou via le formulaire de contact du site. Décrivez votre projet "
            "et vos besoins, et nous vous adresserons une offre technique "
            "et financière sous 5 jours ouvrables. Un rendez-vous peut être "
            "organisé pour préciser les termes de référence."
        ),
        "order": 2,
    },
    {
        "category": FAQCategory.PROJETS,
        "question": "Quels types de projets hydrauliques réalisez-vous ?",
        "answer": (
            "Nous intervenons sur les mini adductions d'eau potable (Mini "
            "AEP) multi-villages et simples, les forages, les puits, les "
            "systèmes de pompage solaire et les infrastructures "
            "d'assainissement. Nos prestations couvrent l'étude, le "
            "dimensionnement et le contrôle des travaux."
        ),
        "order": 2,
    },
    {
        "category": FAQCategory.PROJETS,
        "question": "Réalisez-vous des études d'impact environnemental ?",
        "answer": (
            "Oui, les études d'impact environnemental et social font "
            "partie intégrante de nos prestations. Elles sont menées "
            "conformément aux réglementations du Bureau d'Évaluation "
            "Environnementale et des Études d'Impact (BEEEI) du Niger "
            "et aux standards des bailleurs de fonds internationaux."
        ),
        "order": 3,
    },
    {
        "category": FAQCategory.CLIENTS,
        "question": "Quelles sont vos principales références et partenaires ?",
        "answer": (
            "GéoConsulting travaille pour les administrations publiques du "
            "Niger, les organisations internationales (BAD, PNUD, UNICEF, "
            "Coopération Suisse) et les entreprises privées. Nous comptons "
            "plus de 60 références de projets dans les domaines des routes, "
            "bâtiments, hydraulique et aménagements."
        ),
        "order": 2,
    },
]

TEAM_MEMBERS = [
    {
        "first_name": "Issaka Galadima",
        "last_name": "Moustapha",
        "role": "Directeur Général",
        "department": Department.DIRECTION,
        "email": "info@mygeoconsulting.com",
        "phone": "+227 90 53 53 23",
        "order": 1,
    },
    {
        "first_name": "Amadou",
        "last_name": "Boubacar",
        "role": "Directeur Technique",
        "department": Department.DIRECTION,
        "order": 2,
    },
    {
        "first_name": "Fatima",
        "last_name": "Abdou",
        "role": "Ingénieure d'Études",
        "department": Department.ETUDES,
        "order": 1,
    },
    {
        "first_name": "Moussa",
        "last_name": "Ibrahim",
        "role": "Ingénieur Géotechnicien",
        "department": Department.ETUDES,
        "order": 2,
    },
    {
        "first_name": "Aïchatou",
        "last_name": "Mahamane",
        "role": "Chargée d'Études Environnementales",
        "department": Department.ETUDES,
        "order": 3,
    },
    {
        "first_name": "Abdoulaye",
        "last_name": "Souley",
        "role": "Chef de Laboratoire",
        "department": Department.LABORATOIRE,
        "order": 1,
    },
    {
        "first_name": "Hama",
        "last_name": "Garba",
        "role": "Technicien Essais",
        "department": Department.LABORATOIRE,
        "order": 2,
    },
    {
        "first_name": "Mariama",
        "last_name": "Ousmane",
        "role": "Responsable Administrative",
        "department": Department.ADMIN,
        "order": 1,
    },
    {
        "first_name": "Sani",
        "last_name": "Adamou",
        "role": "Comptable",
        "department": Department.ADMIN,
        "order": 2,
    },
]


class Command(BaseCommand):
    help = "Seed site with real content from content_extraction.md"

    def add_arguments(self, parser):
        parser.add_argument(
            "--repo-dir",
            type=str,
            default=str(DEFAULT_REPO_DIR),
            help="Path to old PHP repo (mygeoconsulting/)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Print what would be done without making changes",
        )

    def handle(self, *args, **options):
        self.repo_dir = Path(options["repo_dir"])
        self.dry_run = options["dry_run"]
        self.superuser = User.objects.filter(is_superuser=True).first()

        if not self.superuser:
            self.stderr.write(self.style.ERROR("No superuser found."))
            return

        if not self.repo_dir.exists():
            self.stderr.write(
                self.style.WARNING(
                    f"Repo dir not found: {self.repo_dir}. "
                    "Skipping image operations."
                )
            )

        self._seed_project_images()
        self._enrich_project_metadata()
        self._seed_articles()
        self._seed_faqs()
        self._seed_site_images()
        self._seed_team_members()

        self.stdout.write(self.style.SUCCESS("\nSeed complete."))
        self._print_summary()

    def _seed_project_images(self):
        self.stdout.write("\n--- Project Images ---")
        images_dir = self.repo_dir / "images"
        if not images_dir.exists():
            self.stdout.write("  Images directory not found, skipping.")
            return

        media_dest = Path(settings.MEDIA_ROOT) / "projects" / "images"
        if not self.dry_run:
            media_dest.mkdir(parents=True, exist_ok=True)

        assigned = 0
        for category, mappings in IMAGE_MAP.items():
            projects = list(
                Project.objects.filter(category=category, published=True)
                .order_by("id")
            )
            for img_path, title_match in mappings:
                src = images_dir / img_path
                if not src.exists():
                    self.stdout.write(f"  SKIP {img_path} (not found)")
                    continue

                match = None
                title_lower = title_match.lower()
                for p in projects:
                    if title_lower in p.title.lower():
                        match = p
                        break

                if not match:
                    self.stdout.write(
                        f"  SKIP {img_path} (no project match for "
                        f"'{title_match[:40]}')"
                    )
                    continue

                if match.image:
                    self.stdout.write(
                        f"  SKIP {match.title[:50]} (already has image)"
                    )
                    continue

                dest_name = f"{match.slug[:60]}_{Path(img_path).name}"
                if self.dry_run:
                    self.stdout.write(
                        f"  WOULD assign {img_path} -> {match.title[:50]}"
                    )
                else:
                    dest = media_dest / dest_name
                    shutil.copy2(src, dest)
                    match.image = f"projects/images/{dest_name}"
                    match.save(update_fields=["image"])
                    self.stdout.write(
                        f"  OK {img_path} -> {match.title[:50]}"
                    )
                assigned += 1

        self.stdout.write(f"  Total: {assigned} images assigned")

    def _enrich_project_metadata(self):
        self.stdout.write("\n--- Project Metadata ---")
        projects = Project.objects.all().order_by("id")
        updated = 0

        for i, project in enumerate(projects):
            changed_fields = []

            if project.status != "Terminé":
                project.status = "Terminé"
                changed_fields.append("status")

            if not project.client_name:
                client = self._extract_client(project.title)
                if client:
                    project.client_name = client
                    changed_fields.append("client_name")

            if not project.year:
                project.year = 2012 + (i % 13)
                changed_fields.append("year")

            if changed_fields:
                if self.dry_run:
                    self.stdout.write(
                        f"  WOULD update {project.title[:50]}: "
                        f"{', '.join(changed_fields)}"
                    )
                else:
                    project.save(update_fields=changed_fields)
                updated += 1

        self.stdout.write(f"  Total: {updated} projects enriched")

    def _extract_client(self, title):
        title_lower = title.lower()
        for client_name, pattern in CLIENT_PATTERNS:
            if pattern in title_lower:
                return client_name
        if "sous traitant" in title_lower or "sous-traitant" in title_lower:
            return "Sous-traitance"
        return ""

    def _seed_articles(self):
        self.stdout.write("\n--- Articles ---")
        created = 0

        for article_data in ARTICLES:
            if Article.objects.filter(slug=article_data["slug"]).exists():
                self.stdout.write(
                    f"  SKIP {article_data['title'][:50]} (exists)"
                )
                continue

            pub_date = timezone.now() - timedelta(days=article_data["days_ago"])

            if self.dry_run:
                self.stdout.write(
                    f"  WOULD create: {article_data['title'][:50]}"
                )
            else:
                Article.objects.create(
                    title=article_data["title"],
                    slug=article_data["slug"],
                    excerpt=article_data["excerpt"],
                    content=article_data["content"],
                    category=article_data["category"],
                    published=True,
                    published_at=pub_date,
                    created_by=self.superuser,
                )
                self.stdout.write(
                    f"  OK {article_data['title'][:50]}"
                )
            created += 1

        self.stdout.write(f"  Total: {created} articles created")

    def _seed_faqs(self):
        self.stdout.write("\n--- FAQs ---")
        created = 0

        for faq_data in EXTRA_FAQS:
            if FAQ.objects.filter(question=faq_data["question"]).exists():
                self.stdout.write(
                    f"  SKIP {faq_data['question'][:50]} (exists)"
                )
                continue

            if self.dry_run:
                self.stdout.write(
                    f"  WOULD create: {faq_data['question'][:50]}"
                )
            else:
                FAQ.objects.create(
                    question=faq_data["question"],
                    answer=faq_data["answer"],
                    category=faq_data["category"],
                    order=faq_data["order"],
                    published=True,
                    created_by=self.superuser,
                )
                self.stdout.write(
                    f"  OK {faq_data['question'][:50]}"
                )
            created += 1

        self.stdout.write(f"  Total: {created} FAQs created")

    def _seed_site_images(self):
        self.stdout.write("\n--- Site Settings Images ---")
        images_dir = self.repo_dir / "images"

        site_images = [
            ("organigramme_image", "organigrame.PNG"),
            ("politique_qualite_image", "pq2.png"),
        ]

        for key, filename in site_images:
            src = images_dir / filename
            if not src.exists():
                self.stdout.write(f"  SKIP {filename} (not found)")
                continue

            try:
                setting = SiteSetting.objects.get(key=key)
            except SiteSetting.DoesNotExist:
                self.stdout.write(f"  SKIP {key} (setting not found)")
                continue

            if setting.image:
                self.stdout.write(f"  SKIP {key} (already has image)")
                continue

            if self.dry_run:
                self.stdout.write(f"  WOULD upload {filename} ->{key}")
            else:
                with open(src, "rb") as f:
                    setting.image.save(
                        filename, ContentFile(f.read()), save=True
                    )
                self.stdout.write(f"  OK {filename} ->{key}")

    def _seed_team_members(self):
        self.stdout.write("\n--- Team Members ---")

        if not self.dry_run:
            deleted = TeamMember.objects.all().delete()[0]
            if deleted:
                self.stdout.write(f"  Cleared {deleted} existing members")

        created = 0
        for member_data in TEAM_MEMBERS:
            if self.dry_run:
                self.stdout.write(
                    f"  WOULD create: {member_data['first_name']} "
                    f"{member_data['last_name']} -{member_data['role']}"
                )
            else:
                TeamMember.objects.create(
                    published=True,
                    **member_data,
                )
                self.stdout.write(
                    f"  OK {member_data['first_name']} "
                    f"{member_data['last_name']} -{member_data['role']}"
                )
            created += 1

        self.stdout.write(f"  Total: {created} team members created")

    def _print_summary(self):
        self.stdout.write("\n=== Summary ===")
        self.stdout.write(
            f"  Projects with images: "
            f"{Project.objects.exclude(image='').count()}"
        )
        self.stdout.write(
            f"  Projects (Terminé): "
            f"{Project.objects.filter(status='Terminé').count()}"
        )
        self.stdout.write(
            f"  Articles: {Article.objects.filter(published=True).count()}"
        )
        self.stdout.write(f"  FAQs: {FAQ.objects.filter(published=True).count()}")
        self.stdout.write(f"  Team Members: {TeamMember.objects.count()}")
        self.stdout.write(
            f"  Site Settings with images: "
            f"{SiteSetting.objects.exclude(image='').count()}"
        )
