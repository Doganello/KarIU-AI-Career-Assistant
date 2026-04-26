from docx import Document
from docx.shared import Pt
import os

TEMPLATES = {
    "ru": "templates/cv_ru.docx",
    "kz": "templates/cv_kz.docx",
    "en": "templates/cv_en.docx",
}

class CVGenerator:
    def generate(self, graduate, lang="ru", vacancy="") -> str:
        doc = Document(TEMPLATES.get(lang, TEMPLATES["ru"]))

        self._fill_header(doc, graduate)
        self._fill_education(doc, graduate)
        self._fill_experience(doc, graduate)
        self._fill_skills(doc, graduate)
        self._fill_certificates(doc, graduate)

        filename = f"cv_{graduate.user_id}_{lang}.docx"
        path     = os.path.join("storage", "cvs", filename)
        doc.save(path)
        return filename

    def _fill_header(self, doc, graduate):
        for para in doc.paragraphs:
            if "{{FULL_NAME}}" in para.text:
                para.text = para.text.replace(
                    "{{FULL_NAME}}",
                    f"{graduate.last_name} {graduate.first_name}"
                )
            # ... остальные плейсхолдеры

    def _fill_education(self, doc, graduate): ...
    def _fill_experience(self, doc, graduate): ...
    def _fill_skills(self, doc, graduate): ...
    def _fill_certificates(self, doc, graduate): ...