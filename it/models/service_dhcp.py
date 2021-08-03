##############################################################################
#
#    Copyright (C) 2021 Michael Telahun Makonnen <telahunmike@gmail.com>
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


class ItServiceDhcp4(models.Model):
    _name = "it.service.dhcp4"
    _description = "DHCP Service"

    name = fields.Char(required=True)
    network_id = fields.Many2one("it.site.network", "Network")
    start_address = fields.Many2one("it.site.network.ip4")
    end_address = fields.Many2one("it.site.network.ip4")
    reservation_ids = fields.One2many(
        "it.equipment.ipreservation", "dhcp_id", "IPv4 reservations"
    )
