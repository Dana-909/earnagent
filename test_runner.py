import unittest
from runner import dry_run
class RunnerTests(unittest.TestCase):
 def test_end_to_end_fail_closed(self):
  r=dry_run({"title":"Fix README typo","body":"docs","eligible":True,"reward_usd":25,"url":"x"})
  self.assertTrue(r["ok"]); self.assertEqual(r["record"]["state"],"verified")
  self.assertFalse(r["live_submission_attempted"]); self.assertEqual(r["verified_revenue_usd"],0)
if __name__=="__main__": unittest.main()
