import googlemaps

def get_location(location):
    gmaps = googlemaps.Client(key='AIzaSyBghzEi6KS3FxnNpo01q0gesf8pERNl-Iw')
    geocode_result = gmaps.geocode(location)
    return geocode_result[0]['geometry']['location']['lat'], geocode_result[0]['geometry']['location']['lng']