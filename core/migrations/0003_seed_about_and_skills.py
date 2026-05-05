from django.db import migrations


def seed_content(apps, schema_editor):
	AboutPage = apps.get_model('core', 'AboutPage')
	SkillsPage = apps.get_model('core', 'SkillsPage')

	AboutPage.objects.get_or_create(
		title='About',
		defaults={
			'intro': 'Use this page to explain who you are, what roles you are targeting, and how you approach AI projects.',
			'story_title': 'My Story',
			'story_text': 'Replace this with a short narrative: background, interests, and what motivates your work.',
			'bring_title': 'What I Bring',
			'bring_points': 'End-to-end delivery (idea -> MVP -> demo)\nClear communication of business value\nPractical AI engineering and evaluation',
		},
	)

	SkillsPage.objects.get_or_create(
		title='Skills',
		defaults={
			'intro': 'A quick snapshot of tools and strengths I use across projects.',
			'skills_text': 'Python\nDjango\nSQL / SQLite\nGit & GitHub\nLangChain / LLM tooling\nn8n workflows\nPrompting & evaluation\nscikit-learn',
			'tip_title': 'Tip',
			'tip_text': 'Tailor this list to the roles you are interviewing for (AI engineer, data analyst, full-stack, etc.).',
		},
	)


class Migration(migrations.Migration):

	dependencies = [
		('core', '0002_aboutpage_skillspage'),
	]

	operations = [
		migrations.RunPython(seed_content, migrations.RunPython.noop),
	]