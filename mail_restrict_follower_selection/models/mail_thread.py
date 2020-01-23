from odoo import api, models
from odoo.tools.safe_eval import safe_eval


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    @api.multi
    def _message_add_suggested_recipient(
        self, result, partner=None, email=None, reason=''):
        result = super(MailThread, self)._message_add_suggested_recipient(
            result, partner=partner, email=email, reason=reason)
        for key in result:
            for partner_id, email, reason in result[key]:
                if partner_id:
                    domain = self.env[
                        'mail.wizard.invite'
                    ]._mail_restrict_follower_selection_get_domain()
                    partner = self.env['res.partner'].search(
                        [('id', '=', partner_id)] +
                        safe_eval(domain)
                    )
                    if not partner:
                        result[key].remove((partner_id, email, reason))
        return result
