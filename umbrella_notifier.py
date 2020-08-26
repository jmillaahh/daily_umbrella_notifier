import os
from twilio.rest import Client
import requests
import datetime, pytz

# Extension for rain identification
import re

account_sid = os.getenv('TWILIO_SID')
auth_token = os.getenv('TWILIO_TOKEN')
source_number = os.getenv('TWILIO_TRIAL1_NUMBER')
receiving_contact = os.getenv("US_NUMBER")
client = Client(account_sid, auth_token)

weather_api_key = os.getenv("openweather_api_key")
nash_id = "4644585"

nash_lat, nash_long = "36.1659", "-86.7844"
location = 'Nashville'

unit_type = "metric"
temp_unit = {
    "metric": "°C",
    "imperial": "°F",
    "kelvin": "K",
}

api_call = f"https://api.openweathermap.org/data/2.5/onecall?lat={nash_lat}&lon={nash_long}&units={unit_type}" \
           f"&exclude=minutely,current&appid={weather_api_key}"

def convertToReadableTime(unix_time):
    if type(unix_time) is not int:
        unix_time = int(unix_time)
    return datetime.datetime.fromtimestamp(unix_time).strftime("%I:%M%p")


# Make API call
# Make API call
html = requests.get(api_call)
c = html.json()

# Extract Data #

# Times for sunrise and sunset
sunrise_time = convertToReadableTime(c['daily'][0]['sunrise'])
sunset_time = convertToReadableTime(c['daily'][0]['sunset'])
if sunrise_time[0] == '0': sunrise_time = sunrise_time[1:]
if sunset_time[0] == '0': sunset_time = sunset_time[1:]

# Highs and Lows
min_temp = c['daily'][0]['temp']['min']
max_temp = c['daily'][0]['temp']['max']

tz = pytz.timezone('America/Chicago')
hour = int(datetime.datetime.now(tz=tz).strftime("%H"))
if hour < 12: greeting_time = 'morning'
elif hour >= 12 and hour < 18: greeting_time = 'afternoon'
else: greeting_time = 'evening'

# Determine whether there will be rain at all or not
weather_today = { i: c['hourly'][i]['weather'][0]['description'] for i in range(48) }
some_rain = []
for j in range(len(weather_today)):
    if 'rain' in weather_today[j] or 'RAIN' in weather_today[j]:
        some_rain.append(j)         # j = 30-minute block where it'll rain

# Rain/No Rain -- Umbrella Notifier!
if len(some_rain) > 0:
    rain_message = "\nYou can expect some rainfall today, so check the weather app for specific times to bring your umbrella out!\n"
else:
    rain_message = "\nThe forecast indicates there will be no rain today, so no need for an umbrella!\n"


weather_update = f"""Good {greeting_time} in {location}! Here is your daily weather update for {datetime.date.today().strftime('%A')}, {datetime.datetime.today().strftime("%B %d")}:
\nThe sun will have risen at {sunrise_time} and will set beyond the horizon at {sunset_time}.
\nThe coldest it will be is {min_temp}{temp_unit[unit_type]} while temperatures will cap at {max_temp}{temp_unit[unit_type]}.
\n{rain_message}
\nThat is all for now. Have a great day and see you tomorrow!
"""

print(weather_update)

message = client.messages.create(body=weather_update,
                                 from_=source_number,
                                 to=receiving_contact)

# Only prints if message sent successfully
print(f"message.sid: {message.sid}")
