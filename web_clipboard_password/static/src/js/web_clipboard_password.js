"use strict";
/**
 * Copyright 2018 Modoolar <info@modoolar.com>
 * License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
 *
 */

odoo.define('web_clipboard_password', function (require) {
    const InputField = require("web.basic_fields").InputField;
    const setClipboard = require("web_clipboard_password.set_clipboard");
    const field_registry = require('web.field_registry');
    const core = require('web.core');
    const _t = core._t;

    InputField.include({
        events: Object.assign({}, InputField.prototype.events, {
            'click .copy-to-clipboard': '_onCopyToClipboardClick',
        }),
        init() {
            this._super.apply(this, arguments);
            this.nodeOptions.isCopyable = 'copyable' in this.attrs;
        },
        _renderEdit: function () {
            this._super.apply(this, arguments);
            if (this.nodeOptions.isCopyable) {
                this.$el.append('<a class="btn btn-default copy-to-clipboard" href="#"><i class="fa fa-copy"/></a>');
            }
        },
        _renderReadonly() {
            this._super.apply(this, arguments);
            if (this.nodeOptions.isCopyable) {
                this.$el.append('<a class="btn btn-default copy-to-clipboard" href="#"><i class="fa fa-copy"/></a>');
            }
        },
        _onCopyToClipboardClick(event) {
            event.preventDefault();
            event.stopPropagation();
            const value = this.$input ? this.$input.attr("value") : this.value;
            setClipboard(value);
            this.do_notify(_t("Copied to clipboard"));
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
