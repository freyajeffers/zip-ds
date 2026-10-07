import asyncio
import time
from collections.abc import Callable

from pydantic import BaseModel, ConfigDict, Field


class TokenBucketSettings(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    capacity: int = Field(ge=1)
    refill_rate: float = Field(gt=0.0, allow_inf_nan=False)


class TokenBucket:
    def __init__(
        self, settings: TokenBucketSettings, clock: Callable[[], float] | None = None
    ) -> None:
        if not isinstance(settings, TokenBucketSettings):
            raise TypeError("settings must be TokenBucketSettings")
        self.capacity = float(settings.capacity)
        self.refill_rate = settings.refill_rate
        self._tokens = self.capacity
        self._updated_at = (clock or time.monotonic)()
        self._clock = clock or time.monotonic

    def _refill(self) -> None:
        now = self._clock()
        elapsed = max(0.0, now - self._updated_at)
        self._tokens = min(self.capacity, self._tokens + elapsed * self.refill_rate)
        self._updated_at = now

    def try_acquire(self, tokens: float = 1.0) -> bool:
        if not isinstance(tokens, float) or tokens <= 0.0 or tokens > self.capacity:
            raise ValueError("tokens must be positive and no greater than capacity")
        self._refill()
        if self._tokens < tokens:
            return False
        self._tokens -= tokens
        return True

    async def acquire(self, tokens: float = 1.0) -> None:
        while not self.try_acquire(tokens):
            self._refill()
            wait_seconds = (tokens - self._tokens) / self.refill_rate
            await asyncio.sleep(max(0.0, wait_seconds))
