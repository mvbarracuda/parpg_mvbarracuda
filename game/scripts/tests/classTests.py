import unittest
from scripts.objects.containers import WoodenCrate

class WoodenCrateTest(unittest.TestCase):
    def setUp(self):
        self.crate = WoodenCrate(ID='crate01')
        self.crate2 = WoodenCrate(ID='crate02', locked=False)

    def test_creation(self):
        self.assertEqual(self.crate.ID, 'crate01')
        self.assertEqual(self.crate.name, 'Wooden Crate')
        self.assertEqual(self.crate.text, 'A battered down crate')
        self.assertEqual(self.crate.gfx, \
                {'map': 'objects/objects/crate/image.png'})
        self.assertEqual(self.crate.coords, (0.0, 0.0))
        self.assertEqual(self.crate.map_id, None)
        self.assertEqual(self.crate.blocking, True)
        self.assertEqual(self.crate.is_open, True)
        self.assertEqual(self.crate.locked, True)
        self.assertEqual(self.crate.scripts, {})

        self.assertEqual(self.crate2.ID, 'crate02')
        self.assertEqual(self.crate2.locked, False)

    # can't test containing functionality...there are no containable objects
   
    def test_lockable(self):
        self.crate2.lock()
        self.assertEqual(self.crate2.locked, True)
        self.crate2.unlock()
        self.assertEqual(self.crate2.locked, False)

if __name__=='__main__':
    unittest.main()
