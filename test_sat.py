import itertools
import random
import unittest
from sat import two_sat, dpll, verify

class SatTests(unittest.TestCase):
    def test_exhaustive_2sat(self):
        n = 3
        options = [(), *[(lit,) for lit in (-3,-2,-1,1,2,3)],
                   *itertools.combinations_with_replacement((-3,-2,-1,1,2,3),2)]
        for a in options:
            for b in options:
                f = [a,b]
                oracle = any(verify(n, f, assignment)
                             for assignment in itertools.product((False,True),repeat=n))
                model = two_sat(n,f)
                self.assertEqual(model is not None, oracle, f)
                if model is not None: self.assertTrue(verify(n,f,model))
    def test_random_general_cnf(self):
        r = random.Random(20261030)
        for n in range(1,6):
            literals = [v for v in range(-n,n+1) if v]
            for _ in range(120):
                f = [tuple(r.choice(literals) for _ in range(r.randrange(4)))
                     for _ in range(r.randrange(12))]
                oracle = any(verify(n,f,a)
                             for a in itertools.product((False,True),repeat=n))
                witness = dpll(n,f)
                self.assertEqual(witness is not None, oracle, f)
                if witness is not None: self.assertTrue(verify(n,f,witness))
    def test_invalid(self):
        with self.assertRaises(ValueError): two_sat(2,[[3]])
        with self.assertRaises(ValueError): two_sat(2,[[1,2,-1]])
if __name__ == "__main__":
    unittest.main()
