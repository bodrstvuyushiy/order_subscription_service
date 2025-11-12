from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("subscriptions", "0002_alter_usersubscription_user"),
    ]

    operations = [
        migrations.CreateModel(
            name="SubscriptionPlan",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("subscribe_type", models.CharField(max_length=128, unique=True)),
                ("title", models.CharField(blank=True, max_length=128)),
                ("price", models.PositiveIntegerField()),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "ordering": ("subscribe_type",),
            },
        ),
    ]
