import csv
from datetime import datetime, timedelta
from collections import OrderedDict


def get_schedule(debug=False):

    # Initialize dt_start and dt_end, so they are defined on the first loop in for loop below.
    dt_start = datetime.strptime("2000/01/01 12:34:50", "%Y/%m/%d %H:%M:%S")
    dt_end = datetime.strptime("2000/01/01 12:34:56", "%Y/%m/%d %H:%M:%S")

    # Date/time written assumed not found.
    dt_written = None

    # Extract appointments in schedule from file.
    dt_dict = OrderedDict()
    with open('templates/schedule.tsv', 'r', newline='') as input_file:
        input_csv = csv.reader(input_file, delimiter='\t')
        for row in input_csv:
            previous_dt_start = dt_start
            previous_dt_end = dt_end

            # Appointment start and end date/times, or date/time of update.
            string_start = row[0]
            string_end = row[1]
            if string_start == "Written":
                dt_written = string_end
                dt_written = datetime.strptime(dt_written, "%Y/%m/%d %H:%M:%S")
            else:
                dt_start = datetime.strptime(string_start, "%Y/%m/%d %H:%M:%S")
                dt_end = datetime.strptime(string_end, "%Y/%m/%d %H:%M:%S")

                # Handle dt_dict[dt_start].
                if previous_dt_start >= dt_start:
                    print("WTF? previous_dt_start >= dt_start in getSchedule")
                    print(f"{previous_dt_start=} {dt_start=}")
                elif previous_dt_end >= dt_end:
                    print("WTF? previous_dt_end >= dt_end in getSchedule")
                    print(f"{previous_dt_end=} {dt_end=}")
                elif previous_dt_end > dt_start:
                    print("OVERLAPPING ITEMS")
                    print(f"{previous_dt_end=} {dt_start=}")
                elif dt_start not in dt_dict:
                    # Start day/time not in dt_dict.
                    dt_dict[dt_start] = "start"
                    if debug:
                        print(dt_start, "start")
                elif dt_dict[dt_start] == "end":
                    # Start day/time already in dt_dict as end of previous appointment, so
                    # combine this appointment with previous appointment, delete this end marker.
                    del dt_dict[dt_start]
                    if debug:
                        print(dt_start, "end delete")
                else:
                    print("WTF? else in getSchedule")

                # Handle dt_dict[dt_end].
                dt_dict[dt_end] = "end"
                if debug:
                    print(dt_end, "end")

    return dt_dict, dt_written


if __name__ == "__main__":
    get_schedule(debug=True)
