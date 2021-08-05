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


import base64
import os

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from random import choice

from odoo import _, api, fields, models, _
from odoo.exceptions import AccessDenied, ValidationError


PARAM_PASS = "it_passkey"
PARAM_SALT = "it_passsalt"


class ItAccess(models.Model):
    _name = "it.access"
    _inherit = ["mail.activity.mixin", "mail.thread"]
    _description = "Credential"

    @api.onchange("equipment_id")
    def onchange_equipment(self):
        if self.equipment_id:
            self.partner_id = self.equipment_id.partner_id
        else:
            self.partner_id = None

    def get_random_password(self):
        for access in self:
            longitud = 16
            valores = (
                "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ<=>@#%&+"
            )
            p = ""
            p = p.join([choice(valores) for i in range(longitud)])
            token = self.encrypt_string(p)
            access.password = token

    def get_urlsafe_key(self):

        ConfigParam = self.env["ir.config_parameter"]
        salt = None
        passphrase = ConfigParam.sudo().get_param(PARAM_PASS)
        if not passphrase:
            passphrase = base64.urlsafe_b64encode(os.urandom(64)).decode()
            salt = os.urandom(16)
            ConfigParam.sudo().set_param(PARAM_PASS, passphrase)
            ConfigParam.sudo().set_param(PARAM_SALT, base64.urlsafe_b64encode(salt).decode())
        else:
            salt = base64.urlsafe_b64decode(ConfigParam.sudo().get_param(PARAM_SALT).encode())

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256,
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(passphrase.encode()))

    @api.model
    def encrypt_string(self, str):
        """Returns a URL-safe string containing the encrypted version of str."""

        key = self.get_urlsafe_key()
        f = Fernet(key)
        token = f.encrypt(str.encode())
        return base64.urlsafe_b64encode(token)

    def decrypt_password(self):

        key = self.get_urlsafe_key()
        f = Fernet(key)

        for rec in self:
            token = base64.urlsafe_b64decode(rec.password)
            password = f.decrypt(token).decode()
            raise AccessDenied(password)

    @api.model
    def _get_partner_id(self):
        if self.env.context.get("active_model") == "it.equipment":
            equip = self.env["it.equipment"].browse(self.env.context.get("active_id"))
            if equip.partner_id:
                return equip.partner_id.id
        return False

    @api.model
    def _get_site_id(self):
        if self.env.context.get("active_model") == "it.equipment":
            equip = self.env["it.equipment"].browse(self.env.context.get("active_id"))
            if equip.site_id:
                return equip.site_id.id
        return False

    company_id = fields.Many2one(
        "res.company",
        "Company",
        default=lambda self: self.env.company,
    )
    equipment_id = fields.Many2one("it.equipment", "Asset", ondelete="restrict")
    site_id = fields.Many2one("it.site", "Site", required=True, ondelete="restrict", default=_get_site_id)
    name = fields.Char("Username", required=True, tracking=True)
    password = fields.Char()
    partner_id = fields.Many2one(
        "res.partner",
        "Partner",
        domain="[('manage_it','=',1)]",
        default="_get_partner_id",
        tracking=True,
    )
    active = fields.Boolean(default=True)
    ssl_csr = fields.Binary("CSR", tracking=True)
    ssl_csr_filename = fields.Char("CSR Filename")
    ssl_cert = fields.Binary("Cert", tracking=True)
    ssl_cert_filename = fields.Char("Cert Filename")
    ssl_publickey = fields.Binary("Public Key", tracking=True)
    ssl_publickey_filename = fields.Char("Public Key Filename")
    ssl_privatekey = fields.Binary("Private Key", tracking=True)
    ssl_privatekey_filename = fields.Char("Private Key Filename")

    @api.model
    def create(self, vals):

        # Encrypt the password before saving it. The unencrypted password should not be
        # saved to the database even temporarily.
        #
        if 'password' in vals.keys() and vals['password'] is not False:
            vals['password'] = self.encrypt_string(vals['password'])

        res = super(ItAccess, self).create(vals)

        # Log a note to Site and Equipment chatter.
        #
        mt_note = self.env.ref('mail.mt_note')
        author = self.env.user.partner_id and self.env.user.partner_id.id or False
        msg = _('<div class="o_mail_notification"><ul><li>A new %s was created: <a href="#" class="o_redirect" data-oe-model=it.access data-oe-id="%s">%s</a></li></ul></div>', res._description, res.id, res.name)
        if res.site_id:
            res.site_id.message_post(body=msg, subtype_id=mt_note.id, author_id=author)
        if res.equipment_id:
            res.equipment_id.message_post(body=msg, subtype_id=mt_note.id, author_id=author)

        return res

    # Log a note on deletion of credential to Site and Equipment chatter. Since
    # more than one record at a time may be deleted post all deleted records
    # for each site and each equipment together in one post.
    #
    def unlink(self):

        mt_note = self.env.ref('mail.mt_note')
        author = self.env.user.partner_id and self.env.user.partner_id.id or False

        # map access records to sites and equipment
        #
        sites = {}
        equips = {}
        for res in self:
            if res.site_id:
                if res.site_id.id not in sites.keys():
                    sites.update({res.site_id.id: [{'id': res.id, 'name': res.name}]})
                else:
                    sites[res.site_id.id].append({'id': res.id, 'name': res.name})
            if res.equipment_id:
                if res.equipment_id.id not in equips.keys():
                    equips.update({res.equipment_id.id: [{'id': res.id, 'name': res.name}]})
                else:
                    equips[res.equipment_id.id].append({'id': res.id, 'name': res.name})

        Site = self.env["it.site"]
        for k,v in sites.items():
            msg = ""
            for r in v:
                msg = msg + _("<li> %s was deleted: %s</li>", self._description, r['name'])
            note = '<div class="o_mail_notification"><ul>' + msg + '</ul></div>'
            Site.browse(k).message_post(body=note, subtype_id=mt_note.id, author_id=author)

        Equipment = self.env['it.equipment']
        for k,v in equips.items():
            msg = ""
            for r in v:
                msg = msg + _("<li> %s record was deleted: %s</li>", self._description, r['name'])
            note = '<div class="o_mail_notification"><ul>' + msg + '</ul></div>'
            Equipment.browse(k).message_post(body=note, subtype_id=mt_note.id, author_id=author)

        return super(ItAccess, self).unlink()
