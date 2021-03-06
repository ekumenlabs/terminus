#!/bin/sh

# Copyright (C) 2017 Open Source Robotics Foundation
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

PYTHONPATH=$PYTHONPATH:.:./terminus python - <<EOF
import unittest
import logging

logging.basicConfig(level=logging.ERROR)

if __name__ == "__main__":

    suite = unittest.TestLoader().discover('./terminus/tests', pattern = "*_test.py")
    unittest.TextTestRunner(verbosity=1).run(suite)
EOF
