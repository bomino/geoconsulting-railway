import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0006_populate_department_division_fks"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="teammember",
            name="department",
        ),
        migrations.RemoveField(
            model_name="teammember",
            name="division",
        ),
        migrations.RenameField(
            model_name="teammember",
            old_name="department_fk",
            new_name="department",
        ),
        migrations.RenameField(
            model_name="teammember",
            old_name="division_fk",
            new_name="division",
        ),
        migrations.AlterField(
            model_name="teammember",
            name="department",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="members",
                to="core.department",
            ),
        ),
        migrations.AlterField(
            model_name="teammember",
            name="division",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="members",
                to="core.division",
            ),
        ),
        migrations.AlterModelOptions(
            name="teammember",
            options={
                "ordering": [
                    "department__order",
                    "division__order",
                    "order",
                    "last_name",
                ],
                "verbose_name": "Membre de l'équipe",
                "verbose_name_plural": "Membres de l'équipe",
            },
        ),
    ]
