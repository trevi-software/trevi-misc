# Copyright (C) 2024 Yuriy Gural <jg.gural@gmail.com>
# Based on the hr_maintenance module
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "IT Infrastructure Management - HR",
    "version": "16.0.1.0.1",
    "category": "Human Resources",
    "summary": "Bridge between HR and IT Infrastructure Management",
    "author": """TREVI Software,
        Yuriy Gural""",
    "license": "AGPL-3",
    "depends": ["hr", "itm"],
    "data": [
        "views/equipment_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
