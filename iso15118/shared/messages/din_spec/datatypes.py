"""
This modules contains classes which implement all the elements of the
ISO DIN SPEC 70121 XSD file V2G_CI_DataTypes.xsd (see folder 'schemas').
These are the data types used by both the header and the body elements of the
V2GMessages exchanged between the EVCC and the SECC.

All classes are ultimately subclassed from pydantic's BaseModel to ease
validation when instantiating a class and to reduce boilerplate code.
Pydantic's Field class is used to be able to create a json schema of each model
(or class) that matches the definitions in the XSD schema, including the XSD
element names by using the 'alias' attribute.
"""

from enum import Enum, IntEnum
from typing import List
from pydantic import Field, conbytes, root_validator

from iso15118.shared.messages.datatypes_iso15118_2_dinspec import (
    PhysicalValue,
    PVEVSENominalVoltage,
    PVEAmount,
    PVEVMaxVoltage,
    PVEVMaxCurrent,
    PVEVMinCurrent,
    PVEVMaxPowerLimit,
    PVEVMaxVoltageLimit,
    PVEVEnergyCapacity,
    PVEVEnergyRequest,
    PVStartValue,
    PVEVMaxCurrentLimit,
    PVEVSEMaxCurrent,
)
from iso15118.shared.messages import BaseModel
from iso15118.shared.messages.enums import (
    INT_8_MAX,
    INT_8_MIN,
    INT_16_MAX,
    INT_16_MIN,
    UINT_32_MAX,
    EnergyTransferModeEnum,
    DCEVErrorCode,
)

from iso15118.shared.validators import one_field_must_be_set


# https://pydantic-docs.helpmanual.io/usage/types/#constrained-types
# constrained types
# Check Annex C.6 or the certificateType in V2G_CI_MsgDataTypes.xsd
Certificate = conbytes(max_length=800)


class EnergyTransferModeList(BaseModel):
    """See section 8.5.2.4 in ISO 15118-2"""

    energy_modes: List[EnergyTransferModeEnum] = Field(
        ..., max_items=6, alias="EnergyTransferMode"
    )


class ServiceID(IntEnum):
    """See section 8.4.3.3.2 in ISO 15118-2"""

    CHARGING = 1
    CERTIFICATE = 2
    INTERNET = 3
    # There's conflicting information in the standard. Annex C.6 (page 269)
    # lists this as 'OtherCustom', but Table 105 lists this as 'EVSEInformation'
    # ("Service enabling the exchange of use case specific information about
    # the EVSE"). No idea what they mean by that, so we go with 'OtherCustom'.
    CUSTOM = 4


class ServiceCategory(str, Enum):
    """Annex A.1.1.6 in DIN SPEC 70121"""

    CHARGING = "EVCharging"
    CERTIFICATE = "ContractCertificate"
    INTERNET = "Internet"
    CUSTOM = "OtherCustom"


class ServiceName(str, Enum):
    """
    In the scope of DIN SPEC 70121, the optional element “ServiceName”
    shall not be used.
    """

    CHARGING = "AC_DC_Charging"
    CERTIFICATE = "Certificate"
    INTERNET = "InternetAccess"
    CUSTOM = "UseCaseInformation"


class ServiceDetails(BaseModel):
    """
    See section 9.5.2.1 in DIN SPEC 70121
    [V2G-DC-628] In the scope of DIN SPEC 70121, the optional
    element “ServiceName” shall not be used.
    [V2G-DC-629] In the scope of DIN SPEC 70121, the optional
    element “ServiceScope” shall not be used.
    """

    # XSD type unsignedShort (16 bit integer) with value range [0..65535]
    service_id: ServiceID = Field(..., ge=0, le=65535, alias="ServiceID")
    service_name: ServiceName = Field(None, max_length=32, alias="ServiceName")
    service_category: ServiceCategory = Field(..., alias="ServiceCategory")
    service_scope: str = Field(None, max_length=64, alias="ServiceScope")


