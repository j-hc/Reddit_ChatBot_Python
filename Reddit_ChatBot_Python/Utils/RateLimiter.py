import time


class RateLimiter:
    is_enabled = False
    max_calls = 0
    period = 0
    _msg_counter = 0
    _period_end_ts = 0

    @staticmethod
    def _check():
        current_ts = RateLimiter._get_current_ts()
        if RateLimiter._period_end_ts < current_ts:
            RateLimiter._msg_counter = 0
            RateLimiter._create_new_period(current_ts)
        if RateLimiter._msg_counter > RateLimiter.max_calls:
            return True
        else:
            RateLimiter._msg_counter += 1
            return False

    @staticmethod
    def _create_new_period(current_ts):
        RateLimiter._period_end_ts = current_ts + RateLimiter.period * 60

    @staticmethod
    def _get_current_ts():
        return int(time.time())
