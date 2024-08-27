# Copyright 2016-2024 Neuraville Inc. Authors. All Rights Reserved.
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
# ==============================================================================


from fastapi import APIRouter

from ...schemas import BurstEngine
from ...commons import *

from src.inf import runtime_data


router = APIRouter()


# ######  Burst-Engine Endpoints #########
# ########################################
@router.get("/burst_counter")
async def burst_engine_params():
    """
    Return the number associated with current FEAGI burst instance.
    """
    if runtime_data.burst_count:
        return runtime_data.burst_count


@router.get("/stimulation_period")
async def burst_engine_params():
    """
    Returns the time it takes for each burst to execute in seconds.
    """
    if runtime_data.burst_timer:
        return runtime_data.burst_timer


@router.post("/stimulation_period")
async def change_stimulation_period(message: BurstEngine):
    """
    Enables changes against various Burst Engine parameters.
    """

    message = message.dict()
    message = {'burst_management': message}
    api_queue.put(item=message)
