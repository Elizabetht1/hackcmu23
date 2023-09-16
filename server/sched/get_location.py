import googlemaps

def get_location(location):
    gmaps = googlemaps.Client(key='AIzaSyCS6tSvh4hrFB-ZA4sp4TvwxOeCfMTnKaM')
    geocode_result = gmaps.geocode(location)
    return geocode_result[0]['geometry']['location']['lat'], geocode_result[0]['geometry']['location']['lng']