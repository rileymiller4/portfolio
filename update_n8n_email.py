import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from projects.models import Project

email_content = """Subject: Regarding Your Faucet Replacement Request - Estimate & Scheduling
From: millertopics@gmail.com

Hi Jack,

Thank you for reaching out! We received your request to replace your faucet at 123 ABC St.

You mentioned wanting the service this Monday at 3pm. While we are unavailable at that specific time, we can offer the following slots for your faucet replacement:

* Thursday at 4:30pm
* Thursday at 5:30pm
* Saturday at 9:00am

The estimated cost for this service is $120.

Please reply with your preferred slot to confirm. Our arrival window is 2 hours.

We look forward to assisting you!

Sincerely,
Your Handyman Team

---
This email was sent automatically with n8n
https://n8n.io"""

project = Project.objects.get(slug='n8n-agent-workflow-project')
project.email_output = email_content
project.save()
print("Email content added to n8n project!")
