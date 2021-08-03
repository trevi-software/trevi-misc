# Copyright (C) 2021 TREVI Software
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models


class ItSite(models.Model):
    _name = "it.site"
    _description = "IT Site"

    @api.depends("equipment_ids")
    def compute_equipment_count(self):
        for site in self:
            site.equipment_count = len(site.equipment_ids)

    @api.depends("access_ids")
    def compute_access_count(self):
        for site in self:
            site.access_count = len(site.access_ids)

    name = fields.Char(required=True)
    partner_id = fields.Many2one("res.partner", "Partner")
    equipment_count = fields.Integer(compute="compute_equipment_count", string="Equipment")
    equipment_ids = fields.One2many("it.equipment", "site_id", "Equipments")
    access_count = fields.Integer(compute="compute_access_count", string="Credentials")
    access_ids = fields.One2many("it.access", "site_id", "Credential")
    ad_ids = fields.One2many("it.service.ad", "site_id", "Active Directory")
    notes = fields.Text()


class ItSiteNetwork(models.Model):
    _name = "it.site.network"
    _description = "Network"

    name = fields.Char(required=True)
    domain = fields.Char()
    netmask = fields.Char(required=True)
    default_gw = fields.Many2one("it.site.network.ip4", "Default Gateway")
    dns_ids = fields.Many2many(comodel_name="it.site.network.ip4", string="DNS Servers")


class ItSiteNetworkIp4(models.Model):
    _name = "it.site.network.ip4"
    _description = "Network IPv4 Address"

    name = fields.Char(required=True)
