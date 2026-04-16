from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from api.models import JobSeekerProfile, EmployerProfile, Job

User = get_user_model()


class Command(BaseCommand):
    help = 'Seeds demo data for the job portal'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding demo data...')

        # Create employer users
        employers_data = [
            {
                'email': 'hr@techcorp.com', 'username': 'techcorp',
                'password': 'demo1234', 'role': 'employer',
                'company': {'company_name': 'TechCorp India', 'industry': 'Information Technology',
                            'company_size': '200-500', 'location': 'Bangalore', 'website': 'https://techcorp.in',
                            'description': 'Leading software product company building enterprise solutions.'}
            },
            {
                'email': 'jobs@startupx.com', 'username': 'startupx',
                'password': 'demo1234', 'role': 'employer',
                'company': {'company_name': 'StartupX', 'industry': 'FinTech',
                            'company_size': '10-50', 'location': 'Delhi',
                            'description': 'Fast-growing fintech startup disrupting payments.'}
            },
            {
                'email': 'recruit@datahouse.io', 'username': 'datahouse',
                'password': 'demo1234', 'role': 'employer',
                'company': {'company_name': 'DataHouse Analytics', 'industry': 'Data Analytics',
                            'company_size': '50-200', 'location': 'Hyderabad',
                            'description': 'AI and data analytics firm serving Fortune 500 clients.'}
            },
        ]

        created_employers = []
        for ed in employers_data:
            user, created = User.objects.get_or_create(email=ed['email'], defaults={
                'username': ed['username'], 'role': ed['role']
            })
            if created:
                user.set_password(ed['password'])
                user.save()
            emp, _ = EmployerProfile.objects.get_or_create(user=user, defaults=ed['company'])
            created_employers.append(emp)
            self.stdout.write(f'  Employer: {emp.company_name}')

        # Create seeker users
        seekers_data = [
            {
                'email': 'saim@demo.com', 'username': 'saim_dev', 'password': 'demo1234',
                'profile': {'full_name': 'Saim Khan', 'skills': 'Python, Django, REST API, SQL, JavaScript, HTML, CSS',
                            'experience_years': 1, 'education': 'B.Sc. Computer Science',
                            'location': 'Delhi', 'bio': 'CS grad passionate about backend development.'}
            },
            {
                'email': 'rahul@demo.com', 'username': 'rahul_ds', 'password': 'demo1234',
                'profile': {'full_name': 'Rahul Sharma', 'skills': 'Python, Machine Learning, Pandas, NumPy, SQL, TensorFlow',
                            'experience_years': 2, 'education': 'M.Sc. Data Science',
                            'location': 'Bangalore', 'bio': 'Data science enthusiast with ML expertise.'}
            },
        ]

        for sd in seekers_data:
            user, created = User.objects.get_or_create(email=sd['email'], defaults={
                'username': sd['username'], 'role': 'seeker'
            })
            if created:
                user.set_password(sd['password'])
                user.save()
            JobSeekerProfile.objects.get_or_create(user=user, defaults=sd['profile'])
            self.stdout.write(f'  Seeker: {sd["profile"]["full_name"]}')

        # Create jobs
        jobs_data = [
            {
                'employer': created_employers[0],
                'title': 'Python Backend Developer',
                'description': 'We are looking for a Python developer to build scalable REST APIs.\n\nResponsibilities:\n- Build and maintain Django REST APIs\n- Write clean, tested code\n- Work with PostgreSQL databases\n- Collaborate with frontend team',
                'required_skills': 'Python, Django, REST API, SQL, Git',
                'location': 'Bangalore (Hybrid)',
                'job_type': 'full_time',
                'salary_min': 40000, 'salary_max': 80000,
                'experience_required': 1,
            },
            {
                'employer': created_employers[0],
                'title': 'Full Stack Developer (Django + React)',
                'description': 'Join our product team to build cutting-edge web applications.\n\nYou will be working on both backend APIs and modern React frontends.\n\nIdeal for developers who love end-to-end ownership.',
                'required_skills': 'Django, React, JavaScript, Python, REST API, HTML, CSS',
                'location': 'Bangalore',
                'job_type': 'full_time',
                'salary_min': 50000, 'salary_max': 100000,
                'experience_required': 2,
            },
            {
                'employer': created_employers[1],
                'title': 'Backend Developer Intern',
                'description': 'Exciting internship opportunity at a fast-growing fintech startup.\n\nYou will work directly with senior engineers on real payment systems.\n\nPerfect for final year students or fresh graduates.',
                'required_skills': 'Python, Django, SQL, REST API',
                'location': 'Delhi',
                'job_type': 'internship',
                'salary_min': 15000, 'salary_max': 25000,
                'experience_required': 0,
            },
            {
                'employer': created_employers[1],
                'title': 'Junior Django Developer',
                'description': 'Looking for a motivated Django developer to join our growing team.\n\nWork on live fintech products serving thousands of users.\n\nFull training and mentorship provided.',
                'required_skills': 'Django, Python, HTML, CSS, JavaScript, SQL',
                'location': 'Delhi (Remote)',
                'job_type': 'remote',
                'salary_min': 30000, 'salary_max': 55000,
                'experience_required': 1,
            },
            {
                'employer': created_employers[2],
                'title': 'Data Analyst',
                'description': 'Join our analytics team and help clients make data-driven decisions.\n\nYou will build dashboards, run SQL queries, and present insights to stakeholders.',
                'required_skills': 'Python, SQL, Pandas, Excel, Power BI, Data Visualization',
                'location': 'Hyderabad',
                'job_type': 'full_time',
                'salary_min': 35000, 'salary_max': 65000,
                'experience_required': 1,
            },
            {
                'employer': created_employers[2],
                'title': 'Machine Learning Engineer',
                'description': 'Build production ML models for our enterprise clients.\n\nWork with large datasets and deploy models at scale using Python and cloud platforms.',
                'required_skills': 'Python, Machine Learning, TensorFlow, Scikit-learn, SQL, NumPy, Pandas',
                'location': 'Hyderabad (Hybrid)',
                'job_type': 'full_time',
                'salary_min': 60000, 'salary_max': 120000,
                'experience_required': 2,
            },
            {
                'employer': created_employers[0],
                'title': 'Frontend Developer (HTML/CSS/JS)',
                'description': 'Create beautiful, responsive web interfaces.\n\nWork closely with designers to implement pixel-perfect UIs.\n\nNo framework required — pure HTML, CSS, and JavaScript.',
                'required_skills': 'HTML, CSS, JavaScript, Responsive Design, Git',
                'location': 'Remote',
                'job_type': 'remote',
                'salary_min': 25000, 'salary_max': 50000,
                'experience_required': 0,
            },
            {
                'employer': created_employers[1],
                'title': 'Product Manager - FinTech',
                'description': 'Lead product development for our payment platform.\n\nWork with engineering, design, and business teams to deliver world-class products.\n\nMBA preferred.',
                'required_skills': 'Product Management, Agile, SQL, Data Analysis, Communication',
                'location': 'Delhi',
                'job_type': 'full_time',
                'salary_min': 80000, 'salary_max': 150000,
                'experience_required': 3,
            },
        ]

        for jd in jobs_data:
            Job.objects.get_or_create(
                title=jd['title'], employer=jd['employer'],
                defaults=jd
            )
            self.stdout.write(f'  Job: {jd["title"]}')

        self.stdout.write(self.style.SUCCESS('\n✅ Seed data created successfully!'))
        self.stdout.write('\nDemo login credentials:')
        self.stdout.write('  Seeker:   saim@demo.com / demo1234')
        self.stdout.write('  Seeker:   rahul@demo.com / demo1234')
        self.stdout.write('  Employer: hr@techcorp.com / demo1234')
        self.stdout.write('  Employer: jobs@startupx.com / demo1234')
