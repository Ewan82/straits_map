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

    easting, northing = pyproj.transform(wgs84, bng, lon, lat)
    easting = round(easting, 0)
    northing = round(northing, 0)
    return easting, northing

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

def save_bng2file(bnglist, fname):
    """ Save transect point list to file.
    """
    arr = np.zeros((len(bnglist), 3))
    for x in xrange(len(arr)):
        arr[x,0]=bnglist[x][0]
        arr[x,1]=bnglist[x][1]
        if bnglist[x] in mensuration_plot_dict.values():
            arr[x,2]=1
    np.savetxt(fname, arr, delimiter=',', header='Easting, Northing, M_plot', fmt='%1.0f')
    return arr

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
            lonlats = g.npts(lon1, lat1, lon2, lat2, (dist/samplength))

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

def plot_single_t(map, sampdist=50):
    key_list = ['E26', 'E4', 'E8', 'E9', 'lakepoint', 'E20', 'W13', 'W11', 'W10', 'W15', 'W7',
                'W3', 'W18', 'W16', 'E19', 'E11', 'E14', 'E23', 'E5', 'E25']
    lakepoint = (480087,139885)
    transect = []
    for x in key_list:
        if x=='lakepoint':
            transect.append(lakepoint)
        else:
            transect.append(mensuration_plot_dict[x])
    t_list = [transect]
    lonlatslist = plot_transect(map, t_list, sampdist)
    bnglist = latlonlist2bng(lonlatslist)
    return bnglist

def plot_mensuration(map):
    """Plots all mensuration sites.
    """
    fluxtower = (51.153533, -0.8583)
    flux_x, flux_y = map(fluxtower[1], fluxtower[0])
    map.plot(flux_x, flux_y, marker='D', color='k')
    for x in xrange(len(mensuration_plot_dict)):
        lon, lat = bng2latlon(mensuration_plot_dict.values()[x][0], mensuration_plot_dict.values()[x][1])
        xplt, yplt = map(lon, lat)
        map.plot(xplt, yplt, marker='x', color='k')
        plt.scatter(xplt+30, yplt, marker='$ %s $'%mensuration_plot_dict.keys()[x], s=300, color='m')
    plt.show()

transect = [[(480436, 139989), (480304, 139935), (480208, 139816), (480087, 139849), (480087,139885),
            (479957, 139885), (479833, 139917), (479839, 139820), (479867, 139757), (479634, 139716),
            (479491, 139718), (479500, 139940), (479543, 140051), (479630, 140000), (479640, 140150),
            ]]

mensuration_plot_dict={'W1': (479640, 140150), 'W2': (479630, 140000), 'W3': (479500, 139940), 'W4': (479410, 139760),
                       'W5': (479250, 139620), 'W6': (479360, 139560), 'W7': (479491, 139718), 'W8': (479569, 139600),
                       'W9': (479673, 139599), 'W10': (479867, 139757), 'W11': (479839, 139820),
                       'W12': (479602, 139813), 'W13': (479833, 139892), 'W14': (479768, 139917),
                       'W15': (479634, 139716), 'W16': (479759, 140087), 'W17': (479416, 140134),
                       'W18': (479543, 140051),
                       'E3': (480421, 139852), 'E4': (480304, 139935), 'E5': (480207, 140105), 'E6': (480022, 140098),
                       'E7': (480225, 139760), 'E8': (480208, 139816), 'E9': (480087, 139849), 'E10': (480115, 139730),
                       'E11': (480010, 140258), 'E12': (480143, 140376), 'E13': (479982, 140425),
                       'E14': (480086, 140328), 'E15': (479898, 140343), 'E16': (479792, 140389),
                       'E17': (479600, 140353), 'E18': (479723, 140285), 'E19': (479869, 140190),
                       'E20': (479957, 139885), 'E21': (479982, 139782), 'E22': (479999, 139679),
                       'E23': (480192, 140205), 'E24': (480280, 140144), 'E25': (480360, 140047),
                       'E26': (480436, 139989)
                       }