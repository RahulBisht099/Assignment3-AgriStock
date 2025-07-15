import frappe
from frappe.model.document import Document

class PurchaseRequest(Document):

    def on_update(self):
        if self.status == "Approved":
            # ✅ Update stock
            current_stock = frappe.db.get_value("Inventory Item", self.item_name, "current_stock") or 0
            new_stock = current_stock + self.quantity
            frappe.db.set_value("Inventory Item", self.item_name, "current_stock", new_stock)

            # ✅ Try to find a supplier who supplies this item
            supplier = frappe.db.get_value('Supplied Items', {'item_name': self.item_name}, 'parent')

            if supplier:
                rate = frappe.db.get_value('Supplied Items', {
                    'parent': supplier,
                    'item_name': self.item_name
                }, 'price') or 0

                invoice = frappe.new_doc("Invoice")
                invoice.invoice_date = frappe.utils.nowdate()
                invoice.supplier = supplier
                customer = frappe.db.get_value("Farms", self.farm, "farm_manager") or "Unknown"
                invoice.customer = customer
                invoice.item_name = self.item_name
                invoice.quantity = self.quantity
                invoice.rate = rate
                invoice.total = self.quantity * rate
                invoice.status = 'Pending'
                invoice.insert()

                frappe.msgprint(f"🧾 Invoice auto-created for {self.quantity} x {self.item_name} @ ₹{rate} → ₹{self.quantity * rate}")
            else:
                frappe.msgprint("❗No supplier found for this item. Invoice not created.")

            # ✅ User Feedback
            frappe.msgprint(f"✅ Purchase Request Approved. {self.quantity} units added to '{self.item_name}'.")

        elif self.status == "Rejected":
            frappe.msgprint("❌ Purchase Request Rejected. No stock or invoice changes made.")
