from django.db import migrations

DEPARTMENTS = [
    {"name": "Direction Générale", "slug": "direction", "order": 0, "is_direction": True},
    {"name": "Recherche, Innovation, Qualité", "slug": "recherche", "order": 1, "is_direction": False},
    {"name": "Administratif", "slug": "admin", "order": 2, "is_direction": False},
    {"name": "Études, Maîtrise d'Oeuvre, Contrôles Extérieurs", "slug": "etudes", "order": 3, "is_direction": False},
    {"name": "Laboratoire", "slug": "laboratoire", "order": 4, "is_direction": False},
]

DIVISIONS = [
    {"name": "Ressource Humaine, Communication, Marketing", "slug": "rh-comm", "dept_slug": "admin", "order": 1},
    {"name": "Comptable et Développement", "slug": "comptable", "dept_slug": "admin", "order": 2},
    {"name": "Béton", "slug": "beton", "dept_slug": "laboratoire", "order": 1},
    {"name": "Environnement, Hydrogéologie, Pédologie, Bitume", "slug": "environnement", "dept_slug": "laboratoire", "order": 2},
    {"name": "Géotechnique Routière et Bâtiment", "slug": "geotechnique", "dept_slug": "laboratoire", "order": 3},
]

OLD_DIVISION_SLUG_MAP = {
    "rh_comm": "rh-comm",
    "comptable": "comptable",
    "beton": "beton",
    "environnement": "environnement",
    "geotechnique": "geotechnique",
}


def forward(apps, schema_editor):
    Department = apps.get_model("core", "Department")
    Division = apps.get_model("core", "Division")
    TeamMember = apps.get_model("core", "TeamMember")

    dept_map = {}
    for d in DEPARTMENTS:
        dept = Department.objects.create(**d)
        dept_map[dept.slug] = dept

    div_map = {}
    for d in DIVISIONS:
        dept = dept_map[d["dept_slug"]]
        div = Division.objects.create(
            name=d["name"], slug=d["slug"], department=dept, order=d["order"]
        )
        div_map[div.slug] = div

    for member in TeamMember.objects.all():
        if member.department:
            member.department_fk = dept_map.get(member.department)
        if member.division:
            new_slug = OLD_DIVISION_SLUG_MAP.get(member.division)
            if new_slug:
                member.division_fk = div_map.get(new_slug)
        member.save(update_fields=["department_fk", "division_fk"])


def reverse(apps, schema_editor):
    Department = apps.get_model("core", "Department")
    Division = apps.get_model("core", "Division")
    TeamMember = apps.get_model("core", "TeamMember")

    slug_to_old_div = {v: k for k, v in OLD_DIVISION_SLUG_MAP.items()}

    for member in TeamMember.objects.all():
        if member.department_fk:
            member.department = member.department_fk.slug
        if member.division_fk:
            member.division = slug_to_old_div.get(member.division_fk.slug, "")
        member.save(update_fields=["department", "division"])

    Division.objects.all().delete()
    Department.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0005_department_division_models"),
    ]

    operations = [
        migrations.RunPython(forward, reverse),
    ]
