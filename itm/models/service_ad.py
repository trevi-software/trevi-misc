# Copyright (C) 2021,2022 TREVI Software
# Copyright (C) 2014 Leandro Ezequiel Baldi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ItServiceAD(models.Model):
    _name = "itm.service.ad"
    _inherit = ["mail.thread"]
    _description = "Active Directory"

    active = fields.Boolean(default=True)
    name = fields.Char("Domain", required=True)
    name_pre2000 = fields.Char("Domain (Pre-Windows 2000)", required=True)
    type = fields.Selection(
        [("primary", "PRIMARY"), ("secundary", "SECONDARY"), ("slave", "SLAVE")],
        "AD Type",
    )
    obj_ids = fields.One2many(
        "itm.service.ad.object", "ad_id", "Active Directory Objects"
    )
    site_id = fields.Many2one("itm.site", "Site", ondelete="restrict")
    equipment_id = fields.Many2one("itm.equipment", "Asset")
    partner_id = fields.Many2one(
        "res.partner",
        "Partner",
        compute="_compute_partner_id",
        store=True,
    )

    # Both site_id and equipment_id have partner fields. But, theoreticaly
    # the asset that the AD lives on could be owned by someone other than
    # the AD owner. We can be pretty sure that the owner of the site is
    # the owner of the AD.
    #
    @api.depends("site_id.partner_id")
    def _compute_partner_id(self):
        for ad in self:
            if ad.site_id and ad.site_id.partner_id:
                ad.partner_id = ad.site_id.partner_id

    @api.model
    def create(self, vals):

        res = super(ItServiceAD, self).create(vals)

        # Log a note to Site and Equipment chatter.
        #
        mt_note = self.env.ref("mail.mt_note")
        author = self.env.user.partner_id and self.env.user.partner_id.id or False
        msg = (
            _(
                '<div class="o_mail_notification"><ul><li>A new %(dsc)s was created: \
                <a href="#" class="o_redirect" data-oe-model=itm.service.ad \
                data-oe-id="%(id)s"> %(name)s</a></li></ul></div>'
            )
            % {
                "dsc": res._description,
                "id": res.id,
                "name": res.name,
            }
        )
        if res.site_id:
            res.site_id.message_post(body=msg, subtype_id=mt_note.id, author_id=author)
        if res.equipment_id:
            res.equipment_id.message_post(
                body=msg, subtype_id=mt_note.id, author_id=author
            )

        return res

    # Log a note on deletion of AD to Site and Equipment chatter. Since
    # more than one record at a time may be deleted post all deleted records
    # for each site and each equipment together in one post.
    #
    def unlink(self):

        mt_note = self.env.ref("mail.mt_note")
        author = self.env.user.partner_id and self.env.user.partner_id.id or False

        # map AD records to sites and equipment
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
                msg = msg + _("<li> %s(dsc) record was deleted: %(name)s</li>") % {
                    "dsc": self._description,
                    "name": r["name"],
                }
            note = '<div class="o_mail_notification"><ul>' + msg + "</ul></div>"
            Equipment.browse(k).message_post(
                body=note, subtype_id=mt_note.id, author_id=author
            )

        return super(ItServiceAD, self).unlink()


