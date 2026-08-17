import unittest
from app.validate import validate
from app.errors import AppError

class ValidationTests(unittest.TestCase):

    def test_boolean_is_not_money(self):
        with self.assertRaises(AppError):
            validate({'fields': {'amount': {'type': 'integer'}}}, {'amount': True})

    def test_non_finite_number_rejected(self):
        for value in (float('nan'), float('inf')):
            with self.assertRaises(AppError):
                validate({'fields': {'value': {'type': 'number'}}}, {'value': value})

    def test_unknown_fields_rejected(self):
        with self.assertRaises(AppError):
            validate({'fields': {'name': {'type': 'string'}}}, {'name': 'valid', 'extra': 'hidden'})

    def test_invalid_calendar_date_rejected(self):
        with self.assertRaises(AppError):
            validate({'fields': {'date': {'type': 'string', 'format': 'date'}}}, {'date': '2026-02-30'})

    def test_naive_datetime_rejected(self):
        with self.assertRaises(AppError):
            validate({'fields': {'date': {'type': 'string', 'format': 'datetime'}}}, {'date': '2026-01-01T09:00:00'})

    def test_identifier_path_rejected(self):
        with self.assertRaises(AppError):
            validate({'fields': {}}, {'id': '../../file'})
