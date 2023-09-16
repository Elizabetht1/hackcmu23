import get_calender
import get_location
import get_distance
import add_event

# parse request : Parse from client
# time, location, duration, deadline, task
request = [None, "Target Penn Ave", 3, None, "Shop", "shop for 10 minutes"]

if request[0] is not None:
    add_event.add_event(request[0], request[0] + request[2], request[4], request[1])

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

    
    add_event.add_event(predicted_start, predicted_start + request[2], request[4], request[1], request[5])

    # get_free_slots : location prev mapping
    # free_slots = {0 : None}

    # #get user non-slots for outside tasks from DB
    # non_outside_slots = [i for i in range(12, 16)]
    # non_home_slots = [i for i in range(12)]
    # #get user non-slots for home tasks from DB

    # #slot by 30 mins -> location before / HOME

    # for key, value in free_slots:
    #     if()



    #sent result to user

    #user accepts

    #ask user for time
        #add to calender
        #why reject : #Im at home at this time
                    #Im asleep
                    #Not at this time today






