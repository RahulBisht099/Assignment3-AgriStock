import frappe
from frappe.utils import flt

def execute(filters=None):
    columns = get_columns()
    data = get_data()
    return columns, data

def get_columns():
    return [
        {"label": "Farm", "fieldname": "farm", "fieldtype": "Link", "options": "Farm", "width": 200},
        {"label": "Item", "fieldname": "item", "fieldtype": "Data", "width": 200},
        {"label": "Category", "fieldname": "category", "fieldtype": "Data", "width": 120},
        {"label": "UOM", "fieldname": "uom", "fieldtype": "Link", "options": "UOM", "width": 100},
        {"label": "Current Stock", "fieldname": "current_stock", "fieldtype": "Float", "width": 120},
    ]

def get_data():
    items = frappe.get_all("Inventory Item",
        fields=["farm", "item_name as item", "category", "uom", "current_stock"],
        order_by="farm"
    )
    return items
