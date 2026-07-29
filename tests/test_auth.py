import unittest
from app.auth import authorize
from app.errors import Unauthorized

class AuthTests(unittest.TestCase):

    def test_valid_operator(self):
        authorize({'Authorization': 'Bearer secret'}, 'secret')

    def test_missing_wrong_or_empty_token(self):
        for headers, token in (({}, 'secret'), ({'Authorization': 'Bearer wrong'}, 'secret'), ({'Authorization': 'Bearer '}, '')):
            with self.assertRaises(Unauthorized):
                authorize(headers, token)
