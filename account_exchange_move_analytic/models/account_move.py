# Copyright 2024 Jarsa (https://www.jarsa.com/)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move.line"

    def _create_exchange_difference_move(self):
        res = super()._create_exchange_difference_move()
        if not res:
            return res
        invoice_move = self.mapped("move_id").filtered(
            lambda move: move.journal_id.type in ["sale", "purchase"]
        )
        if invoice_move:
            analytic_account = invoice_move.mapped("line_ids.analytic_account_id")
            if analytic_account:
                res.line_ids.filtered(
                    lambda line: line.account_id.user_type_id.id in [13, 15]
                ).write(
                    {
                        "analytic_account_id": analytic_account[0].id,
                    }
                )
        return res
