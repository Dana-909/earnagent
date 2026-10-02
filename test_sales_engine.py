import unittest, tempfile, os
from pathlib import Path
import sales_engine

class SalesEngineTests(unittest.TestCase):
    def test_product_plan_has_unique_slugs_and_prices(self):
        slugs=[p["slug"] for p in sales_engine.PRODUCTS_PLAN]
        self.assertEqual(len(slugs),len(set(slugs)))
        self.assertTrue(all(float(p["price"])>0 for p in sales_engine.PRODUCTS_PLAN))
    def test_product_generation_is_local(self):
        with tempfile.TemporaryDirectory() as td:
            old=sales_engine.PRODUCTS
            try:
                sales_engine.PRODUCTS=Path(td)
                sales_engine.PRODUCTS.mkdir()
                p=sales_engine.PRODUCTS_PLAN[0]
                out=sales_engine.write_product(p)
                self.assertTrue(out.exists())
                self.assertGreater(out.stat().st_size,100)
            finally:
                sales_engine.PRODUCTS=old

if __name__=="__main__":
    unittest.main()
