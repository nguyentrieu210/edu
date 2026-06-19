import frappe

def execute():
    leads = frappe.get_all("Student Lead", filters={"status": "Consulting"}, fields=["name"])
    for lead in leads:
        exists = frappe.db.exists("Student Appointment", {"lead": lead.name})
        if not exists:
            doc = frappe.get_doc({
                "doctype": "Student Appointment",
                "lead": lead.name,
                "appointment_date": frappe.utils.today(),
                "appointment_time": "09:00",
                "purpose": "Tư vấn / Gọi lại",
                "status": "Scheduled"
            })
            doc.insert(ignore_permissions=True)
            print(f"Created appointment for {lead.name}")
    frappe.db.commit()
    print("Done")
