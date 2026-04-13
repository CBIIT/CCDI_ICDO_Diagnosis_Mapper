import unittest
import pandas as pd
import subprocess
import os
from pathlib import Path

class TestScript(unittest.TestCase):
    def setUp(self):
        """Define paths and create test data."""
        # obtain and confirm folder and file paths
        self.root = Path(__file__).resolve().parent.parent
        self.input_dir = self.root / "input"
        self.input_dir.mkdir(exist_ok=True)

        self.output_dir = self.root / "output"
        self.output_dir.mkdir(exist_ok=True)
        self.output_files = []

        self.script_path = self.root / "scripts" / "icdo_group_mapper.py"

        # create a test input in the input folder
        test_data = {'code':['8000/0', '8000/1', '8000/2','8000/3', '8000/6',  '8011/2'],
                    'terms':["Neoplasm, benign","Neoplasm, uncertain whether benign or malignant",
                     "unknown","Neoplasm, malignant","Neoplasm, metastatic","unknown"]}
        test_data = pd.DataFrame(test_data)
        self.test_file = self.input_dir / "test_input.csv"
        pd.DataFrame(test_data).to_csv(self.test_file, index=False)

    def test_script_execution(self):
        """Run the script and check if it produces output."""
        # run the script
        result = subprocess.run(['python', str(self.script_path)], capture_output=True, text=True)
        
        # print the test script logs
        print("\n---- TEST SCRIPT LOG ----")
        print(result.stdout.replace('\\u2705', 'PASS:')) 
        print(result.stderr.replace('\\u2705', 'PASS:')) 
        print("----------------------------")

        # check script ran & output file was created
        self.assertEqual(result.returncode, 0, f"Script crashed with error: {result.stderr}")
        self.output_files = list(self.output_dir.glob("test_input_icdomapper_output_*.tsv"))
        self.assertTrue(len(self.output_files) > 0, "No output file was generated in /output")

        # define expected output
        expected_data = {
            'code': ['8000/0', '8000/1', '8000/2', '8000/3', '8000/6', '8011/2'],
            'term': [
                "Neoplasm, benign", 
                "Neoplasm, uncertain whether benign or malignant",
                "unknown", 
                "Neoplasm, malignant", 
                "Neoplasm, metastatic", 
                "unknown"
            ],
            'range': ['800', '800', '800', '800', '800', '801-804'],
            'group': ["Neoplasms, NOS", "Neoplasms, NOS", "Neoplasms, NOS", 
                "Neoplasms, NOS", "Neoplasms, NOS", "Epithelial neoplasms, NOS"
            ]
        }
        expected_df = pd.DataFrame(expected_data)
        
        # read the output file and compare with expected data
        output_data = max(self.output_files, key=os.path.getctime)
        output_df = pd.read_csv(output_data, sep='\t')

        # delete self.assertTrue(output_df.equals(expected_df), "the output file contains the expected data")
        pd.testing.assert_frame_equal(output_df, expected_df, check_dtype=False)
        print("Test Passed: The output file contains the expected data.")


    def tearDown(self):
        """clean up the test files."""
        if self.test_file.exists():
            os.remove(self.test_file)
        for out_file in self.output_files:
                    if out_file.exists():
                        os.remove(out_file)

if __name__ == '__main__':
    unittest.main(buffer=False)