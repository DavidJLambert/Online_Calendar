from datetime import datetime, timedelta

delta_1_day = timedelta(days=1)


def us_can_dst(dt_now) -> bool:
    """
    Args:
        dt_now (datetime): the current datetime, in my timezone.

    Returns:
        boolean: True if today is daylight savings time in the United States and Canada.

    US and Canada DST starts on the second Sunday in March, and ends on the first Sunday in November.
    The output of weekday(): 0=Monday, 1=Tuesday, 2=Wednesday, 3=Thursday, 4=Friday, 5=Saturday, 6=Sunday.
    """
    this_year = dt_now.year

    march_1 = datetime(this_year, month=3, day=1)
    weekday_march_1 = march_1.weekday()
    march_2nd_sunday = march_1 + (7 + 6 - weekday_march_1)*delta_1_day

    november_1 = datetime(this_year, month=11, day=1)
    weekday_november_1 = november_1.weekday()
    november_1st_sunday = november_1 + (6 - weekday_november_1)*delta_1_day

    return march_2nd_sunday <= dt_now < november_1st_sunday


def eu_dst(dt_now) -> bool:
    """
    Args:
        dt_now (datetime): the current datetime, in my timezone.

    Returns:
        boolean: True if today is daylight savings time in the European Union.

    EU DST starts on the last Sunday of March and ends on the last Sunday of October.
    The output of weekday(): 0=Monday, 1=Tuesday, 2=Wednesday, 3=Thursday, 4=Friday, 5=Saturday, 6=Sunday.
    """
    this_year = dt_now.year

    march_31 = datetime(this_year, month=3, day=31)
    weekday_march_31 = march_31.weekday()
    if weekday_march_31 == 6:
        march_last_sunday = march_31
    else:
        march_last_sunday = march_31 - (1 + weekday_march_31)*delta_1_day

    october_31 = datetime(this_year, month=10, day=31)
    weekday_october_31 = october_31.weekday()
    if weekday_october_31 == 6:
        october_last_sunday = october_31
    else:
        october_last_sunday = october_31 - (1 + weekday_october_31)*delta_1_day

    return march_last_sunday <= dt_now < october_last_sunday


