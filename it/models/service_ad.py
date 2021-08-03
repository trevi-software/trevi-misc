# Copyright (C) 2021 TREVI Software
# Copyright (C) 2014 Leandro Ezequiel Baldi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import fields, models


class ItServiceAD(models.Model):
    _name = "it.service.ad"
    _description = "Active Directory"

    name = fields.Char("Domain", required=True)
    type = fields.Selection(
        [("primary", "PRIMARY"), ("secundary", "SECONDARY"), ("slave", "SLAVE")],
        "AD Type",
    )
    adgroup_ids = fields.One2many(
        "it.service.ad.group", "ad_id", "Active Directory Groups"
    )
    aduser_ids = fields.One2many(
        "it.service.ad.user", "ad_id", "Active Directory Users"
    )
    site_id = fields.Many2one("it.site", "Site", ondelete="restrict")


class ItServiceAdGroup(models.Model):

    _name = "it.service.ad.group"
    _description = "Active Directory Group"

    name = fields.Char(required=True)
    description = fields.Text()
    actived = fields.Boolean(default=True)
    ad_id = fields.Many2one("it.service.ad", "Active Directory", ondelete="cascade")


class ItServiceAdUser(models.Model):
    _name = "it.service.ad.user"
    _description = "Active Directory User"

    name = fields.Char(required=True)
    username = fields.Char(required=True)
    email = fields.Char()
    active = fields.Boolean(default=True)
    ad_id = fields.Many2one("it.service.ad", "Active Directory", ondelete="cascade")
