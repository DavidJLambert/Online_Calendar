""" generate_online_calendar.py

REPOSITORY:
    https://github.com/DavidJLambert/wyzant

AUTHOR:
    David J. Lambert

VERSION:
    0.5.0

DATE:
    August 4, 2024
"""

from datetime import datetime, timedelta
from timezones import get_timezones, us_can_dst
from getSchedule import get_schedule
from jinja2 import Environment, FileSystemLoader
from neocitizen import NeocitiesApi
from pathlib import Path

dt_now = datetime.now()

# My time zone name and UTC offset.
if us_can_dst(dt_now):
    tz_name = "PDT (UTC-7)"
    utc_offset = -7
else:
    tz_name = "PST (UTC-8)"
    utc_offset = -8

# Get timezone information.
# long_tzs, short_tzs, utc, and files are dicts with keys
# -12, -11, ... 14, and decimal numbers for a few oddball timezones whose UTC offsets are not integers.
# The keys are the number of hours relative to UTC.
long_tzs, short_tzs, utc, files = get_timezones(dt_now)

print("Timezone information:")
print(f"{'KEY':4s}   {'UTC':10s} {'FILES':10s} {'SHORT_TZ':10s} {'LONG_TZS':55s}")
print(f"{'---':4s}   {'---':10s} {'-----':10s} {'--------':10s} {'--------':55s}")
for key in sorted(long_tzs):
    print(f"{key:4}   {utc[key]:10s} {files[key]:10s} {short_tzs[key]:10s} {long_tzs[key]:55s}")
print()

# Generate index.html
results_filename = "web/index.html"
environment = Environment(loader=FileSystemLoader("templates/"), trim_blocks=True, lstrip_blocks=True)
results_template = environment.get_template("index_template.html")
context = {
    "tz_name": tz_name,
    "long_tzs": long_tzs,
    "files": files
}
with open(results_filename, mode="w", encoding="utf-8") as results:
    results.write(results_template.render(context))
    print(f"Wrote {results_filename}")
print()

'''
Get schedule from schedule.tsv, which lists unavailable time slots.
These time slots begin with 'start' and end with 'end'.
dt_dict =
{'2023-11-13 21:00:00': 'start',
 '2023-11-14 09:00:00': 'end', ... }
'''
dt_dict, dt_written = get_schedule()

'''
Check dt_dict for any problems.
'''
# Debug output.
previous_value = "end"
# print("Schedule:")
# print(f"{'KEY':19s}   {'VALUE':5s}")
# print(f"{'---':19s}   {'-----':5s}")
for key, value in dt_dict.items():
    # print(f"{key}   {value:5s}")
    if ((previous_value == "start" and value != "end") or
            (previous_value == "end" and value != "start")):
        print(f"INVALID COMBO OF VALUE {value} AND PREVIOUS_VALUE {previous_value}")
        exit(1)
    previous_value = value

print("Schedule 'start' and 'end' are OK.")
print()

'''
Convert dt_dict to list of available time slots, in this format:
[[slot 1 start datetime, slot 1 end datetime],
 [slot 2 start datetime, slot 2 end datetime],
 ...]
'''
# Remove items from dt_dict if they're in the past.
dt_now = datetime.now()
for key in sorted(dt_dict):
    if key < dt_now:
        del dt_dict[key]

# Remove last item (chronologically) in dt_dict if it is "end", the start of a free time-slot.
max_key = max(dt_dict.keys())
max_val = dt_dict[max_key]
if max_val == "end":
    del dt_dict[max_key]

# If first item in dt_dict is "start", the end of a free time-slot, insert an "end" with the current date-time.
min_key = min(dt_dict.keys())
min_val = dt_dict[min_key]
if min_val == "start":
    dt_dict[dt_now] = "end"

# Put the key/value pairs into temp_list in chronological order.
temp_list = []
for key in sorted(dt_dict):
    value = dt_dict[key]
    temp_list.append([key, value])

# Third, move pairs of items from temp_list into final list free_slots:
# [[0,1],
#  [2,3],
#  ...]
free_slots = list()
for item_number in range(0, len(temp_list), 2):
    if temp_list[item_number][1] != 'end':
        print("WTF end in generate_online_calendar")
        exit(1)
    if temp_list[item_number+1][1] != 'start':
        print("WTF start in generate_online_calendar")
        exit(1)
    free_slots.append([temp_list[item_number][0], temp_list[item_number+1][0]])

