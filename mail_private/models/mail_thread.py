# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from lxml import etree
from odoo import api, fields, models
from odoo.osv.orm import setup_modifiers


class MailThread(models.AbstractModel):

    _inherit = 'mail.thread'

    allow_private = fields.Boolean(
        compute='_compute_allow_private',
    )

    def _compute_allow_private(self):
        groups = self.env['mail.security.group'].search([
            ('model_ids.model', '=', self._name),
            ])
        users = groups.mapped('group_ids.users')
        for record in self:
            record.allow_private = groups and self.env.user in users

    @api.model
    def get_message_security_groups(self):
        return self.env['mail.security.group'].search([
            ('model_ids.model', '=', self._name),
            ('group_ids.users', '=', self.env.user.id)
        ])._get_security_groups()

    @api.model
    def fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        res = super().fields_view_get(
            view_id=view_id,
            view_type=view_type,
            toolbar=toolbar,
            submenu=submenu,
        )
        if view_type == 'form':
            doc = etree.XML(res['arch'])
            for node in doc.xpath("//field[@name='message_ids']/.."):
                element = etree.Element(
                    'field',
                    attrib={
                        "name": "allow_private",
                        "invisible": "1",
                    }
                )
                setup_modifiers(element)
                node.insert(0, element)
            res['arch'] = etree.tostring(doc, encoding='unicode')
        return res
