# Copyright (C) 2021 TREVI Software
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.exceptions import ValidationError
from odoo.tests import common


class TestEquipmentComponent(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TestEquipmentComponent, cls).setUpClass()

        cls.Equipment = cls.env["itm.equipment"]
        cls.Component = cls.env["itm.equipment.component"]
        cls.ComponentType = cls.env["itm.equipment.component.type"]
        cls.Specification = cls.env["itm.equipment.component.specification"]
        cls.Selector = cls.env["itm.equipment.component.specification.selector"]
        cls.Key = cls.env["itm.equipment.component.specification.key"]
        cls.Value = cls.env["itm.equipment.component.specification.value"]
        cls.ItSite = cls.env["itm.site"]
        cls.Partner = cls.env["res.partner"]

        cls.defaultComponentType = cls.ComponentType.create({"name": "A"})
        cls.defaultSite = cls.ItSite.create({"name": "site"})
        cls.defaultPartner = cls.Partner.create(
            {
                "name": "Partner A",
                "email": "a@example.org",
            }
        )
        cls.equipment = cls.Equipment.create(
            {
                "name": "My Equipment",
                "partner_id": cls.defaultPartner.id,
                "site_id": cls.defaultSite.id,
            }
        )

    def test_create_updates_equipment_chatter(self):
        """Creating a component updates equipment chatter"""

        msg_count = len(self.equipment.message_ids)
        self.Component.create(
            {
                "name": "Component X",
                "equipment_id": self.equipment.id,
                "component_type_id": self.defaultComponentType.id,
            }
        )

        self.assertEqual(msg_count + 1, len(self.equipment.message_ids))

    def test_new_key_from_specification(self):
        """
        When a new key is created from the component specification form the
        relevant linkages between component type and key are created.
        """

        component = self.Component.create(
            {
                "name": "Component X",
                "equipment_id": self.equipment.id,
                "component_type_id": self.defaultComponentType.id,
            }
        )
        selector = self.Selector.create({"name": "Some Selector"})
        key = self.Key.with_context(
            default_component_type_id=component.component_type_id.id
        ).create(
            {
                "name": "K",
                "value_type_id": selector.id,
            }
        )

        self.assertIn(component.component_type_id, key.component_type_ids)

    def test_new_value_set_specification(self):
        """
        When a new value is created automatically set the selector
        """

        selector = self.Selector.create({"name": "Some Selector"})
        val = self.Value.with_context(default_value_type_id=selector.id).create(
            {"name": "V"}
        )

        self.assertEqual(val.value_type_id, selector)

    def test_unique_value_name(self):
        """
        The (name, value_type_id) field combo of ITM Value should be
        (case insensitive) unique.
        """

        typeA = self.Selector.create({"name": "Some Selector A"})
        typeB = self.Selector.create({"name": "Some Selector B"})
        self.Value.create({"name": "SCSI", "value_type_id": typeA.id})
        self.Value.create({"name": "SATA", "value_type_id": typeB.id})

        with self.assertRaises(ValidationError):
            self.Value.create({"name": "scsi", "value_type_id": typeA.id})

        try:
            self.Value.create({"name": "scsi", "value_type_id": typeB.id})
        except ValidationError:
            self.fail("Unexpected ValidationError!")
