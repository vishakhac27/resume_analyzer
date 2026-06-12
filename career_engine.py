import json
from openai import OpenAI
from dotenv import load_dotenv
import os



load_dotenv()

client = OpenAI(
   
    api_key=os.getenv("GROQ_API_KEY"),
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
            "roadmap": ["Learn basics", "Build projects", "Practice DSA"]
        }

    return {
        "career": "Explorer",
        "score": 70,
        "technologies": [],
        "roadmap": ["Explore tech fields"]
    }



def recommend_career_llm(name, education, skills, interests, goal):

    prompt = f"""
You are an expert career counselor AI.

Return ONLY valid JSON.

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
            {"role": "system", "content": "Return ONLY JSON."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    content = response.choices[0].message.content

    if not content:
        raise ValueError("Empty LLM response")

    content = content.strip().replace("```json", "").replace("```", "")
    return content



def get_career_data(name, education, skills, interests, goal):

    try:
        print(" Calling LLM...")

        raw = recommend_career_llm(name, education, skills, interests, goal)

        print(" RAW LLM OUTPUT:")
        print(raw)

        data = json.loads(raw)
        return data

    except Exception as e:
        print(" LLM failed, using fallback:", e)
        return recommend_career(skills, interests)