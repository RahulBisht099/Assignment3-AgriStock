import frappe
from frappe.model.document import Document

class StockTransaction(Document):

    def on_submit(self):
        current_stock = frappe.db.get_value("Inventory Item", self.item_name, "current_stock") or 0

        if self.type == "In(New Stock Incoming)":
            new_stock = current_stock + self.quantity
        elif self.type == "Out(Used or Lost)":
            new_stock = current_stock - self.quantity

            if new_stock < 0:
                frappe.throw("❌ Not enough stock to perform this transaction.")

        frappe.db.set_value("Inventory Item", self.item_name, "current_stock", new_stock)

        # 🟡 Auto Reorder Logic
        reorder_level = frappe.db.get_value("Inventory Item", self.item_name, "reorder_level") or 0
        if new_stock <= reorder_level:
            existing_request = frappe.db.exists(
                "Purchase Request",
                {
                    "item": self.item_name,
                    "farm": self.farm,
                    "status": "Pending"
                }
            )

            if not existing_request:
                farm_manager = frappe.db.get_value("Farms", self.farm, "farm_manager")
                pr = frappe.new_doc("Purchase Request")
                pr.item_name = self.item_name
                pr.quantity = 50
                pr.required_by = frappe.utils.nowdate()
                pr.farm = self.farm
                pr.farm_manager = farm_manager
                pr.status = "Pending"
                pr.insert()
                frappe.msgprint(f"📦 Auto Purchase Request created for {self.item_name}.")

        # ✅ NEW: Auto-create Invoice if Stock is coming IN
        if self.type == "In(New Stock Incoming)":
            rate = frappe.db.get_value('Supplied Items', {
                'parent': self.supplier,
                'item_name': self.item_name
            }, 'price') or 0

            invoice = frappe.new_doc("Invoice")
            invoice.invoice_date = frappe.utils.nowdate()
            invoice.supplier = self.supplier
            customer = frappe.db.get_value("Farms", self.farm, "farm_manager") or "Unknown"
            invoice.customer = customer 
            invoice.item_name = self.item_name
            invoice.quantity = self.quantity
            invoice.rate = rate
            invoice.total = self.quantity * rate
            invoice.status = 'Pending'
            invoice.insert()

            frappe.msgprint(f"🧾 Invoice auto-created for {self.quantity} x {self.item_name} @ ₹{rate} → ₹{self.quantity * rate}")

    def on_cancel(self):
        current_stock = frappe.db.get_value("Inventory Item", self.item_name, "current_stock") or 0

        if self.type == "In(New Stock Incoming)":
            new_stock = current_stock - self.quantity
        elif self.type == "Out(Used or Lost)":
            new_stock = current_stock + self.quantity

        frappe.db.set_value("Inventory Item", self.item_name, "current_stock", new_stock)
