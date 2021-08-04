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


class ItEquipmentMapping(models.Model):
    _name = "it.equipment.mapping"
    _description = "Network Share Mapping"

    equipment_id = fields.Many2one("it.equipment", "Asset", ondelete="cascade")
    name = fields.Char("Share Name", required=True)
    path = fields.Char("Filesystem Path", required=True)
    adgroup_ids = fields.Many2many(comodel_name="it.service.ad.group", string="Groups")
    aduser_ids = fields.Many2many(comodel_name="it.service.ad.user", string="Users")
    perm_read = fields.Boolean("Perm Read")
    perm_write = fields.Boolean("Perm Write")
    perm_create = fields.Boolean("Perm Create")
    perm_delete = fields.Boolean("Perm Delete")
