# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MailMessage(models.Model):
    _inherit = 'mail.message'

    related_message_rel_ids = fields.One2many(
        'message.attachment.related',
        inverse_name='message_id',
    )
    related_message_rel_count = fields.Integer(
        store=True,
        readonly=True,
        compute='_compute_related_message_rel_count'
    )
    attachment_ids = fields.Many2many(
        compute='_compute_attachments',
        inverse='_inverse_attachments',
        search='_search_attachments',
    )
    mail_group_id = fields.Many2one('mail.security.group', readonly=False)

    @api.depends('related_message_rel_ids')
    def _compute_related_message_rel_count(self):
        for rec in self:
            rec.related_message_rel_count = len(rec.related_message_rel_ids)

    @api.depends('related_message_rel_ids',
                 'related_message_rel_ids.attachment_id')
    def _compute_attachments(self):
        for record in self:
            record.attachment_ids = record.related_message_rel_ids.mapped(
                'attachment_id'
            )

    @api.multi
    def _inverse_attachments(self):
        for record in self:
            attachments = record.attachment_ids
            new_attachments = (
                set(attachments.ids) -
                set(record.mapped('related_message_rel_ids.attachment_id.id'))
            )
            unlink_attachments = record.related_message_rel_ids.filtered(
                lambda r: r.attachment_id not in attachments
            )
            data = [
                (0, 0, {'attachment_id': id}) for id in new_attachments]
            data += [
                (2, unlink.id) for unlink in unlink_attachments
            ]
            if data:
                record.write({
                    'related_message_rel_ids': data
                })

    @api.model
    def _search_attachments(self, operator, operand):
        if (operator == '=' and not operand):
            return [('related_message_rel_count', '=', 0)]
        return [('related_message_rel_ids.attachment_id', operator, operand)]

    @api.model
    def _message_read_dict_postprocess(self, messages, message_tree):
        result = super()._message_read_dict_postprocess(messages, message_tree)
        for message_dict in messages:
            message_id = message_dict.get('id')
            message = message_tree[message_id]
            message_dict['private'] = bool(message.mail_group_id)
            message_dict['mail_group_id'] = message.mail_group_id.id
            message_dict['mail_group'] = message.mail_group_id.name
        return result
