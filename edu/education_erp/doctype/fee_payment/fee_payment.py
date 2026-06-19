import frappe
from frappe.model.document import Document

class FeePayment(Document):
    # Type Annotations for v15+
    student: str
    posting_date: str
    payment_date: str
    payment_method: str
    amount: float
    reference_no: str | None
    reference_date: str | None
    references: list

    def validate(self) -> None:
        if self.amount <= 0:
            frappe.throw("Payment amount must be greater than 0.")

        if not self.references:
            frappe.throw("At least one invoice must be referenced for payment allocation.")

        total_allocated = 0.0
        allocated_by_invoice = {}
        for ref in self.references:
            # Check student matching
            invoice_student = frappe.db.get_value("Fee Invoice", ref.invoice, "student")
            if invoice_student != self.student:
                frappe.throw(f"Invoice {ref.invoice} does not belong to student {self.student}.")

            # Check allocation amount
            if ref.allocated_amount <= 0:
                frappe.throw(f"Allocated amount for invoice {ref.invoice} must be greater than 0.")

            # Check against outstanding
            outstanding = frappe.db.get_value("Fee Invoice", ref.invoice, "outstanding_amount")
            if ref.allocated_amount > outstanding + 0.01: # allow slight floating point tolerance
                frappe.throw(f"Allocated amount {ref.allocated_amount} for invoice {ref.invoice} cannot exceed its outstanding amount of {outstanding}.")

            total_allocated += ref.allocated_amount
            allocated_by_invoice[ref.invoice] = allocated_by_invoice.get(ref.invoice, 0.0) + ref.allocated_amount

        for invoice, allocated in allocated_by_invoice.items():
            outstanding = frappe.db.get_value("Fee Invoice", invoice, "outstanding_amount")
            if allocated > outstanding + 0.01:
                frappe.throw(
                    f"Total allocated amount {allocated} for invoice {invoice} cannot exceed outstanding amount {outstanding}."
                )

        if abs(total_allocated - self.amount) > 0.01:
            frappe.throw(f"Total allocated amount ({total_allocated}) does not match the payment amount ({self.amount}).")

    def on_submit(self) -> None:
        for ref in self.references:
            frappe.db.sql("select name from `tabFee Invoice` where name=%s for update", ref.invoice)
            invoice = frappe.get_doc("Fee Invoice", ref.invoice)
            if invoice.docstatus != 1 or invoice.status == "Cancelled":
                frappe.throw(f"Invoice {invoice.name} is not payable.")
            if ref.allocated_amount > invoice.outstanding_amount + 0.01:
                frappe.throw(
                    f"Allocated amount {ref.allocated_amount} for invoice {invoice.name} exceeds current outstanding amount {invoice.outstanding_amount}."
                )
            new_outstanding = max(0.0, invoice.outstanding_amount - ref.allocated_amount)
            new_status = "Paid" if new_outstanding <= 0.01 else "Partially Paid"
            
            invoice.db_set("outstanding_amount", new_outstanding, update_modified=False)
            invoice.db_set("status", new_status, update_modified=True)

    def on_cancel(self) -> None:
        for ref in self.references:
            frappe.db.sql("select name from `tabFee Invoice` where name=%s for update", ref.invoice)
            invoice = frappe.get_doc("Fee Invoice", ref.invoice)
            new_outstanding = invoice.outstanding_amount + ref.allocated_amount
            new_status = "Unpaid" if abs(new_outstanding - invoice.total_amount) < 0.01 else "Partially Paid"
            
            invoice.db_set("outstanding_amount", new_outstanding, update_modified=False)
            invoice.db_set("status", new_status, update_modified=True)
