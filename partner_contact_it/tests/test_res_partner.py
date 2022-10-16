# Copyright (C) 2021 TREVI Software
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import common


class TestPartnerContact(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestPartnerContact, cls).setUpClass()
        cls.ResPartner = cls.env["res.partner"]
        cls.partner = cls.ResPartner.create(
            {
                "name": "Partner A",
            }
        )
        cls.contact = cls.ResPartner.create(
            {
                "name": "Contact A1",
                "parent_id": cls.partner.id,
            }
        )

    def test_create(self):
        partner = self.ResPartner.create(
            {
                "name": "Partner B",
            }
        )
        contact1 = self.ResPartner.create(
            {
                "name": "Contact B1",
                "parent_id": partner.id,
                "it_contact": True,
            }
        )
        self.ResPartner.create(
            {
                "name": "Contact B2",
                "parent_id": partner.id,
            }
        )

        self.assertTrue(contact1.it_contact, "IT Contact field field should be True")
        self.assertEqual(
            len(partner.it_contact_ids),
            1,
            "The parent's list of IT Contacts should only contain one record",
        )
        self.assertEqual(
            partner.it_contact_ids[0],
            contact1,
            "The list of IT Contacts should contain the contact set as IT Contact",
        )

    def test_write(self):

        self.assertFalse(
            self.contact.it_contact,
            "Initially, the contact should NOT be an IT Contact",
        )

        self.contact.it_contact = True

        self.assertEqual(
            len(self.partner.it_contact_ids),
            1,
            "The parent's list of IT Contacts should only contain one record",
        )
        self.assertEqual(
            self.partner.it_contact_ids[0],
            self.contact,
            "The list of IT Contacts should contain the contact set as IT Contact",
        )

    def test_add_parent_after_toggle(self):
        """Test setting of parent after enabling IT Contact toggle."""

        self.contact.it_contact = False
        self.contact.parent_id = False
        self.assertNotIn(
            self.contact,
            self.partner,
            "Contact should NOT be in partner's list of IT Contacts",
        )

        self.contact.it_contact = True
        self.contact.parent_id = self.partner
        self.assertIn(
            self.contact,
            self.partner.it_contact_ids,
            "Contact should be in partner's list of IT Contacts",
        )
