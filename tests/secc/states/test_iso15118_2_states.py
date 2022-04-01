import pytest
from unittest.mock import Mock

from tests.secc.states.test_messages import (
    get_dummy_v2g_message_welding_detection_req,
    get_sa_schedule_list,
    get_v2g_message_power_delivery_req,
)

from iso15118.secc.comm_session_handler import SECCCommunicationSession
from iso15118.secc.controller.simulator import SimEVSEController
from iso15118.secc.states.iso15118_2_states import (
    CurrentDemand,
    PowerDelivery,
    WeldingDetection,
)
from iso15118.shared.messages.enums import Protocol
from iso15118.shared.messages.iso15118_2.datatypes import EnergyTransferModeEnum
from iso15118.shared.notifications import StopNotification


@pytest.fixture
def comm_session_mock():
    comm_session_mock = Mock(spec=SECCCommunicationSession)
    comm_session_mock.session_id = "F9F9EE8505F55838"
    comm_session_mock.offered_schedules = get_sa_schedule_list()
    comm_session_mock.selected_energy_mode = EnergyTransferModeEnum.DC_EXTENDED
    comm_session_mock.selected_charging_type_is_ac = False
    comm_session_mock.stop_reason = StopNotification(False, "pytest")
    comm_session_mock.evse_controller = SimEVSEController()
    comm_session_mock.protocol = Protocol.UNKNOWN
    # to exi must return something or the V2GTPMessage creation fails during extraction
    # of the payload length
    comm_session_mock.to_exi = Mock(return_value=b'\x01')
    return comm_session_mock


def test_current_demand_to_power_delivery_when_power_delivery_received(
    comm_session_mock,
):
    current_demand = CurrentDemand(comm_session_mock)
    current_demand.expecting_current_demand_req = False
    current_demand.process_message(message=get_v2g_message_power_delivery_req())
    assert isinstance(comm_session_mock.current_state, PowerDelivery)


def test_power_delivery_to_welding_detection_when_welding_detection_received(
    comm_session_mock,
):
    # V2G2-601 (to WeldingDetection)
    power_delivery = PowerDelivery(comm_session_mock)
    power_delivery.expecting_power_delivery_req = False
    power_delivery.process_message(
        message=get_dummy_v2g_message_welding_detection_req()
    )
    assert isinstance(comm_session_mock.current_state, WeldingDetection)


def test_welding_detection_to_session_stop_when_session_stop_received(
    comm_session_mock,
):
    pass
    # V2G2-570
