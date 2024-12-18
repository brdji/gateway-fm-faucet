from django.test import TestCase, Client
from mock import patch

from faucet.models import FaucetRequest


@patch("faucet.chain.send_ETH", return_value="default_mocked_tx_hash")
@patch("faucet.chain.wallet_balance_check")
class FaucetTestCase(TestCase):

    client = Client()

    default_req_data = {"address": "0xE4f15C618689ff0de68E110EE97d017B91C26871"}

    def test_valid_fund_request(self, balanceMock, sendMock):
        sendMock.return_value = "tx_hash_#23445443"
        resp = self.client.post("/faucet/fund", self.default_req_data)
        self.assertEqual(resp.status_code, 200)

        # Validate returned tx hash is equal to mocked value
        returned_tx_hash = resp.json()["tx_hash"]
        self.assertEqual(returned_tx_hash, sendMock.return_value)

        # Validate record in DB
        db_record = FaucetRequest.objects.get(
            destination_address=self.default_req_data["address"]
        )
        self.assertIsNotNone(db_record)
        self.assertEqual(db_record.tx_hash, sendMock.return_value)

    def test_wallet_insufficient_funds(self, balanceMock, sendMock):
        balanceMock.return_value = False
        resp = self.client.post("/faucet/fund", self.default_req_data)
        self.assertEqual(resp.status_code, 500)
        self.assertIn("Insufficient faucet funds", str(resp.content))

    def test_invalid_address_request(self, balanceMock, sendMock):
        invalid_address_data = {"address": "invalid_chain_address"}
        resp = self.client.post("/faucet/fund", invalid_address_data)
        self.assertEqual(resp.status_code, 400)
        self.assertIn("Ensure this value has at least 42 characters", str(resp.content))

    def test_too_many_requests_per_ip(self, *args):
        # insert record into db
        db_record = FaucetRequest(
            destination_address="0x47713b56F32fCeBf4552d8937831F4159686d986",
            ip_address="testserver",
            tx_hash="123123",
        )
        db_record.save()

        resp = self.client.post("/faucet/fund", self.default_req_data)
        self.assertEqual(resp.status_code, 400)

    def test_too_many_requests_per_dest_address(self, *args):
        # insert record into db
        db_record = FaucetRequest(
            destination_address=self.default_req_data["address"],
            ip_address="0.0.0.0",
            tx_hash="123123",
        )
        db_record.save()

        resp = self.client.post("/faucet/fund", self.default_req_data)
        self.assertEqual(resp.status_code, 400)

    def test_list_faucet_stats(self, *args):
        # Successful tx
        db_record1 = FaucetRequest(
            destination_address="0x47713b56F32fCeBf4552d8937831F4159686d986",
            ip_address="testserver",
            tx_hash="123123",
        )
        db_record1.save()

        # Failed tx
        db_record2 = FaucetRequest(
            destination_address="0x47713b56F32fCeBf4552d8937831F4159686d986",
            ip_address="testserver",
        )
        db_record2.save()

        resp = self.client.get("/faucet/stats")
        json_data = resp.json()

        self.assertEqual(json_data["successful_txs"], 1)
        self.assertEqual(json_data["failed_txs"], 1)
