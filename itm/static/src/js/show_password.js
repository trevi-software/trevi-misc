/**
 * Copyright 2021 TREVI Software <support@trevi.et>
 * Copyright 2018 Modoolar <info@modoolar.com>
 * License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
 *
 */

odoo.define("itm.show_password", function (require) {
  "use strict";

  const InputField = require("web.basic_fields").InputField;
  const rpc = require("web.rpc");

  var ShowPasswordInput = InputField.include({
    events: Object.assign({}, InputField.prototype.events, {
      "click .o_show_password": "_onShowPasswordClick",
      "click .o_hide_password": "_onHidePasswordClick",
    }),
    _renderReadonly() {
      this._super.apply(this, arguments);
      if (this.nodeOptions.isPassword) {
        this.$el.text("***************".padEnd(20, "\u00a0"));
        this.$el.append(
          '<a class="btn btn-default o_show_password" href="#"><i class="fa fa-eye"/></a>'
        );
      }
    },
    _onShowPasswordClick(event) {
      event.preventDefault();
      event.stopPropagation();
      var my_id = this.record.data.id;
      var obj = this;

      rpc
        .query({
          model: "itm.access",
          method: "decrypt_password_as_string",
          args: [my_id],
        })
        .then(function (plaintext) {
          obj.$el.text(plaintext.padEnd(20, "\u00a0"));
          obj.$el.append(
            '<a class="btn btn-default o_hide_password" href="#"><i class="fa fa-eye-slash"/></a>'
          );
        });
    },
    _onHidePasswordClick(event) {
      event.preventDefault();
      event.stopPropagation();
      var obj = this;

      obj.$el.text("***************".padEnd(20, "\u00a0"));
      obj.$el.append(
        '<a class="btn btn-default o_show_password" href="#"><i class="fa fa-eye"/></a>'
      );
    },
  });

  return ShowPasswordInput;
});
