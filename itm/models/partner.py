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


from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.depends("equipment_ids")
    def _equipment_count(self):
        for partner in self:
            partner.equipment_count = len(partner.equipment_ids)

    @api.depends("access_ids")
    def _access_count(self):
        for partner in self:
            partner.access_count = len(partner.access_ids)

    @api.depends("backup_ids")
    def _backup_count(self):
        for partner in self:
            partner.backup_count = len(partner.backup_ids)

    manage_it = fields.Boolean("Manage IT")
    equipment_ids = fields.One2many("itm.equipment", "partner_id", "Assets")
    equipment_count = fields.Integer(compute=_equipment_count)
    access_ids = fields.One2many("itm.access", "partner_id", "Credentials")
    access_count = fields.Integer(compute=_access_count)
    backup_ids = fields.One2many("itm.backup", "partner_id", "Backups")
    backup_count = fields.Integer(compute=_backup_count)
