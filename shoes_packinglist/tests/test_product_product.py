from odoo.tests.common import TransactionCase


class TestProductProductFields(TransactionCase):

    def test_width_length_high_on_product_product(self):
        product = self.env["product.product"].create(
            {"name": "Test Shoe", "type": "consu"}
        )
        product.write({"width_length_high": "25×30×50"})
        self.assertEqual(product.width_length_high, "25×30×50")

    def test_width_length_high_independent_per_variant(self):
        tmpl = self.env["product.template"].create(
            {
                "name": "Test Shoe Multi",
                "type": "consu",
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": self.env["product.attribute"]
                            .create({"name": "Size"})
                            .id,
                            "value_ids": [
                                (
                                    0,
                                    0,
                                    {"name": "36"},
                                ),
                                (
                                    0,
                                    0,
                                    {"name": "37"},
                                ),
                            ],
                        },
                    )
                ],
            }
        )
        v1, v2 = tmpl.product_variant_ids
        v1.write({"width_length_high": "25×30×50"})
        v2.write({"width_length_high": "26×31×51"})
        self.assertEqual(v1.width_length_high, "25×30×50")
        self.assertEqual(v2.width_length_high, "26×31×51")
