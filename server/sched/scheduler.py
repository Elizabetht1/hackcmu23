import get_calender
import get_location
import get_distance
import add_event

import dateparser

def propose(request):
    # parse request : Parse from client
    # time, location, duration, deadline, task
    # request = [None, "Target Penn Ave", 3, None, "Shop", "shop for 10 minutes"]
    if request[0] is not None:
        # add_event.add_event(request[0], request[0] + request[2], request[4], request[1])
        proposal = {
            "start_time": str(request[0]),
            "end_time": str(request[0] + request[2]),
            "task": request[4],
            "location": request[1],
            "description": request[5]
        }
    else:
        # #get calender
        calender = get_calender.get_calender()
        # add location coordinates
        for (key,value) in calender.items():
            if value is not None:
                calender[key] = get_location.get_location('Rashid Auditorium')
        lat, lon = get_location.get_location(request[1])
        predicted_start = -1
        for i in range(24):
            ok = True
            for j in range(i, i+request[2]):
                if calender[j] is not None:
                    ok = False
            if ok:
                predicted_start = i
                break        
        # add_event.add_event(predicted_start, predicted_start + request[2], request[4], request[1], request[5])
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





