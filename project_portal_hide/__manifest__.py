# Copyright (C) 2021 TREVI Software
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Website Hide Projects and Tasks",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": """TREVI Software,
        Odoo Community Association (OCA)""",
    "summary": """Hide projects &amp; tasks in the customer portal.""",
    "category": "Project Management",
    "maintainers": ["TREVI Software"],
    "images": ["static/src/img/main_screenshot.png"],
    "website": "https://github.com/trevi-software/trevi-misc",
    "depends": [
        "portal",
        "project",
    ],
    "data": [
        "views/project_portal_templates.xml",
    ],
    "installable": True,
}
