import os
import re
import json
import statistics
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def llm_classify(text):
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an AI-generated text detector. "
                    "Given a passage of text, estimate the probability it was written by an AI (not a human). "
                    "Respond with only a JSON object: {\"ai_probability\": <float between 0.0 and 1.0>}. "
                    "1.0 = certainly AI-generated, 0.0 = certainly human-written."
                ),
            },
            {"role": "user", "content": text},
        ],
        response_format={"type": "json_object"},
        temperature=0,
    )
    result = json.loads(response.choices[0].message.content)
    return round(float(result.get("ai_probability", 0.5)), 4)

def stylometric_score(text):
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    words = re.findall(r'\b\w+\b', text.lower())
    if len(sentences) < 2 or not words:
        return 0.5
    sent_lengths = [len(re.findall(r'\b\w+\b', s)) for s in sentences]
    slv_score = 1 / (1 + statistics.variance(sent_lengths))
    ttr_score = 1 - (len(set(words)) / len(words))
    punct_counts = [len(re.findall(r'[^\w\s]', s)) for s in sentences]
    mean_punct = statistics.mean(punct_counts)
    punct_score = 1 / (1 + statistics.stdev(punct_counts) / mean_punct) if mean_punct > 0 else 0.5
    return round((slv_score + ttr_score + punct_score) / 3, 4)

text = """
Artificial intelligence represents a transformative paradigm shift in modern society. 
It is important to note that while the benefits of AI are numerous, it is equally 
essential to consider the ethical implications. Furthermore, stakeholders across 
various sectors must collaborate to ensure responsible deployment.
"""

style = stylometric_score(text.strip())
llm = llm_classify(text.strip())
confidence = round(0.6 * llm + 0.4 * style, 4)

print(f"style_score:  {style}")
print(f"llm_score:    {llm}")
print(f"confidence:   {confidence}")
