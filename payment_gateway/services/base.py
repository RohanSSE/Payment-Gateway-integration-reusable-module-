from abc import ABC, abstractmethod


class BasePaymentProvider(ABC):
    """Abstract base class that enforces provider interface."""

    @abstractmethod
    def create_payment(self, order_id: str, amount: float, currency: str, **kwargs) -> dict:
        raise NotImplementedError

    @abstractmethod
    def verify_payment(self, order_id: str, transaction_id: str, **kwargs) -> dict:
        raise NotImplementedError

    @abstractmethod
    def refund(self, order_id: str, transaction_id: str, amount: float, **kwargs) -> dict:
        raise NotImplementedError
