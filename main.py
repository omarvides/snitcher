import core
from os import environ
from datetime import date, datetime

domain = environ.get("DOMAIN", None)
port = environ.get("PORT", 443)
webhook = environ.get("WEBHOOK", None)
channel = environ.get("CHANNEL", None)


def main():
    not_after = core.get_notafter(domain, port)
    today = datetime.today()
    days_to_expire = core.get_days_to_expire(not_after, today)
    should_notify = core.should_notify(days_to_expire)
    if should_notify["notify"]:
        slack_message = core.build_slack_message(
            channel, "Snitcher bot", should_notify["level"], domain, days_to_expire, "days", "cyberei")
        core.notify_slack(slack_message, webhook)


if __name__ == '__main__':
    main()
