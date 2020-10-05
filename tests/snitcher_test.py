import unittest
from datetime import datetime
from unittest import TestCase, main, mock
from unittest.mock import MagicMock, patch
import snitcher.core


class TestSSLFetch(TestCase):

    example_cert = None

    def setUp(self):
        example_cert = open("tests/fixtures/example-cert.cert", "r")
        cert = example_cert.read()
        example_cert.close()
        self.example_cert = cert

    def teardown_class(self):
        self.example_cert = None

    @patch("ssl.get_server_certificate")
    def test_get_notafter_called_once(self, getcert):
        getcert.return_value = self.example_cert
        snitcher.core.get_notafter(("example.domain"))
        assert getcert.called_once
        snitcher.core.get_notafter(("example.domain", 443))
        assert getcert.called_twice

    @patch("ssl.get_server_certificate")
    def test_get_notafter_returns_expected_date(self, getcert):
        getcert.return_value = self.example_cert
        not_after = snitcher.core.get_notafter("example.domain")
        self.assertEqual(not_after, datetime.strptime(
            "2030-01-01 00:00:00", "%Y-%m-%d %H:%M:%S"))


class TestMatchWeek(TestCase):

    def test_get_days_to_expire(self):
        not_after = "2021-01-01 00:00:00"
        target_date = "2020-09-24 00:00:00"
        not_after = datetime(2021, 1, 1)
        target_date = datetime(2020, 12, 31)
        days_left = snitcher.core.get_days_to_expire(not_after, target_date)
        self.assertEqual(days_left, 1)

        not_after = datetime(2030, 1, 1)
        target_date = datetime(2020, 9, 24)
        days_left = snitcher.core.get_days_to_expire(not_after, target_date)
        self.assertEqual(days_left, 3386)


class TestSlackMessageBuilder(TestCase):

    def test_build_slack_message(self):
        message = snitcher.core.build_slack_message(channel="#ssl-check", bot_name="SSL check bot",
                                                    domain="www.cyberei.io", time_amount="15",
                                                    units="days", level="info", organization="Cyberei")
        assert type(message) is dict
        assert "channel" in message
        assert message["channel"] == "#ssl-check"
        assert message["username"] == "SSL check bot"
        assert message["attachments"][0]["fields"][0]["value"] == "info"


class TestShouldNotify(TestCase):

    def test_should_not_notify_before_30_days(self):
        self.assertEqual(snitcher.core.should_notify(31), {"notify": False})

    def test_should_be_info_between_30_and_16_days_before(self):
        self.assertEqual(snitcher.core.should_notify(30), {
                         "notify": True, "level": "info"})
        self.assertEqual(snitcher.core.should_notify(25), {
                         "notify": True, "level": "info"})
        self.assertEqual(snitcher.core.should_notify(16), {
                         "notify": True, "level": "info"})

    def test_should_be_warning_between_15_and_8_days_before(self):
        self.assertEqual(snitcher.core.should_notify(15), {
                         "notify": True, "level": "warning"})
        self.assertEqual(snitcher.core.should_notify(10), {
                         "notify": True, "level": "warning"})
        self.assertEqual(snitcher.core.should_notify(8), {
                         "notify": True, "level": "warning"})

    def test_should_be_critical_between_7_and_0_days_before(self):
        self.assertEqual(snitcher.core.should_notify(7), {
                         "notify": True, "level": "critical"})
        self.assertEqual(snitcher.core.should_notify(5), {
                         "notify": True, "level": "critical"})
        self.assertEqual(snitcher.core.should_notify(1), {
                         "notify": True, "level": "critical"})
        self.assertEqual(snitcher.core.should_notify(0), {
                         "notify": True, "level": "critical"})


if __name__ == '__main__':
    main()
