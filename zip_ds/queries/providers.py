import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from pydantic import BaseModel, ConfigDict, Field

from zip_ds.models import ValidatedModel
from zip_ds.queries.models import SearchCandidate


class ProviderError(RuntimeError):
    """Base provider error."""


class ProviderRateLimit(ProviderError):
    """Raised when a provider returns a rate-limit (HTTP 429) or quota error."""


class ProviderClient(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    name: str = Field(min_length=1)
    call: Callable[[str], Awaitable[list[SearchCandidate]]]


class ProviderStatus(ValidatedModel):
    """Observable provider circuit-breaker state without exposing credentials."""

    name: str = Field(min_length=1)
    available: bool
    failed_until: float = Field(ge=0.0)


@dataclass
class ProviderState:
    client: ProviderClient
    failed_until: float = 0.0


class ProviderManager:
    """Dispatches queries to a primary provider and fails over to secondaries on rate-limit.

    Circuit breaker: when a provider raises ProviderRateLimit, it is cooled-off
    for `cooldown` seconds and the next provider in the list is tried. If all
    providers fail, ProviderRateLimit is propagated.
    """

    def __init__(
        self,
        providers: list[ProviderClient],
        cooldown: float = 60.0,
        clock: Callable[[], float] | None = None,
    ) -> None:
        if not providers:
            raise ValueError("providers list must be non-empty")
        self._clock = clock or time.monotonic
        self._states = [ProviderState(client=p) for p in providers]
        self._cooldown = float(cooldown)

    async def search(self, query: str) -> list[SearchCandidate]:
        last_exc: Exception | None = None
        now = self._clock()
        for state in self._states:
            if state.failed_until > now:
                continue
            try:
                return await state.client.call(query)
            except ProviderRateLimit as exc:
                state.failed_until = self._clock() + self._cooldown
                last_exc = exc
                continue
            except (OSError, TimeoutError, ValueError, RuntimeError) as exc:
                last_exc = exc
                continue
        if last_exc is not None:
            if isinstance(last_exc, ProviderRateLimit):
                raise last_exc
            raise ProviderError("all providers failed") from last_exc
        raise ProviderError("no available providers")

    def statuses(self) -> list[ProviderStatus]:
        """Return current provider availability for downgraded-coverage reporting."""
        now = self._clock()
        return [
            ProviderStatus(
                name=state.client.name,
                available=state.failed_until <= now,
                failed_until=state.failed_until,
            )
            for state in self._states
        ]
