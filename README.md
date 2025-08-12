An easy-to-use Flask-based web app that helps you create ATS-friendly resumes and download them as PDFs.
It also uses OpenAI GPT to generate a professional summary for your resume — making you look like the next Elon Musk (well, almost 🚀).

✨ Features
📄 ATS-Friendly Format – Ensures resumes pass Applicant Tracking Systems.

🤖 AI-Powered Summary – Generates impressive professional summaries using OpenAI API.

📥 One-Click PDF Download – Instantly download resumes in PDF format.

🧹 Clean Input Handling – Removes HTML tags & sanitizes inputs.

🗑 Auto File Cleanup – Deletes generated files after 60 seconds.

🛠 Customizable Templates – Edit resume_template.html for your own style.

🚀 Tech Stack
Backend: Flask (Python)

Frontend: HTML, CSS, JavaScript (Jinja2 templating)

PDF Generation: pdfkit + wkhtmltopdf

AI Integration: OpenAI GPT models

Environment Management: python-dotenv

git clone https://github.com/yourusername/ats-resume-builder.git
cd ats-resume-builder
💡 How It Works
Fill the Form – Enter personal details, education, experience, skills, and more.

AI Summary – The app generates a strong professional summary using GPT.

Generate PDF – Your resume is converted into an ATS-friendly PDF.

Download – Get your resume instantly (auto-deleted after 60 seconds).

⚠️ Notes
Make sure wkhtmltopdf path is correctly set in app.py.

The app deletes generated PDFs after 60 seconds for security.

Works locally; for deployment, configure Render/Heroku/Docker and adjust paths.

📜 License
This project is open-source under the MIT License.
