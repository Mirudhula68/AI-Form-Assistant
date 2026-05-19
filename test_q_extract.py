import sys
from app.services.form_parser import extract_questions

try:
    qs = extract_questions("uploaded_forms/Election form.pdf")
    import json
    print(json.dumps(qs, indent=2))
except Exception as e:
    print(e)
