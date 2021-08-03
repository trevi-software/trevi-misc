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
    _name = "it.equipment.partition"
    _description = "Equipment Partition"

    equipment_id = fields.Many2one("it.equipment", "Equipment", ondelete="cascade")
    name = fields.Char("Identificator", required=True)
    disks = fields.Char(help="Disks splitted by , ")
    type = fields.Char()
    format = fields.Char()
    mount_ids = fields.One2many(
        "it.equipment.partition.mount", "partition_id", "Mount on this partition"
    )


class ItEquipmentPartitionMount(models.Model):
    _name = "it.equipment.partition.mount"
    _description = "Partition Mounts"

    partition_id = fields.Many2one(
        "it.equipment.partition", "Partition", ondelete="cascade"
    )
    name = fields.Char(required=True)
    size = fields.Char()
