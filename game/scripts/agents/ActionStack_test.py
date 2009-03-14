import unittest
import sys, os, random,copy

from agent import ActionStack

class ActionStackTestCase (unittest.TestCase):
    def setUp (self):
        self.stack = ActionStack()
        
        # some vars to play with
        self.x = 5
        self.l = []
        #sample action entries
        self.sample_action = (int, ('111',), {'base':2}, int, ('1221',), {'base':3}) 
        self.sample_action_empty_kw = (int, ('1001',), {}, int, ('1221',), {}) 
        self.short_action = self.sample_action_empty_kw[:2] + \
            self.sample_action_empty_kw[3:5]
        self.sample_action_invalid_a = ('nofunc',(),{},bool, (True,),{})
        self.sample_action_invalid_s = (bool,(True,),{},'nofunc', (),{})
        
    def test_creation (self):
        self.assertEqual (self.stack.action_list,[])
        self.assertEqual (self.stack.running, False)

    def test_add_kw_args_action (self):
        self.assertRaises (ValueError, self.stack.add_kw_args_action, 
                           *self.sample_action_invalid_a)

        self.assertRaises (ValueError, self.stack.add_kw_args_action, 
                           *self.sample_action_invalid_s)
        
        self.stack.add_kw_args_action (*self.sample_action)
        self.assertEqual (self.stack.action_list[0],self.sample_action)
        
        self.stack.run()
        self.assertEqual (self.stack.running, True)
        
        self.stack.add_kw_args_action (*self.sample_action)
        self.assertEqual (len(self.stack.action_list),1)
        self.assertEqual (self.stack.running, False)
    
    def test_add_action (self):
        self.stack.add_action (*self.short_action)
        self.assertEqual (self.stack.action_list[0],self.sample_action_empty_kw)
    
    def test_remove_current_action (self):
        self.stack.add_kw_args_action (*self.sample_action)
        new_action = (self.sample_action[0],self.x + 1) + self.sample_action[2:]
        self.stack.add_kw_args_action (*new_action)
        
        self.stack.remove_current_action()
        self.assertEqual (len(self.stack.action_list),1)
        self.assertEqual (self.stack.action_list[0],new_action)
    
    
    def test_clear (self):
        num_actions = 5
        for i in range (num_actions):
            self.stack.add_kw_args_action (*self.sample_action)
        
        self.assertEqual (len(self.stack.action_list),num_actions)
        self.stack.clear()
        self.assertEqual (self.stack.action_list,[])
    
    def test_perform_action (self):
        l=[]

        perform = (l.append, (self.x,), None, ())
        self.stack.add_action (*perform)
        self.assertTrue (self.stack.run())
        self.assertEqual (l[0], self.x)
    
    def test_run (self):
        iterations = 5
        # check correct exit conditions and iteration count
        perform = (self.l.append, (self.x,), lambda x: len(x)>=iterations, (self.l,)) 
        self.stack.add_action (*perform)
        while (self.stack.run()):
            pass
        self.assertEqual (len(self.l), iterations)
        self.assertEqual (len (self.stack.action_list),0)
        
        # assert empty success functions are called just once
        self.l = []
        perform = (self.l.append, (self.x,))
        self.stack.add_action (*perform)
        self.assertTrue (self.stack.run())
        self.assertFalse (self.stack.run())
        self.assertEqual (self.l,[self.x])
    
    def test_run_random (self):
        def compare_len (x,y):
            return len(x) >=y
        # how many action items to put in the stack
        num_actions = 100
        # max number of repetitions for each non-empty action
        max_repetitions = 10
        action_part = (self.l.append, (self.x,))
        empty_success = (None, ())
        total_len = 0

        for i in xrange(num_actions):
            empty = random.choice ( (True,False))
            if empty:
                self.stack.add_action (* (action_part + empty_success))
                total_len +=1
            else:
                repetitions = random.randint(1, max_repetitions)
                total_len += repetitions
                success_part = (compare_len, (self.l,copy.copy(total_len)))
                entry = (action_part + success_part)
                self.stack.add_action (*entry)
        
        self.assertEqual (len (self.stack.action_list), num_actions)
        while (self.stack.run()):
            pass
        # check if the actions were performed exactly as many times as expected
        self.assertEqual (len(self.l), total_len)

if __name__ == '__main__':
    unittest.main()

import unittest
import sys, os

from agent import ActionStack

class ActionStackTestCase (unittest.TestCase):
    def setUp (self):
        self.stack = ActionStack()
        
        # some vars to play with
        self.x = 5
        self.l = []
        
        #sample action entries
        self.sample_action = (int, ('111',), {'base':2}, int, ('1221',), {'base':3}) 
        self.sample_action_empty_kw = (int, ('1001',), {}, int, ('1221',), {}) 
        self.short_action = self.sample_action_empty_kw[:2] + self.sample_action_empty_kw[3:5]
        self.sample_action_invalid_a = ('nofunc',(),{},bool, (True,),{})
        self.sample_action_invalid_s = (bool,(True,),{},'nofunc', (),{})
        
    def test_creation (self):
        self.assertEqual (self.stack.action_list,[])
        self.assertEqual (self.stack.running, False)

    def test_add_kw_args_action (self):
        self.assertRaises (ValueError, self.stack.add_kw_args_action, 
                           *self.sample_action_invalid_a)

        self.assertRaises (ValueError, self.stack.add_kw_args_action, 
                           *self.sample_action_invalid_s)
        
        self.stack.add_kw_args_action (*self.sample_action)
        self.assertEqual (self.stack.action_list[0],self.sample_action)
        
        self.stack.run()
        self.assertEqual (self.stack.running, True)
        
        self.stack.add_kw_args_action (*self.sample_action)
        self.assertEqual (len(self.stack.action_list),1)
        self.assertEqual (self.stack.running, False)
    
    def test_add_action (self):
        self.stack.add_action (*self.short_action)
        self.assertEqual (self.stack.action_list[0],self.sample_action_empty_kw)
    
    def test_remove_current_action (self):
        self.stack.add_kw_args_action (*self.sample_action)
        new_action = (self.sample_action[0],self.x + 1) + self.sample_action[2:]
        self.stack.add_kw_args_action (*new_action)
        
        self.stack.remove_current_action()
        self.assertEqual (len(self.stack.action_list),1)
        self.assertEqual (self.stack.action_list[0],new_action)
    
    
    def test_clear (self):
        num_actions = 5
        for i in range (num_actions):
            self.stack.add_kw_args_action (*self.sample_action)
        
        self.assertEqual (len(self.stack.action_list),num_actions)
        self.stack.clear()
        self.assertEqual (self.stack.action_list,[])
    
    def test_perform_action (self):
        l=[]

        perform = (l.append, (self.x,), None, ())
        self.stack.add_action (*perform)
        self.assertTrue (self.stack.run())
        self.assertEqual (l[0], self.x)
    
    def test_run (self):
        iterations = 5
        # check correct exit conditions and iteration count
        perform = (self.l.append, (self.x,), lambda x: len(x)==iterations, (self.l,)) 
        self.stack.add_action (*perform)
        while (self.stack.run()):
            pass
        self.assertEqual (len(self.l), iterations)
        self.assertAlmostEqual (len (self.stack.action_list),0)
        
        # assert empty success functions are called just once
        self.l = []
        perform = (self.l.append, (self.x,))
        self.stack.add_action (*perform)
        self.assertTrue (self.stack.run())
        self.assertFalse (self.stack.run())
        self.assertEqual (self.l,[self.x])

if __name__ == '__main__':
    unittest.main()