def get_timezones(dt_now):
    """
    Args:
        dt_now (datetime): the current datetime, in my timezone.

    Returns:
        long_tzs: dictionary with keys = UTC offsets, values = full name of a time zone with that UTC offset.
        short_tzs: dictionary with keys = UTC offsets, values = abbreviation of time zone with that UTC offset.
        utc: UTC offset of each time zone.
        files: the name of the file containing my schedule in that time zone.

    Reference: List of all time zones on this planet: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones

        I only pay attention to timezones with Type = "Canonical".

        The time zones with nothing under "Time zone abbreviation DST" do not have daylight savings time.
        The year around time zone abbreviation is listed under "Time zone abbreviation SDT",
        and their year around UTC offset is listed under "UTC offset SDT".

        The time zones with something under "Time zone abbreviation DST" do have daylight savings time.
        The two time zone abbreviations are listed "Time zone abbreviation SDT" and "Time zone abbreviation DST",
        and their UTC offsets are listed under "UTC offset SDT" and "UTC offset DST".

    Also useful: https://en.wikipedia.org/wiki/Time_zone.
    """

    long_tzs = dict()
    short_tzs = dict()
    utc = dict()
    files = dict()

    # Unlisted time zones.
    # 14

    # New Zealand and Australian East timezones.
    # Always show daylight and standard times, since we want all UTC offsets used.

    long_tzs[13] = "New Zealand Daylight Time"
    short_tzs[13] = "NZDT"

    long_tzs[12] = "New Zealand Standard Time"
    short_tzs[12] = "NZST"

    long_tzs[11] = "Australian E. Daylight Time"
    short_tzs[11] = "AEDT"

    long_tzs[10] = "Australian E. Standard Time"
    short_tzs[10] = "AEST"

    # Asian year-around timezones.

    long_tzs[9] = "Japan Standard Time"
    long_tzs[8] = "Singapore Time"
    long_tzs[7] = "Indochina Standard Time"
    long_tzs[6] = "Bangladesh Standard Time"
    long_tzs[5] = "Pakistan Standard Time"
    long_tzs[4] = "Gulf Standard Time"
    long_tzs[3] = "Saudi Arabia Standard Time"

    short_tzs[9] = "JST"
    short_tzs[8] = "SGT"
    short_tzs[7] = "ICT"
    short_tzs[6] = "BST"
    short_tzs[5] = "PKT"
    short_tzs[4] = "GST"
    short_tzs[3] = "SAST"

    # EU Timezones.

    if eu_dst(dt_now):
        long_tzs[3] = "Eastern European Summer Time" # Overwrites "Saudi Arabia Standard Time"/"SAST" 
        long_tzs[2] = "Central European Summer Time"
        long_tzs[1] = "British Summer Time"

        short_tzs[3] = "EEST" # Overwrites "Saudi Arabia Standard Time"/"SAST"
        short_tzs[2] = "CEST"
        short_tzs[1] = "BST"
    else:
        long_tzs[2] = "Eastern European Time"
        long_tzs[1] = "Central European Time"
        long_tzs[0] = "Greenwich Mean Time"

        short_tzs[2] = "EET"
        short_tzs[1] = "CET"
        short_tzs[0] = "GMT"

    # More unlisted time zones.
    #  0 (in the summer)
    # -1
    # -2

    # US/Canada Timezones.

    if us_can_dst(dt_now):
        long_tzs[-2.5] = "Newfoundland Daylight Time"
        short_tzs[-2.5] = "NDT"

        long_tzs[-3] = "Atlantic Daylight Time"
        long_tzs[-4] = "Eastern Daylight Time"
        long_tzs[-5] = "Central Daylight Time"
        long_tzs[-6] = "Mountain Daylight Time"
        long_tzs[-7] = "Pacific Daylight Time"
        long_tzs[-8] = "Alaska Daylight Time"

        short_tzs[-3] = "ADT"
        short_tzs[-4] = "EDT"
        short_tzs[-5] = "CDT"
        short_tzs[-6] = "MDT"
        short_tzs[-7] = "PDT"
        short_tzs[-8] = "AKDT"
    else:
        long_tzs[-3.5] = "Newfoundland Standard Time"
        short_tzs[-3.5] = "NST"

        long_tzs[-4] = "Atlantic Standard Time"
        long_tzs[-5] = "Eastern Standard Time"
        long_tzs[-6] = "Central Standard Time"
        long_tzs[-7] = "Mountain Standard Time"
        long_tzs[-8] = "Pacific Standard Time"
        long_tzs[-9] = "Alaska Standard Time"

        short_tzs[-4] = "AST"
        short_tzs[-5] = "EST"
        short_tzs[-6] = "CST"
        short_tzs[-7] = "MST"
        short_tzs[-8] = "PST"
        short_tzs[-9] = "AKST"

    # US year-around timezones.

    long_tzs[-10] = "Hawaii Standard Time"
    short_tzs[-10] = "HST"

    # More unlisted time zones.
    # -11
    # -12

    # Oddball timezones.  No attempt to calculate daylight standard time.
    long_tzs[10.5] = "Australia Central Daylight Time"
    short_tzs[10.5] = "ACDT"

    long_tzs[9.5] = "Australia Central Standard Time"
    short_tzs[9.5] = "ACST"

    # long_tzs[6.5] = "Myanmar Standard Time"
    # short_tzs[6.5] = "MMT"
    #
    # long_tzs[5.75] = "Nepal Standard Time"
    # short_tzs[5.75] = "NPT"

    long_tzs[5.5] = "Indian Standard Time"
    short_tzs[5.5] = "IST"

    # long_tzs[4.5] = "Afghanistan Time"
    # short_tzs[4.5] = "AFT"
    #
    # long_tzs[3.5] = "Iran Standard Time"
    # short_tzs[3.5] = "IRST"

    # Regular time zones.
    for key in range(-12, 15):
        if key < 0:
            utc[key] = f"UTC{key}"
        else:
            utc[key] = f"UTC+{key}"

        if key in long_tzs:
            long_tzs[key] += " (" + utc[key] + ")"
        else:
            long_tzs[key] = utc[key]

        if key not in short_tzs:
            short_tzs[key] = utc[key]

        files[key] = utc[key].replace("+", "")

    oddball_keys = set(long_tzs.keys()) - set(range(-12, 15))

    for key in oddball_keys:
        if key < 0:
            utc[key] = f"UTC{key}"
        else:
            utc[key] = f"UTC+{key}"

        if key in long_tzs:
            long_tzs[key] += " (" + utc[key] + ")"

        files[key] = utc[key].replace("+", "")

    # Sort by the keys in ascending order.
    files = {key: files[key] for key in sorted(files.keys())}

    return long_tzs, short_tzs, utc, files
