# Copyright (C) 2021 TREVI Software
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Website Hide Purchase Orders",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": """TREVI Software,
        Odoo Community Association (OCA)""",
    "summary": """Hide purchase orders in the customer portal.""",
    "category": "Purchase",
    "maintainers": ["TREVI Software"],
    "website": "https://github.com/trevi-software/trevi-misc",
    "depends": [
        "purchase",
    ],
    "data": [
        "views/purchase_portal_templates.xml",
    ],
    "installable": True,
}