class ChargeService(BaseModel):
    """See section 9.5.2.3 in DIN SPEC 70121"""

    service_tag: ServiceDetails = Field(..., alias="ServiceTag")
    free_service: bool = Field(..., alias="FreeService")
    energy_transfer_type: EnergyTransferModeEnum = Field(
        ..., alias="EnergyTransferType"
    )


class PaymentOptionType(BaseModel):
    paymentOptionType: str = Field(..., alias="PaymentOptionType")


class ContractID(BaseModel):
    contract_id: str = Field(..., max_length=24, alias="ContractID")


class EVSENotification(str, Enum):
    """See sections 8.5.3.1 and 8.5.4.1 in ISO 15118-2"""

    NONE = "None"
    STOP_CHARGING = "StopCharging"
    RE_NEGOTIATION = "ReNegotiation"


class EVSEStatus(BaseModel):
    """See sections 8.5.3.1 and 8.5.4.1 in ISO 15118-2"""

    # XSD type unsignedShort (16 bit integer) with value range [0..65535]
    notification_max_delay: int = Field(
        ..., ge=0, le=65535, alias="NotificationMaxDelay"
    )
    evse_notification: EVSENotification = Field(..., alias="EVSENotification")


class ACEVSEStatus(EVSEStatus):
    """See section 8.5.3.1 in ISO 15118-2"""

    rcd: bool = Field(..., alias="RCD")


class ACEVSEChargeParameter(BaseModel):
    """See section 8.5.3.3 in ISO 15118-2"""

    ac_evse_status: ACEVSEStatus = Field(..., alias="AC_EVSEStatus")
    evse_nominal_voltage: PVEVSENominalVoltage = Field(..., alias="EVSENominalVoltage")
    evse_max_current: PVEVSEMaxCurrent = Field(..., alias="EVSEMaxCurrent")


class EVChargeParameter(BaseModel):
    """See section 8.4.3.8.2 in ISO 15118-2"""


class ACEVChargeParameter(EVChargeParameter):
    """See section 8.5.3.2 in ISO 15118-2"""

    # XSD type unsignedInt (32-bit unsigned integer) with value range
    departure_time: int = Field(None, ge=0, le=UINT_32_MAX, alias="DepartureTime")
    e_amount: PVEAmount = Field(..., alias="EAmount")
    ev_max_voltage: PVEVMaxVoltage = Field(..., alias="EVMaxVoltage")
    ev_max_current: PVEVMaxCurrent = Field(..., alias="EVMaxCurrent")
    ev_min_current: PVEVMinCurrent = Field(..., alias="EVMinCurrent")


class ServiceList(BaseModel):
    """See section 8.5.2.2 in ISO 15118-2"""

    services: List[ServiceDetails] = Field(..., max_items=8, alias="Service")


class ValueType(str, Enum):
    BOOL_TYPE = "bool"
    BYTE_TYPE = "byte"
    SHORT_TYPE = "short"
    INT_TYPE = "int"
    PHYSICAL_VALUE_TYPE = "physicalValue"
    STRING_TYPE = "string"


class Parameter(BaseModel):
    """See section 8.5.2.23 in ISO 15118-2"""

    # 'Name' is actually an XML attribute, but JSON (our serialisation method)
    # doesn't have attributes. The EXI codec has to en-/decode accordingly.
    name: str = Field(..., alias="Name")
    bool_value: bool = Field(None, alias="boolValue")
    # XSD type byte with value range [-128..127]
    byte_value: int = Field(None, ge=INT_8_MIN, le=INT_8_MAX, alias="byteValue")
    # XSD type short (16 bit integer) with value range [-32768..32767]
    short_value: int = Field(None, ge=INT_16_MIN, le=INT_16_MAX, alias="shortValue")
    int_value: int = Field(None, alias="intValue")
    physical_value: PhysicalValue = Field(None, alias="physicalValue")
    str_value: str = Field(None, alias="stringValue")
    value_type: ValueType = Field(..., alias="ValueType")

    @root_validator(pre=True)
    def at_least_one_parameter_value(cls, values):
        """
        Either bool_value, byte_value, short_value, int_value, physical_value,
        or str_value must be set, depending on the datatype of the parameter.

        Pydantic validators are "class methods",
        see https://pydantic-docs.helpmanual.io/usage/validators/
        """
        # pylint: disable=no-self-argument
        # pylint: disable=no-self-use
        if one_field_must_be_set(
            [
                "bool_value",
                "boolValue",
                "byte_value",
                "byteValue",
                "short_value",
                "shortValue",
                "int_value",
                "intValue",
                "physical_value",
                "physicalValue",
                "str_value",
                "stringValue",
            ],
            values,
            True,
        ):
            return values


