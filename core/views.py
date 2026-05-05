from django.conf import settings
from django.shortcuts import render
from .models import AboutPage, SkillsPage
from projects.models import Project


def home(request):
	featured_projects = Project.objects.order_by('title')[:3]
	return render(request, 'core/home.html', {'featured_projects': featured_projects})


def about(request):
	about_page = AboutPage.objects.first()
	return render(request, 'core/about.html', {'about_page': about_page})


def skills(request):
	skills_page = SkillsPage.objects.first()
	return render(request, 'core/skills.html', {'skills_page': skills_page})


def resume(request):
	resume_pdf = settings.BASE_DIR / 'static' / 'resume' / 'resume.pdf'
	resume_enabled = resume_pdf.exists()
	return render(request, 'core/resume.html', {'resume_enabled': resume_enabled})


def contact(request):
	profile_dir = settings.BASE_DIR / 'static' / 'profile'
	profile_candidates = [
		'gradpic.jpg',
		'me.jpg',
		'me.png',
		'profile.jpg',
		'profile.png',
	]
	profile_photo_path = None
	for filename in profile_candidates:
		candidate = profile_dir / filename
		if candidate.exists():
			profile_photo_path = f'profile/{filename}'
			break
	profile_enabled = bool(profile_photo_path)
	return render(
		request,
		'core/contact.html',
		{
			'profile_enabled': profile_enabled,
			'profile_photo_path': profile_photo_path,
			'contact_name': 'Riley Miller',
			'contact_email': 'millertopics@gmail.com',
			'contact_phone': '5129947672',
		},
	)
