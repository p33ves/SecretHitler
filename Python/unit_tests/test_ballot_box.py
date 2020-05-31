import unittest
import sys

sys.path.append("../")
from ballot_box import BallotBox, Vote

class Test_Ballot_Box(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.bb_object = BallotBox()
        cls.bb_object.vote(1, Vote.JA)
        cls.bb_object.vote(5, Vote.NEIN)

    def test_getTotalVoteCount(self):
        self.assertEqual(2, self.bb_object.getTotalVoteCount())

    def test_getVoteSplit(self):
        v_j, v_n = self.bb_object.getVoteSplit()
        self.assertEqual(1, v_j)
        self.assertEqual(1, v_n)

    def test_result(self):
        self.assertEqual(Vote.NEIN, self.bb_object.result())

    def test_getVote(self):
        self.assertEqual(Vote.JA, self.bb_object.getVote(1))
        self.assertEqual(Vote.NEIN, self.bb_object.getVote(5))
        self.assertIsNone(self.bb_object.getVote(1995))
    
    def test_vote(self):
        bb_object_copy = BallotBox()
        bb_object_copy = self.bb_object
        bb_object_copy.vote(10, Vote.JA)
        self.assertEqual(Vote.JA, bb_object_copy.result())