class ItServiceAdObject(models.Model):

    _name = "itm.service.ad.object"
    _description = "Active Directory Object"
    _rec_name = "complete_name"
    _order = "complete_name"

    @api.model
    def default_get(self, fields):
        if "ad_id" not in fields:
            fields.append("ad_id")
        res = super(ItServiceAdObject, self).default_get(fields)
        return res

    def _get_default_ad(self):
        if self.env.context.get("default_ad_id"):
            return self.env.context.get("default_ad_id")
        return False

    parent_id = fields.Many2one(
        "itm.service.ad.object",
        "AD Folder",
        domain="[('type', '=', 'folder'), ('ad_id', '=', ad_id)]",
    )
    ad_id = fields.Many2one(
        "itm.service.ad",
        "Active Directory",
        ondelete="cascade",
        default=_get_default_ad,
    )
    access_id = fields.Many2one("itm.access", "Related Credential")
    complete_name = fields.Char(
        compute="_compute_complete_name", store=True, recursive=True
    )
    description = fields.Text()
    active = fields.Boolean(default=True)
    type = fields.Selection(
        [("folder", _("Folder")), ("group", _("Group")), ("user", _("User"))],
        string="Object Type",
        default="folder",
    )

    # Folder related fields
    folder_name = fields.Char()

    # Group related fields
    group_name = fields.Char()

    # User related fields
    logon_name = fields.Char(string="User logon name")
    complete_logon = fields.Char(compute="_compute_complete_logon")
    first_name = fields.Char()
    last_name = fields.Char()
    full_name = fields.Char(compute="_compute_full_name", store=True)

    @api.constrains("parent_id")
    def _check_parent_id(self):
        if not self._check_recursion():
            raise ValidationError(
                _("You cannot create recursive Active Directory objects.")
            )

    @api.depends("logon_name", "ad_id.name")
    def _compute_complete_logon(self):
        for rec in self:
            if rec.logon_name and rec.ad_id and rec.ad_id.name:
                rec.complete_logon = "{}@{}".format(rec.logon_name, rec.ad_id.name)
            else:
                rec.complete_logon = False

    @api.depends("first_name", "last_name")
    def _compute_full_name(self):
        for rec in self:
            rec.full_name = "{} {}".format(
                rec.first_name or "", rec.last_name or ""
            ).strip()

    @api.depends("folder_name", "group_name", "logon_name", "parent_id.complete_name")
    def _compute_complete_name(self):
        for obj in self:
            name = False
            if obj.type == "folder":
                name = obj.folder_name
            elif obj.type == "group":
                name = obj.group_name
            elif obj.type == "user":
                name = obj.logon_name

            if obj.parent_id:
                obj.complete_name = r"%s \ %s" % (obj.parent_id.complete_name, name)
            else:
                obj.complete_name = name

    @api.model
    def create(self, vals):

        res = super(ItServiceAdObject, self).create(vals)

        # Log a note to Site and Equipment chatter.
        #
        mt_note = self.env.ref("mail.mt_note")
        author = self.env.user.partner_id and self.env.user.partner_id.id or False
        msg = (
            _(
                '<div class="o_mail_notification"><ul><li>A new %(dsc)s was created: \
                <a href="#" \
                class="o_redirect" \
                data-oe-model=itm.service.ad.object data-oe-id="%(id)s"> \
                %(name)s</a></li></ul></div>'
            )
            % {
                "dsc": res._description,
                "id": res.id,
                "name": res.complete_name,
            }
        )
        if res.ad_id and res.ad_id.site_id:
            res.ad_id.site_id.message_post(
                body=msg, subtype_id=mt_note.id, author_id=author
            )
        if res.ad_id and res.ad_id.equipment_id:
            res.ad_id.equipment_id.message_post(
                body=msg, subtype_id=mt_note.id, author_id=author
            )

        return res

    # Log a note on deletion of AD object to Site and Equipment chatter. Since
    # more than one record at a time may be deleted post all deleted records
    # for each site and each equipment together in one post.
    #
    def unlink(self):

        mt_note = self.env.ref("mail.mt_note")
        author = self.env.user.partner_id and self.env.user.partner_id.id or False

        # map AD records to sites and equipment
        #
        sites = {}
        equips = {}
        for obj in self:
            if obj.ad_id.site_id:
                if obj.ad_id.site_id.id not in sites.keys():
                    sites.update(
                        {
                            obj.ad_id.site_id.id: [
                                {"id": obj.id, "name": obj.complete_name}
                            ]
                        }
                    )
                else:
                    sites[obj.ad_id.site_id.id].append(
                        {"id": obj.id, "name": obj.complete_name}
                    )
            if obj.ad_id.equipment_id:
                if obj.ad_id.equipment_id.id not in equips.keys():
                    equips.update(
                        {
                            obj.ad_id.equipment_id.id: [
                                {"id": obj.id, "name": obj.complete_name}
                            ]
                        }
                    )
                else:
                    equips[obj.ad_id.equipment_id.id].append(
                        {"id": obj.id, "name": obj.complete_name}
                    )

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

        return super(ItServiceAdObject, self).unlink()
