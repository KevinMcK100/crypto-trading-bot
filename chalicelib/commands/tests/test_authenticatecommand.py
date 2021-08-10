import json
import unittest

from chalicelib.commands.authenticatecommand import AuthenticateCommand


class AuthenticationCommandTest(unittest.TestCase):

    valid_user_config = {}
    valid_json_payload = {}

    def setUp(self):
        with open("./sample-user-config.json") as user_config_json:
            self.valid_user_config = json.load(user_config_json)
        with open("./sample-json-payload.json") as sample_payload:
            self.valid_json_payload = json.load(sample_payload)

    def test_authenticated_user_return_true(self):
        # given
        auth_command = AuthenticateCommand(payload=self.valid_json_payload, user_config=self.valid_user_config);

        # when
        result = auth_command.execute()

        # then
        self.assertTrue(result)

    def test_unauthenticated_user_return_false(self):
        # given
        invalid_auth_payload = self.valid_json_payload
        invalid_auth_payload.update({"auth": "invalid_api_key"})
        auth_command = AuthenticateCommand(payload=invalid_auth_payload, user_config=self.valid_user_config)

        # when
        result = auth_command.execute()

        # then
        self.assertFalse(result)

    def test_missing_auth_return_false(self):
        # given
        invalid_auth_payload = self.valid_json_payload
        invalid_auth_payload.pop("auth")
        auth_command = AuthenticateCommand(payload=invalid_auth_payload, user_config=self.valid_user_config)

        # when
        result = auth_command.execute()

        # then
        self.assertFalse(result)

    def test_missing_user_config_api_key_return_false(self):
        # given
        invalid_user_config = self.valid_user_config
        invalid_user_config.pop("BOT_API_KEY")
        auth_command = AuthenticateCommand(payload=self.valid_json_payload, user_config=invalid_user_config)

        # when
        result = auth_command.execute()

        # then
        self.assertFalse(result)
