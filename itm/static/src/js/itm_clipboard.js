/* @odoo-module */

import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";

/**
 * Copyright 2021,2022 TREVI Software <support@trevi.et>
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
 *
 */

const {Component, xml, onMounted, onWillUnmount, useRef, useState} = owl;

export class CopyToClipboard extends Component {
    setup() {
        super.setup();
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.state = useState({name: this.env.config.getDisplayName(), plaintext: ""});
        this.cbRef = useRef("clipboard-btn");

        onMounted(async () => {
            this.state.plaintext = await this.decrypt_password();
            var $clipboardBtn =
                this.cbRef.el.getElementsByClassName("o_clipboard_button");
            // eslint-disable-next-line no-undef
            var me = this;
            var clipboard = new ClipboardJS($clipboardBtn, {
                text: function () {
                    return me.state.plaintext;
                },
            });
            this.clipboard = clipboard;
        });

        onWillUnmount(async () => {
            this.clipboard.destroy();
        });
    }

    async decrypt_password() {
        return this.orm
            .call("itm.access", "decrypt_password_as_string", [
                this.props.record.data.id,
            ])
            .then(function (plaintext) {
                return plaintext;
            });
    }

    async onClick(event) {
        event.preventDefault();
        // event.stopPropagation();
        let myprops = this.props.data;
        this.notification.add(this.env._t("Copied password to clipboard"), {
            title: this.state.name,
            type: "info",
        });
    }
}
CopyToClipboard.template = "itm.CopyToClipboard";
registry.category("view_widgets").add("copy_to_clipboard", CopyToClipboard);
