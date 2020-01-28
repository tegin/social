import logging
from odoo import api, SUPERUSER_ID
from odoo.tools.sql import table_exists
_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    if table_exists(cr, 'message_attachment_rel'):
        cr.execute("""
            INSERT INTO
                message_attachment_related
                (
                id,
                attachment_id,
                message_id
                )
            SELECT
                nextval('message_attachment_related_id_seq'),
                attachment_id,
                message_id
            FROM
                message_attachment_rel
        """)
        cr.execute("""
            DROP TABLE message_attachment_rel
        """)

def uninstall_hook(cr, registry):
    query = """
        CREATE TABLE "{rel}" ("{id1}" INTEGER NOT NULL,
                              "{id2}" INTEGER NOT NULL,
                              UNIQUE("{id1}","{id2}"));
        COMMENT ON TABLE "{rel}" IS %s;
        CREATE INDEX ON "{rel}" ("{id1}");
        CREATE INDEX ON "{rel}" ("{id2}")
    """.format(
        rel='message_attachment_rel', id1='message_id', id2='attachment_id')
    cr.execute(
        query,
        ['RELATION BETWEEN %s AND %s' % (
            'mail_message', 'ir_attachment')])
    cr.execute("""
        INSERT INTO
            message_attachment_rel
            (
            attachment_id,
            message_id
            )
        SELECT
            attachment_id,
            message_id
        FROM
            message_attachment_related
        """)
