# Copyright (C) 2021 TREVI Software
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ItSite(models.Model):
    _name = "it.site"
    _inherit = ["mail.activity.mixin", "mail.thread"]
    _description = "IT Site"

    @api.depends("equipment_ids")
    def _compute_equipment_count(self):
        for site in self:
            site.equipment_count = len(site.equipment_ids)

    @api.depends("access_ids")
    def _compute_access_count(self):
        for site in self:
            site.access_count = len(site.access_ids)

    company_id = fields.Many2one(
        "res.company",
        "Company",
        default=lambda self: self.env.company,
    )
    name = fields.Char(required=True)
    partner_id = fields.Many2one("res.partner", "Partner", tracking=True)
    equipment_count = fields.Integer(
        compute="_compute_equipment_count",
        string="Assets",
        store=True,
    )
    equipment_ids = fields.One2many("it.equipment", "site_id", "Asset{s)")
    access_count = fields.Integer(
        compute="_compute_access_count", string="Credentials", store=False
    )
    active = fields.Boolean(default=True, tracking=True)
    access_ids = fields.One2many("it.access", "site_id", "Credential(s)")
    ad_ids = fields.One2many("it.service.ad", "site_id", "Active Directory")
    network_ids = fields.One2many("it.site.network", "site_id", string="Networks")


class ItSiteNetwork(models.Model):
    _name = "it.site.network"
    _description = "Network"

    site_id = fields.Many2one("it.site", "Site")
    name = fields.Char(string="Domain", required=True)
    subnet = fields.Char(required=True)
    netmask = fields.Char(required=True)
    default_gw = fields.Many2one("it.site.network.ip4", "Default Gateway")
    dns_ids = fields.Many2many(comodel_name="it.site.network.ip4", string="DNS Servers")
    dhcp4_ids = fields.One2many("it.service.dhcp4", "network_id", "DHCP")


class ItSiteNetworkIp4(models.Model):
    _name = "it.site.network.ip4"
    _description = "Network IPv4 Address"

    name = fields.Char(required=True)

    @api.constrains("name")
    def check_name(self):
        IpAddr = self.env["it.site.network.ip4"]
        for rec in self:
            duplicates = IpAddr.search([("name", "=", rec.name), ("id", "!=", rec.id)])
            if duplicates:
                raise ValidationError(_("IP address '%s' already exists.", rec.name))
