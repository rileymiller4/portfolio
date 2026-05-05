# AI Portfolio (Django)

A Django portfolio site with pages for Home, About, Projects + Project Detail, Skills, Resume, and Contact.

## Run locally

```powershell
./.venv/Scripts/Activate.ps1
python manage.py runserver
```

Admin: http://127.0.0.1:8000/admin/

## Reset / create Admin login

If you can’t log into `/admin/`, create a fresh superuser and set a password:

```powershell
./.venv/Scripts/Activate.ps1

# create admin user (no password yet)
python manage.py createsuperuser --username admin --email admin@example.com --noinput

# set password (you will type it in the terminal)
python manage.py changepassword admin
```

To change the admin username later:

```powershell
python manage.py shell
```

Then run:

```python
from django.contrib.auth import get_user_model
User = get_user_model()
u = User.objects.get(username="admin")
u.username = "new_username_here"
u.save()
```

## Add / edit your projects

1. Create an admin user:

```powershell
python manage.py createsuperuser
```

2. In Admin → Projects → Projects, edit each project:
- **GitHub URL**: link to the repo (or a specific folder/README)
- **Demo URL**: link to a deployed demo (best), or a local link during your mock interview
- **Image**: upload a screenshot (shown on list + detail pages)

## Screenshot for SkillSwap (home page)

Because images must be files on your computer, the easiest workflow is:

1. Open your SkillSwap home page in a browser.
2. Take a screenshot.
3. Save it as `PNG` or `JPG`.
4. Go to Admin → Projects → **Campus SkillSwap Django Project** → upload the file in the **Image** field.

Django will store it under `media/projects/` automatically.

### Alternative: attach a screenshot without uploading in Admin

1. Save your screenshot file into `media/projects/` (example: `media/projects/skillswap-home.png`).
2. Run this to point the SkillSwap portfolio project at that file:

```powershell
python manage.py shell -c "from projects.models import Project; p=Project.objects.get(slug='campus-skillswap-django-project'); p.image='projects/skillswap-home.png'; p.save(); print('updated image')"
```

## Note about local demo links

`http://127.0.0.1:8000/` only works on your machine.
For a link you can share publicly, deploy SkillSwap (Render/Railway/Fly.io/etc.) and paste the public URL into **Demo URL**.

## SkillSwap inside this portfolio

This portfolio project includes a `/skillswap/` route (see `skillswap/`).
If your SkillSwap app lives inside this same Django project, set the SkillSwap project's **Demo URL** to:

- `/skillswap/`

### Integrated SkillSwap app

If you have an existing SkillSwap Django project (like your `campus_skillswap` folder), the portfolio can host the real app under:

- http://127.0.0.1:8000/skillswap/

In this repo, the SkillSwap app code is located at:

- `MainApp/` (Django app)
- `templates/skillswap/` (SkillSwap templates)

### Seed SkillSwap demo data

The SkillSwap app includes several Django **management commands** you can run from this portfolio repo:

```powershell
python manage.py seed
```

Other useful seed helpers:

```powershell
python manage.py seed_unreviewed_completed --username <your_username> --provided 3 --received 3
python manage.py normalize_dummy_peers --seed 123
python manage.py cleanup_dummy_seed --yes
```

Tip: after seeding, open SkillSwap at http://127.0.0.1:8000/skillswap/

### Connecting your projects (GitHub, demos, screenshots)

The portfolio site is driven by the `projects.Project` model, so each project’s detail page is generated from database fields.

- **Add/edit project content**: go to `/admin/` → Projects → Projects.
- **GitHub link (coding projects)**: paste your repo URL into **GitHub URL** (example: `https://github.com/<you>/<repo>`).
- **Demo link**:
	- For external demos: use a full URL (example: `https://…`).
	- For internal demos inside this Django site: use a path (example: `/skillswap/`).
	- If the URL is a YouTube/Vimeo share link, the project detail page will embed the video automatically.
- **Screenshot / visual**:
	- Upload an image in the **Image** field.
	- Images are served from `/media/…` in development.
	- You can also upload a local `.mp4`/`.webm` in the **Video** field to embed it directly on the project page.
	- Optional: paste your generation prompt into the **Prompt text** field to display it under the visual.

SkillSwap specifically is mounted at `/skillswap/` and should be linked from the **Campus SkillSwap Django Project** detail page via its Demo link.

## Google AI Studio: show your prompt + starting image

If you have a starting image and a `.docx` file containing your prompt, you can attach both to the **Google AI Studio Media Project** in one command:

```powershell
python scripts/set_google_ai_studio_assets.py <path-to-image> <path-to-prompt-docx>
```

Example:

```powershell
python scripts/set_google_ai_studio_assets.py assets/dino.png assets/dinoprompt.docx
```

This copies the image into `media/projects/` and saves the prompt text into the project’s **Prompt Used** section.
