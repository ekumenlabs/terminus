"""
/*
 * Copyright (C) 2017 Open Source Robotics Foundation
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 */
"""


class CityElement(object):
    """A city element is an object that belongs to a city and that may
    be visited by a generator to create the contents for a file.
    We are using a vistor pattern here to do the double-dispatching and
    the entry point is the `accept` message"""

    def accept(self, generator):
        raise NotImplementedError()
