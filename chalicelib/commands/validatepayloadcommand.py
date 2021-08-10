from chalicelib.commands.command import Command
from chalicelib.requests.webhookjsonvalidator import WebhookJsonValidator


class ValidatePayloadCommand(Command):
    """
    Command to perform validation on request JSON payloads.
    """

    def __init__(self, payload: dict, payload_validator: WebhookJsonValidator):
        self.payload = payload
        self.payload_validator = payload_validator

    def execute(self) -> bool:
        return self.payload_validator.validate_payload(self.payload)
