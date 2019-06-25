from icalendar import Calendar, Event
from datetime import datetime
from pytz import UTC
from uuid import uuid1

cal = Calendar()
cal.add('prodid', '-//fz_spider product//Version 1.0//CN')
cal.add('version', '2.0')
cal['X-WR-CALNAME'] = '课表'

event = Event()
event.add('uid', str(uuid1()) + '@fz_spider')
event.add('summary', 'Python meeting about calendaring')
event.add('dtstart', datetime(2018, 12, 17, 8, 0, 0, tzinfo=UTC))
event.add('dtend', datetime(2018, 12, 17, 10, 0, 0, tzinfo=UTC))
event.add('dtstamp', datetime.now())
event.add('rrule',
          {'freq': 'weekly', 'interval': 1,
           'count': 5})
event.add('location', 'location 00')
cal.add_component(event)

with open('example.ics', 'wb') as f:
    f.write(cal.to_ical())
