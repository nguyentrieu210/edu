import frappe
from frappe.modules.utils import make_boilerplate

def generate():
    for dt in ["Guardian", "Education Settings", "Student Sibling", "Program Enrollment"]:
        make_boilerplate("DocType", dt)
        print(f"Boilerplate created for {dt}")
