from datetime import datetime
import re
import sys

class Log:
  def __generate_key(self, args):
    [clock_in, clock_out, date] = args

    return re.sub(r'\D', '', f'{date}{clock_in}{clock_out}')

  def __get_date(self, date):
    try: 
      return datetime.strptime(date, f'%Y.%m.%d').date()
    except:
      return date

  def __get_time_log(self, args):
    [date, time] = args

    try:
      time = datetime.strptime(time, f'%H:%M').time()

      return datetime.combine(date, time)
    except:
      return time

  def __init__(self, args):
    [date, clock_in, clock_out, type] = args
    
    date = self.__get_date(date)

    self.activities = []
    self.clock_in = self.__get_time_log([date, clock_in])
    self.clock_out = self.__get_time_log([date, clock_out])
    self.date = date
    self.key = self.__generate_key([clock_in, clock_out, date])
    self.type = type
  
  def __repr__(self):
    return (
      '{\n'
      f'  activities: {self.activities}\n'
      f'  clock-in: {self.clock_in}\n'
      f'  clock-out: {self.clock_out}\n'
      f'  date: {self.date}\n'
      f'  type: {self.type}\n'
      '}'
    )

log_file = open(sys.argv[1])

ACTIVITY_PREFIX = '- '

current_key = ''
logs = {}
for line in log_file:
  if re.match(r'^\d{4}.\d{2}.\d{2}.*$', line):
    log = Log(line.strip().split(' - '))

    current_key = log.key

    logs[log.key] = log
  elif line.startswith(ACTIVITY_PREFIX):
    logs[current_key].activities.append(
      line.strip().removeprefix(ACTIVITY_PREFIX)
    )

for log in logs:
  print(logs[log])

log_file.close()
