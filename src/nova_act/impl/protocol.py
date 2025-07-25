# Copyright 2025 Amazon Inc

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
import json
from enum import Enum
from typing import Any, cast

from nova_act.impl.backend import BackendInfo
from nova_act.types.act_errors import (
    ActActuationError,
    ActAgentError,
    ActBadRequestError,
    ActBadResponseError,
    ActCanceledError,
    ActExceededMaxStepsError,
    ActGuardrailsError,
    ActInternalServerError,
    ActInvalidInputError,
    ActModelError,
    ActNotAuthorizedError,
    ActProtocolError,
    ActRateLimitExceededError,
    ActServiceUnavailableError,
    ActTimeoutError,
)
from nova_act.types.errors import AuthError
from nova_act.types.state.act import Act, ActFailed

NOVA_ACT_SERVICE = "NovaActService"
NOVA_ACT_CLIENT = "NovaActClient"


class NovaActClientErrors(Enum):
    BAD_RESPONSE = "BAD_RESPONSE"
    MAX_STEPS_EXCEEDED = "MAX_STEPS_EXCEEDED"
    ACTUATION_ERROR = "ACTUATION_ERROR"


class NovaActServiceError(Enum):
    INVALID_INPUT = "INVALID_INPUT"
    MODEL_ERROR = "MODEL_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    GUARDRAILS_ERROR = "GUARDRAILS_ERROR"
    UNAUTHORIZED_ERROR = "UNAUTHORIZED_ERROR"
    TOO_MANY_REQUESTS = "TOO_MANY_REQUESTS"
    DAILY_QUOTA_LIMIT_ERROR = "DAILY_QUOTA_LIMIT_ERROR"


def parse_errors(act: Act, backend_info: BackendInfo, extension_version: str):
    if not isinstance(act.result, ActFailed) or not act.is_complete:
        raise ValueError(f"Expected ActFailed result when attempting to parse, got act: {act}")

    result = cast(ActFailed, act.result)
    message = result.response
    error = message.get("error", "")

    if act.did_timeout:
        return ActTimeoutError(metadata=act.metadata)
    if message.get("subErrorCode") == "AGENT_ERROR":
        return ActAgentError(message=error, metadata=act.metadata)
    if error == "Canceled.":
        return ActCanceledError(metadata=act.metadata)

    try:
        error_message = json.loads(error)
        request_id = error_message.get("requestId", "")
    except json.JSONDecodeError:
        return ActProtocolError(
            metadata=act.metadata,
            message="failed to load error message as json",
            raw_message=json.dumps(error),
            extension_version=extension_version,
        )

    if "type" not in error_message:
        return ActProtocolError(
            metadata=act.metadata,
            message="missing type in error message",
            failed_request_id=request_id,
            raw_message=json.dumps(error),
            extension_version=extension_version,
        )

    if error_message.get("type") == NOVA_ACT_SERVICE:
        return handle_nova_act_service_error(error_message, act, backend_info, extension_version)
    if error_message.get("type") == NOVA_ACT_CLIENT:
        return handle_nova_act_client_error(error_message, act, extension_version)

    return ActProtocolError(
        metadata=act.metadata,
        message="unhandled failure type",
        failed_request_id=request_id,
        raw_message=error,
        extension_version=extension_version,
    )


def handle_nova_act_service_error(error: dict, act: Act, backend_info: BackendInfo, extension_version: str | None):
    request_id = error.get("requestId", "")
    code = error.get("code")
    message = error.get("message")

    if isinstance(code, str):
        error = _handle_service_error_with_string_code(error, act)
        return error

    if not isinstance(code, int) or code == -1:
        return ActProtocolError(
            metadata=act.metadata,
            message="invalid error code in Server Response",
            failed_request_id=request_id,
            raw_message=json.dumps(error),
            extension_version=extension_version,
        )

    if 400 == code:
        error_dict = check_error_is_json(message)
        if error_dict is None:
            return ActBadRequestError(
                metadata=act.metadata, failed_request_id=request_id, raw_message=json.dumps(error)
            )

        if "AGENT_GUARDRAILS_TRIGGERED" == error_dict.get("reason"):
            return ActGuardrailsError(message=error_dict, metadata=act.metadata)
        if "INVALID_INPUT" == error_dict.get("reason"):
            return ActInvalidInputError(metadata=act.metadata)
        if "MODEL_ERROR" == error_dict.get("reason"):
            return ActModelError(message=error_dict, metadata=act.metadata)
    if 403 == code:
        raise AuthError(backend_info, request_id=request_id)
        # else continue, fall back to generic 4xx
    if 429 == code:
        maybe_error_dict = check_error_is_json(message)
        return ActRateLimitExceededError(
            message=maybe_error_dict,
            metadata=act.metadata,
            failed_request_id=request_id,
            raw_message=json.dumps(error),
        )
    # 4xx
    if code < 500 and code >= 400:
        return ActBadRequestError(metadata=act.metadata, failed_request_id=request_id, raw_message=json.dumps(error))
    if 503 == code:
        return ActServiceUnavailableError(
            metadata=act.metadata, failed_request_id=request_id, raw_message=json.dumps(error)
        )
    # 5xx
    if code < 600 and code >= 500:
        return ActInternalServerError(
            metadata=act.metadata, failed_request_id=request_id, raw_message=json.dumps(error)
        )

    return ActProtocolError(
        message="Unhandled NovaActService error",
        metadata=act.metadata,
        failed_request_id=request_id,
        raw_message=json.dumps(error),
        extension_version=extension_version,
    )


