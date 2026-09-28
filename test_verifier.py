import unittest
from verifier import verify
class VerifierTests(unittest.TestCase):
    def test_good(self):
        p={"files":[{"path":"README.md","bytes":120}],"acceptance_criteria_checked":True,"tests_passed":True}
        self.assertTrue(verify(p)["verified"])
    def test_secret_block(self):
        p={"files":[{"path":".env","bytes":20}],"acceptance_criteria_checked":True,"tests_passed":True}
        self.assertFalse(verify(p)["verified"])
    def test_tests_required(self):
        p={"files":[{"path":"README.md","bytes":20}],"acceptance_criteria_checked":True,"tests_passed":False}
        self.assertFalse(verify(p)["verified"])
if __name__=="__main__": unittest.main()
