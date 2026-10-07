from zip_ds.queries.limiter import TokenBucket, TokenBucketSettings


def test_token_bucket_allows_capacity_then_denies_until_refill():
    now = [100.0]
    bucket = TokenBucket(TokenBucketSettings(capacity=2, refill_rate=1.0), clock=lambda: now[0])

    assert bucket.try_acquire() is True
    assert bucket.try_acquire() is True
    assert bucket.try_acquire() is False

    now[0] += 1.0
    assert bucket.try_acquire() is True


def test_token_bucket_never_exceeds_capacity_after_long_idle_period():
    now = [100.0]
    bucket = TokenBucket(TokenBucketSettings(capacity=2, refill_rate=1.0), clock=lambda: now[0])

    now[0] += 100.0

    assert bucket.try_acquire() is True
    assert bucket.try_acquire() is True
    assert bucket.try_acquire() is False


def test_token_bucket_settings_reject_invalid_values():
    import pytest

    with pytest.raises(ValueError):
        TokenBucketSettings(capacity=0, refill_rate=1.0)
    with pytest.raises(ValueError):
        TokenBucketSettings(capacity=1, refill_rate=0.0)
