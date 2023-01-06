# Copyright (C) 2021,2022 TREVI Software
# Copyright (C) 2014 Leandro Ezequiel Baldi <baldileandro@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


import base64
import os
from random import choice

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from odoo import _, api, fields, models

PARAM_PASS = "itm_passkey"
PARAM_SALT = "itm_salt"


class ItAccess(models.Model):
    _name = "itm.access"
    _inherit = ["mail.thread"]
    _description = "Credential"

    @api.onchange("equipment_id")
    def onchange_equipment(self):
        if self.equipment_id:
            self.partner_id = self.equipment_id.partner_id
        else:
            self.partner_id = None

    @api.model
    def get_random_string(self):
        longitud = 16
        valores = (
            "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ<=>@#%&+"
        )
        p = ""
        p = p.join([choice(valores) for i in range(longitud)])
        return p

    def get_random_password(self):
        for access in self:
            access.password = self.get_random_string()

    def get_urlsafe_key(self):

        ConfigParam = self.env["ir.config_parameter"]
        salt = None
        passphrase = ConfigParam.sudo().get_param(PARAM_PASS)
        if not passphrase:
            passphrase = base64.urlsafe_b64encode(os.urandom(64)).decode()
            salt = os.urandom(16)
            ConfigParam.sudo().set_param(PARAM_PASS, passphrase)
            ConfigParam.sudo().set_param(
                PARAM_SALT, base64.urlsafe_b64encode(salt).decode()
            )
        else:
            salt = base64.urlsafe_b64decode(
                ConfigParam.sudo().get_param(PARAM_SALT).encode()
            )

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256,
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(passphrase.encode()))

    @api.model
    def encrypt_string(self, plaintext):
        """Returns a URL-safe string containing the encrypted version of plaintext."""

        key = self.get_urlsafe_key()
        f = Fernet(key)
        cipher = f.encrypt(plaintext.encode())
        return base64.urlsafe_b64encode(cipher)

    @api.model
    def decrypt_password_as_string(self, obj_id):
        """Returns a string representing the plaintext password in record with
        database ID obj_id. Returns empty string if the password is not set."""

        key = self.get_urlsafe_key()
        f = Fernet(key)

        plaintext = ""
        rec = self.browse(obj_id)
        if rec and rec.password:
            token = base64.urlsafe_b64decode(rec.password)
            plaintext = f.decrypt(token).decode()
        return plaintext

    @api.model
    def _get_partner_id(self):
        # Get the partner from either asset or site
        #
        if self.env.context.get("active_model") == "itm.equipment":
            equip = self.env["itm.equipment"].browse(self.env.context.get("active_id"))
            if equip.partner_id:
                return equip.partner_id.id
        elif self.env.context.get("active_model") == "itm.site":
            site = self.env["itm.site"].browse(self.env.context.get("active_id"))
            if site.partner_id:
                return site.partner_id.id
        return False

    @api.model
    def _get_site_id(self):
        if self.env.context.get("active_model") == "itm.equipment":
            equip = self.env["itm.equipment"].browse(self.env.context.get("active_id"))
            if equip.site_id:
                return equip.site_id.id
        return False

    company_id = fields.Many2one(
        "res.company",
        "Company",
        default=lambda self: self.env.company,
    )
    equipment_id = fields.Many2one("itm.equipment", "Asset", ondelete="restrict")
    site_id = fields.Many2one(
        "itm.site", "Site", required=True, ondelete="restrict", default=_get_site_id
    )
    name = fields.Char("Username", required=True, tracking=True)
    password = fields.Char()
    partner_id = fields.Many2one(
        "res.partner",
        "Partner",
        domain="[('manage_it','=',1)]",
        default=_get_partner_id,
        tracking=True,
    )
    active = fields.Boolean(default=True, tracking=True)
    ssl_csr = fields.Binary("CSR", tracking=True)
    ssl_csr_filename = fields.Char("CSR Filename")
    ssl_cert = fields.Binary("Cert", tracking=True)
    ssl_cert_filename = fields.Char("Cert Filename")
    ssl_publickey = fields.Binary("Public Key", tracking=True)
    ssl_publickey_filename = fields.Char("Public Key Filename")
    ssl_privatekey = fields.Binary("Private Key", tracking=True)
    ssl_privatekey_filename = fields.Char("Private Key Filename")

    def write(self, vals):

        # Log a note to Site and Equipment chatter.
        # Map access records to sites and equipment.
        #
        mt_note = self.env.ref("mail.mt_note")
        author = self.env.user.partner_id and self.env.user.partner_id.id or False
        sites = {}
        equips = {}
        for res in self:
            if res.site_id:
                if res.site_id.id not in sites.keys():
                    sites.update({res.site_id.id: [{"id": res.id, "name": res.name}]})
                else:
                    sites[res.site_id.id].append({"id": res.id, "name": res.name})
            if res.equipment_id:
                if res.equipment_id.id not in equips.keys():
                    equips.update(
                        {res.equipment_id.id: [{"id": res.id, "name": res.name}]}
                    )
                else:
                    equips[res.equipment_id.id].append({"id": res.id, "name": res.name})

        Site = self.env["itm.site"]
        for k, v in sites.items():
            msg = ""
            for r in v:
                msg = msg + _("<li>A %(dsc)s's password was updated: %(name)s</li>") % {
                    "dsc": self._description,
                    "name": r["name"],
                }
            note = '<div class="o_mail_notification"><ul>' + msg + "</ul></div>"
            Site.browse(k).message_post(
                body=note, subtype_id=mt_note.id, author_id=author
            )

        Equipment = self.env["itm.equipment"]
        for k, v in equips.items():
            msg = ""
            for r in v:
                msg = msg + _("<li>A %(dsc)s's password was updated: %(name)s</li>") % {
                    "dsc": self._description,
                    "name": r["name"],
                }
            note = '<div class="o_mail_notification"><ul>' + msg + "</ul></div>"
            Equipment.browse(k).message_post(
                body=note, subtype_id=mt_note.id, author_id=author
            )

        # Encrypt the password before saving it. The unencrypted password should not be
        # saved to the database even temporarily.
        #
        if "password" in vals.keys() and vals["password"] is not False:
            vals["password"] = self.encrypt_string(vals["password"])

        return super(ItAccess, self).write(vals)

    @api.model
    def create(self, vals):

        # Encrypt the password before saving it. The unencrypted password should not be
        # saved to the database even temporarily.
        #
        if "password" in vals.keys() and vals["password"] is not False:
            vals["password"] = self.encrypt_string(vals["password"])

        res = super(ItAccess, self).create(vals)

        # Log a note to Site and Equipment chatter.
        #
        mt_note = self.env.ref("mail.mt_note")
        author = self.env.user.partner_id and self.env.user.partner_id.id or False
        msg = (
            _(
                '<div class="o_mail_notification"><ul><li>A new %(dsc)s was created: \
                <a href="#" class="o_redirect" data-oe-model=itm.access data-oe-id="%(id)s"> \
                %(name)s</a></li></ul></div>'
            )
            % {"dsc": res._description, "id": res.id, "name": res.name}
        )
        if res.site_id:
            res.site_id.message_post(body=msg, subtype_id=mt_note.id, author_id=author)
        if res.equipment_id:
            res.equipment_id.message_post(
                body=msg, subtype_id=mt_note.id, author_id=author
            )

        return res

    # Log a note on deletion of credential to Site and Equipment chatter. Since
    # more than one record at a time may be deleted post all deleted records
    # for each site and each equipment together in one post.
    #
    def unlink(self):

        mt_note = self.env.ref("mail.mt_note")
        author = self.env.user.partner_id and self.env.user.partner_id.id or False

        # map access records to sites and equipment
        #
        sites = {}
        equips = {}
        for res in self:
            if res.site_id:
                if res.site_id.id not in sites.keys():
                    sites.update({res.site_id.id: [{"id": res.id, "name": res.name}]})
                else:
                    sites[res.site_id.id].append({"id": res.id, "name": res.name})
            if res.equipment_id:
                if res.equipment_id.id not in equips.keys():
                    equips.update(
                        {res.equipment_id.id: [{"id": res.id, "name": res.name}]}
                    )
                else:
                    equips[res.equipment_id.id].append({"id": res.id, "name": res.name})

        Site = self.env["itm.site"]
        for k, v in sites.items():
            msg = ""
            for r in v:
                msg = msg + _("<li> %(dsc)s was deleted: %(name)s</li>") % {
                    "dsc": self._description,
                    "name": r["name"],
                }
            note = '<div class="o_mail_notification"><ul>' + msg + "</ul></div>"
            Site.browse(k).message_post(
                body=note, subtype_id=mt_note.id, author_id=author
            )

        Equipment = self.env["itm.equipment"]
        for k, v in equips.items():
            msg = ""
            for r in v:
                msg = msg + _("<li> %(dsc)s record was deleted: %(name)s</li>") % {
                    "dsc": self._description,
                    "name": r["name"],
                }
            note = '<div class="o_mail_notification"><ul>' + msg + "</ul></div>"
            Equipment.browse(k).message_post(
                body=note, subtype_id=mt_note.id, author_id=author
            )

        return super(ItAccess, self).unlink()
