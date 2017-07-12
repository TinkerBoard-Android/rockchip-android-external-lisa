# SPDX-License-Identifier: Apache-2.0
#
# Copyright (C) 2015, ARM Limited and contributors.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import re
import os
import logging

from time import sleep

from target_script import TargetScript
from android import Screen, System
from android.workload import Workload


# Description: This experiments tests suspend/resume by turning off
# the screen and cutting off USB
# REQUIRES DEVICE TO BE CONNECTED THROUGH MONSOON SO THAT PASSTHROUGH
# CAN BE TURNED OFF.
# The dirty hack we have is we forcefully add 'energy' into the
# collect parameters so that the USB is cut off (as a side effect, we
# also measure energy while suspended). There's no way of knowing for
# sure if device did enter suspend.
class SuspendResume(Workload):
    """
    Android SuspendResume workload
    """

    # Package is optional for this test
    package = 'optional'

    def __init__(self, test_env):
        super(SuspendResume, self).__init__(test_env)
        self._log = logging.getLogger('SuspendResume')
        self._log.debug('Workload created')

        # Set of output data reported by SuspendResume
        self.db_file = None

    def run(self, out_dir, duration_s, collect=''):
        """
        Run single Gmaps workload.

        :param out_dir: Path to experiment directory where to store results.
        :type out_dir: str

        :param location_search: Search string to be used in SuspendResume
        :type location_search: str

        :param swipe_count: Number of sets of (left, right, up, down) swipes to do
        :type swipe_count: int

        :param collect: Specifies what to collect. Possible values:
            - 'energy'
            - 'systrace'
            - 'ftrace'
            - any combination of the above
        :type collect: list(str)
        """

        # Suspend/resume should always disconnect USB so rely on
        # the Energy meter to disconnect USB (We only support USB disconnect
        # mode for energy measurement, like with Monsoon
        if 'energy' not in collect:
            collect = collect + ' energy'

        # Keep track of mandatory parameters
        self.out_dir = out_dir
        self.collect = collect

        # Set min brightness
        Screen.set_brightness(self._target, auto=False, percent=0)
        # Unlock device screen (assume no password required)
        Screen.unlock(self._target)

        sleep(1)
        Screen.set_screen(self._target, on=False)
        sleep(1)
        self.tracingStart(screen_always_on=False)

        self._log.info('Waiting for duration {}'.format(duration_s))
        sleep(duration_s)

        self.tracingStop(screen_always_on=False)

# vim :set tabstop=4 shiftwidth=4 expandtab