import os
import shutil
import sys
import tempfile

import pytest
from shapely.geometry import Point, Polygon, MultiPolygon, MultiPoint, \
    LineString, MultiLineString

import geopandas
from geopandas import GeoDataFrame
from geopandas.testing import assert_geodataframe_equal

# Credit: Polygons below come from Montreal city Open Data portal
# http://donnees.ville.montreal.qc.ca/dataset/unites-evaluation-fonciere
city_hall_boundaries = Polygon((
    (-73.5541107525234, 45.5091983609661),
    (-73.5546126200639, 45.5086813829106),
    (-73.5540185061397, 45.5084409343852),
    (-73.5539986525799, 45.5084323044531),
    (-73.5535801792994, 45.5089539203786),
    (-73.5541107525234, 45.5091983609661)
))
vauquelin_place = Polygon((
    (-73.5542465586147, 45.5081555487952),
    (-73.5540185061397, 45.5084409343852),
    (-73.5546126200639, 45.5086813829106),
    (-73.5548825850032, 45.5084033554357),
    (-73.5542465586147, 45.5081555487952)
))

city_hall_walls = [
    LineString((
        (-73.5541107525234, 45.5091983609661),
        (-73.5546126200639, 45.5086813829106),
        (-73.5540185061397, 45.5084409343852)
    )),
    LineString((
        (-73.5539986525799, 45.5084323044531),
        (-73.5535801792994, 45.5089539203786),
        (-73.5541107525234, 45.5091983609661)
    ))
]

city_hall_entrance = Point(-73.553785, 45.508722)
city_hall_balcony = Point(-73.554138, 45.509080)
city_hall_council_chamber = Point(-73.554246, 45.508931)

point_3D = Point(-73.553785, 45.508722, 300)


# *****************************************
# TEST CASES
_geodataframes_to_write = []

# Points
gdf = GeoDataFrame(
    {'a': [1, 2]},
    crs={'init': 'epsg:4326'},
    geometry=[city_hall_entrance, city_hall_balcony]
)
_geodataframes_to_write.append(gdf)

# MultiPoints
gdf = GeoDataFrame(
    {'a': [1, 2]},
    crs={'init': 'epsg:4326'},
    geometry=[
        MultiPoint([
            city_hall_balcony,
            city_hall_council_chamber]),
        MultiPoint([
            city_hall_entrance,
            city_hall_balcony,
            city_hall_council_chamber]
        )]
)
_geodataframes_to_write.append(gdf)

# LineStrings
gdf = GeoDataFrame(
    {'a': [1, 2]},
    crs={'init': 'epsg:4326'},
    geometry=city_hall_walls
)
_geodataframes_to_write.append(gdf)

# LineStrings and MultiLineStrings
gdf = GeoDataFrame(
    {'a': [1, 2]},
    crs={'init': 'epsg:4326'},
    geometry=[MultiLineString(city_hall_walls), city_hall_walls[0]]
)
_geodataframes_to_write.append(gdf)

# MultiLineStrings
gdf = GeoDataFrame(
    {'a': [1, 2]},
    crs={'init': 'epsg:4326'},
    geometry=[
        MultiLineString(city_hall_walls),
        MultiLineString(city_hall_walls)
    ]
)
_geodataframes_to_write.append(gdf)

# Polygons
gdf = GeoDataFrame(
    {'a': [1, 2]},
    crs={'init': 'epsg:4326'},
    geometry=[city_hall_boundaries, vauquelin_place]
)
_geodataframes_to_write.append(gdf)

# MultiPolygon and Polygon
gdf = GeoDataFrame(
    {'a': [1, 2]},
    crs={'init': 'epsg:4326'},
    geometry=[
        MultiPolygon((city_hall_boundaries, vauquelin_place)),
        city_hall_boundaries
    ]
)
_geodataframes_to_write.append(gdf)

