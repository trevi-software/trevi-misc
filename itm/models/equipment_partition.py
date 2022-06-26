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


from odoo import fields, models


class ItEquipmentPartition(models.Model):
    _name = "itm.equipment.partition"
    _description = "Partition"

    equipment_id = fields.Many2one("itm.equipment", "Asset", ondelete="cascade")
    name = fields.Char(
        "Identificator",
        required=True,
        help="Identificator or flag for ease identification",
    )
    disks = fields.Char(help="Disks")
    type = fields.Char(help="Disk storage controllers")
    format = fields.Char(help="Partition format type")
    mount_ids = fields.One2many(
        "itm.equipment.partition.mount",
        "partition_id",
        "Mount on this partition",
        help="Mount partition",
    )


class ItEquipmentPartitionMount(models.Model):
    _name = "itm.equipment.partition.mount"
    _description = "Partition Mounts"

    partition_id = fields.Many2one(
        "itm.equipment.partition", "Partition", ondelete="cascade"
    )
    name = fields.Char(required=True)
    size = fields.Char()
