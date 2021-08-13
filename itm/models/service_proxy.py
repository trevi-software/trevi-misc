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


class ItServiceProxy(models.Model):
    _name = "itm.service.proxy"
    _description = "Network Proxy Service"

    name = fields.Char(required=True)
    transparent = fields.Boolean("Transparent Proxy")
    enable_ssk = fields.Boolean("Proxy Enable Single Sign-On (Kerberos)")
    adblocking = fields.Boolean("Proxy Ad Blocking")
    port = fields.Char("Proxy Port")
    cache_size = fields.Char("Proxy Cache File Size")
