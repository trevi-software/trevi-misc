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


class ItServiceWireless(models.Model):
    _name = "it.service.wireless"
    _description = "Wireless Access Point/Router Service"

    name = fields.Char("SSID", required=True)
    type = fields.Selection(
        [
            ("ap", "Access Point"),
            ("bridge", "Bridge"),
            ("extender", "Extender"),
            ("router_wireless", "Wireless Router"),
            ("router_wired", "Wired Router"),
        ],
    )
    auth_type = fields.Selection(
        [
            ("none", "NONE"),
            ("wep64", "WEP-64bits"),
            ("wep128", "WEP-128bits"),
            ("wpa_tkip", "WPA-TKIP"),
            ("wpa_aes", "WPA-AES"),
            ("wpa2_aes", "WPA2-AES"),
            ("wpa2_tkip", "WPA2-TKIP"),
            ("other", "OTHER"),
        ],
        "Authentication Type",
    )
    password = fields.Char("Key")
    guest = fields.Boolean("Enable Guest Access")
    guest_ssid = fields.Char("Guest SSID")
    guest_password = fields.Char("Guest Key")
    access_id = fields.Many2one("it.access", "Access Credentials")
