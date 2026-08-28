from django.db import connection
from django.test import TestCase


class PublicationSchemaTest(TestCase):
    def test_salon_publication_media_column_exists(self):
        columns = {
            column[0]
            for column in connection.introspection.get_table_description(
                connection.cursor(), "salons_salonpublication"
            )
        }
        self.assertIn("media", columns)

    def test_hairstyle_publication_media_column_exists(self):
        columns = {
            column[0]
            for column in connection.introspection.get_table_description(
                connection.cursor(), "salons_hairstylepublication"
            )
        }
        self.assertIn("media", columns)
