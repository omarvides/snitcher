from dateutil.relativedelta import relativedelta
from datetime import datetime
from jinja2 import Template
import logging as logger
import requests
import OpenSSL
import json
import ssl


logger.basicConfig(
    format='%(asctime)s %(message)s',
    level=logger.INFO)


def get_notafter(domain, port=443):
    crt = ssl.get_server_certificate((domain, port))
    x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, crt)
    x509_date = x509.get_notAfter().decode('UTF-8')
    not_after = datetime.strptime(x509_date, "%Y%m%d%H%M%SZ")
    return not_after


def get_days_to_expire(not_after, compare_date):
    rd = relativedelta(not_after, compare_date)
    logger.debug(f"days before expiration {rd.days}")
    delta = not_after - compare_date
    return delta.days


def should_notify(days):
    # Fixed dates for now
    if days <= 7 and days >= 0:
        return {"notify": True, "level": "critical"}
    elif days <= 15 and days > 7:
        return {"notify": True, "level": "warning"}
    elif days <= 30 and days > 15:
        return {"notify": True, "level": "info"}
    else:
        return {"notify": False}


def notify_slack(message, webhook):
    # Plain request for now
    logger.info(f"Attempting to notify to slack channel")
    logger.debug(F"The message attempting to send to slack is {message}")
    logger.debug(F"The webhook is {webhook}")
    webhook = webhook
    data = message
    r = requests.post(webhook, json=data)
    logger.info(f"Slack API answered with status_code: {r.status_code}")
    logger.debug(f"The response text is: {r.text}")


def build_slack_message(channel, bot_name, level, domain, time_amount, units, organization):
    if level == "info" or level == "warning" or level == "critical":
        filename = f"snitcher/templates/{level}.json.j2"
    else:
        filename = f"snitcher/templates/info.json.j2"
    templ = open(filename, "r")

    jinja_template = Template(templ.read())
    result = jinja_template.render(channel=channel, bot_name=bot_name, level=level,
                                   domain=domain, time_amount=time_amount, units=units, organization=organization)
    templ.close()
    logger.debug(result)
    jsonresult = json.loads(result)
    return jsonresult
