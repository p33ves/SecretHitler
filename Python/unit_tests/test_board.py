import unittest
import sys

sys.path.append("../")
from board import *
from static_data import images

class Test_BoardType(unittest.TestCase):
        
    def test_getBaseBoard(self):
        for bt_object in BoardType:
            img_loc = bt_object.getBaseBoard()
            self.assertEqual(img_loc, f"./images/Board{bt_object}.png")

    def test_getPowers(self):
        bt_object = BoardType.NineToTen
        self.assertEqual(bt_object.getPowers(1).value, 1)

#class Test_Board(unittest.TestCase):

