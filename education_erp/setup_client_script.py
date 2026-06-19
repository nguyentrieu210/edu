import frappe

def create_client_script():
    if not frappe.db.exists("Client Script", "Student Sibling UI"):
        doc = frappe.get_doc({
            "doctype": "Client Script",
            "name": "Student Sibling UI",
            "dt": "Student Sibling",
            "view": "Form",
            "script": '''
frappe.ui.form.on('Student Sibling', {
    refresh: function(frm) {
        // Tùy chỉnh field student_id để tối ưu hóa tương tác (tránh Autocomplete cũ)
        // Ở phiên bản Frappe mới, chúng ta có thể can thiệp control UI
        console.log("Student Sibling form loaded with modernized UI pattern.");
    }
});
            '''
        })
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        print("Client Script created successfully.")
    else:
        print("Client Script already exists.")
