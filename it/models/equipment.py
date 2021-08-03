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
from random import choice

from odoo import tools, api, fields, models
from odoo.modules.module import get_module_resource


class ItEquipmentBrand(models.Model):
    _name = "it.equipment.brand"
    _description = "IT Equipment Brand Names"

    name = fields.Char(required=True)
    is_computer = fields.Boolean("Computing Devices")
    is_network = fields.Boolean("Network Devices")
    is_accessories = fields.Boolean("Computing Accessories")


class ItEquipment(models.Model):
    _name = "it.equipment"
    _description = "Equipments"

    _rec_name = "identification"

    @api.model
    def _get_pin(self):
        longitud = 12
        valores = (
            "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ<=>@#%&+"
        )
        p = ""
        p = p.join([choice(valores) for i in range(longitud)])
        return p

    @api.depends("partner_id")
    def _get_identification(self):
        for equipment in self:
            equipment.identification = equipment.name + " - " + equipment.partner_id.name

    def name_search(self, name, args, limit=80, operator="ilike"):
        ids = None
        if name:
            ids = self.search(
                [("identification", operator, name)] + args,
                limit=limit,
            )
        if ids is None or len(ids) == 0:
            ids = self.search([("name", operator, name)] + args, limit=limit)
        return ids.name_get()

    @api.depends("virtual_ids")
    def _virtual_count(self):
        for equipment in self:
            equipment.virtual_count = len(equipment.virtual_ids)

    @api.depends("access_ids")
    def _access_count(self):
        for equipment in self:
            equipment.access_count = len(equipment.access_ids)

    @api.depends("backup_ids")
    def _backup_count(self):
        for equipment in self:
            equipment.backup_count = len(equipment.backup_ids)

    @api.model
    def _get_default_image(self):
        image_path = get_module_resource(
            "it", "static/src/img", "default_image_equipment.png"
        )
        return base64.b64encode(open(image_path, 'rb').read())

    # For openerp structure
    company_id = fields.Many2one(
        "res.company",
        "Company",
        required=True,
        default=lambda self: self.env["res.company"]._company_default_get(
            "account.invoice"
        ),
    )
    site_id = fields.Many2one("it.site", "Site", required=True)
    active = fields.Boolean(default=True)
    # Counts
    access_count = fields.Integer(compute="_access_count", string="Logins")
    access_ids = fields.One2many("it.access", "equipment_id", string="Login Users")
    backup_count = fields.Integer(compute="_backup_count")
    backup_ids = fields.One2many("it.backup", "equipment_id", "Backups")
    virtual_count = fields.Integer(compute="_virtual_count")
    virtual_ids = fields.One2many("it.equipment", "virtual_parent_id", "Virtuals")
    # General Info
    identification = fields.Char(
        compute="_get_identification", string="Complete Name", store=True
    )
    name = fields.Char("Name", required=True)
    brand_id = fields.Many2one("it.equipment.brand", "Brand")
    model = fields.Char()
    partner_id = fields.Many2one(
        "res.partner", "Partner", required=True, domain="[('manage_it','=',1)]"
    )
    function_ids = fields.Many2many(
        "it.equipment.function",
        "equipment_function_rel",
        "equipment_id",
        "function_id",
        "Functions",
    )
    description = fields.Char("Description", required=False)
    note = fields.Text("Note")
    image = fields.Binary(
        "Photo",
        default=_get_default_image,
        help="Equipment Photo, limited to 1024x1024px.",
    )
    # Applications Page
    application_ids = fields.Many2many(
        "it.application",
        "equipment_application_rel",
        "equipment_id",
        "application_id",
        "Applications",
    )
    # Config Page
    equipment_type = fields.Selection(
        [
            ("bundle", "PHYSICAL"),
            ("virtual", "VIRTUAL"),
            ("product", "PRODUCT"),
            ("other", "OTHER"),
        ],
        "Equipment Type",
        required=True,
        default="bundle",
    )
    is_contracted = fields.Boolean("Contracted Service")
    is_static_ip = fields.Boolean("Static IP")
    is_partitioned = fields.Boolean("Partitions")
    is_backup = fields.Boolean("Backup")
    is_access = fields.Boolean("Credentials")
    is_os = fields.Boolean("Operating System")
    is_application = fields.Boolean("Application")
    is_config_file = fields.Boolean("Store Config Files")
    # Config Page - Functions
    function_fileserver = fields.Boolean("File Server")
    function_host = fields.Boolean("Host")
    function_router = fields.Boolean("Router")
    function_database = fields.Boolean("Database Server")
    function_vpn = fields.Boolean("VPN Server")
    function_firewall = fields.Boolean("Firewall & Proxy Server")
    function_dhcp = fields.Boolean("DHCP Server")
    function_ap = fields.Boolean("Access Point")
    # Audit Page
    pin = fields.Char("PIN", default=_get_pin, readonly=True, required=True, copy=False)
    # Worklogs Page
    worklog_ids = fields.One2many(
        "it.equipment.worklog", "equipment_id", "Worklogs on this equipment"
    )
    # Contract Page
    contract_partner_id = fields.Many2one("res.partner", "Contractor")
    contract_client_number = fields.Char("Client Nummber")
    contract_owner = fields.Char("Titular")
    contract_nif = fields.Char("NIF")
    contract_direction = fields.Char("Invoice Direction")
    # Virtual Machine Page
    virtual_parent_id = fields.Many2one(
        "it.equipment", "Virtual Machine", domain="[('function_host','=',1)]"
    )
    virtual_memory_amount = fields.Char("Memory")
    virtual_disk_amount = fields.Char("Disk Size")
    virtual_processor_amount = fields.Char("Number of Processor")
    virtual_network_amount = fields.Char("Number of Network")
    # Partition Page
    partitions_ids = fields.One2many(
        "it.equipment.partition", "equipment_id", "Partitions on this equipment"
    )
    # Router Page
    router_dmz = fields.Char("DMZ")
    router_forward_ids = fields.One2many(
        "it.equipment.forward", "equipment_id", "Forward Rules"
    )
    # "router_nat_ids": fields.one2many(
    #    "it.equipment.nat", "equipment_id", "NAT Rules"
    # ),
    router_rules_ids = fields.One2many(
        "it.equipment.rule", "equipment_id", "Firewall Rules"
    )
    # Network Configuration Page
    equipment_network_ids = fields.One2many(
        "it.equipment.network", "equipment_id", "Network on this equipment"
    )
    # Product Page
    product_id = fields.Many2one("product.product", "Product")
    product_serial_number = fields.Char("Serial Number")
    product_warranty = fields.Char("Warranty")
    product_buydate = fields.Date("Buy Date")
    product_note = fields.Text("Product Note")
    # DC Page
    function_dc = fields.Boolean("Domain Controller")
    ad_service_id = fields.Many2one("it.service.ad", "Active Directory Service")
    # Fileserver Page
    equipment_mapping_ids = fields.One2many(
        "it.equipment.mapping", "equipment_id", "Network Shares"
    )
    # OS Page
    os_name = fields.Char("OS Name")
    os_company = fields.Char("OS Company")
    os_version = fields.Char("OS Version")
    # DHCP Server Page
    dhcp_service_id = fields.Many2one("it.service.dhcp4", "DHCP Service")
    # Access Point Page
    wireless_service_id = fields.Many2one("it.service.wireless", "Wireless Service")
    # Database Page
    db_ids = fields.One2many("it.equipment.db", "equipment_id", "Databases")
    # Firewall & Proxy Page
    # "firewall_filter_ids": fields.one2many(
    #    "it.equipment.firewallfilter", "equipment_id", "Firewall Filters"
    # ),
    proxy_service_id = fields.Many2one("it.service.proxy", "Proxy Service")
    use_proxy = fields.Boolean("Use Proxy")
    proxy_client_config_id = fields.Many2one(
        "it.equipment.network.proxy", "Proxy Configuration"
    )
    # VPN Page
    vpn_service_id = fields.Many2one("it.service.vpn", "VPN Service")
    # Store Config File Page
    configuration_file_ids = fields.One2many(
        "it.equipment.configuration", "equipment_id", "Configuration Files"
    )

    _sql_constraints = [("name_uniq", "unique(pin)", "PIN must be unique!")]
