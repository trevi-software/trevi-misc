# Copyright (C) 2021,2022 TREVI Software
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import fields, models


class ItServiceWireless(models.Model):
    _name = "itm.service.wireless"
    _description = "Wireless Service"

    name = fields.Char("Description", required=True)
    type = fields.Selection(
        [
            ("ap", "Access Point"),
            ("bridge", "Bridge"),
            ("extender", "Extender"),
            ("router_wireless", "Wireless Router"),
        ],
    )
    network_id = fields.Many2one("itm.site.network", "Network")
    access_id = fields.Many2one("itm.access", "Access Credentials")
    bssid_ids = fields.One2many("itm.service.wireless.ssid", "wireless_id", "SSI")

    def _compute_display_name(self):

        res = super()._compute_display_name()

        for rec in self:
            if len(rec.bssid_ids) == 1:
                rec.display_name = f"{rec.name} ({rec.bssid_ids.name})"
            elif len(rec.bssid_ids) > 1:
                rec.display_name = f"{rec.name} (multi SSID)"
        return res


class WirelessSsid(models.Model):

    _name = "itm.service.wireless.ssid"
    _description = "Wireless Base Station ID"

    name = fields.Char("SSID", required=True)
    wireless_id = fields.Many2one("itm.service.wireless", "Wireless service")
    is_guest = fields.Boolean(help="If checked, this is a Guest SSID")
    auth_type = fields.Selection(
        [
            ("none", "NONE"),
            ("wep64", "WEP-64bits"),
            ("wep128", "WEP-128bits"),
            ("wpa", "WPA Personal (Pre-shared key)"),
            ("wpa_ent", "WPA Enterprise"),
            ("wpa2", "WPA2 Personal (Pre-shared key)"),
            ("wpa2_ent", "WPA2 Enterprise"),
            ("auto", "Auto"),
            ("other", "Other"),
        ],
        "Authentication Type",
        default="wpa2",
    )
    encryption_type = fields.Selection(
        [
            ("none", "NONE"),
            ("auto", "Auto"),
            ("tkip", "TKIP"),
            ("aes", "AES"),
        ],
        default="auto",
    )
    passkey = fields.Char("Key")
