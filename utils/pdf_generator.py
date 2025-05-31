from flask import render_template
from weasyprint import HTML

def generate_pdf_from_template(template_name, context):
    html = render_template(template_name, **context)
    pdf = HTML(string=html, base_url='.').write_pdf()
    return pdf