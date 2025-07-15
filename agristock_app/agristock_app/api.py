import frappe

@frappe.whitelist()
def get_suppliers_by_item(doctype, txt, searchfield, start, page_len, filters):
    item_name = filters.get("item_name")
    if not item_name:
        return []

    return frappe.db.sql("""
        SELECT s.name, s.supplier_name
        FROM `tabSupplier` s
        JOIN `tabSupplied Items` si ON si.parent = s.name
        WHERE si.item_name = %s AND s.docstatus < 2
    """, (item_name,))



@frappe.whitelist()
def get_item_rate_from_supplier(supplier, item_name):
    price = frappe.db.get_value(
        'Supplied Items',
        {
            'parent': supplier,
            'item_name': item_name
        },
        'price'
    )
    return price

