from django.views.generic import DetailView, ListView

from .models import Project


class ProjectListView(ListView):
	model = Project
	template_name = 'projects/project_list.html'
	context_object_name = 'projects'


class ProjectDetailView(DetailView):
	model = Project
	template_name = 'projects/project_detail.html'
	context_object_name = 'project'
