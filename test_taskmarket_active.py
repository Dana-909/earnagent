import unittest
import taskmarket_active as a
import office_fixer as f

class ActiveWorkerTests(unittest.TestCase):
    def test_safe_formats(self):
        self.assertEqual(a.kind('Create one self-contained offline HTML file'), 'html')
        self.assertEqual(a.kind('Write a short article about testing'), 'md')
    def test_blocks_external_side_effects(self):
        self.assertIsNone(a.kind('Log in to the account and send an email using an API key'))
    def test_fixer_accepts_safe_decision(self):
        fixed=f.repair({"decision":"execute","plan":"submit the self-contained artifact"},{"description":"offline artifact"},"html")
        self.assertEqual(fixed.get("fixer"),"validated")
    def test_fixer_rejects_unsafe_decision(self):
        ok,errors=f.validate({"decision":"execute","plan":"use api key to login"})
        self.assertFalse(ok)
        self.assertTrue(errors)

    def test_free_action_gate(self):
        self.assertTrue(a.free({'action':'submit','requiresPayment':False},'submit'))
        self.assertFalse(a.free({'action':'submit','requiresPayment':True},'submit'))
        self.assertFalse(a.free({'action':'submit','requiresPayment':False,'costUsd':0.001},'submit'))

if __name__=='__main__': unittest.main()