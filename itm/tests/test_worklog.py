# Copyright (C) 2021 TREVI Software
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.tests import common


class TestEquipmentComponent(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TestEquipmentComponent, cls).setUpClass()

        cls.Equipment = cls.env["itm.equipment"]
        cls.ItSite = cls.env["itm.site"]
        cls.Partner = cls.env["res.partner"]
        cls.Log = cls.env["itm.equipment.worklog"]

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

    def test_fix_issue17(self):
        """Creating worklog entry doesn't cause an exception"""

        try:
            self.Log.default_get(["user_id"])
        except AttributeError:
            self.fail("Unexpected failure")
