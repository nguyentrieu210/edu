import os

doctypes = ["guardian", "education_settings", "student_sibling", "program_enrollment"]

for dt in doctypes:
    class_name = dt.replace("_", " ").title().replace(" ", "")
    code = f"""import frappe
from frappe.model.document import Document

class {class_name}(Document):
\tpass
"""
    path = f"/home/frappe/frappe-bench/apps/edu/edu/education_erp/doctype/{dt}/{dt}.py"
    with open(path, "w") as f:
        f.write(code)
    print(f"Created {path}")
