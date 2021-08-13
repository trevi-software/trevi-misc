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


class ItEquipmentConfiguration(models.Model):
    _name = "itm.equipment.configuration"
    _description = "Equipment Configuration"

    _order = "date desc"

    name = fields.Char("Description", required=True)
    date = fields.Datetime(default=fields.Datetime.now())
    config_file = fields.Binary("Configuration File")
    config_file_filename = fields.Char("Configuration File Filename")
    equipment_id = fields.Many2one("itm.equipment", "Asset", ondelete="restrict")
