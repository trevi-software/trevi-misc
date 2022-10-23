/** @odoo-module **/

/**
 * Copyright 2021,2022 TREVI Software <support@trevi.et>
 * Copyright 2018 Modoolar <info@modoolar.com>
 * License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
 *
 */

import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";
import {CharField} from "@web/views/fields/char/char_field";

const {onWillStart, useState} = owl;

export class PasswordCharField extends CharField {
    setup() {
        super.setup();
        this.orm = useService("orm");
        this.state = useState({is_visible: 0});
        this.ciphertext = "";
        this.is_edited = 0;

        onWillStart(() => {
            this.ciphertext = this.props.value;
        });
    }

    onClick(event) {
        event.preventDefault();
        event.stopPropagation();
        if (this.state.is_visible === 0) {
            // when the user is editing the password show that instead
            if (this.input.el.value != this.ciphertext) {
                this.is_edited = 1;
                this.props.isPassword = 0;
                this.state.is_visible = 1;
            } else {
                this.show_decrypted_password();
            }
        } else {
            if (this.is_edited == 0) {
                this.props.value = this.ciphertext;
            }
            this.props.isPassword = 1;
            this.state.is_visible = 0;
        }
    }

    async show_decrypted_password() {
        var me = this;
        return this.orm
            .call("itm.access", "decrypt_password_as_string", [
                this.props.record.data.id,
            ])
            .then(function (plaintext) {
                me.props.value = plaintext;
                me.props.isPassword = 0;
                me.state.is_visible = 1;
            });
    }
}
PasswordCharField.template = "itm.PasswordCharField";
registry.category("fields").add("password_char", PasswordCharField);
