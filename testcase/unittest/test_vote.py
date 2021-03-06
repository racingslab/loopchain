#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2017 theloop, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Test Vote Object"""

import logging
import unittest
import loopchain.utils as util
import testcase.unittest.test_util as test_util
from loopchain.peer import Vote
from loopchain.baseservice import PeerManager
from loopchain.protos import loopchain_pb2
from loopchain import configure as conf

util.set_log_level_debug()


class TestVote(unittest.TestCase):

    def setUp(self):
        test_util.print_testname(self._testMethodName)

    def tearDown(self):
        pass

    @staticmethod
    def __make_peer_info(peer_id, group_id):
        peer_info = loopchain_pb2.PeerRequest()
        peer_info.peer_target = peer_id + "_target"
        peer_info.peer_type = loopchain_pb2.PEER
        peer_info.peer_id = peer_id
        peer_info.group_id = group_id
        return peer_info

    def test_vote_init_from_audience(self):
        # GIVEN
        peer_info1 = self.__make_peer_info("peerid-1", "groupid-1")
        peer_info2 = self.__make_peer_info("peerid-2", "groupid-2")
        audience = {peer_info1.peer_id: peer_info1, peer_info2.peer_id: peer_info2}

        # WHEN
        vote = Vote("block_hash", audience)
        logging.debug("votes: " + str(vote.votes))

        # THEN
        self.assertTrue(vote.check_vote_init(audience))

    def test_vote_init_from_peer_list(self):
        # GIVEN
        peer_manager = PeerManager()
        peer_manager.add_peer("peerid-1", "groupid-1", "peerid-1_target")
        peer_manager.add_peer("peerid-2", "groupid-2", "peerid-2_target")

        # WHEN
        vote = Vote("block_hash", peer_manager)
        logging.debug("votes: " + str(vote.votes))

        # THEN
        self.assertTrue(vote.check_vote_init(peer_manager))

    def test_vote_init_from_different_source(self):
        # GIVEN
        peer_info1 = self.__make_peer_info("peerid-1", "groupid-1")
        peer_info2 = self.__make_peer_info("peerid-2", "groupid-2")
        audience = {peer_info1.peer_id: peer_info1, peer_info2.peer_id: peer_info2}
        peer_manager = PeerManager()
        peer_manager.add_peer("peerid-1", "groupid-1", "peerid-1_target")
        peer_manager.add_peer("peerid-2", "groupid-2", "peerid-2_target")

        # WHEN
        vote = Vote("block_hash", audience)
        logging.debug("votes: " + str(vote.votes))

        # THEN
        self.assertTrue(vote.check_vote_init(peer_manager))

    def test_add_vote(self):
        # GIVEN
        peer_manager = PeerManager()
        peer_manager.add_peer("peerid-1", "groupid-1", "peerid-1_target")
        peer_manager.add_peer("peerid-2", "groupid-2", "peerid-2_target")
        peer_manager.add_peer("peerid-3", "groupid-3", "peerid-3_target")
        peer_manager.add_peer("peerid-4", "groupid-3", "peerid-4_target")
        peer_manager.add_peer("peerid-5", "groupid-3", "peerid-5_target")
        vote = Vote("block_hash", peer_manager)
        logging.debug("votes: " + str(vote.votes))

        # WHEN
        vote.add_vote("groupid-1", "peerid-1", None)
        self.assertFalse(vote.get_result("block_hash", 0.51))

        # THEN
        vote.add_vote("groupid-2", "peerid-2", None)
        self.assertTrue(vote.get_result("block_hash", 0.51))

    def test_add_vote_fail_before_add_peer(self):
        # GIVEN
        peer_manager = PeerManager()
        peer_manager.add_peer("peerid-1", "groupid-1", "peerid-1_target")
        peer_manager.add_peer("peerid-2", "groupid-2", "peerid-2_target")
        peer_manager.add_peer("peerid-3", "groupid-3", "peerid-3_target")
        peer_manager.add_peer("peerid-4", "groupid-3", "peerid-4_target")
        peer_manager.add_peer("peerid-5", "groupid-3", "peerid-5_target")
        vote = Vote("block_hash", peer_manager)
        logging.debug("votes: " + str(vote.votes))

        # WHEN
        vote.add_vote("groupid-1", "peerid-1", None)
        vote.add_vote("groupid-3", "peerid-4", None)
        ret1 = vote.add_vote("groupid-4", "peerid-1", None)
        ret2 = vote.add_vote("groupid-1", "peerid-9", None)
        self.assertFalse(ret1)
        self.assertFalse(ret2)

        # THEN
        ret = vote.get_result_detail("block_hash", 0.51)
        self.assertEqual(ret[5], 5)

    def test_fail_vote(self):
        # GIVEN
        peer_manager = PeerManager()
        peer_manager.add_peer("peerid-1", "groupid-1", "peerid-1_target")
        peer_manager.add_peer("peerid-2", "groupid-2", "peerid-2_target")
        peer_manager.add_peer("peerid-3", "groupid-3", "peerid-3_target")
        peer_manager.add_peer("peerid-4", "groupid-3", "peerid-4_target")
        peer_manager.add_peer("peerid-5", "groupid-3", "peerid-5_target")
        vote = Vote("block_hash", peer_manager)
        logging.debug("votes: " + str(vote.votes))

        # WHEN
        vote.add_vote("groupid-1", "peerid-1", conf.TEST_FAIL_VOTE_SIGN)
        vote.add_vote("groupid-3", "peerid-4", conf.TEST_FAIL_VOTE_SIGN)
        vote.add_vote("groupid-3", "peerid-5", conf.TEST_FAIL_VOTE_SIGN)
        vote.get_result("block_hash", 0.51)

        # THEN
        self.assertTrue(vote.is_failed_vote("block_hash", 0.51))
