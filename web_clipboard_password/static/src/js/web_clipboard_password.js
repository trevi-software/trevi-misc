"use strict";
/**
 * Copyright 2021 TREVI Software <support@trevi.et>
 * Copyright 2018 Modoolar <info@modoolar.com>
 * License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
 *
 */

odoo.define('web_clipboard_password', function (require) {
    const InputField = require("web.basic_fields").InputField;
    const field_registry = require('web.field_registry');
    const core = require('web.core');
    const rpc = require('web.rpc')
    const _t = core._t;

    InputField.include({
        events: Object.assign({}, InputField.prototype.events, {
            'click .o_clipboard_button': '_onCopyToClipboardClick',
        }),
        init() {
            this._super.apply(this, arguments);
            this.nodeOptions.isCopyable = 'copyable' in this.attrs;

        },
        _renderEdit: function () {
            this._super.apply(this, arguments);
            if (this.nodeOptions.isCopyable) {
                this.$el.append('<a class="btn btn-default o_clipboard_button" href="#"><i class="fa fa-clipboard"/></a>');
            }
        },
        _renderReadonly() {
            this._super.apply(this, arguments);
            if (this.nodeOptions.isCopyable) {
                this.$el.append('<a class="btn btn-default o_clipboard_button" href="#"><i class="fa fa-clipboard"/></a>');
            }
        },
        _onCopyToClipboardClick(event) {
            event.preventDefault();
            event.stopPropagation();
            var my_id = this.record.data.id;
            var do_notify = this.do_notify;
            var $clipboardBtn = this.$el.find('.o_clipboard_button');

            rpc.query({
                model: 'itm.access',
                method: 'decrypt_password_as_string',
                args: [my_id]
            }).then(function (plaintext) {
                var clipboard = new ClipboardJS($clipboardBtn[0], {
                    text: function (trigger) {
                        return plaintext;
                    }
                });
                clipboard.onClick(event)
                clipboard.destroy();
                do_notify(_t("Copied password to clipboard"));
            });
        }
    });
    const CopyableInput = InputField.extend({
        init() {
            this._super.apply(this, arguments);
            this.nodeOptions.isCopyable = true;
        },
    });
    field_registry.add("copyable", CopyableInput);
    return CopyableInput;
});
