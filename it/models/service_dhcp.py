# Copyright (C) 2021 TREVI Software
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import fields, models


class ItServiceDhcp4(models.Model):
    _name = "it.service.dhcp4"
    _description = "DHCP Service"

    name = fields.Char(required=True)
    equipment_id = fields.Many2one("it.equipment", "Asset", required=False)
    network_id = fields.Many2one("it.site.network", "Network", required=False)
    subnet = fields.Char()
    subnet_mask = fields.Char()
    start_address = fields.Many2one("it.site.network.ip4")
    end_address = fields.Many2one("it.site.network.ip4")
    lease_time = fields.Integer(help="Default lease time in seconds")
    reservation_ids = fields.One2many(
        "it.equipment.ipreservation", "dhcp_id", "IPv4 reservations"
    )
