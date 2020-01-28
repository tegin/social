# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MessageAttachmentRelated(models.Model):
    _name = 'message.attachment.related'

    _log_access = False

    message_id = fields.Many2one(
        'mail.message',
        required=True,
        auto_join=True,
    )
    attachment_id = fields.Many2one(
        'ir.attachment',
        required=True
    )


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    related_message_rel_ids = fields.One2many(
        'message.attachment.related',
        auto_join=True,
        inverse_name='attachment_id'
    )
    related_message_rel_count = fields.Integer(
        store=True,
        compute='_compute_related_message_rel_count'
    )

    @api.depends('related_message_rel_ids')
    def _compute_related_message_rel_count(self):
        for rec in self:
            rec.related_message_rel_count = len(rec.related_message_rel_ids)
