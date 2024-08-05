===============
Online_Calendar
===============

:SUMMARY: Use VBA to extract my Free/Busy calendar from MS Outlook, and Python &
          jinja2 to post it at https://DavidTutor.Neocities.org.  

:REPOSITORY: https://github.com/DavidJLambert/Online_Calendar/

:AUTHOR: David J. Lambert

:VERSION: 0.5.0

:DATE: August 4, 2024

Problem Description
-------------------
I keep my calendar in the desktop version of Microsoft Outlook (the Classic Version,
not the New Version).  As a professional tutor who works online, I want to be able
to post my Free/Busy schedule online, in my own format, so that my clients can see
my schedule and request a time slot without my having to manually send my calendar
to each person, and without having to manually re-send my calendar to each client
every time the schedule changes.

Furthermore, I want to post my schedule converted into each major time zone on
this planet (I've tutored students in Europe, the Far East, Australia, and the
Middle East), so they can conveniently see my Free/Busy schedule in their own time
zone.

This GitHub repository shows the code I have written to do this.  You can see
the resulting calendar at https://davidtutor.neocities.org.

Note that my online schedule is read-only.  There exist websites that allow people
to book appointments online, such as Calendly, but they rarely synchronize with
desktop Outlook, and I have never seen one that allows clients to self-select
when their appointment starts and ends.  In principle, I could do this, but I
have decided it is not worth the effort.

How It All Works
----------------

1.  In Microsoft Outlook, execute the VBA subroutine WriteSchedule (included in
    this project's WriteSchedule.bas).
   
    a.  This VBA goes through the next 10 days of my Outlook Calendar.

    b.  Finds all calendar items with BusyStatus="Busy".

    c.  Withholds the name/subject of each item.

    d.  Consolidates consecutive items.

    e.  Finds the **available** time slots between the busy time slots.

    f.  And saves a summary of my available time slots to templates/schedule.tsv.

        Note: the VBA assumes there are never overlapping "Busy" calendar items.
    
2.  Execute generate_online_calendar.py, which

    a.  Reads a list of the planet's timezones from function get_timezones (in
        timezones.py).

    b.  Writes the list of time zones to web/index.html using jinja2 and
        templates/index_template.html.

    c.  Reads my schedule from templates/schedule.tsv.

    d.  Translates this schedule into each timezone obtained in Step 2b.

    e.  Writes each time zone's translated schedule to web/UTC<NNN>.html using
        jinja2 and templates/tz_template.html, where <NNN> is the UTC offset for
        that time zone.

        Also included in the web directory is styles.css.
    
3.  Uses the neocitizen API to upload all the files in the web folder to
    https://davidtutor.neocities.org.
