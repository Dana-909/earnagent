import unittest
from worker import classify, make_plan, fingerprint

class WorkerTests(unittest.TestCase):
    def test_docs(self):
        self.assertEqual(classify({"title":"Fix README typo","body":""}),"docs_edit")
    def test_unknown_blocked(self):
        p=make_plan({"title":"Build entire mobile app","body":"","eligible":True,"reward_usd":100,"url":"x"})
        self.assertIn("unsupported_task_kind",p["blockers"])
    def test_quality_block(self):
        p=make_plan({"title":"Fix docs","body":"","eligible":False,"reward_usd":20,"url":"y"})
        self.assertIn("quality_gate_failed",p["blockers"])
    def test_duplicate(self):
        c={"title":"Fix docs","body":"","eligible":True,"reward_usd":20,"url":"z"}
        self.assertIn("duplicate",make_plan(c,[fingerprint(c)])["blockers"])

    def test_live_candidate_contract(self):
        c={"title":"Documentation bounty $25","body":"Update README documentation","url":"https://example.invalid/1","reward_usd":25,"eligible":True}
        p=make_plan(c)
        self.assertEqual(p["state"],"planned")
        self.assertEqual(p["kind"],"docs_edit")
        self.assertEqual(p["submission"],"disabled_until_payout_and_submission_ready")

if __name__=="__main__": unittest.main()
