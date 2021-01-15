odoo.define('crm_tbm_advanced.user_menu', function (require) {
    "use strict";

    var UserMenu = require('web.UserMenu');

    UserMenu.include({
        start: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                self.$el.on('click', 'a[data-reset-tour]', function (ev) {
                    ev.preventDefault();
                    var f = self['_onMenuResetTour']
                    f.call(self, $(this));
                });
            });
        },
        _onMenuResetTour: function (ev) {
            var self = this;
            var session = this.getSession();
            return this._rpc({
                model: 'web_tour.tour',
                method: 'reset_tour',
                args: [session.uid, ],
            }).then(function (result) {
                self.do_action({
                    type: 'ir.actions.client',
                    res_model: 'res.users',
                    tag: 'reload_context',
                    target: 'current',
                });
            });
        },
    })
});