# Copyright 2024 Jarsa (https://www.jarsa.com/)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestExchangeMoveAnalytic(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.analytic_plan = cls.env["account.analytic.plan"].create(
            {"name": "Test Plan"}
        )
        cls.analytic_account = cls.env["account.analytic.account"].create(
            {
                "name": "Test Analytic Account",
                "plan_id": cls.analytic_plan.id,
            }
        )

    def test_exchange_move_vals_get_invoice_analytic(self):
        invoice = self.init_invoice(
            "out_invoice", products=self.product_a, invoice_date="2024-01-01"
        )
        invoice.invoice_line_ids.analytic_distribution = {
            str(self.analytic_account.id): 100
        }
        invoice.action_post()
        receivable_line = invoice.line_ids.filtered(
            lambda line: line.account_id.account_type == "asset_receivable"
        )
        res = receivable_line._prepare_exchange_difference_move_vals(
            [{"amount_residual": 100.0}]
        )
        line_vals = [command[2] for command in res["move_values"]["line_ids"]]
        self.assertEqual(
            line_vals[1]["analytic_distribution"],
            {str(self.analytic_account.id): 100},
            "The exchange gain/loss line must take the analytic distribution from the invoice lines.",
        )

    def test_exchange_move_vals_no_analytic(self):
        invoice = self.init_invoice(
            "out_invoice", products=self.product_a, invoice_date="2024-01-01"
        )
        invoice.action_post()
        receivable_line = invoice.line_ids.filtered(
            lambda line: line.account_id.account_type == "asset_receivable"
        )
        res = receivable_line._prepare_exchange_difference_move_vals(
            [{"amount_residual": 100.0}]
        )
        line_vals = [command[2] for command in res["move_values"]["line_ids"]]
        self.assertNotIn(
            "analytic_distribution",
            line_vals[1],
            "Without analytic on the invoice the exchange line must not set a distribution.",
        )
