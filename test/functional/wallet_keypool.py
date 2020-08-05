#!/usr/bin/env python3
# Copyright (c) 2014-2017 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
"""Test the wallet keypool and interaction with wallet encryption/locking."""

from test_framework.test_framework import NestEggTestFramework
from test_framework.util import *

class KeyPoolTest(NestEggTestFramework):
    def set_test_params(self):
        self.num_nodes = 1

    def run_test(self):
        nodes = self.nodes
        addr_before_encrypting = nodes[0].getnewaddress()
        addr_before_encrypting_data = nodes[0].validateaddress(addr_before_encrypting)

        # Encrypt wallet and wait to terminate
        nodes[0].node_encrypt_wallet('test')
        # Restart node 0
        self.start_node(0)
        # Keep creating keys
        addr = nodes[0].getnewaddress()
        addr_data = nodes[0].validateaddress(addr)
        assert_raises_rpc_error(-12, "Keypool ran out, please call keypoolrefill first, or unlock the wallet.",
                                nodes[0].getnewaddress)

        # put six (plus 2) new keys in the keypool (100% external-, +100% internal-keys, 1 in min)
        nodes[0].walletpassphrase('test', 12000)
        nodes[0].keypoolrefill(6)
        nodes[0].walletlock()
        wi = nodes[0].getwalletinfo()
        assert_equal(wi['keypoolsize'], 7)

        # drain the internal keys
        nodes[0].getrawchangeaddress()
        nodes[0].getrawchangeaddress()
        nodes[0].getrawchangeaddress()
        nodes[0].getrawchangeaddress()
        nodes[0].getrawchangeaddress()
        nodes[0].getrawchangeaddress()
        nodes[0].getrawchangeaddress()
        addr = set()
        # the next one should fail
        assert_raises_rpc_error(-12, "Keypool ran out", nodes[0].getrawchangeaddress)

        # drain the external keys
        #addr.add(nodes[0].getnewaddress())
        #addr.add(nodes[0].getnewaddress())
        #addr.add(nodes[0].getnewaddress())
        #addr.add(nodes[0].getnewaddress())
        #addr.add(nodes[0].getnewaddress())
        #addr.add(nodes[0].getnewaddress())
        #addr.add(nodes[0].getnewaddress())
        #assert(len(addr) == 7)
        # the next one should fail
        #assert_raises_rpc_error(-12, "Error: Keypool ran out, please call keypoolrefill first", nodes[0].getnewaddress)

        # refill keypool with three new addresses
        nodes[0].walletpassphrase('test', 1)
        nodes[0].keypoolrefill(3)

        # test walletpassphrase timeout
        time.sleep(1.1)
        assert_equal(nodes[0].getwalletinfo()["unlocked_until"], 0)

        # drain them by mining
        #nodes[0].generate(1)
        #nodes[0].generate(1)
        #nodes[0].generate(1)
        #assert_raises_rpc_error(-12, "Keypool ran out", nodes[0].generate, 1)

        nodes[0].walletpassphrase('test', 100)
        nodes[0].keypoolrefill(100)
        wi = nodes[0].getwalletinfo()
        assert_equal(wi['keypoolsize'], 101)

if __name__ == '__main__':
    KeyPoolTest().main()
