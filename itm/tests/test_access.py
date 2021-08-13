# Copyright (C) 2021 TREVI Software
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


import base64

from cryptography.fernet import Fernet

from odoo.tests.common import TransactionCase


class TestAccess(TransactionCase):
    def setUp(self):
        super().setUp()

        self.ItAccess = self.env["it.access"]
        self.ItSite = self.env["it.site"]
        self.defaultSite = self.ItSite.create({"name": "site"})

        # Prime salt and decryption password creation
        self.ItAccess.create(
            {"name": "a", "password": "a", "site_id": self.defaultSite.id}
        )

    def _decrypt(self, ciphertext):
        key = self.ItAccess.get_urlsafe_key()
        f = Fernet(key)

        token = base64.urlsafe_b64decode(ciphertext)
        plaintext = f.decrypt(token).decode()
        return plaintext

    def test_change_password(self):
        """Changing password results in encrypted version of new password"""

        cred = self.ItAccess.create(
            {"name": "a", "password": "123", "site_id": self.defaultSite.id}
        )
        self.assertEqual("123", self._decrypt(cred.password))
        cred.write({"password": "456"})
        self.assertEqual("456", self._decrypt(cred.password))
