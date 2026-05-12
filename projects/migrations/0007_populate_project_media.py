from django.db import migrations


def populate_project_media(apps, schema_editor):
    Project = apps.get_model('projects', 'Project')

    media_map = {
        'chatbot-project': {
            'image': 'projects/7b0377c8-f16d-4bdf-986c-485571ab8a5e.png',
        },
        'n8n-agent-workflow-project': {
            'image': 'projects/n8npic.png',
            'workflow_image': 'projects/workflows/workflow1.png',
        },
        'langchain-agent-project': {
            'image': 'projects/handyman_wcuovjd.png',
            'workflow_image': 'projects/workflows/handyman_appointment.png',
        },
        'google-ai-studio-media-project': {
            'image': 'projects/trex-1.jpg',
            'video': 'projects/videos/jurassicpark_1.mp4',
        },
        'machine-learning-project-scikit-learn': {
            'image': 'projects/irisresult.png',
        },
        'campus-skillswap-django-project': {
            'image': 'projects/Screenshot_2026-05-01_141747.png',
        },
    }

    for slug, values in media_map.items():
        project = Project.objects.filter(slug=slug).first()
        if not project:
            continue

        changed_fields = []
        for field_name, path in values.items():
            current_value = getattr(project, field_name)
            if not current_value:
                setattr(project, field_name, path)
                changed_fields.append(field_name)

        if changed_fields:
            project.save(update_fields=changed_fields)


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0006_project_email_output'),
    ]

    operations = [
        migrations.RunPython(populate_project_media, migrations.RunPython.noop),
    ]