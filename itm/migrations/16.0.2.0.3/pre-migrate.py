# Copyright (C) 2024 Yuriy Gural <jg.gural@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if version == "16.0.2.0.2":
        cr.execute("UPDATE itm_equipment SET brand_id = brand WHERE brand_id IS NULL")
        _logger.info("Updated %s itm_equipment", cr.rowcount)
