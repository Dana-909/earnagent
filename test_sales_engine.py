import unittest
import sales_engine

class SalesEngineTests(unittest.TestCase):
    def test_product_plan_is_unique_and_positive(self):
        slugs=[p["slug"] for p in sales_engine.PRODUCTS_PLAN]
        self.assertEqual(len(slugs),len(set(slugs)))
        self.assertTrue(all(float(p["price"])>0 for p in sales_engine.PRODUCTS_PLAN))
        self.assertTrue(all(p["kind"] in ("html","md","svg") for p in sales_engine.PRODUCTS_PLAN))

    def test_lemon_variant_fallback_is_deterministic(self):
        import os
        old=os.environ.get("LEMONSQUEEZY_API_KEY")
        os.environ["LEMONSQUEEZY_API_KEY"]="test-key"
        original=sales_engine.lemon_api_get
        def fake(path,key):
            if path.startswith("stores"): return {"data":[{"id":"1","attributes":{"name":"Demo","slug":"demo-store"}}]}
            if path.startswith("products"): return {"data":[{"id":"10","attributes":{"slug":"freelancer-invoice-kit","name":"Freelancer","status":"published","buy_now_url":None,"price":700}}]}
            if path.startswith("variants"): return {"data":[{"id":"77","attributes":{"status":"published"},"relationships":{"product":{"data":{"id":"10"}}}]}
            if path.startswith("orders"): return {"data":[]}
            return {"data":[]}
        sales_engine.lemon_api_get=fake
        try:
            state=sales_engine.lemon_commercial_state()
            self.assertEqual(state["published_products"][0]["variant_id"],"77")
            self.assertEqual(state["published_products"][0]["buy_now_url"],"https://demo-store.lemonsqueezy.com/checkout/buy/77")
        finally:
            sales_engine.lemon_api_get=original
            if old is None: os.environ.pop("LEMONSQUEEZY_API_KEY",None)
            else: os.environ["LEMONSQUEEZY_API_KEY"]=old

    def test_optimizer_has_product_sales_mapping(self):
        import sales_optimizer
        self.assertEqual(sales_optimizer.PRODUCT_TO_NICHE["Freelancer Invoice & Quote Kit"],"local-service-admin")

    def test_optimizer_module_imports(self):
        import sales_optimizer
        self.assertGreaterEqual(len(sales_optimizer.NICHES), 10)

if __name__=="__main__":
    unittest.main()
