odoo.define("mail_broker/static/src/js/broker_model.js", function (require) {
    "use strict";

    const {registerNewModel} = require("mail/static/src/model/model_core.js");
    const {attr} = require("mail/static/src/model/model_field.js");

    function factoryBroker(dependencies) {
        class Broker extends dependencies["mail.model"] {}
        Broker.modelName = "mail.broker";
        Broker.fields = {
            id: attr(),
            name: attr(),
        };

        return Broker;
    }
    registerNewModel("mail.broker", factoryBroker);

    function factoryBrokerChannel(dependencies) {
        class BrokerChannel extends dependencies["mail.model"] {
            async open() {
                const discuss = this.env.messaging.discuss;
                return discuss.openBrokerChannel(this);
            }
        }
        BrokerChannel.modelName = "mail.broker.channel";
        BrokerChannel.fields = {
            id: attr(),
            name: attr(),
            broker_id: attr(),
            localMessageUnreadCounter: attr(),
        };

        return BrokerChannel;
    }

    registerNewModel("mail.broker.channel", factoryBrokerChannel);
});
