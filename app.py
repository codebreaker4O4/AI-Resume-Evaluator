from flask import Flask, request, render_template
from openai import OpenAI
from PyPDF2 import PdfReader
import os


app = Flask(__name__)
base_url = "https://api.aimlapi.com/v1"
api_key = "4c0de60ff78b462aa1b15812f6d4a263"
system_prompt = "You are a resume evaluator."
user_prompt = "Analyze this resume under the following categories: 1. Skills: Identify key strengths. 2. Experience: Assess relevance and clarity. 3. Formatting: Suggest improvements. 4. Language: Correct grammar and tone."
api = OpenAI(api_key=api_key, base_url=base_url)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/", methods=["GET", "POST"])
def index():
    feedback = ""
    if request.method == "POST":
        file = request.files["resume"]
        if file:
            file_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(file_path)
            resume_text =""
            if file.filename.endswith(".pdf"):
                reader = PdfReader(file)
                resume_text = "".join(page.extract_text() for page in reader.pages)
            elif file.filename.endswith(".docx"):
                from docx import Document
                doc = Document(file)
                resume_text = "\n".join(paragraph.text for paragraph in doc.paragraphs)
            else:
                resume_text = request.form["resume"]
            response = api.chat.completions.create(
                model="mistralai/Mistral-7B-Instruct-v0.2",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.7,
                max_tokens=256,
            )
            feedback = response.choices[0].message.content
            os.remove(file_path)
        else:
            feedback = "Unsupported file format. Please upload your file in PDF or DOCX format."

    return render_template("index.html", feedback=feedback, feedback_type="info")

if __name__ == "__main__":
    app.run(debug=True)


