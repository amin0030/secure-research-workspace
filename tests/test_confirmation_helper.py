
import unittest

from campus_confirmation import build_confirmation


class ConfirmationHelperTests(unittest.TestCase):
    def make_booking(self, booking_id=42):
        return {
            "id": booking_id,
            "room_id": 1,
            "owner_user_id": "amin",
            "starts_at": "2027-07-20T10:00:00Z",
            "ends_at": "2027-07-20T11:00:00Z",
            "status": "active",
        }

    def test_confirmation_contains_correct_booking_details(self):
        result = build_confirmation(self.make_booking())

        self.assertIn("Booking ID: 42", result["content"])
        self.assertIn("Student: amin", result["content"])
        self.assertTrue(result["reference"])

    def test_same_booking_produces_same_confirmation(self):
        booking = self.make_booking()

        first = build_confirmation(booking)
        second = build_confirmation(booking)

        self.assertEqual(first["reference"], second["reference"])
        self.assertEqual(first["content"], second["content"])

    def test_different_bookings_have_different_references(self):
        first = build_confirmation(self.make_booking(42))
        second = build_confirmation(self.make_booking(43))

        self.assertNotEqual(first["reference"], second["reference"])


if __name__ == "__main__":
    unittest.main()