def handle_nova_act_client_error(error: dict, act: Act, extension_version: str | None):
    request_id = error.get("requestId", "")
    code = error.get("code", "")

    try:
        error_type = NovaActClientErrors[code]
    except (KeyError, TypeError, ValueError, IndexError) as e:
        return ActProtocolError(
            message="invalid NovaActClient error code",
            metadata=act.metadata,
            failed_request_id=request_id,
            raw_message=str(e),
            extension_version=extension_version,
        )

    if error_type == NovaActClientErrors.BAD_RESPONSE:
        return ActBadResponseError(metadata=act.metadata, failed_request_id=request_id, raw_message=json.dumps(error))
    if error_type == NovaActClientErrors.MAX_STEPS_EXCEEDED:
        return ActExceededMaxStepsError(metadata=act.metadata)
    if error_type == NovaActClientErrors.ACTUATION_ERROR:
        return ActActuationError(metadata=act.metadata, message=error.get("message", ""))

    return ActProtocolError(
        message="Unhandled NovaActClient error",
        metadata=act.metadata,
        failed_request_id=request_id,
        raw_message=json.dumps(error),
        extension_version=extension_version,
    )


def check_error_is_json(message: Any) -> dict | None:
    try:
        return json.loads(message)
    except (json.JSONDecodeError, TypeError):
        return None


def _handle_service_error_with_string_code(error: dict, act: Act):
    """Translates errors returned by Nova Act backends that return string error codes."""
    code = error.get("code", "")
    message: str | None = error.get("message")

    try:
        error_type = NovaActServiceError[code]
    except (KeyError, TypeError, ValueError, IndexError):
        return ActProtocolError(
            message=f"invalid NovaActService error code: {code}",
            metadata=act.metadata,
        )

    if error_type == NovaActServiceError.INVALID_INPUT:
        return ActInvalidInputError(message=message, metadata=act.metadata)

    if error_type == NovaActServiceError.INTERNAL_ERROR:
        return ActInternalServerError(message=message, metadata=act.metadata)

    if error_type == NovaActServiceError.UNAUTHORIZED_ERROR:
        return ActNotAuthorizedError(
            message="Access denied. To request access, email nova-act@amazon.com with your use case.",
            metadata=act.metadata,
        )

    if error_type == NovaActServiceError.MODEL_ERROR:
        message_fields = {"fields": [{"message": message}]}
        return ActModelError(message=message_fields, metadata=act.metadata)

    if error_type == NovaActServiceError.GUARDRAILS_ERROR:
        message_fields = {"fields": [{"message": message}]}
        return ActGuardrailsError(message=message_fields, metadata=act.metadata)

    if error_type == NovaActServiceError.TOO_MANY_REQUESTS:
        message_dict = {
            "throttleType": "RATE_LIMIT_EXCEEDED",
        }
        return ActRateLimitExceededError(message=message_dict, metadata=act.metadata, raw_message=message)

    if error_type == NovaActServiceError.DAILY_QUOTA_LIMIT_ERROR:
        message_dict = {
            "throttleType": "DAILY_QUOTA_LIMIT_EXCEEDED",
        }
        return ActRateLimitExceededError(message=message_dict, metadata=act.metadata, raw_message=message)

    return ActProtocolError(
        message=f"Unhandled NovaActService error: {code}",
        metadata=act.metadata,
    )
