# Generated by Django 4.2.2 on 2024-06-04 14:36

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('djapp', '0009_alter_issue_assignee'),
    ]

    operations = [
        migrations.AddField(
            model_name='epic',
            name='Priority',
            field=models.CharField(default='', max_length=30),
        ),
        migrations.AddField(
            model_name='epic',
            name='StoryPoint',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='issue',
            name='Priority',
            field=models.CharField(default='', max_length=30),
        ),
        migrations.AddField(
            model_name='issue',
            name='StoryPoint',
            field=models.IntegerField(default=1),
        ),
        migrations.CreateModel(
            name='Comments',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('CommentId', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('WrittenBy', models.CharField(default='', max_length=50)),
                ('CreatedAt', models.DateTimeField(default=django.utils.timezone.now)),
                ('EditedAt', models.DateTimeField(default=django.utils.timezone.now)),
                ('CommentBody', models.TextField(default='', max_length=300)),
                ('IssueId', models.ForeignKey(blank=True, default='null', null=True, on_delete=django.db.models.deletion.CASCADE, to='djapp.issue')),
                ('ProjectId', models.ForeignKey(blank=True, default='null', null=True, on_delete=django.db.models.deletion.SET_NULL, to='djapp.project')),
            ],
        ),
    ]