class ParameterSet(BaseModel):
    """TODO: NO description found in spec"""

    parameter_set_id: int = Field(..., ge=0, le=65535, alias="ParameterSetID")
    parameter: List[Parameter] = Field(..., max_items=16, alias="Parameter")


class ServiceParameterList(BaseModel):
    """TODO: NO description found in spec"""

    parameter_set: List[ParameterSet] = Field(..., max_items=255, alias="ParameterSet")


class SelectedService(BaseModel):
    """See section 9.5.2.14 in DIN SPEC 70121"""

    # XSD type unsignedShort (16 bit integer) with value range [0..65535]
    service_id: int = Field(..., ge=0, le=65535, alias="ServiceID")
    # XSD type unsignedShort (16 bit integer) with value range [0..65535]
    parameter_set_id: int = Field(None, ge=0, le=65535, alias="ParameterSetID")


class SelectedServiceList(BaseModel):
    """See section 9.5.2.13 in DIN SPEC 70121"""

    selected_service: List[SelectedService] = Field(
        ..., max_items=16, alias="SelectedService"
    )


class CostKind(str, Enum):
    """See section 8.5.2.20 in ISO 15118-2"""

    RELATIVE_PRICE_PERCENTAGE = "relativePricePercentage"
    RENEWABLE_GENERATION_PERCENTAGE = "RenewableGenerationPercentage"
    CARBON_DIOXIDE_EMISSION = "CarbonDioxideEmission"


class Cost(BaseModel):
    """See section 8.5.2.20 in ISO 15118-2"""

    cost_kind: CostKind = Field(..., alias="costKind")
    amount: int = Field(..., alias="amount")
    # XSD type byte with value range [-3..3]
    amount_multiplier: int = Field(None, ge=-3, le=3, alias="amountMultiplier")


class ConsumptionCost(BaseModel):
    """See section 8.5.2.19 in ISO 15118-2"""

    start_value: PVStartValue = Field(..., alias="startValue")
    cost: List[Cost] = Field(..., max_items=3, alias="Cost")


class RelativeTimeInterval(BaseModel):
    """See section 9.5.2.12 in DIN SPEC 70121"""

    start: int = Field(..., ge=0, le=16777214, alias="start")
    duration: int = Field(None, ge=0, le=86400, alias="duration")


class PMaxScheduleEntryDetails(BaseModel):
    """See section 9.5.2.10 in DIN SPEC 70121"""

    p_max: int = Field(..., ge=0, le=255, alias="PMax")
    time_interval: RelativeTimeInterval = Field(..., alias="RelativeTimeInterval")


class PMaxScheduleEntry(BaseModel):
    """See section 9.5.2.10 in DIN SPEC 70121"""

    p_max_schedule_id: int = Field(..., ge=0, le=255, alias="PMaxScheduleID")
    entry_details: List[PMaxScheduleEntryDetails] = Field(
        ..., max_items=1024, alias="PMaxScheduleEntry"
    )


class SalesTariffEntry(BaseModel):
    """NOT USED IN DIN SPEC 70121"""

    pass


class SalesTariff(BaseModel):
    """NOT USED IN DIN SPEC 70121"""

    pass


class SAScheduleTupleEntry(BaseModel):
    """See section 9.5.2.8 in DIN SPEC 70121"""

    # [V2G-DC-554] In the scope of DIN SPEC 70121, the element
    # “SalesTariff” shall not be used.

    # XSD type unsignedByte with value range [1..255]
    sa_schedule_tuple_id: int = Field(..., ge=1, le=255, alias="SAScheduleTupleID")
    p_max_schedule: PMaxScheduleEntry = Field(..., alias="PMaxSchedule")
    sales_tariff: SalesTariff = Field(None, alias="SalesTariff")


