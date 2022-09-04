# Copyright (C) 2021 TREVI Software
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ItSite(models.Model):
    _name = "itm.site"
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
    equipment_ids = fields.One2many("itm.equipment", "site_id", "Asset{s)")
    access_count = fields.Integer(
        compute="_compute_access_count", string="Credentials", store=False
    )
    active = fields.Boolean(default=True, tracking=True)
    access_ids = fields.One2many("itm.access", "site_id", "Credential(s)")
    ad_ids = fields.One2many("itm.service.ad", "site_id", "Active Directory")
    network_ids = fields.One2many("itm.site.network", "site_id", string="Networks")


class ItSiteNetwork(models.Model):
    _name = "itm.site.network"
    _description = "Network"

    site_id = fields.Many2one("itm.site", "Site")
    name = fields.Char(string="Domain", required=True)
    subnet = fields.Char(required=True)
    netmask = fields.Char(required=True)
    default_gw = fields.Many2one("itm.site.network.ip4", "Default Gateway")
    dns_ids = fields.Many2many(
        comodel_name="itm.site.network.ip4", string="DNS Servers"
    )
    dhcp4_ids = fields.One2many("itm.service.dhcp4", "network_id", "DHCP")
    ip4_ids = fields.One2many(
        "itm.site.network.ip4", "network_id", string="IPv4 Addresses"
    )


class ItSiteNetworkIp4(models.Model):
    _name = "itm.site.network.ip4"
    _description = "Network IPv4 Address"

    name = fields.Char(required=True)
    network_id = fields.Many2one("itm.site.network", required=True)

    # Upgrade earlier installations that didn't have 'network_id' field
    #
    def _initialize_network_id(self):
        _logger.warning(
            "Beginning initialize of 'network_id' field of itm.site.network.ip4"
        )
        iface_obj = self.env["itm.equipment.network"]
        ips = self.env["itm.site.network.ip4"].search([("network_id", "=", False)])
        _logger.warning(f"Found {len(ips)} records to update")
        for ip in ips:
            iface = iface_obj.search(
                [
                    "|",
                    ("static_ipv4_id", "=", ip.id),
                    ("dhcp_ipv4_id", "=", ip.id),
                ]
            )
            if iface:
                _logger.warning(f"IP {ip.name}: set network: {iface.network_id.name}")
                ip.network_id = iface.network_id

    @api.constrains("name", "network_id")
    def check_name(self):
        IpAddr = self.env["itm.site.network.ip4"]
        for rec in self:
            duplicates = IpAddr.search(
                [
                    ("name", "=", rec.name),
                    ("network_id", "=", rec.network_id.id),
                    ("id", "!=", rec.id),
                ]
            )
            if duplicates:
                raise ValidationError(_("IP address '%s' already exists.", rec.name))
