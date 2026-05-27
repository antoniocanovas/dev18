"""
Enhanced tests for the pnt_product_ean_barcode module in Odoo 18.
These cover business logic, view loading, and field extensions.
"""

from odoo.tests.common import TransactionCase, tagged


@tagged("pnt")
class TestEANBarcode(TransactionCase):
    at_install = True
    post_install = True

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category_model = cls.env["product.category"]
        cls.sequence_model = cls.env["ir.sequence"]
        cls.product_tmpl_model = cls.env["product.template"]
        cls.product_model = cls.env["product.product"]

    def test_no_ean_if_not_required(self):
        """Products in categories without EAN requirement should have empty barcode."""
        categ = self.category_model.create({"name": "NoEAN", "pnt_ean_required": False})
        tmpl = self.product_tmpl_model.create(
            {"name": "NoEANProd", "categ_id": categ.id}
        )
        variant = self.product_model.search(
            [("product_tmpl_id", "=", tmpl.id)], limit=1
        )
        self.assertFalse(variant.barcode)

    def test_sequence_increment_behavior(self):
        """Sequence _next returns prefix + incrementing number."""
        seq = self.sequence_model.create(
            {
                "name": "IncTest",
                "code": "pnt.product.ean.code",
                "prefix": "000000000001",
                "padding": 0,
                "number_next_actual": 1,
            }
        )
        first = seq._next()
        second = seq._next()
        self.assertNotEqual(first, second)
        self.assertTrue(first.startswith(seq.prefix))
        self.assertTrue(second.startswith(seq.prefix))
        self.assertTrue(first.endswith("1"), f"Expected suffix '1', got {first}")
        self.assertTrue(second.endswith("2"), f"Expected suffix '2', got {second}")

    def test_model_fields_existence(self):
        """Check that custom fields exist on sequence and product models."""
        seq_fields = self.sequence_model.fields_get()
        self.assertIn("pnt_ean14_prefix", seq_fields)
        tmpl_fields = self.product_tmpl_model.fields_get()
        self.assertIn("pnt_ean_required", tmpl_fields)

    def test_view_loading_and_architecture(self):
        """Ensure the custom sequence form view is loaded and valid XML."""
        view = self.env.ref(
            "pnt_product_ean_barcode.pnt_sequence_view", raise_if_not_found=True
        )
        self.assertEqual(view.model, "ir.sequence")
        self.assertIn("pnt_ean14_prefix", view.arch_db)
        self.assertIn("number_next_actual", view.arch_db)