class SAScheduleList(BaseModel):
    values: List[SAScheduleTupleEntry] = Field(
        ..., max_items=3, alias="SAScheduleTuple"
    )


class ProfileEntryDetails(BaseModel):
    """See section 9.5.2.7 in DIN SPEC 70121"""

    start: int = Field(..., alias="ChargingProfileEntryStart")
    max_power: int = Field(..., ge=1, le=255, alias="ChargingProfileMaxPower")


class ChargingProfile(BaseModel):
    """See section 9.5.2.6 in DIN SPEC 70121"""

    sa_schedule_tuple_id: int = Field(..., ge=0, le=65535, alias="SAScheduleTupleID")
    profile_entries: List[ProfileEntryDetails] = Field(
        ..., max_items=24, alias="ProfileEntry"
    )


class DCEVSEStatusCode(str, Enum):
    """See Table 68 in DIN SPEC 70121"""

    EVSE_NOT_READY = "EVSE_NotReady"
    EVSE_READY = "EVSE_Ready"
    EVSE_SHUTDOWN = "EVSE_Shutdown"
    # XSD typo in "Interrupt"
    EVSE_UTILITY_INTERUPT_EVENT = "EVSE_UtilityInterruptEvent"
    EVSE_ISOLATION_MONITORING_ACTIVE = "EVSE_IsolationMonitoringActive"
    EVSE_EMERGENCY_SHUTDOWN = "EVSE_EmergencyShutdown"
    EVSE_MALFUNCTION = "EVSE_Malfunction"
    RESERVED_8 = "Reserved_8"
    RESERVED_9 = "Reserved_9"
    RESERVED_A = "Reserved_A"
    RESERVED_B = "Reserved_B"
    RESERVED_C = "Reserved_C"


class IsolationLevel(str, Enum):
    """See Table 67 in DIN SPEC (Section 9.5.3.1)"""

    INVALID = "Invalid"
    VALID = "Valid"
    WARNING = "Warning"
    FAULT = "Fault"


class DCEVStatus(BaseModel):
    """See Table 69 in section 9.5.3.2 in DIN SPEC 70121"""

    """
    For DC charging according to DINSPEC 70121, the elements EVReady,
    EVCabinConditioning and EVRESSConiditioning shall not affect the charging session.
    However, they may be used for customer information.
    """
    ev_ready: bool = Field(..., alias="EVReady")
    ev_cabin_conditioning: bool = Field(None, alias="EVCabinConditioning")
    ev_ress_conditioning: bool = Field(None, alias="EVRESSConditioning")
    ev_error_code: DCEVErrorCode = Field(..., alias="EVErrorCode")
    # XSD type byte with value range [0..100]
    ev_ress_soc: int = Field(..., ge=0, le=100, alias="EVRESSSOC")


class DCEVChargeParameter(EVChargeParameter):
    """See section 9.5.3.3 in DIN SPEC 70121"""

    dc_ev_status: DCEVStatus = Field(..., alias="DC_EVStatus")
    ev_maximum_current_limit: PVEVMaxCurrentLimit = Field(
        ..., alias="EVMaximumCurrentLimit"
    )
    """
    In the scope of DIN SPEC 70121, if the element “EVMaximumPowerLimit”
    is contained the message ChargeParameterDiscoveryReq, it shall represent
    the maximum power that the EV will request (by means of CurrentDemandReq)
    at any time during the charging process. If the element “EVMaximumPowerLimit”
    is contained in the message ChargeParameterDiscoveryReq, this allows the
    EVSE to compute suitable PMaxSchedules.
     """
    ev_maximum_power_limit: PVEVMaxPowerLimit = Field(None, alias="EVMaximumPowerLimit")
    ev_maximum_voltage_limit: PVEVMaxVoltageLimit = Field(
        ..., alias="EVMaximumVoltageLimit"
    )
    ev_energy_capacity: PVEVEnergyCapacity = Field(None, alias="EVEnergyCapacity")
    ev_energy_request: PVEVEnergyRequest = Field(None, alias="EVEnergyRequest")
    # XSD type byte with value range [0..100]
    full_soc: int = Field(None, ge=0, le=100, alias="FullSOC")
    # XSD type byte with value range [0..100]
    bulk_soc: int = Field(None, ge=0, le=100, alias="BulkSOC")


