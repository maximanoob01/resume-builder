from dotenv import load_dotenv
load_dotenv()  # ✅ Loads variables from .env

from flask import Flask, render_template, request, send_file, redirect, flash, url_for
import pdfkit
import os
import threading
import re
import logging
import shutil

# ✅ Locate wkhtmltopdf binary
path_wkhtmltopdf = shutil.which("wkhtmltopdf")
if not path_wkhtmltopdf:
    raise FileNotFoundError("❌ wkhtmltopdf not found. Install it and add to PATH.")

config = pdfkit.configuration(
    wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
)

# Flask app
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "supersecretkey")

# Logging
os.makedirs("output", exist_ok=True)
logging.basicConfig(
    filename="resume_log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# -------------------- UTILITIES --------------------
def sanitize_input(text: str) -> str:
    """Remove HTML tags and strip spaces from user input."""
    if not text:
        return ""
    return re.sub(r"<[^>]*?>", "", text).strip()


def delete_file_later(filepath: str, delay: int = 60):
    """Delete file automatically after `delay` seconds."""
    def delete():
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                logging.info(f"🗑️ Deleted expired file: {filepath}")
            except Exception as e:
                logging.error(f"❌ Failed to delete {filepath}: {e}")
    threading.Timer(delay, delete).start()


# -------------------- ROUTES --------------------
@app.route("/")
def home():
    return render_template("form.html")


@app.route("/generate", methods=["POST"])
def generate_resume():
    """🔹 Generate PDF resume from form input."""
    try:
        # Collect education entries
        education = [
            {
                "degree": sanitize_input(deg),
                "institution": sanitize_input(inst),
                "year_of_passing": sanitize_input(yr)
            }
            for deg, inst, yr in zip(
                request.form.getlist("degree[]"),
                request.form.getlist("institution[]"),
                request.form.getlist("year_of_passing[]")
            )
        ]

        # Collect experience entries
        experience = [
            {
                "job_title": sanitize_input(title),
                "company": sanitize_input(comp),
                "exp_start": sanitize_input(start),
                "exp_end": sanitize_input(end),
                "experience_desc": sanitize_input(desc)
            }
            for title, comp, start, end, desc in zip(
                request.form.getlist("job_title[]"),
                request.form.getlist("company[]"),
                request.form.getlist("exp_start[]"),
                request.form.getlist("exp_end[]"),
                request.form.getlist("experience_desc[]")
            )
        ]

        # Required fields
        name = sanitize_input(request.form.get("name", ""))
        email = sanitize_input(request.form.get("email", ""))
        phone = sanitize_input(request.form.get("phone", ""))

        if not name or not email or not phone:
            flash("⚠️ Name, Email, and Phone are required!")
            return redirect(url_for("home"))

        # Render HTML template
        html = render_template(
            "resume_template.html",
            name=name,
            email=email,
            phone=phone,
            location=sanitize_input(request.form.get("location", "")),
            linkedin=sanitize_input(request.form.get("linkedin", "")),
            skills=sanitize_input(request.form.get("skills", "")),
            projects=sanitize_input(request.form.get("projects", "")),
            certifications=sanitize_input(request.form.get("certifications", "")),
            other_details=sanitize_input(request.form.get("other_details", "")),
            education=education,
            experience=experience
        )

        # Save PDF
        filename = f"{name.replace(' ', '_')}_resume.pdf"
        pdf_path = os.path.join("output", filename)

        pdfkit.from_string(html, pdf_path, configuration=config)

        # Schedule delete
        delete_file_later(pdf_path, delay=120)

        logging.info(f"✅ Resume created for {name} ({email})")

        return send_file(pdf_path, as_attachment=True)

    except Exception as e:
        logging.error(f"❌ Resume generation failed: {e}")
        flash("Error generating resume. Please try again.")
        return redirect(url_for("home"))


# -------------------- START SERVER --------------------
if __name__ == "__main__":
    print("\n🚀 Server is running! Open this link in browser:")
    print("👉 http://127.0.0.1:5000\n")
    app.run(host="0.0.0.0", port=5000, debug=True)
