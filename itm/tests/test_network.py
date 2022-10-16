# Copyright (C) 2022 TREVI Software
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestEquipment(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.Equipment = cls.env["itm.equipment"]
        cls.NetworkIp4 = cls.env["itm.site.network.ip4"]
        cls.SiteNetwork = cls.env["itm.site.network"]

    def test_ip_in_multiple_networks(self):

        net1 = self.SiteNetwork.create(
            {
                "name": "local.lan",
                "subnet": "192.168.0",
                "netmask": "255.255.255.0",
            }
        )
        net2 = self.SiteNetwork.create(
            {
                "name": "remote.lan",
                "subnet": "192.168.0",
                "netmask": "255.255.255.0",
            }
        )
        ip1 = self.NetworkIp4.create({"name": "192.168.0.1", "network_id": net1.id})
        ip2 = self.NetworkIp4.create({"name": "192.168.0.1", "network_id": net2.id})

        self.assertEqual(ip1.network_id, net1, "First IP is in first network")
        self.assertEqual(ip2.network_id, net2, "Second IP is in second network")

    def test_automatic_network_id(self):

        net1 = self.SiteNetwork.create(
            {
                "name": "local.lan",
                "subnet": "192.168.0",
                "netmask": "255.255.255.0",
            }
        )
        self.SiteNetwork.create(
            {
                "name": "remote.lan",
                "subnet": "192.168.0",
                "netmask": "255.255.255.0",
            }
        )
        ip1 = self.NetworkIp4.with_context(default_network_id=net1.id).create(
            {"name": "192.168.0.1"}
        )
        self.assertEqual(
            ip1.network_id, net1, "The network from the context is auto-assigned"
        )
