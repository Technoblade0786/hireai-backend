# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


def calculate_match_score(seeker_skills: list, job_skills: list, 
                            seeker_exp: int, job_exp_required: int) -> float:
    """
    Calculate AI match score between a job seeker and a job.
    Uses TF-IDF cosine similarity on skills + experience bonus.
    Returns score between 0 and 100.
    """
    if not seeker_skills or not job_skills:
        return 0.0

    # Skill matching using cosine similarity
    seeker_text = ' '.join(seeker_skills)
    job_text = ' '.join(job_skills)

    common = set(seeker_skills) & set(job_skills)
    skill_score = len(common) / max(len(job_skills), 1)

    # Experience bonus (0 to 0.2)
    exp_bonus = 0.0
    if seeker_exp >= job_exp_required:
        exp_bonus = 0.2
    elif job_exp_required > 0:
        exp_bonus = min(seeker_exp / job_exp_required, 1.0) * 0.2

    # Keyword overlap bonus
    seeker_set = set(seeker_skills)
    job_set = set(job_skills)
    overlap = len(seeker_set & job_set) / max(len(job_set), 1)
    keyword_bonus = overlap * 0.1

    final_score = (skill_score * 0.7 + exp_bonus + keyword_bonus)
    return round(min(final_score * 100, 100), 1)


def get_recommended_jobs(seeker_profile, jobs_queryset, top_n=10):
    """
    Returns top N jobs sorted by match score for a seeker.
    """
    seeker_skills = seeker_profile.skills_list()
    seeker_exp = seeker_profile.experience_years

    scored_jobs = []
    for job in jobs_queryset:
        job_skills = job.required_skills_list()
        score = calculate_match_score(seeker_skills, job_skills, seeker_exp, job.experience_required)
        scored_jobs.append((job, score))

    scored_jobs.sort(key=lambda x: x[1], reverse=True)
    return scored_jobs[:top_n]
