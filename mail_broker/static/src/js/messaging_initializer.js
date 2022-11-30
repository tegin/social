odoo.define("mail_broker/static/src/js/messaging_initializer.js", function (require) {
    "use strict";
    const {
        registerInstancePatchModel,
        registerFieldPatchModel,
    } = require("mail/static/src/model/model_core.js");
    const {many2one} = require("mail/static/src/model/model_field.js");

    registerInstancePatchModel(
        "mail.messaging_initializer",
        "mail/static/src/models/messaging_initializer/messaging_initializer.js",
        {
            async _init({broker_slots, broker_channel_slots}) {
                _.each(broker_slots, (broker_slot) =>
                    this.env.models["mail.broker"].insert(
                        Object.assign({model: "mail.broker"}, broker_slot)
                    )
                );
                _.each(broker_channel_slots, (broker_channel_slot) =>
                    this.env.models["mail.broker.channel"].insert(
                        Object.assign(
                            {model: "mail.broker.channel"},
                            broker_channel_slot
                        )
                    )
                );
                return this._super(...arguments);
            },
        }
    );
    registerInstancePatchModel(
        "mail.discuss",
        "mail/static/src/models/discuss/discuss.js",
        {
            async openBrokerChannel(thread) {
                this.update({
                    brokerChannel: [["link", thread]],
                });
                this.focus();
                this.env.bus.trigger("do-action", {
                    action: "mail.action_discuss",
                    options: {
                        active_id: this.threadToActiveId(this),
                        clear_breadcrumbs: false,
                        on_reverse_breadcrumb: () => this.close(),
                    },
                });
            },
        }
    );

    registerFieldPatchModel(
        "mail.discuss",
        "mail/static/src/models/discuss/discuss.js",
        {
            brokerChannel: many2one("mail.broker.channel"),
        }
    );
});