# MultiPolygon
gdf = GeoDataFrame(
    {'a': [1]},
    crs={'init': 'epsg:4326'},
    geometry=[MultiPolygon((city_hall_boundaries, vauquelin_place))]
)
_geodataframes_to_write.append(gdf)

# Null geometry and Point
gdf = GeoDataFrame(
    {'a': [1, 2]},
    crs={'init': 'epsg:4326'},
    geometry=[None, city_hall_entrance]
)
_geodataframes_to_write.append(gdf)

# Null geometry and 3D Point
gdf = GeoDataFrame(
    {'a': [1, 2]},
    crs={'init': 'epsg:4326'},
    geometry=[None, point_3D]
)
_geodataframes_to_write.append(gdf)

# Null geometries only
gdf = GeoDataFrame(
    {'a': [1, 2]},
    crs={'init': 'epsg:4326'},
    geometry=[None, None]
)
_geodataframes_to_write.append(gdf)


@pytest.fixture(params=_geodataframes_to_write)
def geodataframe(request):
    return request.param

@pytest.fixture(params=[
    # Points and MultiPoints
    # 'ESRI Shapefile' driver supports writing LineString/MultiLinestring and
    # Polygon/MultiPolygon but does not mention Point/MultiPoint
    # see https://www.gdal.org/drv_shapefile.html
    GeoDataFrame(
        {'a': [1, 2]},
        crs={'init': 'epsg:4326'},
        geometry=[
            MultiPoint([city_hall_entrance, city_hall_balcony]),
            city_hall_balcony
        ]
    ),
    # all shape types
    GeoDataFrame(
        {'a': [1, 2, 3, 4, 5, 6]},
        crs={'init': 'epsg:4326'},
        geometry=[
            MultiPolygon((city_hall_boundaries, vauquelin_place)),
            city_hall_entrance,
            MultiLineString(city_hall_walls),
            city_hall_walls[0],
            MultiPoint([city_hall_entrance, city_hall_balcony]),
            city_hall_balcony
        ]
    ),
    # all 2D shape types and 3D Point
    GeoDataFrame(
        {'a': [1, 2, 3, 4, 5, 6, 7]},
        crs={'init': 'epsg:4326'},
        geometry=[
            MultiPolygon((city_hall_boundaries, vauquelin_place)),
            city_hall_entrance,
            MultiLineString(city_hall_walls),
            city_hall_walls[0],
            MultiPoint([city_hall_entrance, city_hall_balcony]),
            city_hall_balcony,
            point_3D
        ]
    )
])
def mixed_geom_gdf(request):
    return request.param


@pytest.fixture(params=['GeoJSON', 'ESRI Shapefile'])
def ogr_driver(request):
    return request.param


class TestGeoDataFrameToFile():

    def setup_method(self):
        self.output_dir = tempfile.mkdtemp()
        self.output_file = os.path.join(self.output_dir, "output_file")

    def teardown_method(self):
        shutil.rmtree(self.output_dir)

    def test_geodataframe_to_file(self, geodataframe, ogr_driver):
        self.do_test_geodataframe_to_file(geodataframe, ogr_driver)

    def test_write_gdf_with_mixed_geometries(self, mixed_geom_gdf, ogr_driver):
        if ogr_driver == 'ESRI Shapefile':
            with pytest.raises(Exception):
                mixed_geom_gdf.to_file(self.output_file, driver=ogr_driver)
        else:
            self.do_test_geodataframe_to_file(mixed_geom_gdf, ogr_driver)

    def do_test_geodataframe_to_file(self, gdf, ogr_driver):
        gdf.to_file(self.output_file, driver=ogr_driver)

        reloaded = geopandas.read_file(self.output_file)

        check_column_type = 'equiv'
        if sys.version_info[0] < 3:
            # do not check column types in python 2 (or it fails!!!)
            check_column_type = False

        assert_geodataframe_equal(gdf, reloaded,
                                  check_column_type=check_column_type)
