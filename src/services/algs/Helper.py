import math

def haversine(s_lat, s_long, d_lat, d_long):
    R = 6371000.0

    lat1_rad = math.radians(s_lat)
    lat2_rad = math.radians(d_lat)

    delta_lat = math.radians(d_lat - s_lat)
    delta_long = math.radians(d_long - s_long)

    a = (math.sin(delta_lat/2)**2) + (math.cos(lat2_rad) * math.cos(lat1_rad) * (math.sin(delta_long/2)**2))
    a = min(1.0, a)

    dist = 2 * R * math.asin(math.sqrt(a))

    return dist