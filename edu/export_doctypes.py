import frappe
from frappe.modules.export_file import export_to_files

def export_all():
    doctypes = [
        "Guardian", 
        "Education Settings", 
        "Student Sibling", 
        "Student", 
        "Student Lead",
        "Consultation Log",
        "Placement Test",
        "Teacher",
        "Course",
        "Classroom",
        "Class",
        "Class Session",
        "Program Enrollment", 
        "Fee Schedule",
        "Fee Invoice Item",
        "Fee Invoice",
        "Fee Payment Reference",
        "Fee Payment",
        "Student Attendance",
        "Student Assessment",
        "Student Deferment",
        "Class Transfer",
        "Fee Refund",
        "Teacher Salary Slip",
        "Student Appointment",
        "Student Card",
        "Onboarding Task",
        "Room Booking",
        "Internal Task"
    ]
    for dt in doctypes:
        frappe.db.set_value("DocType", dt, "custom", 0)
        frappe.db.commit()
        export_to_files(record_list=[["DocType", dt]], record_module="Education ERP")
        print(f"Exported {dt}")
