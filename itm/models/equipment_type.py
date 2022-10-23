# Copyright (C) 2022 TREVI Software
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ItEquipmentType(models.Model):
    _name = "itm.equipment.type"
    _description = "Asset Type"
    _parent_store = True

    name = fields.Char(required=True)
    parent_id = fields.Many2one("itm.equipment.type", "Parent")
    parent_path = fields.Char(index=True)
    active = fields.Boolean(default=True)
