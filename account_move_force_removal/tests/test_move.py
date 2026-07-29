# Copyright 2020 Tecnativa - Víctor Martínez
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html

from odoo.exceptions import UserError
from odoo.tests import Form, tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestMove(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                mail_create_nolog=True,
                mail_create_nosubscribe=True,
                mail_notrack=True,
                no_reset_password=True,
                tracking_disable=True,
            )
        )
        cls.partner = cls.env["res.partner"].create(
            {"name": "Test customer", "customer_rank": 1}
        )
        cls.billing_user = cls.env["res.users"].create(
            {
                "name": "Test billing user",
                "login": "test_billing_user",
                "groups_id": [
                    (6, 0, [cls.env.ref("account.group_account_invoice").id])
                ],
            }
        )
        cls.journal = cls.env["account.journal"].create(
            {
                "name": "Test journal",
                "type": "sale",
                "code": "TSALE",
                "company_id": cls.env.company.id,
            }
        )
        cls.product = cls.env["product.product"].create(
            {"name": "Test product", "type": "service"}
        )
        cls.company = cls.env.company
        cls.company.currency_id.active = True
        cls.income_account = cls.env["account.account"].search(
            [
                ("account_type", "=", "income_other"),
                ("company_id", "=", cls.company.id),
            ],
            limit=1,
        )

        invoice = Form(
            cls.env["account.move"].with_context(
                default_move_type="out_invoice", default_company_id=cls.env.company.id
            )
        )
        invoice.partner_id = cls.partner
        invoice.journal_id = cls.journal
        with invoice.invoice_line_ids.new() as line_form:
            line_form.name = cls.product.name
            line_form.product_id = cls.product
            line_form.quantity = 1.0
            line_form.price_unit = 10
            line_form.account_id = cls.income_account
        invoice = invoice.save()
        invoice.action_post()
        cls.invoice = invoice
        cls.invoice2 = cls.invoice.copy()
        cls.invoice2.action_post()
        cls.invoice3 = cls.invoice.copy()
        cls.invoice3.action_post()

    def test_remove_invoice_error(self):
        # Delete invoice while name isn't / and
        # user not in group_account_move_force_removal
        with self.assertRaises(UserError):
            self.invoice.with_user(self.billing_user).unlink()
        # Delete invoice (previously draft + cancel) and
        # user not in group_account_move_force_removal
        self.invoice.button_draft()
        self.invoice.button_cancel()
        with self.assertRaises(UserError):
            self.invoice.with_user(self.billing_user).unlink()
        # Delete posted invoice and
        # user in group_account_move_force_removal
        self.billing_user.groups_id += self.env.ref(
            "account_move_force_removal.group_account_move_force_removal"
        )
        with self.assertRaises(UserError):
            self.invoice3.with_user(self.billing_user).unlink()

    def test_ok_invoice_error(self):
        # Delete invoice (previously draft + cancel) and
        # user in group_account_move_force_removal
        self.invoice.button_draft()
        self.invoice.button_cancel()
        self.billing_user.groups_id += self.env.ref(
            "account_move_force_removal.group_account_move_force_removal"
        )
        self.invoice.with_user(self.billing_user).unlink()
