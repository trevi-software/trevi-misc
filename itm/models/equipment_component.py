##############################################################################
#
#    Copyright (C) 2021,2022 TREVI Software
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


from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class EquipmentComponent(models.Model):
    _name = "itm.equipment.component"
    _inherit = ["mail.activity.mixin", "mail.thread"]
    _description = "Component"

    name = fields.Char(required=True)
    equipment_id = fields.Many2one(
        "itm.equipment",
        "Component of",
        required=True,
        tracking=True,
        ondelete="restrict",
    )
    component_type_id = fields.Many2one("itm.equipment.component.type", required=True)
    serial_number = fields.Char()
    manufacturer_id = fields.Many2one("itm.equipment.brand")
    note = fields.Text()
    active = fields.Boolean(default=True)
    spec_line_ids = fields.Many2many(
        "itm.equipment.component.specification",
        "itm_equipment_component_specification_rel",
        domain="[('component_type_id', '=', component_type_id)]",
    )

    def write(self, vals):

        # If the equipment is being changed log a note to Equipment chatter
        # that a compnent was removed. Log a note to the new equipment that
        # a component was added.
        #

        new_eq_id = vals.get("equipment_id", False)
        if not new_eq_id:
            return super(EquipmentComponent, self).write(vals)

        new_equip = {new_eq_id: []}
        mt_note = self.env.ref("mail.mt_note")
        author = self.env.user.partner_id and self.env.user.partner_id.id or False
        old_equips = {}
        for res in self:
            new_equip[new_eq_id].append({"id": res.id, "name": res.name})
            if res.equipment_id:
                if res.equipment_id.id not in old_equips.keys():
                    old_equips.update(
                        {res.equipment_id.id: [{"id": res.id, "name": res.name}]}
                    )
                else:
                    old_equips[res.equipment_id.id].append(
                        {"id": res.id, "name": res.name}
                    )

        Equipment = self.env["itm.equipment"]

        # Log removal from old
        for k, v in old_equips.items():
            msg = ""
            for r in v:
                msg = msg + _("<li>A %(dsc)s was removed: %(name)s</li>") % {
                    "dsc": self._description,
                    "name": r["name"],
                }
            note = '<div class="o_mail_notification"><ul>' + msg + "</ul></div>"
            Equipment.browse(k).message_post(
                body=note, subtype_id=mt_note.id, author_id=author
            )

        # Log installation in new
        msg = ""
        for r in new_equip:
            msg = msg + _("<li>A %(dsc)s was installed: %(name)s</li>") % {
                "dsc": self._description,
                "name": r["name"],
            }
        note = '<div class="o_mail_notification"><ul>' + msg + "</ul></div>"
        Equipment.browse(new_eq_id).message_post(
            body=note, subtype_id=mt_note.id, author_id=author
        )

        return super(EquipmentComponent, self).write(vals)

    @api.model
    def create(self, vals):

        res = super(EquipmentComponent, self).create(vals)

        # Log a note to Site and Equipment chatter.
        #
        mt_note = self.env.ref("mail.mt_note")
        author = self.env.user.partner_id and self.env.user.partner_id.id or False
        msg = (
            _(
                '<div class="o_mail_notification"><ul><li>A new %(dsc)s was installed: \
                <a href="#" class="o_redirect" \
                data-oe-model=itm.equipment.component data-oe-id="%(id)s"> \
                %(name)s</a></li></ul></div>'
            )
            % {
                "dsc": res._description,
                "id": res.id,
                "name": res.name,
            }
        )
        if res.equipment_id:
            res.equipment_id.message_post(
                body=msg, subtype_id=mt_note.id, author_id=author
            )

        return res

    # Log a note on deletion of a component to Equipment chatter. Since
    # more than one record at a time may be deleted post all deleted records
    # for each equipment together in one post.
    #
    def unlink(self):

        mt_note = self.env.ref("mail.mt_note")
        author = self.env.user.partner_id and self.env.user.partner_id.id or False

        # map access records to equipment
        #
        equips = {}
        for res in self:
            if res.equipment_id:
                if res.equipment_id.id not in equips.keys():
                    equips.update(
                        {res.equipment_id.id: [{"id": res.id, "name": res.name}]}
                    )
                else:
                    equips[res.equipment_id.id].append({"id": res.id, "name": res.name})

        Equipment = self.env["itm.equipment"]
        for k, v in equips.items():
            msg = ""
            for r in v:
                msg = msg + _("<li>A %(dsc)s record was deleted: %(name)s</li>") % {
                    "dsc": self._description,
                    "name": r["name"],
                }
            note = '<div class="o_mail_notification"><ul>' + msg + "</ul></div>"
            Equipment.browse(k).message_post(
                body=note, subtype_id=mt_note.id, author_id=author
            )

        return super(EquipmentComponent, self).unlink()