'''
# Debug output.
print("Schedule:")
print(f"{'START':19s}   {'END':5s}")
print(f"{'-----':19s}   {'---':5s}")
for item in free_slots:
    print(f"{item[0]}   {item[1]}")
print()
'''

files_to_upload = {}

# Iterate through time zones, generate html files containing my schedule.
for tz_key in sorted(long_tzs.keys()):
    tz_value = long_tzs[tz_key]
    tz_offset = utc_offset + tz_key

    # Convert my schedule into this time zone.
    free_slots_tz = list()
    for item in free_slots:
        slot_start = item[0] + timedelta(hours=tz_offset)
        slot_end = item[1] + timedelta(hours=tz_offset)
        time_end = slot_end.time()
        if slot_start.date() != slot_end.date():
            # Divide time slot into two time slots at the enclosed midnight.
            new_slot_end = slot_start.replace(hour=23, minute=59, second=59)
            free_slots_tz.append([slot_start, new_slot_end])

            new_slot_start = slot_end.replace(hour=0, minute=0, second=0)
            if new_slot_start != slot_end:
                free_slots_tz.append([new_slot_start, slot_end])
        else:
            free_slots_tz.append([slot_start, slot_end])

    # dt_written = datetime.now()
    if dt_written is None:
        converted_dt_written = None
    else:
        converted_dt_written = dt_written + timedelta(hours=tz_offset)
        converted_dt_written = converted_dt_written.strftime("%b %d, %Y at %I:%M %p")

    '''
    print(tz_key)
    for item in free_slots_tz:
        print(f"{item[0]}   {item[1]}")
    '''

    # Load schedule into dictionary with each day a key,
    # and the values of that key a list of the free time slots.
    calendar_tz = {}
    for item in free_slots_tz:
        this_date = item[0].date().strftime("%a, %b %d")
        if this_date[-2] == "0":
            this_date = this_date.replace("0", "")
        time_start = item[0].time().strftime("%I:%M %p")
        if time_start[0] == "0":
            time_start = "&nbsp; " + time_start[1:]
        time_end = item[1].time().strftime("%I:%M %p")
        if time_end[0] == "0":
            time_end = "&nbsp; " + time_end[1:]
        time_slot = time_start + " - " + time_end
        if this_date not in calendar_tz:
            calendar_tz[this_date] = [time_slot]
        else:
            calendar_tz[this_date].append(time_slot)

    """
    Debug output.
    print()
    for day, time_slots in calendar_tz.items():
        print(f"{day}")
        for time_slot in time_slots:
            print(f"\t{time_slot}")
    print()
    """

    # Generate html file for this timezone.
    results_filename = f"web/{files[tz_key]}.html"
    files_to_upload[results_filename] = f"{files[tz_key]}.html"
    environment = Environment(loader=FileSystemLoader("templates/"), trim_blocks=True, lstrip_blocks=True)
    results_template = environment.get_template("tz_template.html")
    context = {
        "timezone": tz_value,
        "calendar": calendar_tz,
        "written": converted_dt_written
    }
    with open(results_filename, mode="w", encoding="utf-8") as results:
        results.write(results_template.render(context))
        # print(f"Wrote {results_filename}")

'''
# Upload new html to neocities.org.

METHODS AND PROPERTIES OF api:
delete_all:
delete_files:
download_all:
fetch_api_key:
fetch_file_list:
    result is pythonified json.
    result = api.fetch_file_list("/")
    for item in result['files']:
        print(item)
fetch_info:
upload_dir:
upload_files:
verbose:
'''

# Add more key/value pairs to files_to_upload.

files_to_upload['web/index.html'] = 'index.html'
files_to_upload['web/styles.css'] = 'styles.css'
upload_dict = dict()
api = NeocitiesApi(api_key='4a2ea696634aedb07a28312b15dc8763')
for file_to_upload in files_to_upload:
    path = Path(file_to_upload)
    upload_dict[path] = files_to_upload[file_to_upload]
api.upload_files(upload_dict)
# print(f"Uploaded\n{',\n'.join(files_to_upload.values())}")

row_length = 4
for index, (key, value) in enumerate(files_to_upload.items()):
    if index % row_length == row_length - 1:
        print(f"{value:13s}")
    else:
        print(f"{value:13s}", end="")
print()
