import unittest
import sales_engine

class SalesEngineTests(unittest.TestCase):
    def test_product_plan_is_unique_and_positive(self):
        slugs=[p["slug"] for p in sales_engine.PRODUCTS_PLAN]
        self.assertEqual(len(slugs),len(set(slugs)))
        self.assertTrue(all(float(p["price"])>0 for p in sales_engine.PRODUCTS_PLAN))
        self.assertTrue(all(p["kind"] in ("html","md","svg") for p in sales_engine.PRODUCTS_PLAN))

if __name__=="__main__":
    unittest.main()
