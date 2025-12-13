from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="teacher_subject",
            field=models.CharField(blank=True, max_length=120),
        ),
        migrations.AddField(
            model_name="user",
            name="teacher_pack_price_z",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="user",
            name="teacher_bio",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="user",
            name="teacher_enrolled",
            field=models.BooleanField(default=False),
        ),
    ]
