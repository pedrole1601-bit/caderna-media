import unittest,copy,importlib.util,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('qa',ROOT/'scripts/verify_design_qa.py')
qa=importlib.util.module_from_spec(spec);spec.loader.exec_module(qa)
DIR=ROOT/'media'
def load():return json.loads((DIR/'caderna-enem-2026-001-v2-qa.json').read_text())
class VisualQaTests(unittest.TestCase):
    def test_real_exports(self):
        self.assertEqual(qa.validate(load(),DIR)['result'],'PASS_TECHNICAL_ONLY')
    def test_headline_independent_sizes_are_rejected(self):
        x=load();next(b for b in x['text_blocks'] if b['label']=='headline_line_2')['size']=95
        with self.assertRaises(qa.VisualGateError):qa.validate(x,DIR)
    def test_headline_inconsistent_margin_is_rejected(self):
        x=load();next(b for b in x['text_blocks'] if b['label']=='headline_line_2')['anchor_x']=60
        with self.assertRaises(qa.VisualGateError):qa.validate(x,DIR)
    def test_headline_vertical_collision_is_rejected(self):
        x=load();b=next(b for b in x['text_blocks'] if b['label']=='headline_line_2')
        a=b['bbox'];b['bbox']=[a[0],1000,a[2],1090]
        with self.assertRaises(qa.VisualGateError):qa.validate(x,DIR)
    def test_unapproved_cannot_be_fake_approved(self):
        x=load();x['human_approved']=True
        with self.assertRaises(qa.VisualGateError):qa.validate(x,DIR)
if __name__=='__main__':unittest.main()
