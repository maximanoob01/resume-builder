from dotenv import load_dotenv
load_dotenv()  # ✅ Loads variables from .env

from flask import Flask, render_template, request, send_file, redirect, flash, url_for, jsonify
import pdfkit
import os
import threading
import re
import logging
from openai import OpenAI  # ✅ Updated import
import shutil
import pdfkit

# Find wkhtmltopdf on Linux/Render
path_wkhtmltopdf = shutil.which("wkhtmltopdf")

config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

# ✅ Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ✅ Path to wkhtmltopdf executable
config = pdfkit.configuration(
    wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
)

app = Flask(__name__)
app.secret_key = "supersecretkey"

os.makedirs("output", exist_ok=True)

logging.basicConfig(filename="resume_log.txt", level=logging.INFO,
                    format="%(asctime)s - %(message)s")


def sanitize_input(text):
    return re.sub(r"<[^>]*?>", "", text)


def delete_file_later(filepath, delay=60):
    def delete():
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"🗑️ Deleted: {filepath}")
    threading.Timer(delay, delete).start()


@app.route("/")
def home():
    return render_template("form.html")


@app.route("/generate_summary", methods=["POST"])
def generate_summary():
    """🔹 Generates an exaggerated AI professional summary."""
    data = request.json
    name = data.get("name", "Professional")
    skills = data.get("skills", "")

    prompt = f"""
    Create an exaggerated, highly impressive professional summary for {name}.
    Highlight leadership, innovation, and extraordinary skills in:
    {skills}.
    Make it sound like a confident, visionary leader ready to achieve big things.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # ✅ Updated new API usage
            messages=[
                {"role": "system", "content": "You are an expert resume writer."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.8
        )

        summary_text = response.choices[0].message.content.strip()

    except Exception as e:
        print(f"❌ OpenAI Error: {e}")
        return jsonify({"summary": "⚠️ Error generating AI summary. Try again later."})

    return jsonify({"summary": summary_text})


@app.route("/generate", methods=["POST"])
def generate_resume():
    education = []
    for i in range(len(request.form.getlist("degree[]"))):
        education.append({
            "degree": sanitize_input(request.form.getlist("degree[]")[i]),
            "institution": sanitize_input(request.form.getlist("institution[]")[i]),
            "year_of_passing": sanitize_input(request.form.getlist("year_of_passing[]")[i])
        })

    experience = []
    for i in range(len(request.form.getlist("job_title[]"))):
        experience.append({
            "job_title": sanitize_input(request.form.getlist("job_title[]")[i]),
            "company": sanitize_input(request.form.getlist("company[]")[i]),
            "exp_start": sanitize_input(request.form.getlist("exp_start[]")[i]),
            "exp_end": sanitize_input(request.form.getlist("exp_end[]")[i]),
            "experience_desc": sanitize_input(request.form.getlist("experience_desc[]")[i])
        })

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    phone = request.form.get("phone", "").strip()

    if not name or not email or not phone:
        flash("Name, Email, and Phone are required!")
        return redirect(url_for("home"))

    html = render_template(
        "resume_template.html",
        name=name,
        email=email,
        phone=phone,
        location=request.form.get("location", ""),
        linkedin=request.form.get("linkedin", ""),
        skills=request.form.get("skills", ""),
        projects=request.form.get("projects", ""),
        certifications=request.form.get("certifications", ""),
        other_details=request.form.get("other_details", ""),
        education=education,
        experience=experience
    )

    filename = f"{name.replace(' ', '_')}_resume.pdf"
    pdf_path = os.path.join("output", filename)

    try:
        pdfkit.from_string(html, pdf_path, configuration=config)
    except Exception as e:
        print(f"❌ PDF generation error: {e}")
        flash("Error generating PDF. Check wkhtmltopdf path.")
        return redirect(url_for("home"))

    delete_file_later(pdf_path, delay=60)
    logging.info(f"✅ Resume created for {name} ({email})")

    return send_file(pdf_path, as_attachment=True)


if __name__ == "__main__":
    print("\n🚀 Server is running! Open this link in browser:")
    print("👉 http://127.0.0.1:5000\n")
    app.run(host="0.0.0.0", port=5000, debug=True)
