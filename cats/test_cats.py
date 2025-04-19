import unittest
from cats import Cats


class TestsCat(unittest.TestCase):
    def test_case1(self):
        c = Cats("""
                 .....
                 .....
                 ...C.
                 ..C..
                 ....M
                """)
        no_of_moves = c.solve()
        self.assertEqual(no_of_moves,3)

    def test_case2(self):
        c = Cats("""
                 .....
                 .....
                 ...CX
                 ..CX.
                 ....M
                """)
        no_of_moves = c.solve()
        self.assertEqual(no_of_moves,4)

    
    def test_case9(self):
        c = Cats("""
                 ..X..
                 ..C..
                 ....X
                 ..CX.
                 ....M
                """)
        no_of_moves = c.solve()
        self.assertEqual(no_of_moves,4)


    
    def test_case10(self):
        c = Cats("""
                 .....
                 ..C..
                 ....X
                 ..CX.
                 ....M
                """)
        no_of_moves = c.solve()
        self.assertEqual(no_of_moves,4)

    def test_case3(self):
        c = Cats("""
                 .....
                 .....
                 ...CX
                 ..CX.
                 ..X.M
                """)
        no_of_moves = c.solve()
        self.assertEqual(no_of_moves,None)

    def test_case4(self):
        c = Cats("""
                 .....
                 ...C.
                 ...XX
                 ..XC.
                 ..X.M
                """)
        no_of_moves = c.solve()
        self.assertEqual(no_of_moves,None)