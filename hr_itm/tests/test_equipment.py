# Copyright (C) 2024 Yuriy Gural <jg.gural@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests.common import TransactionCase


class TestEquipment(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Partner X",
                "email": "x@example.org",
            }
        )
        cls.site = cls.env["itm.site"].create(
            {
                "name": "Site X",
            }
        )
        cls.employee = cls.env["hr.employee"].create(
            {
                "name": "Employee X",
            }
        )
        cls.department = cls.env["hr.department"].create(
            {
                "name": "Department X",
            }
        )

    def test_equipment_assign_to(self):

        equipment = self.env["itm.equipment"].create(
            {
                "name": "My Equipment",
                "partner_id": self.partner.id,
                "site_id": self.site.id,
            }
        )

        equipment.equipment_assign_to = "department"
        equipment.department_id = self.department
        today = fields.Date.today()
        self.assertFalse(equipment.employee_id)
        self.assertEqual(equipment.assign_date, today, "Assign date should be today")

        equipment.equipment_assign_to = "other"
        equipment.employee_id = self.employee
        self.assertEqual(
            equipment.department_id,
            self.department,
            "Equipment should be assigned to both the employee and the department",
        )
