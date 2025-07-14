import frappe
from frappe.model.document import Document

class StockTransaction(Document):

    def on_submit(self):
        current_stock = frappe.db.get_value("Inventory Item", self.item, "current_stock") or 0

        if self.type == "In":
            new_stock = current_stock + self.quantity
        elif self.type == "Out":
            new_stock = current_stock - self.quantity

            if new_stock < 0:
                frappe.throw("❌ Not enough stock to perform this transaction.")

        frappe.db.set_value("Inventory Item", self.item, "current_stock", new_stock)

        # Auto Reorder Alert Logic
        reorder_level = frappe.db.get_value("Inventory Item", self.item, "reorder_level") or 0
        if new_stock <= reorder_level:
            # Check if a request already exists
            existing_request = frappe.db.exists(
                "Purchase Request",
                {
                    "item": self.item,
                    "farm": self.farm,
                    "status": "Pending"
                }
            )

            if not existing_request:
                pr = frappe.new_doc("Purchase Request")
                pr.item = self.item
                pr.quantity = 50
                pr.required_by = frappe.utils.nowdate()
                pr.farm = self.farm
                pr.status = "Pending"
                pr.insert()
                frappe.msgprint(f"📦 Auto Purchase Request created for {self.item}.")

    def on_cancel(self):
        current_stock = frappe.db.get_value("Inventory Item", self.item, "current_stock") or 0

        if self.type == "In":
            new_stock = current_stock - self.quantity
        elif self.type == "Out":
            new_stock = current_stock + self.quantity

        frappe.db.set_value("Inventory Item", self.item, "current_stock", new_stock)
