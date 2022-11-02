/** @odoo-module **/

/**
 * Copyright 2021,2022 TREVI Software <support@trevi.et>
 * Copyright 2018 Modoolar <info@modoolar.com>
 * License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
 *
 */

import {CharField} from "@web/views/fields/char/char_field";
import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";

const {onMounted, onWillUnmount, onWillStart, onWillUpdateProps, useRef, useState} =
    owl;

export class PasswordCharField extends CharField {
    setup() {
        super.setup();
        this.notification = useService("notification");
        this.inputRef = useRef("input");
        this.orm = useService("orm");
        this.state = useState({
            is_visible: 0,
            name: this.env.config.getDisplayName(),
        });
        this.cbRef = useRef("clipboard-btn");
        this.ciphertext = "";
        this.is_edited = 0;

        onWillStart(async () => {
            this.ciphertext = this.props.value;
            try {
                this.plaintext = await this.decrypt_password();
            } catch (err) {
                console.log("Failed to decrypt password.");
                console.log(err);
            }
        });

        onWillUpdateProps((nextProps) => this.willUpdateProps(nextProps));

        onMounted(() => {
            var $clipboardBtn =
                this.cbRef.el.getElementsByClassName("o_clipboard_button");
            var me = this;
            // eslint-disable-next-line no-undef
            var clipboard = new ClipboardJS($clipboardBtn, {
                text: function () {
                    return me.choosePasswordText();
                },
            });
            this.clipboard = clipboard;
        });

        onWillUnmount(async () => {
            this.clipboard.destroy();
        });
    }

    async willUpdateProps(nextProps) {
        // Set the ciphertext if changed.
        // FIXME: this is not optimal, maybe we can hook the manual save instead?
        if (
            this.props.record.data.create_date !== false &&
            this.props.value !== this.ciphertext
        ) {
            if (this.is_edited === 1) {
                this.ciphertext = nextProps.value;
                this.plaintext = await this.decrypt_password();
            }
        }

        if (nextProps.value !== this.ciphertext) {
            this.is_edited = 1;
        } else if (this.is_edited === 1) {
            this.is_edited = 0;
        }
    }

    choosePasswordText() {
        var txt = this.plaintext;
        if (this.is_edited === 1) {
            txt = this.props.value;
        }
        this.notification.add(this.env._t("Password copied to clipboard"), {
            title: this.state.name,
            type: "info",
        });
        return txt;
    }

    onClickShowPassword() {
        if (this.state.is_visible === 0) {
            // State: password is NOT visible

            // If the user is editing the password show that, otherwise
            // show decrypted password.
            if (this.is_edited === 1) {
                this.props.isPassword = 0;
                this.state.is_visible = 1;
            } else {
                this.show_decrypted_password();
            }
        } else {
            // State: password is visible
            if (this.is_edited === 0) {
                // We do this to show the same number of '*' as before
                this.props.value = this.ciphertext;
            }
            this.props.isPassword = 1;
            this.state.is_visible = 0;
        }
    }

    decrypt_password() {
        if (
            this.props.record.data.create_date === false ||
            this.props.value === "" ||
            this.props.value === false
        ) {
            return "";
        }
        return this.orm
            .call("itm.access", "decrypt_password_as_string", [
                this.props.record.data.id,
            ])
            .then(function (plaintext) {
                return plaintext;
            });
    }

    async show_decrypted_password() {
        var plaintext = await this.decrypt_password();
        this.props.value = plaintext;
        this.props.isPassword = 0;
        this.state.is_visible = 1;
    }
}
PasswordCharField.template = "itm.PasswordCharField";
registry.category("fields").add("password_char", PasswordCharField);
