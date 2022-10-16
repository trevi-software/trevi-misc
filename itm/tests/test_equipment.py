# Copyright (C) 2022 TREVI Software
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestEquipment(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.Equipment = cls.env["itm.equipment"]
        cls.NetInterface = cls.env["itm.equipment.network"]
        cls.NetworkIp4 = cls.env["itm.site.network.ip4"]
        cls.SiteNetwork = cls.env["itm.site.network"]
        cls.ItSite = cls.env["itm.site"]
        cls.Partner = cls.env["res.partner"]

        cls.defaultSite = cls.ItSite.create({"name": "site"})
        cls.defaultNetwork = cls.SiteNetwork.create(
            {
                "name": "local.lan",
                "subnet": "192.168.0",
                "netmask": "255.255.255.0",
                "site_id": cls.defaultSite.id,
            }
        )
        cls.defaultPartner = cls.Partner.create(
            {
                "name": "Partner A",
                "email": "a@example.org",
            }
        )

    def create_equipment(self, name, partner=False, site=False):
        if not partner:
            partner = self.defaultPartner
        if not site:
            site = self.defaultSite
        return self.Equipment.create(
            {
                "name": name,
                "partner_id": partner.id,
                "site_id": site.id,
            }
        )

    def test_ip_dhcp_switch(self):

        static_ip = "192.168.0.1"
        dhcp_ip = "192.168.0.2"
        server = self.create_equipment("My Server")
        iface = server.add_ip4_network_interface(
            "Lan", self.defaultNetwork, "00:00:00:00:00:00", static_ip, dhcp_ip, False
        )

        self.assertTrue(
            iface.static_ipv4_id, "The network interface has a " "static IP address"
        )
        self.assertEqual(
            iface.display_ipv4,
            static_ip,
            "When 'use_dhcp' is NOT set the Static IP is displayed",
        )

        iface.use_dhcp4 = True
        self.assertEqual(
            iface.display_ipv4,
            dhcp_ip,
            "When 'use_dhcp' is set the DHCP IP is displayed",
        )

    def test_ip_no_static(self):

        dhcp_ip = "192.168.0.1"
        static_ip = False
        server = self.create_equipment("My Server")
        iface = server.add_ip4_network_interface(
            "Lan", self.defaultNetwork, "00:00:00:00:00:00", static_ip, dhcp_ip, False
        )

        self.assertTrue(
            iface.dhcp_ipv4_id, "The DHCP network interface has an IP address"
        )
        self.assertFalse(
            iface.static_ipv4_id, "The static interface does NOT have " "an IP address"
        )

    def test_ip_no_dhcp(self):

        static_ip = "192.168.0.1"
        dhcp_ip = False
        server = self.create_equipment("My Server")
        iface = server.add_ip4_network_interface(
            "Lan", self.defaultNetwork, "00:00:00:00:00:00", static_ip, dhcp_ip, False
        )

        self.assertTrue(
            iface.static_ipv4_id, "The network interface has a " "static IP address"
        )
        self.assertFalse(
            iface.dhcp_ipv4_id, "The DHCP interface does NOT have " "an IP address"
        )

    def test_equipment_ip4_addresses(self):
        lan1 = "192.168.0.1"
        lan2 = "192.168.1.2"
        server = self.create_equipment("My Server")
        iface1 = server.add_ip4_network_interface(
            "Lan", self.defaultNetwork, "00:00:00:00:00:00", lan1, False, False
        )
        iface2 = server.add_ip4_network_interface(
            "Lan", self.defaultNetwork, "00:00:00:00:00:01", lan2, False, False
        )

        self.assertIn(
            iface1.static_ipv4_id,
            server.ip4_ids,
            "The IP of the first interface is in the server's list of " "ip addresses",
        )
        self.assertIn(
            iface2.static_ipv4_id,
            server.ip4_ids,
            "The IP of the second interface is in the server's " "list of ip addresses",
        )

    def test_equipment_change_ip4_00(self):
        lan1 = "192.168.0.1"
        server = self.create_equipment("My Server")
        iface1 = server.add_ip4_network_interface(
            "Lan", self.defaultNetwork, "00:00:00:00:00:00", lan1, False, False
        )

        self.assertIn(
            iface1.static_ipv4_id,
            server.ip4_ids,
            "The IP of the interface is in the server's list of ip addresses",
        )

        ip4 = self.NetworkIp4.create(
            {"name": "10.250.250.250", "network_id": self.defaultNetwork.id}
        )
        iface1.static_ipv4_id = ip4
        self.assertIn(
            ip4,
            server.ip4_ids,
            "The interfaces new IP is in the server's list of ip addresses",
        )

    def test_equipment_change_ip4_01(self):
        lan1 = "192.168.0.1"
        server = self.create_equipment("My Server")
        iface1 = server.add_ip4_network_interface(
            "Lan", self.defaultNetwork, "00:00:00:00:00:00", lan1, False, False
        )

        self.assertEqual(
            len(server.ip4_ids), 1, "There is already one IP in the IP4 list"
        )

        ip4 = self.NetworkIp4.create(
            {"name": "10.250.250.250", "network_id": self.defaultNetwork.id}
        )
        iface1.dhcp_ipv4_id = ip4
        self.assertIn(
            iface1.static_ipv4_id,
            server.ip4_ids,
            "The IP of the interface is in the server's list of ip addresses",
        )
        self.assertIn(
            ip4,
            server.ip4_ids,
            "The interfaces new IP is in the server's list of ip addresses",
        )
