from chalicelib.commands.command import Command


class OrderInvoker:
    commands = []
    executed = []

    def set_command(self, command: Command):
        self.commands.append(command)

    def set_commands(self, commands: [Command]):
        self.commands.extend(commands)

    def execute_orders(self):
        print(f"Items to process: {len(self.commands)}")
        while self.commands:
            order_cmd = self.commands.pop(0)
            order_cmd.execute()
            self.executed.append(order_cmd)