class ComponentType(models.Model):
    _name = "itm.equipment.component.type"
    _description = "Asset Component Type"

    name = fields.Char(required=True)
    key_ids = fields.Many2many(
        "itm.equipment.component.specification.key",
        "itm_equipment_component_type_key_rel",
    )


class ComponentSpecification(models.Model):
    _name = "itm.equipment.component.specification"
    _description = "Asset Component Specification"

    component_type_id = fields.Many2one(
        "itm.equipment.component.type", compute="_compute_component_type", store=True
    )
    possible_key_ids = fields.One2many(
        "itm.equipment.component.specification.key",
        compute="_compute_possible_keys",
    )
    key_id = fields.Many2one(
        "itm.equipment.component.specification.key",
        domain="[('id', 'in', possible_key_ids)]",
        required=True,
    )
    value_id = fields.Many2one(
        "itm.equipment.component.specification.value",
        domain="[ \
            '|', \
            ('value_type_id', '=', False), \
            ('value_type_id', '=', value_type_id) \
        ]",
    )
    value_type_id = fields.Many2one(
        "itm.equipment.component.specification.selector",
        related="key_id.value_type_id",
        store=True,
    )

    def _compute_component_type(self):
        default_ctype_id = self.env.context.get("default_component_type_id")
        for res in self:
            if default_ctype_id:
                res.component_type_id = default_ctype_id

    @api.depends("component_type_id")
    def _compute_possible_keys(self):
        for res in self:
            res.possible_key_ids = res.component_type_id.key_ids


class SpecificationKey(models.Model):
    _name = "itm.equipment.component.specification.key"
    _description = "Component Specification Key"

    name = fields.Char(required=True)
    component_type_ids = fields.Many2many(
        "itm.equipment.component.type",
        "itm_equipment_component_type_key_rel",
    )
    value_type_id = fields.Many2one(
        "itm.equipment.component.specification.selector", required=True
    )

    @api.model
    def create(self, vals):

        res = super(SpecificationKey, self).create(vals)

        # When a new key is created from the specification list of the component
        # we need to setup the linkage between component type and key otherwise
        # the new key will not show up in the possible list of keys next time we
        # try to add it to a specification for the same type of component.
        #
        default_ctype_id = self.env.context.get("default_component_type_id")
        if default_ctype_id:
            ctype = self.env["itm.equipment.component.type"].browse(default_ctype_id)
            if res.id not in ctype.key_ids.ids:
                ctype.key_ids += res

        return res


class SpecificationValueType(models.Model):
    """
    This class is a convenient place to group values around. Instead of linking a
    key to all possible values we link it to a value type and then all possible
    values for the key are linked to this type. This also has the added bonus
    that values (via key type) can be re-used in multiple keys without duplications.
    """

    _name = "itm.equipment.component.specification.selector"
    _description = "Component Specification Selector"

    name = fields.Char(required=True)
    key_ids = fields.One2many(
        "itm.equipment.component.specification.key",
        "value_type_id",
    )
    value_ids = fields.One2many(
        "itm.equipment.component.specification.key",
        "value_type_id",
    )


class SpecificationValue(models.Model):
    _name = "itm.equipment.component.specification.value"
    _description = "Component Specification Value"

    name = fields.Char(required=True)
    value_type_id = fields.Many2one("itm.equipment.component.specification.selector")
    active = fields.Boolean(default=True)

    @api.constrains("name", "value_type_id")
    def _check_name_unique(self):
        for rec in self:
            domain = [
                ("name", "=ilike", rec.name),
                ("value_type_id", "=", rec.value_type_id.id),
                ("id", "!=", rec.id),
            ]
            count = self.search_count(domain)
            if count > 0:
                ids = self.search(domain)
                raise ValidationError(
                    _(
                        "The value you entered must be unique within its Value Type.\n"
                        "Previous record: Value Type: %(vname)s, Name: %(name)s"
                    )
                    % {
                        "vname": ids[0].value_type_id.name,
                        "name": ids[0].name,
                    }
                )

    @api.model
    def create(self, vals):

        # When a new value is created from the specification list of the component
        # we need to setup the linkage between value and key type otherwise
        # the new value will show as a possible value for *ALL* keys.
        #
        default_sel_id = self.env.context.get("default_value_type_id")
        if default_sel_id and "value_type_id" not in vals:
            vals.update({"value_type_id": default_sel_id})

        return super(SpecificationValue, self).create(vals)
