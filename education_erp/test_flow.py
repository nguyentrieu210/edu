import frappe
from frappe.utils import add_days, nowdate

def test_flow():
    print("=== STARTING PURE FRAPPE WORKFLOW TEST ===")
    frappe.flags.in_test = True
    
    # 1. Create Guardian
    guardian_name = "Test Guardian Pure"
    if not frappe.db.exists("Guardian", guardian_name):
        guardian = frappe.get_doc({
            "doctype": "Guardian",
            "guardian_name": guardian_name,
            "phone": "0901234567"
        }).insert(ignore_permissions=True)
    else:
        guardian = frappe.get_doc("Guardian", guardian_name)
    print(f"Guardian: {guardian.name}")

    # 2. Create Student
    student = frappe.get_doc({
        "doctype": "Student",
        "full_name": "Test Student Pure 1",
        "guardian": guardian.name,
        "progress": "Buổi 1/30",
        "attendance_status": "Vắng có phép",
        "average_score": 8.5
    }).insert(ignore_permissions=True)
    print(f"Student: {student.name}")
    
    # 3. Create Program Enrollment
    enrollment = frappe.get_doc({
        "doctype": "Program Enrollment",
        "student": student.name,
        "program": "N5 Intensive Pure",
        "enrollment_date": nowdate()
    }).insert(ignore_permissions=True)
    enrollment.submit()
    print(f"Program Enrollment: {enrollment.name} (Submitted)")
    
    # 4. Create Fee Schedule
    fee = frappe.get_doc({
        "doctype": "Fee Schedule",
        "student": student.name,
        "program_enrollment": enrollment.name,
        "total_amount": 5000000.0,
        "due_date": add_days(nowdate(), 10),
        "status": "Invoice Pending"
    }).insert(ignore_permissions=True)
    print(f"Fee Schedule: {fee.name} created (Draft)")
    
    # Submit Fee Schedule -> This should auto-trigger Fee Invoice creation
    fee.submit()
    fee.reload()
    print(f"Fee Schedule submitted! Status changed to: {fee.status}")
    
    # 5. Verify Fee Invoice was created
    invoices = frappe.get_all("Fee Invoice", filters={"fee_schedule": fee.name})
    if not invoices:
        frappe.throw(f"Test failed: No Fee Invoice created for Fee Schedule {fee.name}")
        
    invoice_name = invoices[0].name
    invoice = frappe.get_doc("Fee Invoice", invoice_name)
    print(f"Fee Invoice auto-created and submitted: {invoice.name}")
    print(f"Invoice Total Amount: {invoice.total_amount}, Outstanding: {invoice.outstanding_amount}, Status: {invoice.status}")
    
    assert abs(invoice.total_amount - 5000000.0) < 0.01, "Total amount mismatch"
    assert abs(invoice.outstanding_amount - 5000000.0) < 0.01, "Outstanding amount mismatch"
    assert invoice.status == "Unpaid", "Status mismatch"
    assert invoice.docstatus == 1, "Invoice must be submitted"
    
    # 6. Create Fee Payment (Partial payment of 3,000,000)
    payment1 = frappe.get_doc({
        "doctype": "Fee Payment",
        "student": student.name,
        "posting_date": nowdate(),
        "payment_date": nowdate(),
        "payment_method": "Bank Transfer",
        "amount": 3000000.0,
        "reference_no": "TXN123456",
        "reference_date": nowdate(),
        "references": [
            {
                "invoice": invoice.name,
                "allocated_amount": 3000000.0
            }
        ]
    }).insert(ignore_permissions=True)
    
    payment1.submit()
    print(f"Fee Payment 1 submitted: {payment1.name} (Amount: 3,000,000)")
    
    # Verify invoice outstanding is updated
    invoice.reload()
    print(f"Invoice Outstanding after Payment 1: {invoice.outstanding_amount}, Status: {invoice.status}")
    assert abs(invoice.outstanding_amount - 2000000.0) < 0.01, "Outstanding amount should be 2,000,000"
    assert invoice.status == "Partially Paid", "Invoice status should be Partially Paid"
    
    # 7. Create Fee Payment 2 (Final payment of 2,000,000)
    payment2 = frappe.get_doc({
        "doctype": "Fee Payment",
        "student": student.name,
        "posting_date": nowdate(),
        "payment_date": nowdate(),
        "payment_method": "Cash",
        "amount": 2000000.0,
        "references": [
            {
                "invoice": invoice.name,
                "allocated_amount": 2000000.0
            }
        ]
    }).insert(ignore_permissions=True)
    
    payment2.submit()
    print(f"Fee Payment 2 submitted: {payment2.name} (Amount: 2,000,000)")
    
    # Verify invoice outstanding is 0 and status is Paid
    invoice.reload()
    print(f"Invoice Outstanding after Payment 2: {invoice.outstanding_amount}, Status: {invoice.status}")
    assert abs(invoice.outstanding_amount - 0.0) < 0.01, "Outstanding amount should be 0"
    assert invoice.status == "Paid", "Invoice status should be Paid"
    
    # 8. Cancel Payment 2
    payment2.cancel()
    print(f"Fee Payment 2 cancelled: {payment2.name}")
    
    # Verify invoice outstanding reverted to 2,000,000 and status Partially Paid
    invoice.reload()
    print(f"Invoice Outstanding after Payment 2 cancel: {invoice.outstanding_amount}, Status: {invoice.status}")
    assert abs(invoice.outstanding_amount - 2000000.0) < 0.01, "Outstanding amount should revert to 2,000,000"
    assert invoice.status == "Partially Paid", "Invoice status should revert to Partially Paid"
    
    # Rollback everything to keep the test environment clean
    frappe.db.rollback()
    print("=== PURE FRAPPE WORKFLOW TEST COMPLETED SUCCESSFULLY (ROLLBACKED) ===")
