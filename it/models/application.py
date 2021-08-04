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
    _name = "it.application"
    _description = "Application"

    name = fields.Char(required=True)
    is_webapp = fields.Boolean("Web Application")
    company_id = fields.Many2one(
        "res.company",
        "Company",
        required=True,
        default=lambda self: self.env["res.company"]._company_default_get(
            "account.invoice"
        ),
    )
    active = fields.Boolean("Active", default=True)
    developer = fields.Char("Developer")
    link_download = fields.Char("Download Link")
    link_page = fields.Char("Link")
    license_id = fields.Many2one("it.application.license", "License")
    license_type = fields.Selection(
        [("opensource", "OPEN SOURCE"), ("closedsource", "COMMERCIAL")],
        required=True,
        default="opensource",
    )
    documentation = fields.Binary()
    documentation_filename = fields.Char()
    note = fields.Text()
    equipment_ids = fields.Many2many(
        "it.equipment",
        "equipment_application_rel",
        "application_id",
        "equipment_id",
        "Assets",
    )
    db_ids = fields.One2many("it.equipment.db", "application_id", "Databases")
    # Closed Source
    key = fields.Char()
    keygen = fields.Binary()
    crack = fields.Binary()