class DCEVPowerDeliveryParameter(BaseModel):
    """See section 8.5.4.5 in ISO 15118-2"""

    dc_ev_status: DCEVStatus = Field(..., alias="DC_EVStatus")
    bulk_charging_complete: bool = Field(None, alis="BulkChargingComplete")
    charging_complete: bool = Field(..., alias="ChargingComplete")


class PaymentOption(str, Enum):
    CONTRACT = "Contract"
    EXTERNAL_PAYMENT = "ExternalPayment"


class AuthOptionList(BaseModel):
    """
    See section 9.5.2.5 in DIN SPEC 70121
    For DIN SPEC, this list will only contain one item - External Payment
    """

    auth_options: List[PaymentOption] = Field(
        ..., min_items=1, max_items=2, alias="PaymentOption"
    )


class FaultCode(str, Enum):
    """See xml schema V2G_CI_MsgDataTypes.xsd"""

    PARSING_ERROR = "ParsingError"
    # Typo in XSD file ("Certificat")
    NO_TLS_ROOT_CERTIFICATE_AVAILABLE = "NoTLSRootCertificatAvailable"
    UNKNOWN_ERROR = "UnknownError"


class Notification(BaseModel):
    """See xml schema V2G_CI_MsgDataTypes.xsd (PAGE )"""

    fault_code: FaultCode = Field(..., alias="FaultCode")
    fault_msg: str = Field(None, max_length=64, alias="FaultMsg")

    def __str__(self):
        additional_info = f" ({self.fault_msg})" if self.fault_msg else ""
        return self.fault_code + additional_info


class ResponseCode(str, Enum):
    """See page 202 in DIN SPEC 70121:2014-12"""

    OK = "OK"
    OK_NEW_SESSION_ESTABLISHED = "OK_NewSessionEstablished"
    OK_OLD_SESSION_JOINED = "OK_OldSessionJoined"
    OK_CERTIFICATE_EXPIRES_SOON = "OK_CertificateExpiresSoon"
    FAILED = "FAILED"
    FAILED_SEQUENCE_ERROR = "FAILED_SequenceError"
    FAILED_SERVICE_ID_INVALID = "FAILED_ServiceIDInvalid"
    FAILED_UNKNOWN_SESSION = "FAILED_UnknownSession"
    FAILED_SERVICE_SELECTION_INVALID = "FAILED_ServiceSelectionInvalid"
    FAILED_PAYMENT_SELECTION_INVALID = "FAILED_PaymentSelectionInvalid"
    FAILED_CERTIFICATE_EXPIRED = "FAILED_CertificateExpired"
    FAILED_SIGNATURE_ERROR = "FAILED_SignatureError"
    FAILED_NO_CERTIFICATE_AVAILABLE = "FAILED_NoCertificateAvailable"
    FAILED_CERT_CHAIN_ERROR = "FAILED_CertChainError"
    FAILED_CHALLENGE_INVALID = "FAILED_ChallengeInvalid"
    FAILED_CONTRACT_CANCELED = "FAILED_ContractCanceled"
    FAILED_WRONG_CHARGE_PARAMETER = "FAILED_WrongChargeParameter"
    FAILED_POWER_DELIVERY_NOT_APPLIED = "FAILED_PowerDeliveryNotApplied"
    FAILED_TARIFF_SELECTION_INVALID = "FAILED_TariffSelectionInvalid"
    FAILED_CHARGING_PROFILE_INVALID = "FAILED_ChargingProfileInvalid"
    FAILED_EVSE_PRESENT_VOLTAGE_TO_LOW = "FAILED_EVSEPresentVoltageToLow"
    FAILED_METERING_SIGNATURE_NOT_VALID = "FAILED_MeteringSignatureNotValid"
    FAILED_WRONG_ENERGY_TRANSFER_MODE = "FAILED_WrongEnergyTransferMode"
