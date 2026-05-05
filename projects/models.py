from django.db import models
from django.urls import reverse
from django.utils.text import slugify

import re


class Project(models.Model):
	title = models.CharField(max_length=200)
	slug = models.SlugField(max_length=220, unique=True, blank=True)

	one_sentence_summary = models.CharField(max_length=255)
	business_problem = models.TextField()
	tools_used = models.TextField(blank=True)
	key_features = models.TextField(blank=True)
	role_contribution = models.TextField(blank=True)
	biggest_challenge = models.TextField(blank=True)
	what_i_learned = models.TextField(blank=True)
	prompt_text = models.TextField(blank=True)

	image = models.ImageField(upload_to='projects/', blank=True, null=True)
	workflow_image = models.ImageField(upload_to='projects/workflows/', blank=True, null=True)
	video = models.FileField(upload_to='projects/videos/', blank=True, null=True)
	github_url = models.URLField(blank=True)
	demo_url = models.CharField(max_length=500, blank=True)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['title']

	def __str__(self) -> str:
		return self.title

	def save(self, *args, **kwargs):
		self.github_url = (self.github_url or '').strip()
		self.demo_url = (self.demo_url or '').strip()

		if not self.slug:
			base_slug = slugify(self.title)[:200] or 'project'
			candidate = base_slug
			suffix = 2
			while Project.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
				candidate = f"{base_slug}-{suffix}"
				suffix += 1
			self.slug = candidate
		return super().save(*args, **kwargs)

	def get_absolute_url(self):
		return reverse('project_detail', kwargs={'slug': self.slug})

	@staticmethod
	def _split_lines(value: str) -> list[str]:
		return [line.strip() for line in (value or '').splitlines() if line.strip()]

	@staticmethod
	def _clean_tool_label(value: str) -> str:
		"""Return a display-friendly tool label with version pins removed.

		Examples:
		- "langchain==1.2.11" -> "langchain"
		- "Django>=5.2,<6.0" -> "Django"
		- "pkg @ https://..." -> "pkg"
		"""
		label = (value or '').strip()
		if not label:
			return ''

		label = label.split(';', 1)[0].strip()
		label = re.sub(r"\s+@.*$", "", label).strip()
		label = re.sub(r"\s*\(.*\)\s*$", "", label).strip()
		label = re.split(r"\s*(?:==|>=|<=|~=|!=|>|<|=)\s*", label, maxsplit=1)[0].strip()
		label = label.split('[', 1)[0].strip()
		return label

	@property
	def tools_list(self) -> list[str]:
		return self._split_lines(self.tools_used)

	@property
	def tools_list_clean(self) -> list[str]:
		seen: set[str] = set()
		cleaned: list[str] = []
		for item in self.tools_list:
			label = self._clean_tool_label(item)
			if not label:
				continue
			key = label.casefold()
			if key in seen:
				continue
			seen.add(key)
			cleaned.append(label)
		return cleaned

	@property
	def features_list(self) -> list[str]:
		return self._split_lines(self.key_features)

	@property
	def is_handyman(self) -> bool:
		title = (self.title or '').casefold()
		slug = (self.slug or '').casefold()
		return 'handyman' in title or 'handyman' in slug

	@property
	def is_langchain(self) -> bool:
		title = (self.title or '').casefold()
		slug = (self.slug or '').casefold()
		return 'langchain' in title or 'langchain' in slug

	@property
	def is_chatbot(self) -> bool:
		title = (self.title or '').casefold()
		slug = (self.slug or '').casefold()
		return 'chatbot' in title or 'chatbot' in slug
