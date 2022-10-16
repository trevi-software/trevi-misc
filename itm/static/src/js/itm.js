/**
 * Copyright 2021 TREVI Software <support@trevi.et>
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
 *
 */

odoo.define("itm", function (require) {
    "use strict";

    const widgetRegistry = require("web.widget_registry");
    const core = require("web.core");
    const rpc = require("web.rpc");
    const Widget = require("web.Widget");
    const _t = core._t;

    var CopyToClipboard = Widget.extend({
        template: "Copy_to_Clipboard",
        xmlDependencies: ["/itm/static/src/xml/clipboard.xml"],
        events: {
            click: "_onClick",
        },

        init: function (parent, record, nodeInfo) {
            this._super.apply(this, arguments);
            this.res_id = record.res_id;
            this.res_model = record.model;
            this.node = nodeInfo;
        },

        _onClick(event) {
            event.preventDefault();
            event.stopPropagation();
            var do_notify = this.do_notify;
            var $clipboardBtn = this.$el.find(".o_clipboard_button");

            rpc.query({
                model: this.res_model,
                method: "decrypt_password_as_string",
                args: [this.res_id],
            }).then(function (plaintext) {
                // eslint-disable-next-line no-undef
                var clipboard = new ClipboardJS($clipboardBtn[0], {
                    text: function () {
                        return plaintext;
                    },
                });
                clipboard.onClick(event);
                clipboard.destroy();
                do_notify(_t("Copied password to clipboard"));
            });
        },
    });

    widgetRegistry.add("copy_to_clipboard", CopyToClipboard);

    return CopyToClipboard;
});
