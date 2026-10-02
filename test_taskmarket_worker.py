import unittest
from pathlib import Path
from taskmarket_worker import make_umbrella, make_bubble, make_spirals, verify

class TaskmarketWorkerTests(unittest.TestCase):
    def setUp(self):
        self.d=Path("deliverables"); self.d.mkdir(exist_ok=True)
    def test_umbrella(self):
        p=self.d/"test_umbrella.html"; make_umbrella(p); self.assertTrue(verify("umbrella",p)["verified"])
    def test_bubble(self):
        p=self.d/"test_bubble.svg"; make_bubble(p); self.assertTrue(verify("bubble",p)["verified"])
    def test_spirals(self):
        p=self.d/"test_spirals.svg"; make_spirals(p); self.assertTrue(verify("spirals",p)["verified"])

if __name__=="__main__": unittest.main()
