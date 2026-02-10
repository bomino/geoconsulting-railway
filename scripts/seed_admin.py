import os
import sys

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

django.setup()

from django.contrib.auth.models import Group

from apps.core.models import FAQ, FAQCategory, SiteSetting


def seed():
    clients_group, created = Group.objects.get_or_create(name="clients")
    print(f"Group 'clients': {'created' if created else 'already exists'}")

    admins_group, created = Group.objects.get_or_create(name="admins")
    print(f"Group 'admins': {'created' if created else 'already exists'}")

    site_settings = [
        ("organigramme_image", ""),
        ("politique_qualite_image", ""),
    ]
    for key, value in site_settings:
        setting, created = SiteSetting.objects.get_or_create(
            key=key,
            defaults={"value": value},
        )
        print(f"SiteSetting '{key}': {'created' if created else 'already exists'}")

    from apps.accounts.models import User

    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        print("WARNING: No superuser found. FAQ entries require a created_by user. Skipping FAQ seeding.")
        return

    faq_entries = [
        {
            "category": FAQCategory.GENERAL,
            "question": "Qu'est-ce que GeoConsulting SARLU ?",
            "answer": "GeoConsulting SARLU est un bureau d'études en génie civil basé à Niamey, Niger, "
            "certifié ISO 9001:2015 avec plus de 10 ans d'expérience.",
            "order": 1,
        },
        {
            "category": FAQCategory.SERVICES,
            "question": "Quels services proposez-vous ?",
            "answer": "Nous proposons trois services principaux : études techniques, "
            "suivi-contrôle de travaux et essais de laboratoire.",
            "order": 1,
        },
        {
            "category": FAQCategory.PROJETS,
            "question": "Quels types de projets réalisez-vous ?",
            "answer": "Nous intervenons dans les domaines des routes et voiries, bâtiments et structures, "
            "hydraulique et assainissement, et aménagements urbains.",
            "order": 1,
        },
        {
            "category": FAQCategory.CLIENTS,
            "question": "Comment accéder à l'espace client ?",
            "answer": "Après inscription, un administrateur doit vous accorder l'accès client. "
            "Vous pourrez ensuite consulter vos projets et documents via le portail.",
            "order": 1,
        },
        {
            "category": FAQCategory.CONTACT,
            "question": "Comment demander un devis ?",
            "answer": "Utilisez le formulaire de contact sur notre site ou envoyez un email à "
            "info@mygeoconsulting.com avec les détails de votre projet.",
            "order": 1,
        },
    ]

    for entry in faq_entries:
        faq, created = FAQ.objects.get_or_create(
            question=entry["question"],
            defaults={
                "answer": entry["answer"],
                "category": entry["category"],
                "order": entry["order"],
                "published": True,
                "created_by": admin_user,
            },
        )
        print(f"FAQ '{entry['question'][:50]}...': {'created' if created else 'already exists'}")


if __name__ == "__main__":
    seed()
    print("\nSeed complete.")
