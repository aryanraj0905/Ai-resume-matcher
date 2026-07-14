#  AI Resume Matcher

An AI-powered Resume Matcher built with **FastAPI** that analyzes resumes against job descriptions using **Natural Language Processing (NLP)** and **semantic similarity**. The application provides a match score, identifies missing skills, and generates AI-powered recommendations to improve the resume.

---

##  Features

-  Upload Resume (PDF)
-  Analyze Job Descriptions
-  AI-Powered Resume Matching
-  Match Percentage Calculation
-  Skill Extraction
-  Missing Skills Detection
-  AI-Powered Resume Recommendations
-  FastAPI REST API
-  Semantic Similarity using AI Embeddings

---

##  Tech Stack

### Backend
- Python
- FastAPI
- Uvicorn

### AI / Machine Learning
- Sentence Transformers
- Scikit-learn

### Resume Processing
- PyMuPDF
- Regular Expressions (Regex)

### Database
- SQLite

### Version Control
- Git
- GitHub

---

##  Project Structure

```
ai_resume_matcher/
│
├── backend/
│   ├── app/
│   │   ├── ai/
│   │   ├── routes/
│   │   ├── services/
│   │   ├── models/
│   │   ├── utils/
│   │   └── main.py
│   │
│   ├── uploads/
│   ├── tests/
│   └── requirements.txt
│
└── README.md
```

---

##  Installation

Clone the repository

```bash
git clone https://github.com/aryanraj0905/Ai-resume-matcher.git
```

Move into the project

```bash
cd Ai-resume-matcher/backend
```

Create a virtual environment

```bash
python -m venv venv
```

Activate the environment

### Windows

```bash
venv\Scripts\activate
```

### macOS/Linux

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run the FastAPI server

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```
http://127.0.0.1:8000
```

Interactive API Documentation:

```
http://127.0.0.1:8000/docs
```

---

##  How It Works

1. Upload a resume in PDF format.
2. Extract text from the resume.
3. Parse the job description.
4. Extract technical skills.
5. Generate semantic embeddings.
6. Compare the resume with the job description.
7. Calculate a match percentage.
8. Identify missing skills.
9. Generate AI-powered recommendations for improvement.

---

##  Future Improvements

- React Frontend
- User Authentication
- Resume History
- Dashboard
- Multiple Resume Comparison
- Recruiter Portal
- Support for DOCX resumes
- Export analysis as PDF

---


##  Project Goal

The goal of this project is to help job seekers understand how well their resumes match a job description by combining traditional skill matching with AI-powered semantic analysis and personalized recommendations.

---

##  Author

**Aryan Raj**

GitHub: https://github.com/aryanraj0905
