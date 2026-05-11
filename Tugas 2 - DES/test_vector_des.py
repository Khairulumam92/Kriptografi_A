import unittest

from src.des_cli import decrypt_data, encrypt_data
from src.des_core import des_decrypt_block, des_encrypt_block


class TestDES(unittest.TestCase):
    def test_standard_vector(self):
        plaintext = "0123456789ABCDEF"
        key = "133457799BBCDFF1"
        expected_cipher = "85E813540F0AB405"
        self.assertEqual(des_encrypt_block(plaintext, key), expected_cipher)
        self.assertEqual(des_decrypt_block(expected_cipher, key), plaintext)

    def test_round_trip_hex_multiple_blocks(self):
        key = "A1B2C3D4E5F60718"
        plaintext_hex = "0123456789ABCDEFFEDCBA9876543210"
        ciphertext = encrypt_data(plaintext_hex, key, input_format="hex", verbose=False)
        recovered = decrypt_data(ciphertext, key, input_format="hex", verbose=False)
        self.assertEqual(recovered, plaintext_hex)

    def test_round_trip_text_multiple_blocks(self):
        key = "133457799BBCDFF1"
        plaintext = "Ini contoh plaintext lebih dari satu blok DES."
        ciphertext = encrypt_data(plaintext, key, input_format="text", verbose=False)
        recovered = decrypt_data(ciphertext, key, input_format="text", verbose=False)
        self.assertEqual(recovered, plaintext)

    def test_invalid_input(self):
        with self.assertRaises(ValueError):
            des_encrypt_block("123", "133457799BBCDFF1")
        with self.assertRaises(ValueError):
            des_decrypt_block("85E813540F0AB405", "XYZ")


if __name__ == "__main__":
    unittest.main()
