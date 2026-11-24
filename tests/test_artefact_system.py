import io
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import main


class ArtefactSystemTests(unittest.TestCase):
    def setUp(self):
        main.artefacts.clear()
        self.original_data_file = main.DATA_FILE
        temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(temporary_directory.cleanup)
        main.DATA_FILE = Path(temporary_directory.name) / "artefacts.json"

    def tearDown(self):
        main.DATA_FILE = self.original_data_file
        main.artefacts.clear()

    def sample_record(self, artefact_id="ART001", name="Old Photograph",
                      condition="Good", category="Photograph"):
        return {
            "id": artefact_id,
            "name": name,
            "category": category,
            "location": "Display Case B",
            "condition": condition,
            "description": "Test description",
            "acquisition_date": "12-05-2020",
        }

    def test_generate_unique_id_and_find_by_id(self):
        main.artefacts.extend([
            self.sample_record("ART001"),
            self.sample_record("ART002", "Letter"),
        ])
        self.assertEqual(main.generate_artefact_id(), "ART003")
        self.assertIs(main.find_artefact_by_id("art002"),
                      main.artefacts[1])
        self.assertIsNone(main.find_artefact_by_id("ART999"))

    def test_validate_condition(self):
        self.assertTrue(main.validate_condition("Good"))
        self.assertTrue(main.validate_condition("Damaged"))
        self.assertTrue(main.validate_condition("Under Repair"))
        self.assertFalse(main.validate_condition("Broken"))

    def test_add_valid_artefact_and_save(self):
        responses = iter([
            "Old Vase", "Pottery", "Ceramics Gallery",
            "Good", "A pottery vase", "20-06-2024",
        ])
        with patch("builtins.input", side_effect=lambda prompt="": next(responses)):
            main.add_artefact()

        self.assertEqual(len(main.artefacts), 1)
        self.assertEqual(main.artefacts[0]["id"], "ART001")
        self.assertEqual(main.artefacts[0]["name"], "Old Vase")
        self.assertTrue(os.path.exists(main.DATA_FILE))

    def test_add_rejects_empty_name_category_and_invalid_condition(self):
        responses = iter([
            "", " ", "New Name",
            "", "Pottery",
            "Ceramics Gallery",
            "Broken", "Good",
            "A description", "",
        ])
        with patch("builtins.input", side_effect=lambda prompt="": next(responses)):
            main.add_artefact()

        self.assertEqual(main.artefacts[0]["name"], "New Name")
        self.assertEqual(main.artefacts[0]["category"], "Pottery")
        self.assertEqual(main.artefacts[0]["condition"], "Good")

    def test_update_condition_and_nonexistent_id(self):
        main.artefacts.append(self.sample_record())
        with patch("builtins.input", side_effect=["ART001", "2"]):
            main.update_condition()
        self.assertEqual(main.artefacts[0]["condition"], "Damaged")

        with patch("builtins.input", return_value="ART999"):
            output = io.StringIO()
            with redirect_stdout(output):
                main.update_condition()
        self.assertIn("no artefact", output.getvalue())

    def test_update_rejects_invalid_condition_selection(self):
        main.artefacts.append(self.sample_record())
        with patch("builtins.input", side_effect=["ART001", "9", "3"]):
            main.update_condition()
        self.assertEqual(main.artefacts[0]["condition"], "Under Repair")

    def test_view_empty_and_populated_collection(self):
        output = io.StringIO()
        with redirect_stdout(output):
            main.view_all_artefacts()
        self.assertIn("No artefacts", output.getvalue())

        main.artefacts.append(self.sample_record())
        output = io.StringIO()
        with redirect_stdout(output):
            main.view_all_artefacts()
        self.assertIn("ART001", output.getvalue())

    def test_search_partial_and_case_insensitive(self):
        main.artefacts.append(self.sample_record())
        with patch("builtins.input", side_effect=["PHOTO", "N"]):
            output = io.StringIO()
            with redirect_stdout(output):
                main.search_artefact()
        self.assertIn("Old Photograph", output.getvalue())

        with patch("builtins.input", side_effect=["missing", "N"]):
            output = io.StringIO()
            with redirect_stdout(output):
                main.search_artefact()
        self.assertIn("No artefacts matched", output.getvalue())

    def test_delete_confirm_and_cancel_and_missing(self):
        main.artefacts.append(self.sample_record())
        with patch("builtins.input", side_effect=["ART001", "N"]):
            main.delete_artefact()
        self.assertEqual(len(main.artefacts), 1)

        with patch("builtins.input", side_effect=["ART001", "Y"]):
            main.delete_artefact()
        self.assertEqual(len(main.artefacts), 0)

        with patch("builtins.input", return_value="ART999"):
            output = io.StringIO()
            with redirect_stdout(output):
                main.delete_artefact()
        self.assertIn("no artefact", output.getvalue())

    def test_statistics_update_after_operations(self):
        main.artefacts.extend([
            self.sample_record("ART001", "One", "Good", "Photograph"),
            self.sample_record("ART002", "Two", "Damaged", "Document"),
            self.sample_record("ART003", "Three", "Under Repair", "Photograph"),
        ])
        output = io.StringIO()
        with redirect_stdout(output):
            main.display_statistics()
        text = output.getvalue()
        self.assertIn("Total artefacts: 3", text)
        self.assertIn("Good: 1", text)
        self.assertIn("Photograph: 2", text)


if __name__ == "__main__":
    unittest.main()
