import frappe
from frappe.model.document import Document

class FeeInvoice(Document):
    # Type Annotations for v15+
    student: str
    program_enrollment: str | None
    fee_schedule: str | None
    posting_date: str
    due_date: str
    total_amount: float
    outstanding_amount: float
    status: str

    def validate(self) -> None:
        item_total = sum([item.amount for item in self.get("items", [])])
        discount = getattr(self, "discount_amount", 0) or 0
        tax = getattr(self, "tax_amount", 0) or 0
        
        if self.get("items"):
            self.total_amount = max(0, item_total - discount + tax)
            
        if self.is_new():
            self.outstanding_amount = self.total_amount
            self.status = "Unpaid"

    def on_cancel(self) -> None:
        # Check if there are any submitted payments referencing this invoice
        payments = frappe.db.sql("""
            SELECT parent 
            FROM `tabFee Payment Reference` r
            JOIN `tabFee Payment` p ON r.parent = p.name
            WHERE r.invoice = %s AND p.docstatus = 1
        """, (self.name,))
        
        if payments:
            frappe.throw(f"Cannot cancel invoice {self.name} because it is referenced in submitted Fee Payment {payments[0][0]}")

        self.db_set("status", "Cancelled", update_modified=False)
        self.db_set("outstanding_amount", 0, update_modified=True)
        
        if self.fee_schedule:
            frappe.db.set_value("Fee Schedule", self.fee_schedule, "status", "Invoice Pending")
