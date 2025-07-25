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
import dataclasses
from abc import ABC

from nova_act.__version__ import EXTENSION_VERSION
from nova_act.types.act_metadata import ActMetadata
from nova_act.types.errors import NovaActError


# Decorator for allowing optional messages to override the default messages while keeping metadata mandatory
def act_error_class(default_message: str):
    def decorator(cls):
        @dataclasses.dataclass(frozen=True, repr=False)
        class wrapped(cls):
            _DEFAULT_MESSAGE = default_message

            def __init__(
                self,
                *,
                metadata: ActMetadata,
                message: str | None = None,
                extension_version: str | None = None,
                **kwargs,
            ):
                if extension_version is not None:
                    message = check_extension_version(extension_version, message=message)
                super().__init__(metadata=metadata, message=message)
                wrapped.__name__ = cls.__name__
                for key, value in kwargs.items():
                    object.__setattr__(self, key, value)

        wrapped.__qualname__ = cls.__qualname__
        return wrapped

    return decorator


def check_extension_version(extension_version: str | None, *, message: str | None):
    if extension_version is not None and extension_version != EXTENSION_VERSION:
        warning = (
            "Detected incompatible extension version, indicating a corrupted installation. "
            "Re-install nova-act to proceed."
            f"Expected: {EXTENSION_VERSION} Received: {extension_version}"
        )
        if message is not None:
            message = message + "; " + warning
        else:
            message = warning
    return message


"""
Base classes for Errors Occurring during act()
"""


@dataclasses.dataclass(frozen=True, repr=False)
class ActError(NovaActError):
    metadata: ActMetadata
    message: str = dataclasses.field(init=False)
    _DEFAULT_MESSAGE = "An error occurred during act()"

    def __init__(self, *, metadata: ActMetadata, message: str | None = None, extension_version: str | None = None):
        final_message = message or self.__class__._DEFAULT_MESSAGE
        super().__init__(final_message)
        object.__setattr__(self, "metadata", metadata)
        object.__setattr__(self, "message", final_message)

    def __str__(self) -> str:
        try:
            # Get all dataclass fields
            field_strings = []
            for field in dataclasses.fields(self):
                value = getattr(self, field.name)
                if value is not None:  # Only include non-None values
                    if field.name == "metadata":
                        line_break = "\n"
                        metadata_str = f"    {field.name} = {str(value).replace(line_break, line_break + '    ')}"
                    else:
                        field_strings.append(f"    {field.name} = {str(value)}")

            if metadata_str:
                field_strings.append(metadata_str)
            fields_str = "\n".join(field_strings)

            return (
                f"\n\n{self.__class__.__name__}(\n"
                f"{fields_str}\n"
                f")"
                "\n\nPlease consider providing feedback: "
                "https://amazonexteu.qualtrics.com/jfe/form/SV_bd8dHa7Em6kNkMe"
            )
        except Exception as e:
            return f"Error in __str__: {e}"


@dataclasses.dataclass(frozen=True, repr=False)
class ActServerError(ActError, ABC):
    failed_request_id: str | None = None

    def __init__(
        self,
        *,
        metadata: ActMetadata,
        message: str | None = None,
        failed_request_id: str | None = None,
        raw_message: str | None = None,
        extension_version: str | None = None,
    ):
        super().__init__(metadata=metadata, message=message)
        object.__setattr__(self, "failed_request_id", failed_request_id)


@dataclasses.dataclass(frozen=True, repr=False)
class ActClientError(ActError, ABC):
    extension_version: str | None = None

    def __init__(self, *, metadata: ActMetadata, message: str | None = None, extension_version: str | None = None):
        super().__init__(metadata=metadata, message=message, extension_version=extension_version)


@dataclasses.dataclass(frozen=True, repr=False)
class ActPromptError(ActError, ABC):
    """Represents an error specific to the given prompt."""

    def __init__(self, *, metadata: ActMetadata, message: dict):

        fields = message.get("fields", [])
        if fields is not None and len(fields) > 0:
            super().__init__(message=fields[0].get("message"), metadata=metadata)
        else:
            super().__init__(metadata=metadata)


"""
Concrete Errors

"""


@act_error_class("The requested action was not possible")
class ActAgentError(ActError):
    pass


@act_error_class("The model output could not be processed. Please try a different request.")
class ActModelError(ActPromptError):
    pass


@act_error_class("I'm sorry, but I can't engage in unsafe or inappropriate actions. Please try a different request.")
class ActGuardrailsError(ActPromptError):
    pass


@act_error_class("Timed out, you can modify the 'timeout' kwarg on the 'act' call")
class ActTimeoutError(ActError):
    pass


@act_error_class("Allowed Steps Exceeded")
class ActExceededMaxStepsError(ActError):
    pass


@act_error_class("Act Canceled")
class ActCanceledError(ActError):
    pass


@act_error_class("Failed to dispatch act")
class ActDispatchError(ActClientError):

    def __init__(
        self,
        *,
        metadata: ActMetadata,
        message: str | None = None,
        extension_version: str | None = None,
    ):
        super().__init__(
            metadata=metadata,
            message=message,
            extension_version=extension_version,
        )


@act_error_class("Internal Server Error")
class ActInternalServerError(ActServerError):
    pass


@act_error_class("Not Authorized. Check your current IAM role by running 'aws sts get-caller-identity'.")
class ActNotAuthorizedError(ActServerError):
    pass


@act_error_class("Server Unavailable")
class ActServiceUnavailableError(ActServerError):
    pass


@act_error_class("Rate Limit Error")
class ActRateLimitExceededError(ActServerError):
    _QUOTA_MESSAGE = (
        "We have quota limits to ensure sufficient capacity for all users. If you need dedicated "
        "quota for a more ambitious project, please get in touch at nova-act@amazon.com. "
        "We're excited to see what you build!"
    )

    def __init__(
        self,
        *,
        metadata: ActMetadata,
        message: dict | None,
        failed_request_id: str | None = None,
        raw_message: str | None = None,
    ):

        if message is not None and "DAILY_QUOTA_LIMIT_EXCEEDED" == message.get("throttleType"):
            super().__init__(
                metadata=metadata,
                message="Daily API limit exceeded. " + self._QUOTA_MESSAGE,
                failed_request_id=failed_request_id,
                raw_message=raw_message,
            )
        elif message is not None and "RATE_LIMIT_EXCEEDED" == message.get("throttleType"):
            super().__init__(
                message="Too many requests in a short time period. " + self._QUOTA_MESSAGE,
                metadata=metadata,
                failed_request_id=failed_request_id,
                raw_message=raw_message,
            )
        else:
            super().__init__(
                metadata=metadata,
                message=self._QUOTA_MESSAGE,
                failed_request_id=failed_request_id,
                raw_message=raw_message,
            )


@act_error_class("Failed to parse response")
class ActProtocolError(ActServerError, ActClientError):

    def __init__(
        self,
        *,
        metadata: ActMetadata,
        message: str | None = None,
        failed_request_id: str | None = None,
        raw_message: str | None = None,
        extension_version: str | None = None,
    ):
        super().__init__(
            metadata=metadata,
            message=message,
            failed_request_id=failed_request_id,
            raw_message=raw_message,
            extension_version=extension_version,
        )


@act_error_class("Invalid Input")
class ActInvalidInputError(ActClientError):
    pass


@act_error_class("Actuation Error")
class ActActuationError(ActClientError):
    pass


@act_error_class("Bad Request")
class ActBadRequestError(ActProtocolError):
    pass


@act_error_class("Bad Response")
class ActBadResponseError(ActProtocolError):
    pass
