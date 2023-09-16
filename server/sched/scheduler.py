import get_calender
import get_location
import get_distance
import add_event
import re
import datetime
import requests
import dateparser

COORD_CACHE = {}
API_KEY = 'd0febc7119b2bae7c679443a251421ef'


def get_from_cache(location):

    coordinates = (None, None)

    # Iterate through the keys in the cache
    for key in COORD_CACHE:
        # Check if the key is a superset of the location using regex
        pattern = re.compile(rf'\b{re.escape(key)}\b', re.IGNORECASE)
        if pattern.search(location):
            coordinates = COORD_CACHE[key]
            break  # Stop searching once a match is found

    return coordinates


def is_better(time_new, time_old, calender, lat, lon):
    if (time_old != 0 and calender[time_old-1] != None and
        get_distance(calender[time_old-1][0], calender[time_old-1][1], lat, lon) < 1)\
            or (time_new != 0 and calender[time_new-1] != None and
                get_distance(calender[time_new-1][0], calender[time_new-1][1], lat, lon) > 1):
        return False
    return True


def is_outdoor(task_str):
    if task_str in ["shopping", "travel"]:
        return True
    return False


def bad_weather(lat, lon, check_time):
    today = datetime.datetime.now()
    timestamp = int(datetime.datetime(today.year, today.month,
                    today.day, check_time, 0).timestamp())
    url = f'http://api.weatherstack.com/current?access_key={API_KEY}&query={lat},{lon}&historical_date={timestamp}'
    response = requests.get(url)
    if response.status_code == 200:
        weather_data = response.json()
        rainfall_mm = weather_data['current'].get('precip', 0)
        return rainfall_mm > 5
    return False


def propose(request):
    # parse request : Parse from client
    # time, location, duration, deadline, task
    # request = [None, "Target Penn Ave", 3, None, "Shop", "shop for 10 minutes"]
    if request[0] is not None:
        # add_event.add_event(request[0], request[0] + request[2], request[4], request[1])
        proposal = {
            "start_time": str(request[0].hour),
            "end_time": str(request[0].hour + request[2]),
            "task": request[4],
            "location": request[1],
            "description": request[5]
        }
    else:
        # #get calender
        calender = get_calender.get_calender()

        options = []

        current_hour = datetime.datetime.now().hour

        deadline = 24
        if request[3]:
            deadline = request[3]

        for i in range(current_hour, min(24 + 1 - request[2], deadline + 1 - request[2])):
            ok = True
            for j in range(i, i+request[2]):
                if calender[j] is not None:
                    ok = False
            if ok:
                options.append(i)

        # add location coordinates
        for (key, value) in calender.items():
            if value is not None:
                calender[key] = get_location.get_location(value)

        (lat, lon) = get_location.get_location(request[1])
        if lat == None or lon == None:
            (lat, lon) = get_from_cache(request[1])

        location_usage = True
        if lat != None and lon != None:
            COORD_CACHE[request[1]] = (lat, lon)
        else:
            location_usage = False

        predicted_start = options[0]

        if location_usage:
            for i in range(len(options)):
                for j in range(i):
                    if is_better(options[i], options[j], calender, lat, lon):
                        temp = options[j]
                        options[j] = options[i]
                        options[i] = temp

            predicted_start = options[0]

            if is_outdoor(request[4]):
                for i in range(len(options)):
                    if bad_weather(lat, lon, options[i]) == False:
                        predicted_start = options[i]
                        break

        proposal = {
            "start_time": predicted_start,
            "end_time": predicted_start + request[2],
            "task": request[4],
            "location": request[1],
            "description": request[5]
        }
    return proposal


def schedule(sched):
    add_event.add_event(*sched)
