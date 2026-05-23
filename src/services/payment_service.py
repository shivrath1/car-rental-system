"""
Payment Service - mock payment processor.
In a real system this would talk to Stripe, PayPal etc.
For this project it simulates payment with a simple success/fail mechanism.
"""

import random
import uuid


class PaymentService:
    """simulate to process payments."""

    def __init__(self, fail_rate=0.0):
        """
        Args:
            fail_rate: chance of a payment failing (0.0 = never, 1.0 = always).
                       Keep at 0.0 for normal use; set higher to test failure flows.
        """
        self._fail_rate = fail_rate

    def charge(self, amount, card_info):
        """
        Pretend to charge the customer's card.

        Args:
            amount: how much to charge (positive number).
            card_info: dict with card details (we don't actually use it - it's a mock).

        Returns:
            A dict with success status and transaction reference.
        """
        if amount <= 0:
            return {"success": False, "reason": "Invalid amount", "transaction_ref": None}

        # Simulate basic card validation
        if not self._is_card_valid(card_info):
            return {"success": False, "reason": "Invalid card", "transaction_ref": None}

        # Simulate random failure if fail_rate is set
        if random.random() < self._fail_rate:
            return {"success": False, "reason": "Payment declined", "transaction_ref": None}

        # Success - generate a fake transaction reference
        transaction_ref = f"TXN-{uuid.uuid4().hex[:10].upper()}"
        print(f"  [PaymentService] Charged ${amount:.2f}, txn: {transaction_ref}")
        return {"success": True, "reason": "OK", "transaction_ref": transaction_ref}

    def refund(self, amount, original_transaction_ref):
        """Pretend to refund a previous charge."""
        if amount <= 0:
            return {"success": False, "reason": "Invalid refund amount"}

        refund_ref = f"REF-{uuid.uuid4().hex[:10].upper()}"
        print(f"  [PaymentService] Refunded ${amount:.2f}, ref: {refund_ref} "
              f"(for original {original_transaction_ref})")
        return {"success": True, "reason": "OK", "transaction_ref": refund_ref}

    def _is_card_valid(self, card_info):
        """Very basic card validation - just checks the fields are present."""
        if not card_info:
            return False
        required_fields = ["card_number", "expiry", "cvv"]
        for field in required_fields:
            if field not in card_info or not card_info[field]:
                return False
        # Card number should be at least 12 digits (mock check)
        if len(str(card_info["card_number"]).replace(" ", "")) < 12:
            return False
        return True


# Quick test
if __name__ == "__main__":
    print("=== Testing PaymentService ===\n")

    payment = PaymentService()

    # Test 1: Valid charge
    print("Test 1: Valid charge")
    result = payment.charge(225.00, {
        "card_number": "4111111111111111",
        "expiry": "12/27",
        "cvv": "123",
    })
    print(f"  Success: {result['success']}, ref: {result['transaction_ref']}")
    print("  PASS\n")

    # Test 2: Invalid amount
    print("Test 2: Reject negative amount")
    result = payment.charge(-10, {"card_number": "1234567890123456", "expiry": "12/27", "cvv": "123"})
    print(f"  Success: {result['success']}, reason: {result['reason']}")
    print("  PASS\n")

    # Test 3: Invalid card
    print("Test 3: Reject invalid card")
    result = payment.charge(100, {"card_number": "123", "expiry": "12/27", "cvv": "123"})
    print(f"  Success: {result['success']}, reason: {result['reason']}")
    print("  PASS\n")

    # Test 4: Refund
    print("Test 4: Process a refund")
    refund = payment.refund(50.00, "TXN-ABC123")
    print(f"  Success: {refund['success']}, ref: {refund['transaction_ref']}")
    print("  PASS\n")

    print("=== PaymentService tests passed ===")