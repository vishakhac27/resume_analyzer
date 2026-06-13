import json
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")


if not api_key:
    print(" WARNING: GROQ_API_KEY is missing (Render env not set or .env missing)")

client = OpenAI(
    api_key=api_key,
    base_url="https://api.groq.com/openai/v1"
)



def recommend_career(skills, interests):
    skills = skills.lower()
    interests = interests.lower()

    if "python" in skills:
        return {
            "career": "Software Developer",
            "score": 80,
            "technologies": ["Python", "Git", "SQL"],
            "roadmap": ["Learn basics", "Build projects", "Practice DSA"],
            "reason": "Strong Python skills detected"
        }

    return {
        "career": "Explorer",
        "score": 70,
        "technologies": [],
        "roadmap": ["Explore tech fields"],
        "reason": "General profile"
    }



def recommend_career_llm(name, education, skills, interests, goal):

    prompt = f"""
You are an expert career counselor AI.

Return ONLY valid JSON in this format:
{{
  "career": "",
  "score": 0,
  "technologies": [],
  "roadmap": [],
  "reason": ""
}}

Student:
Name: {name}
Education: {education}
Skills: {skills}
Interests: {interests}
Goal: {goal}
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You must return ONLY valid JSON. No explanation."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    content = response.choices[0].message.content

    if not content:
        raise ValueError("Empty LLM response")

    # Clean response
    content = content.strip().replace("```json", "").replace("```", "")

    try:
        return json.loads(content)
    except Exception as e:
        print(" JSON parse failed:", e)
        print("RAW:", content)
        return None



def get_career_data(name, education, skills, interests, goal):

    print("Calling LLM...")

    result = recommend_career_llm(name, education, skills, interests, goal)

    if result:
        return result

    print("Using fallback logic")
    return recommend_career(skills, interests)