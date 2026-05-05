from django.db import models


class AboutPage(models.Model):
	title = models.CharField(max_length=120, default='About')
	intro = models.TextField(blank=True)
	story_title = models.CharField(max_length=120, default='My Story')
	story_text = models.TextField(blank=True)
	bring_title = models.CharField(max_length=120, default='What I Bring')
	bring_points = models.TextField(blank=True, help_text='One bullet per line.')
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['title']

	def __str__(self) -> str:
		return self.title

	@property
	def bring_points_list(self) -> list[str]:
		return [line.strip() for line in (self.bring_points or '').splitlines() if line.strip()]


class SkillsPage(models.Model):
	title = models.CharField(max_length=120, default='Skills')
	intro = models.TextField(blank=True)
	skills_text = models.TextField(blank=True, help_text='One skill per line.')
	tip_title = models.CharField(max_length=120, default='Tip')
	tip_text = models.TextField(blank=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['title']

	def __str__(self) -> str:
		return self.title

	@property
	def skills_list(self) -> list[str]:
		return [line.strip() for line in (self.skills_text or '').splitlines() if line.strip()]


class ContactMessage(models.Model):
	name = models.CharField(max_length=120)
	email = models.EmailField()
	subject = models.CharField(max_length=200)
	message = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-created_at']

	def __str__(self) -> str:
		return f"{self.name}: {self.subject}"
