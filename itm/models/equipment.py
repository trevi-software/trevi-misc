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


import base64

from odoo import _, api, fields, models
from odoo.modules.module import get_module_resource


class ItEquipmentBrand(models.Model):
    _name = "itm.equipment.brand"
    _description = "IT Asset Brand Name"

    name = fields.Char(required=True)
    is_computer = fields.Boolean("Computing Devices")
    is_network = fields.Boolean("Network Devices")
    is_accessories = fields.Boolean("Computing Accessories")
    is_components = fields.Boolean("Component Devices")


class ItEquipment(models.Model):
    _name = "itm.equipment"
    _inherit = ["mail.activity.mixin", "mail.thread"]
    _description = "IT Asset"

    @api.depends("virtual_ids")
    def _compute_virtual_count(self):
        for equipment in self:
            equipment.virtual_count = len(equipment.virtual_ids)

    @api.depends("access_ids")
    def _compute_access_count(self):
        for equipment in self:
            equipment.access_count = len(equipment.access_ids)

    @api.depends("backup_ids")
    def _compute_backup_count(self):
        for equipment in self:
            equipment.backup_count = len(equipment.backup_ids)

    @api.depends("component_ids")
    def _compute_component_count(self):
        for equipment in self:
            equipment.component_count = len(equipment.component_ids)

    @api.model
    def _get_default_image(self):
        image_path = get_module_resource(
            "itm", "static/src/img", "default_image_equipment.png"
        )
        return base64.b64encode(open(image_path, "rb").read())

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

    @api.model
    def _get_type(self):
        # work-arround for upgrading a module
        if not self.env.ref("itm.type_bundle", False):
            return False
        if self.env.context.get("search_default_type_virtual"):
            return self.env.ref("itm.type_virtual").id
        elif self.env.context.get("search_default_type_network"):
            return self.env.ref("itm.type_network").id
        elif self.env.context.get("search_default_type_software"):
            return self.env.ref("itm.type_software").id
        return self.env.ref("itm.type_bundle").id

    # For openerp structure
    company_id = fields.Many2one(
        "res.company",
        "Company",
        default=lambda self: self.env.company,
    )
    site_id = fields.Many2one(
        "itm.site",
        "Site",
        required=True,
        tracking=True,
        default=_get_site_id,
        help="A site or place of which this device is deployed",
    )

    brand = fields.Many2one(
        "itm.equipment.brand", "Brand Name", help="The assets or device brand"
    )

    active = fields.Boolean(default=True, tracking=True)
    # Counts
    access_count = fields.Integer(
        compute="_compute_access_count", string="Credentials Count", store=False
    )
    access_ids = fields.One2many("itm.access", "equipment_id", string="Credentials")
    backup_count = fields.Integer(compute="_compute_backup_count")
    backup_ids = fields.One2many("itm.backup", "equipment_id", "Backups")
    virtual_count = fields.Integer(
        compute="_compute_virtual_count", string="Guests", store=False
    )
    virtual_ids = fields.One2many("itm.equipment", "virtual_parent_id", "Guest(s)")
    # General Info
    identification = fields.Char(
        compute="_compute_identification", string="Complete Name", store=True
    )
    name = fields.Char(
        required=True,
        tracking=True,
        index=True,
        help="A device name, eg. Scanner",
    )
    code = fields.Char(
        tracking=True, index=True, help="Organization specific inventory code"
    )
    brand_id = fields.Many2one("itm.equipment.brand", "Brand")
    model = fields.Char()
    partner_id = fields.Many2one(
        "res.partner",
        "Partner",
        required=True,
        domain="[('manage_it','=',1)]",
        tracking=True,
        default=_get_partner_id,
        help="A partner or user which are using this device",
    )
    function_ids = fields.Many2many(
        "itm.equipment.function",
        "equipment_function_rel",
        "equipment_id",
        "function_id",
        "Functions",
        help="Defining the function of the devices, eg. scanning",
    )
    description = fields.Char(
        required=False,
        help="A device description, eg. 'A basic scanner device for "
        "scanning paper into .pdf files' ",
    )
    image = fields.Binary(
        "Photo",
        default=_get_default_image,
        help="Equipment Photo, limited to 1024x1024px.",
    )
    asset_type_id = fields.Many2one(
        "itm.equipment.type", "Asset type", default=_get_type
    )
    owner = fields.Char()
    location = fields.Char()
    state = fields.Selection(
        selection=[
            ("in_store", "In store"),
            ("in_use", "In use"),
            ("loaned", "Loaned"),
            ("in_repair", "In repair"),
            ("retired", "Retired"),
        ],
        default="in_store",
        tracking=True,
        index=True,
    )
    ip4_ids = fields.Many2many(
        "itm.site.network.ip4",
        string="IPv4 Addresses",
        readonly=True,
        compute="_compute_ip4_ids",
    )

    # Applications Page
    application_ids = fields.Many2many(
        "itm.application",
        "equipment_application_rel",
        "equipment_id",
        "application_id",
        "Applications",
        help="App information of this asset or device",
    )

    # Config Page
    is_contracted = fields.Boolean(
        "Contracted Service",
        help="This asset or device is contracted from other company",
    )
    is_partitioned = fields.Boolean("Partitions", help="This device is partitioned")
    is_backup = fields.Boolean("Backup", help="This asset or device is a backup")
    is_os = fields.Boolean("Operating System")
    is_application = fields.Boolean(
        "Application", help="This asset or device is an application"
    )
    is_config_file = fields.Boolean(
        "Store Config Files", help="Has a configuration files"
    )
    # Config Page - Functions
    function_fileserver = fields.Boolean(
        "File Server", help="This asset or device is a fileserver"
    )
    function_host = fields.Boolean("Host", help="This asset or device is a host")
    function_router = fields.Boolean(
        "Router", help="This asset or device is a network router"
    )
    function_database = fields.Boolean(
        "Database Server", help="This asset or device is a database server"
    )
    function_wireless = fields.Boolean(
        "Wireless Access Device",
        help="This asset acts as a wireless access point or router",
    )
    # Worklogs Page
    worklog_ids = fields.One2many(
        "itm.equipment.worklog",
        "equipment_id",
        "Worklogs on this equipment",
        tracking=True,
        help="Historical progress of work that spent on the asset or device",
    )
    # Contract Page
    contract_partner_id = fields.Many2one(
        "res.partner", "Contractor", help="Contractor name"
    )
    contract_client_number = fields.Char(
        "Client Number", help="The client number of the contractor"
    )
    contract_owner = fields.Char("Titular", help="A person holding the title")
    contract_nif = fields.Char(
        "NIF", help="The tax number for natural and legal person"
    )
    contract_direction = fields.Char("Invoice Direction", help="Invoice Direction")
    # Virtual Machine Page
    virtual_parent_id = fields.Many2one(
        "itm.equipment", "Virtual Machine", domain="[('function_host','=',1)]"
    )
    virtual_memory_amount = fields.Char("Memory")
    virtual_disk_amount = fields.Char("Disk Size")
    virtual_processor_amount = fields.Char("Number of Processor")
    virtual_network_amount = fields.Char("Number of Network")
    # Partition Page
    partitions_ids = fields.One2many(
        "itm.equipment.partition",
        "equipment_id",
        "Partitions on this equipment",
        help="Partition on this equipment",
    )
    # Router Page
    router_dmz = fields.Char("DMZ")
    router_forward_ids = fields.One2many(
        "itm.equipment.forward",
        "equipment_id",
        "Forward Rules",
        tracking=True,
        help="Router's forward rules",
    )
    router_rules_ids = fields.One2many(
        "itm.equipment.rule",
        "equipment_id",
        "Firewall Rules",
        tracking=True,
        help="Router's firewall rules",
    )
    # Network Configuration
    equipment_network_ids = fields.One2many(
        "itm.equipment.network",
        "equipment_id",
        "Network on this equipment",
        tracking=True,
        help="Network setup that configured within this asset or device",
    )
    # Product Page
    product_id = fields.Many2one("product.product", "Product")
    product_serial_number = fields.Char("Serial Number")
    product_warranty = fields.Char("Warranty")
    product_buydate = fields.Date("Buy Date")
    product_note = fields.Text()
    # Fileserver Page
    equipment_mapping_ids = fields.One2many(
        "itm.equipment.mapping",
        "equipment_id",
        "Network Shares",
        tracking=True,
        help="File server information",
    )
    # OS Page
    os_name = fields.Char(
        "OS Name",
        help="Operating system which is installed on device, eg. Windows 10, Ubuntu",
    )
    # Services
    ad_service_id = fields.Many2one(
        "itm.service.ad",
        "Active Directory",
        help="Domain Active Directory that related to this asset",
    )
    dhcp_service_id = fields.Many2one(
        "itm.service.dhcp4",
        "DHCP",
        help="Domain Host Control Protocol address which related to this asset",
    )
    wireless_service_id = fields.Many2one("itm.service.wireless", "Wireless Service")
    proxy_service_id = fields.Many2one("itm.service.proxy", "Proxy Service")
    vpn_service_id = fields.Many2one("itm.service.vpn", "VPN Service")
    # Database Page
    db_ids = fields.One2many(
        "itm.equipment.db", "equipment_id", "Databases", help="Database list"
    )
    use_proxy = fields.Boolean()
    proxy_client_config_id = fields.Many2one(
        "itm.equipment.network.proxy", "Proxy Configuration"
    )
    # Store Config File Page
    configuration_file_ids = fields.One2many(
        "itm.equipment.configuration",
        "equipment_id",
        "Configuration Files",
        help="configuration file of this asset or device",
    )
    # Components
    component_count = fields.Integer(compute=_compute_component_count)
    component_ids = fields.One2many(
        "itm.equipment.component", "equipment_id", "Components"
    )

    @api.depends(
        "equipment_network_ids",
        "equipment_network_ids.static_ipv4_id",
        "equipment_network_ids.dhcp_ipv4_id",
    )
    def _compute_ip4_ids(self):
        for equip in self:
            ifs = self.env["itm.site.network.ip4"]
            for net in equip.equipment_network_ids:
                if net.static_ipv4_id:
                    ifs |= net.static_ipv4_id
                if net.dhcp_ipv4_id:
                    ifs |= net.dhcp_ipv4_id
            equip.ip4_ids = ifs

    # Log a note on creation of equipment to Site and Equipment chatter.
    #
    @api.model
    def create(self, vals):
        res = super(ItEquipment, self).create(vals)
        mt_note = self.env.ref("mail.mt_note")
        author = self.env.user.partner_id and self.env.user.partner_id.id or False
        msg = (
            _(
                '<div class="o_mail_notification"><ul><li>A new %(desc)s was created: \
                <a href="#" class="o_redirect" data-oe-model=itm.equipment \
                data-oe-id="%(id)s"> %(name)s</a></li></ul></div>'
            )
            % {
                "desc": res._description,
                "id": res.id,
                "name": res.name,
            }
        )
        if res.site_id:
            res.site_id.message_post(body=msg, subtype_id=mt_note.id, author_id=author)
        if res.virtual_parent_id:
            res.virtual_parent_id.message_post(
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
            if res.virtual_parent_id:
                if res.virtual_parent_id.id not in equips.keys():
                    equips.update(
                        {res.virtual_parent_id.id: [{"id": res.id, "name": res.name}]}
                    )
                else:
                    equips[res.virtual_parent_id.id].append(
                        {"id": res.id, "name": res.name}
                    )

        Site = self.env["itm.site"]
        for k, v in sites.items():
            msg = ""
            for r in v:
                msg = msg + _("<li> %(dsc)s record was deleted: %(name)s</li>") % {
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

        return super(ItEquipment, self).unlink()

    def add_ip4_network_interface(
        self, name, network, mac, static_ip, dhcp_ip, use_dhcp, note=False
    ):

        # If an IPv4 address does not exist, create it
        ip_obj = self.env["itm.site.network.ip4"]
        static_ip4 = ip_obj.search(
            [
                ("name", "=", static_ip),
                ("network_id", "=", network.id),
            ]
        )
        if static_ip and not static_ip4:
            static_ip4 = ip_obj.create({"name": static_ip, "network_id": network.id})
        dhcp_ip4 = ip_obj.search(
            [
                ("name", "=", dhcp_ip),
                ("network_id", "=", network.id),
            ]
        )
        if dhcp_ip and not dhcp_ip4:
            dhcp_ip4 = ip_obj.create({"name": dhcp_ip, "network_id": network.id})
        return self.env["itm.equipment.network"].create(
            {
                "equipment_id": self.id,
                "name": name,
                "mac": mac,
                "network_id": network.id,
                "note": note,
                "use_dhcp4": use_dhcp,
                "static_ipv4_id": static_ip4.id,
                "dhcp_ipv4_id": dhcp_ip4.id,
            }
        )
