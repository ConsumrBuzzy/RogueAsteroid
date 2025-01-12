#!/usr/bin/env python3
"""
Script to reorganize test files into their new directory structure
"""

import os
import shutil
from pathlib import Path

# Define the test organization
TEST_ORGANIZATION = {
    'unit': [
        'test_components.py',
        'test_entities.py',
        'test_utils.py',
        'test_additional_components.py'
    ],
    'engine': [
        'test_systems.py',
        'test_particles.py'
    ],
    'game': [
        'test_game_state.py',
        'test_scoring.py',
        'test_collision.py'
    ],
    'ui': [
        'test_menu.py'
    ],
    'integration': [
        'test_integration.py',
        'test_performance.py'
    ]
}

def main():
    # Get the tests directory
    tests_dir = Path(__file__).parent
    
    # Create directories if they don't exist
    for directory in TEST_ORGANIZATION.keys():
        dir_path = tests_dir / directory
        dir_path.mkdir(exist_ok=True)
        print(f"Created directory: {dir_path}")
    
    # Move files to their new locations
    for category, files in TEST_ORGANIZATION.items():
        for file in files:
            src = tests_dir / file
            dst = tests_dir / category / file
            if src.exists():
                shutil.move(str(src), str(dst))
                print(f"Moved {file} to {category}/")
            else:
                print(f"Warning: {file} not found")

if __name__ == '__main__':
    main() 