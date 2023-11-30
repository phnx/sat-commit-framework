import time
import calendar

from github import Github


def rate_limit_watcher(g: Github):
    try:
        core_rate_limit = g.get_rate_limit().core

        if (
            core_rate_limit.remaining / core_rate_limit.limit
        ) * 100 < 5:  # keep 5% boundary
            print("rate limit at 5% lower end: sleep until reset time")
            reset_timestamp = calendar.timegm(core_rate_limit.reset.timetuple())
            sleep_time = reset_timestamp - calendar.timegm(time.gmtime()) + 5
            time.sleep(sleep_time)

    except Exception as ex:
        print("get rate limit error: pause 2 minutes for cooling down", str(ex))
        time.sleep(120)
