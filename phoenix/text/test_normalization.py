import unittest
import unicodedata
from phoenix.text.normalization import normalize_truth

class TestNormalization(unittest.TestCase):
    def test_nfc_normalization(self):
        # Combined character vs decomposed character
        decomposed = "a\u0308" # 'ä' decomposed
        normalized = normalize_truth(decomposed)
        self.assertEqual(normalized, unicodedata.normalize("NFC", decomposed).upper())

    def test_cherokee_uppercasing(self):
        # Test lowercase Cherokee characters to uppercase Cherokee characters
        lowercase = "ꭰꭱꭲꭳꭴ"
        expected = "ᎠᎡᎢᎣᎤ"
        self.assertEqual(normalize_truth(lowercase), expected)

    def test_whitespace_normalization(self):
        text = "  Hello \t World \n Cherokee \t\t  "
        expected = "HELLO WORLD CHEROKEE"
        self.assertEqual(normalize_truth(text), expected)

    def test_empty_string(self):
        self.assertEqual(normalize_truth(""), "")
        self.assertEqual(normalize_truth(None), "")

if __name__ == "__main__":
    unittest.main()
