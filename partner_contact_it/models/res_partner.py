# Copyright (C) 2021 TREVI Software
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    it_contact = fields.Boolean("IT Contact")
    it_contact_ids = fields.Many2many(
        "res.partner",
        "res_partner_it_contacts_rel",
        "partner_id",
        "contact_id",
        string="IT Contacts",
    )

    def _update_parent_it_contacts(self, update):
        for contact in self:
            if contact.parent_id:
                if update:
                    contact.parent_id.it_contact_ids |= contact
                elif contact in contact.it_contact_ids:
                    contact.parent_id.it_contact_ids -= contact

    @api.model
    def create(self, vals):
        res = super(ResPartner, self).create(vals)
        if "it_contact" in vals:
            res._update_parent_it_contacts(vals["it_contact"])
        return res

    def write(self, vals):
        res = super(ResPartner, self).write(vals)
        if "it_contact" in vals:
            self._update_parent_it_contacts(vals["it_contact"])
        if vals.get("parent_id", False):
            for contact in self:
                if contact.it_contact:
                    contact._update_parent_it_contacts(True)
        return res
