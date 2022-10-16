##############################################################################
#
#    Copyright (C) 2014 Leandro Ezequiel Baldi
#    <baldileandro@gmail.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


from odoo import fields, models


class ItBackup(models.Model):
    _name = "itm.backup"
    _description = "Backup"

    equipment_id = fields.Many2one(
        comodel_name="itm.equipment",
        string="Asset",
        domain="[('is_backup','=',1)]",
        ondelete="restrict",
        required=True,
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        related="equipment_id.partner_id",
        readonly=True,
        string="Partner",
        store=True,
    )
    name = fields.Char(required=True)
    type = fields.Selection(
        [
            ("diff", "DIFF"),
            ("full", "FULL"),
            ("inc", "INCREMENTAL"),
            ("other", "OTHER"),
        ],
        "Backup Type",
        required=True,
        default="full",
    )
    destination = fields.Char()
    source = fields.Char()
    script = fields.Binary()
    script_filename = fields.Char()
    script_location = fields.Char()
    frequency = fields.Char()
    time_schedule = fields.Float()
    note = fields.Text()
    company_id = fields.Many2one(
        "res.company",
        "Company",
        default=lambda self: self.env.company,
    )
    active = fields.Boolean(default=True)
