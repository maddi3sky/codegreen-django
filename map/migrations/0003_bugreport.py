from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('map', '0002_pledge'),
    ]

    operations = [
        migrations.CreateModel(
            name='BugReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('contact', models.CharField(blank=True, max_length=256)),
                ('site', models.CharField(blank=True, max_length=64)),
                ('url', models.URLField(blank=True, max_length=512)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
