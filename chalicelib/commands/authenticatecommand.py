from chalicelib.commands.command import Command


class AuthenticateCommand(Command):
    """
    Command to authenticate incoming request against the stored user profile config.
    """

    def __init__(self, payload: dict, user_config: dict):
        self._payload = payload
        self._user_config = user_config

    def execute(self) -> bool:
        user_api_key = self._user_config.get("BOT_API_KEY")
        if not user_api_key:
            print("BOT_API_KEY must be set in user-config file. Exiting script.")
            return False
        if "auth" not in self._payload:
            print(f"Authentication value (auth) not present in payload. Payload: {self._payload}")
            return False
        payload_auth_key = self._payload['auth']
        if payload_auth_key != user_api_key:
            print(f"Authentication failed. Invalid API Key {payload_auth_key}. Exiting script...")
            return False
        return True
