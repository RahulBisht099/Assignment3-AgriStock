import frappe
from frappe.model.document import Document

class PurchaseRequest(Document):

    def on_submit(self):
        if self.status == "Approved":
            current_stock = frappe.db.get_value("Inventory Item", self.item, "current_stock") or 0
            new_stock = current_stock + self.quantity

            frappe.db.set_value("Inventory Item", self.item, "current_stock", new_stock)

            frappe.msgprint(f"✅ Purchase Request Approved. {self.quantity} units added to '{self.item}'. New Stock: {new_stock}")

        elif self.status == "Rejected":
            frappe.msgprint("❌ Purchase Request Rejected. No stock changes made.")
