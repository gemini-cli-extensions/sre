# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import subprocess
import os

def test_conversion():
    script_path = os.path.join(os.path.dirname(__file__), 'cloudlogging2apachelogs.py')
    sample_path = os.path.join(os.path.dirname(__file__), '../assets/sample_logs.json')
    
    result = subprocess.run(['python3', script_path, sample_path], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Test Failed with return code {result.returncode}")
        print(f"Error: {result.stderr}")
        return False
    
    output_lines = result.stdout.strip().split('\n')
    if len(output_lines) != 2:
        print(f"Test Failed: Expected 2 lines of output, got {len(output_lines)}")
        return False
    
    print("Test Passed: Output has correct number of lines.")
    print("Sample output line 1:")
    print(output_lines[0])
    return True

if __name__ == "__main__":
    if test_conversion():
        exit(0)
    else:
        exit(1)
