import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from mpl_toolkits.basemap import pyproj
import geopy
from geopy.distance import VincentyDistance as vd


def make_straits_map():
    """ Makes a map of the Straits.
    """
    map = Basemap(resolution='i', projection='tmerc', lat_0 = 51.1515367, lon_0 = -0.8575194,llcrnrlon=-0.871,
                  llcrnrlat=51.148, urcrnrlon=-0.846, urcrnrlat=51.159)#, epsg=4326)
    folder_list = ['su73ne.shp', 'su74se.shp', 'su83nw.shp', 'su84sw.shp']
    subfolder_list = ['Area', 'Line', 'RoadCLine', 'Text', 'VectorMapPoint']
    for x in folder_list:
        for t in subfolder_list:
            if t=='Line':
                map.readshapefile(x+'/'+t, 'out', color='b', linewidth=0.3)
            else:
                map.readshapefile(x+'/'+t, 'out', linewidth=0.7)

    map.drawmapscale(-0.8690655121821721, 51.149290623473476, 0, 0, 100, units='m')
    return map

def bng2latlon(eastings, northings):
    """ Converts British national grid coordinates to lat/lon.
    """
    bng = pyproj.Proj(init='epsg:27700')
    wgs84 = pyproj.Proj(init='epsg:4326')

    lon,lat = pyproj.transform(bng, wgs84, eastings, northings)
    return lon,lat

def latlon2bng(lon,lat):
    """ Converts lon/lat to British national grid coords.
    """
    bng = pyproj.Proj(init='epsg:27700')
    wgs84 = pyproj.Proj(init='epsg:4326')

    lon,lat = pyproj.transform(wgs84, bng, lon, lat)
    return lon,lat

def latlonlist2bng(latlonl):
    """ Converts list of lat lon values to BNG coords.
    """
    bnglist = []
    for x in latlonl:
        bnglist.append(latlon2bng(x[1],x[0]))
    return bnglist

def plot_points_bng(map, eastings, northings):
    """Plots points on map give BNG coords.
    """
    lon,lat = (eastings, northings)
    x,y = map(lon,lat)
    map.plot(x,y, marker='D', color='m')
    return map

def make_unique(original_list):
    """ Removes repeated values from given list and preserves order.
    """
    unique_list = []
    map(lambda x: unique_list.append(x) if (x not in unique_list) else False, original_list)
    return unique_list

def get_lon_lat_dist(lon, lat, bearing, distance):
    origin = geopy.Point(lat, lon)
    dest = vd(meters=distance).destination(origin, bearing)
    lon2, lat2 = dest.longitude, dest.latitude
    return lon2, lat2

def uniquelist(seq):
    seen = set()
    seen_add = seen.add
    return [ x for x in seq if not (x in seen or seen_add(x))]

def save_latlon2file(latlonlist, fname):
    """ Save transect point list to file.
    """
    latlonlist= np.array(latlonlist)
    np.savetxt(fname, latlonlist, delimiter=',', header='Easting, Northing', fmt='%1.0f')

def plot_transect(map, transects, samplength=50):
    fluxtower = (51.153533, -0.8583)
    flux_x, flux_y = map(fluxtower[1], fluxtower[0])
    map.plot(flux_x, flux_y, marker='D', color='k')
    latlon_list = []
    g=pyproj.Geod(ellps='WGS84')
    for tsect in transects:
        for x in xrange(len(tsect)-1):
            lat1, lon1 = bng2latlon(tsect[x][0],tsect[x][1])
            lat2, lon2 = bng2latlon(tsect[x+1][0],tsect[x+1][1])
            (az12, az21, dist) = g.inv(lon1,lat1,lon2,lat2)
            lonlats = g.npts(lon1, lat1, lon2, lat2, 1+int(dist/samplength))

            x1, y1 = map(lat1, lon1)
            x2, y2 = map(lat2, lon2)
            if tsect[x]==(480087,139885):
                map.plot(x1, y1, marker='x', color='m')
            elif tsect[x]!=(480087,139885):
                map.plot(x1, y1, marker='D', color='m')
            if tsect[x+1]==(480087, 139885):
                map.plot(x1, y1, marker='x', color='m')
            elif tsect[x+1]!=(480087, 139885):
                map.plot(x2, y2, marker='D', color='m')

            for lonlat in lonlats:
                xmap, ymap = map(lonlat[1], lonlat[0])
                map.plot(xmap, ymap, marker='x', color='k')

            lonlats.insert(0, (lon1, lat1))
            lonlats.append((lon2, lat2))
            latlon_list.append(lonlats)
    plt.show()
    latlons_temp = [item for sublist in latlon_list for item in sublist]
    latlons = uniquelist(latlons_temp)
    return latlons

def plot_cross_transect(map):
    points = [(480436, 139989), (480207, 140105), (480010, 140258)]
    latlon_list = []
    for point in points:
        lat1, lon1 = bng2latlon(point[0], point[1])
        x1, y1 = map(lat1, lon1)
        map.plot(x1, y1, marker='D', color='m')
        latlon_list.append((lon1,lat1))
        for bearing in [0, 90, 180, 270]:
            for x in xrange(1,5,1):
                lon2, lat2 = get_lon_lat_dist(lon1, lat1, bearing, x*20)
                x2, y2 = map(lat2, lon2)
                latlon_list.append((lon2, lat2))
                map.plot(x2, y2, marker='x', color='k')
    plt.show()
    return latlon_list

def plot_three_t(map, sampdist=50):
    south_t = [(480436, 139989), (480304, 139935), (480208, 139816), (480087, 139849), (480087,139885),
               (479957, 139885), (479833, 139917), (479839, 139820), (479867, 139757), (479634, 139716),
               (479491, 139718)]
    mid_t = [(480280, 140144), (480207, 140105), (480022, 140098), (479768, 139917), (479602, 139813),
             (479500, 139940)]
    #north_t = [(480143, 140376), (480086, 140328), (480010, 140258), (479869, 140190), (479759, 140087),
    #           (479640, 140150), (479630, 140000), (479543, 140051), (479416, 140134)]
    north_t = [(480086, 140328), (480010, 140258), (479869, 140190), (479759, 140087),
               (479640, 140150), (479630, 140000), (479543, 140051)]
    transects = [south_t, mid_t, north_t]
    lonlatslist = plot_transect(map, transects, sampdist)
    bnglist = latlonlist2bng(lonlatslist)
    return bnglist

transect = [(480436, 139989), (480304, 139935), (480208, 139816), (480087, 139849), (480087,139885),
               (479957, 139885), (479833, 139917), (479839, 139820), (479867, 139757), (479634, 139716),
               (479491, 139718), (479500, 139940), (479543, 140051), (479630, 140000), (479640, 140150),
                ]