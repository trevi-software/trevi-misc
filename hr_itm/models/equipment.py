# Copyright (C) 2024 Yuriy Gural <jg.gural@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ItEquipment(models.Model):
    _inherit = "itm.equipment"

    employee_id = fields.Many2one(
        "hr.employee",
        compute="_compute_equipment_assign",
        store=True,
        readonly=False,
        string="Assigned Employee",
        tracking=True,
    )
    department_id = fields.Many2one(
        "hr.department",
        compute="_compute_equipment_assign",
        store=True,
        readonly=False,
        string="Assigned Department",
        tracking=True,
    )
    equipment_assign_to = fields.Selection(
        [("department", "Department"), ("employee", "Employee"), ("other", "Other")],
        string="Used By",
        required=True,
        default="employee",
    )
    owner = fields.Char(compute="_compute_owner", store=True)
    assign_date = fields.Date(
        compute="_compute_equipment_assign",
        tracking=True,
        store=True,
        readonly=False,
        copy=True,
    )

    @api.depends("employee_id", "department_id", "equipment_assign_to")
    def _compute_owner(self):
        for equipment in self:
            if equipment.equipment_assign_to == "employee":
                equipment.owner = equipment.employee_id.name
            elif equipment.equipment_assign_to == "department":
                equipment.owner = equipment.department_id.manager_id.name

    @api.depends("equipment_assign_to")
    def _compute_equipment_assign(self):
        for equipment in self:
            if equipment.equipment_assign_to == "employee":
                equipment.department_id = False
                equipment.employee_id = equipment.employee_id
            elif equipment.equipment_assign_to == "department":
                equipment.employee_id = False
                equipment.department_id = equipment.department_id
            else:
                equipment.department_id = equipment.department_id
                equipment.employee_id = equipment.employee_id
            equipment.assign_date = fields.Date.context_today(self)
