# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from lxml import etree


class TestMailPrivate(TransactionCase):

    def setUp(self):
        super(TestMailPrivate, self).setUp()
        self.user_01 = self.env['res.users'].create({
            'name': 'user_01',
            'login': 'demo_user_01',
            'email': 'demo@demo.de',
            'notification_type': 'inbox',
        })
        self.user_02 = self.env['res.users'].create({
            'name': 'user_02',
            'login': 'demo_user_02',
            'email': 'demo2@demo.de',
            'notification_type': 'inbox',
        })
        self.user_03 = self.env['res.users'].create({
            'name': 'user_03',
            'login': 'demo_user_03',
            'email': 'demo3@demo.de',
            'notification_type': 'inbox',
        })
        self.partner = self.env['res.partner'].create({
            'name': 'Partner',
            'customer': True,
            'email': 'test@test.com',
        })
        self.group_1 = self.env['res.groups'].create({
            'name': 'DEMO GROUP 1',
            'users': [(4, self.user_01.id)],
        })
        self.group_2 = self.env['res.groups'].create({
            'name': 'DEMO GROUP 2',
            'users': [(4, self.user_02.id)],
        })
        self.message_group_1 = self.env['mail.security.group'].create({
            'name': 'GROUP 1',
            'model_ids': [(4, self.browse_ref('base.model_res_partner').id)],
            'group_ids': [(4, self.group_1.id)],
        })
        self.message_group_2 = self.env['mail.security.group'].create({
            'name': 'GROUP 2',
            'model_ids': [(4, self.browse_ref('base.model_res_partner').id)],
            'group_ids': [(4, self.group_2.id)],
        })
        self.subtypes, _ = self.env[
            'mail.message.subtype'
        ].auto_subscribe_subtypes(self.partner._name)
        self.partner.message_subscribe(
            partner_ids=self.user_01.partner_id.ids,
            subtype_ids=self.subtypes.ids,
        )
        self.partner.message_subscribe(
            partner_ids=self.user_02.partner_id.ids,
            subtype_ids=self.subtypes.ids,
        )
        self.partner.message_subscribe(
            partner_ids=self.user_03.partner_id.ids,
            subtype_ids=self.subtypes.ids,
        )

    def _get_notifications(self, message, user):
        return self.env['mail.notification'].search([
            ('mail_message_id', '=', message.id),
            ('res_partner_id', '=', user.partner_id.id),
            ('is_read', '=', False),
        ])

    def test_normal_usage(self):
        # pylint: disable: C8107
        message = self.partner.message_post(body="DEMO_01")
        self.assertTrue(
            self._get_notifications(message, self.user_01)
        )
        self.assertTrue(
            self._get_notifications(message, self.user_02)
        )
        self.assertTrue(
            self._get_notifications(message, self.user_03)
        )

    def test_private_usage(self):
        # pylint: disable: C8107
        message = self.partner.sudo(self.user_01.id).with_context(
            default_mail_group_id=self.message_group_1.id
        ).message_post(body="DEMO_01")
        self.assertFalse(
            self._get_notifications(message, self.user_02)
        )
        self.assertFalse(
            self.env['mail.message'].sudo(self.user_02.id).search([
                ('id', '=', message.id)
            ])
        )
        self.assertFalse(
            self._get_notifications(message, self.user_03)
        )

    def test_private_message_data(self):
        # pylint: disable: C8107
        message = self.partner.with_context(
            default_mail_group_id=self.message_group_1.id
        ).message_post(body="DEMO_01")
        self.assertTrue(message.message_format()[0]['private'])

    def test_message_data(self):
        # pylint: disable: C8107
        message = self.partner.message_post(body="DEMO_01")
        self.assertFalse(message.message_format()[0]['private'])

    def test_private_notification(self):
        # pylint: disable: C8107
        message = self.partner.with_context(
            default_mail_group_id=self.message_group_1.id
        ).message_post(body="DEMO_01")
        self.assertTrue(
            self._get_notifications(message, self.user_01)
        )
        self.assertEqual(
            self.env['mail.message'].sudo(self.user_01.id).search([
                ('id', '=', message.id)
            ]), message
        )
        self.assertFalse(
            self._get_notifications(message, self.user_02)
        )
        self.assertFalse(
            self.env['mail.message'].sudo(self.user_02.id).search([
                ('id', '=', message.id)
            ])
        )
        self.assertFalse(
            self._get_notifications(message, self.user_03)
        )

    def test_allow_private(self):
        self.assertTrue(
            self.partner.sudo(self.user_01.id).allow_private
        )
        self.assertTrue(
            self.partner.sudo(self.user_02.id).allow_private
        )
        view = self.partner.fields_view_get(view_type="form")
        view_element = etree.XML(view['arch'])
        self.assertTrue(view_element.xpath("//field[@name='allow_private']"))
