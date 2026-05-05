import random
from datetime import date, time, timedelta
from decimal import Decimal
from django.contrib.auth.models import User
from django.db import transaction
from MainApp.models import AvailabilitySlot, BookingRequest, Review, Skill, UserReview

# -----------------------------
# CONFIG (change these numbers)
# -----------------------------
NUM_USERS = 40
NUM_SKILLS = 120
MAX_REVIEWS_PER_SKILL = 8
DEFAULT_PASSWORD = "Pass12345!"

CATEGORIES = ["academics", "tech", "creative", "wellness", "other"]
CONTACT_PREFS = ["email", "phone"]
AVAILABILITY = ["available", "busy", "scheduled"]

FIRST_NAMES = ["James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael", "Linda", "David", "Elizabeth", "William", "Barbara", "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah", "Christopher", "Karen", "Charles", "Lisa", "Daniel", "Nancy", "Matthew", "Betty", "Anthony", "Sandra", "Mark", "Margaret", "Donald", "Ashley", "Steven", "Kimberly", "Andrew", "Emily", "Paul", "Donna", "Joshua", "Michelle", "Kenneth", "Carol", "Kevin", "Amanda"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores", "Green", "Adams", "Nelson", "Baker", "Hall"]

SKILL_TOPICS = [
    "Calculus Tutoring", "Python Help", "Chemistry Support", "Essay Editing",
    "Resume Review", "Interview Coaching", "Guitar Lessons", "Piano Basics",
    "Graphic Design Help", "Video Editing", "Photography Tips",
    "Public Speaking", "Spanish Conversation", "French Practice",
    "Time Management Coaching", "Statistics Tutoring", "Web Dev Mentoring",
    "Java Programming Help", "Data Structures Help", "Cooking Basics"
]

REVIEW_COMMENTS = [
    "Very helpful and easy to understand.",
    "Great session, would book again.",
    "Friendly and clear explanations.",
    "Good pace and practical examples.",
    "Helped me improve quickly.",
    "Worth it. Learned a lot.",
    "Professional and patient.",
    "Excellent support for beginners."
]

@transaction.atomic
def run_seed():
    # Clean up old data to prevent duplication
    print("Deleting old data...")
    User.objects.filter(username__startswith="demo_user_").delete()
    User.objects.filter(email__endswith="@campus.edu").exclude(is_superuser=True).delete()
    UserReview.objects.all().delete()
    BookingRequest.objects.all().delete()
    AvailabilitySlot.objects.all().delete()
    Skill.objects.all().delete()
    Review.objects.all().delete()

    users = []
    created_users = 0
    created_skills = 0
    created_reviews = 0

    prefixes = ["Beginner's Guide to", "Advanced", "Mastering", "Creative", "Fundamentals of", "Introduction to"]

    # 1) Create users
    for i in range(1, NUM_USERS + 1):
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        username = f"{first.lower()}.{last.lower()}{random.randint(10,99)}"
        email = f"{username}@campus.edu"
        
        u, created = User.objects.get_or_create(username=username, defaults={
            "email": email,
            "first_name": first,
            "last_name": last
        })
        if created:
            u.set_password(DEFAULT_PASSWORD)
            u.save()
            created_users += 1
            
            # Give user random availability slots for next month
            today = date.today()
            for day_offset in range(1, 31):
                if random.choice([True, False, False]): # 33% chance they are free that day
                    hour = random.choice([10, 11, 13, 14, 15, 16])
                    AvailabilitySlot.objects.create(
                        user=u,
                        date=today + timedelta(days=day_offset),
                        start_time=time(hour, 0),
                        is_booked=random.choice([True, False, False]) # 33% chance it's already booked
                    )
        users.append(u)

    # 2) Create skills
    skills = []
    
    # Map each prefix to a tailored 2-sentence description template
    prefix_descriptions = {
        "Beginner's Guide to": "This session is perfect for those just starting out with {topic}. We will cover all the basic concepts to get you up and running.",
        "Advanced": "Take your knowledge of {topic} to the next level with this advanced session. We will dive deep into complex strategies and expert techniques.",
        "Mastering": "Achieve true expertise and mastery in {topic} through guided practice. This comprehensive session will refine your skills to perfection.",
        "Creative": "Explore the artistic and innovative side of {topic} with this unique session. Get ready to think outside the box and create something amazing.",
        "Fundamentals of": "Build a strong foundation by learning the core principles of {topic}. This session provides everything you need to understand the underlying mechanics.",
        "Introduction to": "Discover the exciting world of {topic} in this welcoming introductory session. No prior experience is required to jump in and start learning."
    }

    for i in range(1, NUM_SKILLS + 1):
        owner = random.choice(users)
        topic = random.choice(SKILL_TOPICS)
        prefix = random.choice(prefixes)
        title = f"{prefix} {topic}"
        is_free = random.choice([True, False])
        desc = prefix_descriptions[prefix].format(topic=topic)
        
        try:
            skill = Skill.objects.create(
                owner=owner,
                title=title,
                description=desc,
                category=random.choice(CATEGORIES),
                is_free=is_free,
                price=None if is_free else Decimal(random.choice([10, 15, 20, 25, 30])),
                contact_preference=random.choice(CONTACT_PREFS),
                availability_status=random.choice(AVAILABILITY),
                )
            skills.append(skill)
            created_skills += 1
        except Exception as e:
            print(f"Error creating skill {title}: {e}")

    # 3) Create reviews/ratings
    print("Creating reviews...")
    if not skills:
        print("No new skills were created, skipping review creation.")
    else:
        for skill in skills:
            possible_reviewers = [u for u in users if u != skill.owner]
            if not possible_reviewers:
                continue
            
            random.shuffle(possible_reviewers)
            n_reviews = random.randint(0, min(MAX_REVIEWS_PER_SKILL, len(possible_reviewers)))

            for reviewer in possible_reviewers[:n_reviews]:
                review, was_created = Review.objects.get_or_create(
                    skill=skill,
                    reviewer=reviewer,
                    defaults={
                        "rating": random.randint(3, 5),
                        "comment": random.choice(REVIEW_COMMENTS),
                    },
                )
                if was_created:
                    created_reviews += 1

    # 4) Add dummy requests for riley_miller5
    print("Creating dummy requests for riley_miller5...")
    try:
        riley, created = User.objects.get_or_create(username='riley_miller5', defaults={
            'email': 'riley_miller5@campus.edu',
            'first_name': 'Riley',
            'last_name': 'Miller'
        })
        if created:
            riley.set_password(DEFAULT_PASSWORD)
            riley.save()
            
        # Give Riley some skills
        riley_skills = []
        for _ in range(3):
            topic = random.choice(SKILL_TOPICS)
            prefix = random.choice(prefixes)
            skill = Skill.objects.create(
                owner=riley,
                title=f"{prefix} {topic}",
                description=prefix_descriptions[prefix].format(topic=topic),
                category=random.choice(CATEGORIES),
                is_free=True,
                contact_preference="email",
                availability_status="available"
            )
            riley_skills.append(skill)
            
            # Give riley availability slots for the skills
            today = date.today()
            for day_offset in range(1, 14):
                if random.choice([True, False]): 
                    hour = random.choice([10, 11, 13, 14])
                    AvailabilitySlot.objects.create(
                        user=riley,
                        date=today + timedelta(days=day_offset),
                        start_time=time(hour, 0),
                        is_booked=False
                    )

        # Create incoming requests for Riley's skills
        for skill in riley_skills:
            # Grab some random available slots for this skill owner
            slots = list(AvailabilitySlot.objects.filter(user=riley, is_booked=False)[:3])
            
            for slot in slots:
                requester = random.choice([u for u in users if u != riley])
                BookingRequest.objects.create(
                    skill=skill,
                    requester=requester,
                    status=random.choice(["pending", "pending", "approved"]),
                    slot=slot
                )
                slot.is_booked = True
                slot.save()
                
            # Create a "completed" incoming request for Riley to review the customer
            past_slot = AvailabilitySlot.objects.create(
                user=riley, date=today - timedelta(days=2), start_time=time(12, 0), is_booked=True
            )
            past_requester = random.choice([u for u in users if u != riley])
            BookingRequest.objects.create(
                skill=skill, requester=past_requester, status="completed", slot=past_slot
            )

            # Create user-to-user reviews for the completed session
            UserReview.objects.get_or_create(
                reviewer=riley,
                reviewee=past_requester,
                defaults={
                    "rating": random.randint(4, 5),
                    "comment": random.choice([
                        "Great communication and showed up on time.",
                        "Friendly and respectful throughout the session.",
                        "Clear goals and easy to work with.",
                    ]),
                },
            )
            UserReview.objects.get_or_create(
                reviewer=past_requester,
                reviewee=riley,
                defaults={
                    "rating": random.randint(4, 5),
                    "comment": random.choice([
                        "Super helpful and explained things clearly.",
                        "Professional session — would book again.",
                        "Made the topic much easier to understand.",
                    ]),
                },
            )
            
        # Create a "completed" outgoing request for Riley (Riley bought a service)
        other_skill = random.choice([s for s in skills if s.owner != riley])
        past_slot2 = AvailabilitySlot.objects.create(
            user=other_skill.owner, date=today - timedelta(days=3), start_time=time(14, 0), is_booked=True
        )
        BookingRequest.objects.create(
            skill=other_skill, requester=riley, status="completed", slot=past_slot2
        )

        # Add reviews for the provider Riley learned from
        UserReview.objects.get_or_create(
            reviewer=riley,
            reviewee=other_skill.owner,
            defaults={
                "rating": random.randint(4, 5),
                "comment": random.choice([
                    "Explained everything in a way that clicked.",
                    "Very patient and knowledgeable.",
                    "Good pacing and practical examples.",
                ]),
            },
        )
        UserReview.objects.get_or_create(
            reviewer=other_skill.owner,
            reviewee=riley,
            defaults={
                "rating": random.randint(4, 5),
                "comment": random.choice([
                    "Came prepared and asked great questions.",
                    "Easy to work with and respectful of time.",
                    "Clear about goals — great session.",
                ]),
            },
        )
                
    except Exception as e:
        print(f"Error creating riley_miller5 dummy data: {e}")

    print("\n✅ Seed complete")
    print(f"Users created:   {created_users}")
    print(f"Skills created:  {created_skills}")
    print(f"Reviews created: {created_reviews}")
    print("--------------------")
    print(f"Total users:     {User.objects.count()}")
    print(f"Total skills:    {Skill.objects.count()}")
    print(f"Total reviews:   {Review.objects.count()}")