import datetime


def _s3_key_prefix(prefix, date, account_id, region):
    pass
    return f"{prefix}/AWSLogs/{account_id}/CloudTrail/{region}/{date.year}/{date.month:02d}/{date.day:02d}"


def _s3_key_prefixes(prefix, past_days, account_ids, regions):
    now = datetime.datetime.now()
    days = [now - datetime.timedelta(days=delta_days) for delta_days in range(past_days + 1)]
    return [_s3_key_prefix(prefix, day, account_id, region)
            for account_id in account_ids
            for day in days
            for region in regions]
