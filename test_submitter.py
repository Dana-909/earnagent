import unittest
from submitter import prepare, may_submit
class SubmitterTests(unittest.TestCase):
    def test_fail_closed(self):
        e=prepare({"id":"1","product_hash":"a"},{"verified":True},{"configured":False},
                  {"automation_allowed":True,"submission_api_ready":True})
        self.assertFalse(may_submit(e)); self.assertIn("payout_not_configured",e["blockers"])
    def test_ready_only_when_all_green(self):
        e=prepare({"id":"1","product_hash":"a"},{"verified":True},{"configured":True},
                  {"automation_allowed":True,"submission_api_ready":True})
        self.assertTrue(may_submit(e))
    def test_idempotent(self):
        args=({"id":"1","product_hash":"a"},{"verified":True},{"configured":True},
              {"automation_allowed":True,"submission_api_ready":True})
        self.assertEqual(prepare(*args)["submission_id"],prepare(*args)["submission_id"])
if __name__=="__main__": unittest.main()
