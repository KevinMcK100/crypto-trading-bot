from abc import ABCMeta, abstractmethod


class OrderFactory(metaclass=ABCMeta):
    @abstractmethod
    def create_orders(self):
        pass

    @staticmethod
    def _split_quantities(total_qty: float, qty_precision: int, qty_splits: list) -> list:
        qty_remaining = total_qty
        splits = []
        # Create a list of quantity splits based on specified percentages, excluding the final split
        for split in qty_splits[:-1]:
            split_multiplier = split / 100
            qty = round(total_qty * split_multiplier, qty_precision)
            qty_remaining -= qty
            splits.append(qty)
        # Last part should be what ever remains to ensure we close out exact position amount
        splits.append(round(qty_remaining, qty_precision))
        return splits
