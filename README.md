# N.O.K – Network of Knowledge (Bootstrap Edition)

Django + SQLite project with:
- Custom user roles: student, teacher, CEO
- Z Coin wallet & referral system
- Courses & course parts with 10% platform commission and XP rewards
- Events/tournaments with Z Coin entry and joining
- Reviews system for courses
- AI Teacher chat using OpenAI (gpt-4o-mini)
- Bootstrap 5 responsive UI with psychology-focused copy

## Setup

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

export OPENAI_API_KEY="your_key_here"
export DJANGO_SECRET_KEY="your_secret"
export DJANGO_DEBUG="False"
export DJANGO_ALLOWED_HOSTS="yourdomain.com"
```

Run migrations:

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 0.0.0.0:8000
```

Open http://localhost:8000

Use /admin/ to:
- Create courses, parts, lessons
- Create activities (tournaments, standups, hackathons)
- Manage users and roles

Students:
- Register with role student
- Use wallet to simulate deposits and convert UZS to Z Coins
- Buy course parts (10% goes to platform, 90% to teacher)
- Ask questions via AI teacher

Teachers:
- Register / be set as teacher in admin
- Create courses via admin
- Earn Z Coins from students

CEOs:
- Register / be set as ceo in admin
- Manage activities and platform health via admin
