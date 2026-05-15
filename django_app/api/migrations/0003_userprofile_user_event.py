import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('api', '0002_userprofile_delete_blogpost'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='user',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('date', models.DateField()),
                ('time', models.TimeField()),
                ('description', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='events', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['date', 'time'],
            },
        ),
    ]
    
    def apply(self, project_state, schema_editor, collect_sql=False):
        # Skip CreateModel if table already exists
        from django.db import connection
        existing_tables = connection.introspection.table_names()
        new_operations = []
        for operation in self.operations:
            if hasattr(operation, 'name') and operation.__class__.__name__ == 'CreateModel':
                table_name = f"api_{operation.name.lower()}"
                if table_name in existing_tables:
                    continue
            new_operations.append(operation)
        self.operations = new_operations
        return super().apply(project_state, schema_editor, collect_sql)
