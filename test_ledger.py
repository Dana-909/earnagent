import unittest
from ledger import transition,verified_total
class LedgerTests(unittest.TestCase):
 def test_reward_not_revenue(self):
  self.assertEqual(verified_total([{"state":"discovered","reward_usd":100}]),0)
 def test_payment_needs_evidence(self):
  with self.assertRaises(ValueError): transition({"state":"accepted"},"paid")
 def test_paid_counts(self):
  r=transition({"state":"accepted"},"paid",{"amount_usd":25,"ref":"tx"})
  self.assertEqual(verified_total([r]),25)
 def test_no_regression(self):
  with self.assertRaises(ValueError): transition({"state":"paid"},"verified")
if __name__=="__main__": unittest.main()
