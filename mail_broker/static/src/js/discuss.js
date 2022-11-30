odoo.define("mail_broker/static/src/discuss.js", function (require) {
    "use strict";

    const Discuss = require("mail/static/src/components/discuss/discuss.js");
    const DiscussSidebar = require("mail/static/src/components/discuss_sidebar/discuss_sidebar.js");
    const DiscussSidebarItem = require("mail/static/src/components/discuss_sidebar_item/discuss_sidebar_item.js");
    const useShouldUpdateBasedOnProps = require("mail/static/src/component_hooks/use_should_update_based_on_props/use_should_update_based_on_props.js");
    const useStore = require("mail/static/src/component_hooks/use_store/use_store.js");
    const {Component} = owl;

    class DiscussSidebarBrokerItem extends Component {
        constructor(...args) {
            super(...args);
            useShouldUpdateBasedOnProps();
            useStore((props) => {
                const thread = this.env.models["mail.broker.channel"].get(
                    props.threadLocalId
                );
                return {
                    thread,
                };
            });
        }
        get discuss() {
            return this.env.messaging && this.env.messaging.discuss;
        }
        get thread() {
            return this.env.models["mail.broker.channel"].get(this.props.threadLocalId);
        }
        _onClick() {
            this.thread.open();
        }
    }
    Object.assign(DiscussSidebarBrokerItem, {
        components: DiscussSidebarItem.components,
        props: DiscussSidebarItem.props,
        template: "mail_broker.DiscussSidebarItem",
    });

    class DiscussSidebarBroker extends Component {
        constructor(...args) {
            super(...args);
            this.mailBroker = this.env.models["mail.broker"].get(this.props.brokerId);
        }
        _onClickChannelAdd() {}
        get quickSearchOrderedAndPinnedBrokerChannels() {
            return this.env.models["mail.broker.channel"].all(
                (channel) => channel.broker_id === this.mailBroker.id
            );
            return this.env.models["mail.thread"]
                .all(
                    (thread) =>
                        thread.channel_type === "channel" &&
                        thread.isPinned &&
                        thread.model === "mail.channel"
                )
                .sort((c1, c2) => {
                    if (c1.displayName && !c2.displayName) {
                        return -1;
                    } else if (!c1.displayName && c2.displayName) {
                        return 1;
                    } else if (
                        c1.displayName &&
                        c2.displayName &&
                        c1.displayName !== c2.displayName
                    ) {
                        return c1.displayName.toLowerCase() <
                            c2.displayName.toLowerCase()
                            ? -1
                            : 1;
                    }
                    return c1.id - c2.id;
                });
        }
    }
    Object.assign(DiscussSidebarBroker, {
        components: Object.assign(DiscussSidebar.components, {
            DiscussSidebarBrokerItem,
        }),
        props: {
            brokerId: String,
        },
        template: "mail_broker.DiscussSidebarBroker",
    });

    class BrokerDiscussSidebar extends DiscussSidebar {
        get mailBrokers() {
            return this.env.models["mail.broker"].all();
        }
    }
    Object.assign(BrokerDiscussSidebar, {
        components: Object.assign(DiscussSidebar.components, {DiscussSidebarBroker}),
        props: DiscussSidebar.props,
        template: "mail_broker.DiscussSidebar",
    });

    class NewDiscuss extends Discuss {}
    Object.assign(NewDiscuss, {
        components: Object.assign({}, Discuss.components, {
            DiscussSidebar: BrokerDiscussSidebar,
        }),
        props: Discuss.props,
        template: Discuss.template,
    });
    return NewDiscuss;
});
