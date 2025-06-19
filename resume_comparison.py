import os
import fitz  # PyMuPDF
import re
import spacy
from textblob import TextBlob
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from ttkthemes import ThemedTk

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

skills_list = ["python", "java", "data analysis", "machine learning", "c++", "sql", "web development"]
job_titles = ["software engineer", "data scientist", "frontend developer", "data analyst"]

def extract_text_from_pdf(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text("text")
        return text
    except Exception as e:
        messagebox.showerror("Error", f"Error reading PDF: {e}")
        return ""

def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def analyze_skills_experience(text):
    text = text.lower()
    found_skills = [skill for skill in skills_list if skill in text]
    found_titles = [job for job in job_titles if job in text]
    return found_skills, found_titles

def predict_personality_traits(text):
    blob = TextBlob(text)
    sentiment = blob.sentiment.polarity
    if sentiment > 0.3:
        return "Positive, Likely to be Agreeable"
    elif sentiment < -0.3:
        return "Negative, Likely to be Less Agreeable"
    else:
        return "Neutral"

def score_candidate(skills, titles, personality):
    score = 0
    score += len(skills) * 5
    score += len(titles) * 3
    if "Positive" in personality:
        score += 5
    elif "Negative" in personality:
        score -= 5
    return score

def resume_feedback(score):
    if score >= 30:
        return "Excellent Resume!"
    elif score >= 20:
        return "Good Resume, but could use more specific skills."
    elif score >= 10:
        return "Average Resume, add more relevant projects and skills."
    else:
        return "Needs improvement, add relevant skills and experience."

def process_pdfs():
    pdf_paths = filedialog.askopenfilenames(filetypes=[("PDF Files", "*.pdf")])
    if not pdf_paths:
        return
    
    all_results = []
    
    for pdf_path in pdf_paths:
        raw_text = extract_text_from_pdf(pdf_path)
        cleaned_text = clean_text(raw_text)
        
        skills, titles = analyze_skills_experience(cleaned_text)
        personality = predict_personality_traits(cleaned_text)
        candidate_score = score_candidate(skills, titles, personality)
        
        result = {
            'file': os.path.basename(pdf_path),
            'skills': skills,
            'titles': titles,
            'personality': personality,
            'score': candidate_score,
            'feedback': resume_feedback(candidate_score)
        }
        all_results.append(result)
    
    display_comparison_results(all_results)

def display_comparison_results(results):
    result_text.config(state=tk.NORMAL)
    result_text.delete(1.0, tk.END)
    
    highest_score = -1
    best_cv = None
    
    for result in results:
        result_text.insert(tk.END, f"📄 Resume: {result['file']}\n")
        result_text.insert(tk.END, f"✅ Skills found: {', '.join(result['skills']) if result['skills'] else 'None'}\n")
        result_text.insert(tk.END, f"💼 Job titles found: {', '.join(result['titles']) if result['titles'] else 'None'}\n")
        result_text.insert(tk.END, f"🧠 Predicted personality traits: {result['personality']}\n")
        result_text.insert(tk.END, f"⭐ Candidate score: {result['score']}\n")
        result_text.insert(tk.END, f"📝 Feedback: {result['feedback']}\n")
        result_text.insert(tk.END, "─" * 50 + "\n")
        
        if result['score'] > highest_score:
            highest_score = result['score']
            best_cv = result['file']
    
    if best_cv:
        result_text.insert(tk.END, f"\n🏆 Best Resume: {best_cv}\n")
        result_text.insert(tk.END, f"🔥 Highest Score: {highest_score}\n")
        result_text.insert(tk.END, "This CV stands out among the selected resumes.\n")
    result_text.config(state=tk.DISABLED)

# --- GUI Setup ---
root = ThemedTk(theme="breeze")
root.title("Resume Comparison & Skill Analyzer")
root.geometry("700x600")
root.resizable(False, False)

# Main frame with padding
main_frame = ttk.Frame(root, padding=20)
main_frame.pack(fill=tk.BOTH, expand=True)

# Title label
title_label = ttk.Label(main_frame, text="Resume Comparison & Skill Analyzer", font=("Segoe UI", 20, "bold"))
title_label.pack(pady=(0, 20))

# Button style
style = ttk.Style()
style.configure("Accent.TButton", font=("Segoe UI", 14, "bold"), foreground="white", background="#0078D7")
style.map("Accent.TButton",
          background=[("active", "#005A9E"), ("disabled", "#A6A6A6")])

# Select and Compare Button
select_button = ttk.Button(main_frame, text="Select and Compare Resumes", style="Accent.TButton", command=process_pdfs)
select_button.pack(pady=(0, 20), ipadx=10, ipady=8)

# Text frame with scrollbar
text_frame = ttk.Frame(main_frame)
text_frame.pack(fill=tk.BOTH, expand=True)

# Text widget for results
result_text = tk.Text(text_frame, wrap="word", font=("Consolas", 11), state=tk.DISABLED, bg="#f5f5f5", relief=tk.SUNKEN, bd=2)
result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Scrollbar
scrollbar = ttk.Scrollbar(text_frame, command=result_text.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
result_text.config(yscrollcommand=scrollbar.set)

root.mainloop()
