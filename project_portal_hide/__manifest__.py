# Copyright (C) 2021 TREVI Software
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Website Hide Projects &amp; Tasks",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": """TREVI Software,
        Odoo Community Association (OCA)""",
    "summary": """Hide projects &amp; tasks in the customer portal.""",
    "category": "Project Management",
    "maintainers": ["TREVI Software"],
    "website": "https://github.com/OCA/project",
    "depends": [
        "project",
    ],
    "data": [
        "views/project_portal_templates.xml",
    ],
    "installable": True,
}
