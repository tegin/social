# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    related_message_ids = fields.Many2many(
        'mail.message', 'message_attachment_rel',
        'attachment_id', 'message_id',
        string='Messages',
        help='Messages that are linked to the attachment'
    )
