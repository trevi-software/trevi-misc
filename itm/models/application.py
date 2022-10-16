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


class ItApplication(models.Model):
    _name = "itm.application"
    _description = "Application"

    name = fields.Char(required=True, help="Name of the application")
    is_webapp = fields.Boolean("Web Application")
    company_id = fields.Many2one(
        "res.company",
        "Company",
        default=lambda self: self.env.company,
    )
    active = fields.Boolean(
        default=True, help="Mark if this app is currently used and running"
    )
    developer = fields.Char(
        help="A company or person who create and develop this application"
    )
    link_download = fields.Char(
        "Download Link", help="Download link of the application"
    )
    link_page = fields.Char("Link", help="Official website link of the application")
    license_id = fields.Many2one(
        "itm.application.license", "License", help="License type"
    )
    license_type = fields.Selection(
        [("opensource", "OPEN SOURCE"), ("closedsource", "COMMERCIAL")],
        required=True,
        default="opensource",
        help="License name",
    )
    documentation = fields.Binary(
        help="Documentation sheet of technical use or standard operational procedure"
    )
    documentation_filename = fields.Char()
    note = fields.Text(help="Note for this application eg")
    equipment_ids = fields.Many2many(
        "itm.equipment",
        "equipment_application_rel",
        "application_id",
        "equipment_id",
        "Assets",
    )
    db_ids = fields.One2many("itm.equipment.db", "application_id", "Databases")
    # Closed Source
    key = fields.Char()
    keygen = fields.Binary()
    crack = fields.Binary()
