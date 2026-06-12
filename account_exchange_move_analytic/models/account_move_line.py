# Copyright 2024 Jarsa (https://www.jarsa.com/)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _prepare_exchange_difference_move_vals(
        self, amounts_list, company=None, exchange_date=None, **kwargs
    ):
        if not kwargs.get("exchange_analytic_distribution"):
            invoice_lines = self.move_id.filtered(
                lambda move: move.journal_id.type in ("sale", "purchase")
            ).line_ids.filtered("analytic_distribution")
            if invoice_lines:
                kwargs["exchange_analytic_distribution"] = invoice_lines[
                    0
                ].analytic_distribution
        return super()._prepare_exchange_difference_move_vals(
            amounts_list, company=company, exchange_date=exchange_date, **kwargs
        )
