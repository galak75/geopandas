from collections import OrderedDict

from shapely.geometry import Point, Polygon, MultiPolygon, MultiPoint, \
    LineString, MultiLineString

from geopandas import GeoDataFrame
from geopandas.io.file import infer_schema, _FIONA18


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
linestring_3D = LineString((
    (-73.5541107525234, 45.5091983609661, 300),
    (-73.5546126200639, 45.5086813829106, 300),
    (-73.5540185061397, 45.5084409343852, 300)
))
polygon_3D = Polygon((
    (-73.5541107525234, 45.5091983609661, 300),
    (-73.5535801792994, 45.5089539203786, 300),
    (-73.5541107525234, 45.5091983609661, 300)
))


def test_infer_schema_only_points(self):
    df = GeoDataFrame(
        geometry=[self.city_hall_entrance, self.city_hall_balcony]
    )

    assert infer_schema(df) == {
        'geometry': 'Point',
        'properties': OrderedDict()
    }


def test_infer_schema_points_and_multipoints(self):
    df = GeoDataFrame(
        geometry=[
            MultiPoint([self.city_hall_entrance, self.city_hall_balcony]),
            self.city_hall_balcony
        ]
    )

    if _FIONA18:
        assert infer_schema(df) == {
            'geometry': ['MultiPoint', 'Point'],
            'properties': OrderedDict()
        }
    else:
        assert infer_schema(df) == {
            'geometry': 'Point',
            'properties': OrderedDict()
        }


def test_infer_schema_only_multipoints(self):
    df = GeoDataFrame(
        geometry=[MultiPoint([
            self.city_hall_entrance,
            self.city_hall_balcony,
            self.city_hall_council_chamber
        ])]
    )

    assert infer_schema(df) == {
        'geometry': 'MultiPoint',
        'properties': OrderedDict()
    }


def test_infer_schema_only_linestrings(self):
    df = GeoDataFrame(geometry=self.city_hall_walls)

    assert infer_schema(df) == {
        'geometry': 'LineString',
        'properties': OrderedDict()
    }


def test_infer_schema_linestrings_and_multilinestrings(self):
    df = GeoDataFrame(
        geometry=[
            MultiLineString(self.city_hall_walls),
            self.city_hall_walls[0]
        ]
    )

    if _FIONA18:
        assert infer_schema(df) == {
            'geometry': ['MultiLineString', 'LineString'],
            'properties': OrderedDict()
        }
    else:
        assert infer_schema(df) == {
            'geometry': 'LineString',
            'properties': OrderedDict()
        }


def test_infer_schema_only_multilinestrings(self):
    df = GeoDataFrame(geometry=[MultiLineString(self.city_hall_walls)])

    assert infer_schema(df) == {
        'geometry': 'MultiLineString',
        'properties': OrderedDict()
    }


def test_infer_schema_only_polygons(self):
    df = GeoDataFrame(
        geometry=[self.city_hall_boundaries, self.vauquelin_place]
    )

    assert infer_schema(df) == {
        'geometry': 'Polygon',
        'properties': OrderedDict()
    }


def test_infer_schema_polygons_and_multipolygons(self):
    df = GeoDataFrame(
        geometry=[
            MultiPolygon((self.city_hall_boundaries, self.vauquelin_place)),
            self.city_hall_boundaries
        ]
    )

    if _FIONA18:
        assert infer_schema(df) == {
            'geometry': ['MultiPolygon', 'Polygon'],
            'properties': OrderedDict()
        }
    else:
        assert infer_schema(df) == {
            'geometry': 'Polygon',
            'properties': OrderedDict()
        }


def test_infer_schema_only_multipolygons(self):
    df = GeoDataFrame(
        geometry=[
            MultiPolygon((self.city_hall_boundaries, self.vauquelin_place))
        ]
    )

    assert infer_schema(df) == {
        'geometry': 'MultiPolygon',
        'properties': OrderedDict()
    }


def test_infer_schema_multiple_shape_types(self):
    df = GeoDataFrame(
        geometry=[
            MultiPolygon((self.city_hall_boundaries, self.vauquelin_place)),
            self.city_hall_boundaries,
            MultiLineString(self.city_hall_walls),
            self.city_hall_walls[0],
            MultiPoint([self.city_hall_entrance, self.city_hall_balcony]),
            self.city_hall_balcony
        ]
    )

    if _FIONA18:
        assert infer_schema(df) == {
            'geometry': [
                'MultiPolygon', 'Polygon',
                'MultiLineString', 'LineString',
                'MultiPoint', 'Point'
            ],
            'properties': OrderedDict()
        }
    else:
        assert infer_schema(df) == {
            'geometry': [
                'Polygon',
                'LineString',
                'Point'
            ],
            'properties': OrderedDict()
        }


def test_infer_schema_mixed_3D_shape_type(self):
    df = GeoDataFrame(
        geometry=[
            MultiPolygon((self.city_hall_boundaries, self.vauquelin_place)),
            self.city_hall_boundaries,
            MultiLineString(self.city_hall_walls),
            self.city_hall_walls[0],
            MultiPoint([self.city_hall_entrance, self.city_hall_balcony]),
            self.city_hall_balcony,
            self.point_3D
        ]
    )

    if _FIONA18:
        assert infer_schema(df) == {
            'geometry': [
                '3D Point',
                'MultiPolygon', 'Polygon',
                'MultiLineString', 'LineString',
                'MultiPoint', 'Point'
            ],
            'properties': OrderedDict()
        }
    else:
        assert infer_schema(df) == {
            'geometry': ['3D Polygon', '3D LineString', '3D Point'],
            'properties': OrderedDict()
        }


def test_infer_schema_mixed_3D_Point(self):
    df = GeoDataFrame(geometry=[self.city_hall_balcony, self.point_3D])

    if _FIONA18:
        assert infer_schema(df) == {
            'geometry': ['3D Point', 'Point'],
            'properties': OrderedDict()
        }
    else:
        assert infer_schema(df) == {
            'geometry': '3D Point',
            'properties': OrderedDict()
        }


def test_infer_schema_only_3D_Points(self):
    df = GeoDataFrame(geometry=[self.point_3D, self.point_3D])

    assert infer_schema(df) == {
        'geometry': '3D Point',
        'properties': OrderedDict()
    }


def test_infer_schema_mixed_3D_linestring(self):
    df = GeoDataFrame(
        geometry=[self.city_hall_walls[0], self.linestring_3D]
    )

    if _FIONA18:
        assert infer_schema(df) == {
            'geometry': ['3D LineString', 'LineString'],
            'properties': OrderedDict()
        }
    else:
        assert infer_schema(df) == {
            'geometry': '3D LineString',
            'properties': OrderedDict()
        }


def test_infer_schema_only_3D_linestrings(self):
    df = GeoDataFrame(geometry=[self.linestring_3D, self.linestring_3D])

    assert infer_schema(df) == {
        'geometry': '3D LineString',
        'properties': OrderedDict()
    }


def test_infer_schema_mixed_3D_Polygon(self):
    df = GeoDataFrame(geometry=[self.city_hall_boundaries, self.polygon_3D])

    if _FIONA18:
        assert infer_schema(df) == {
            'geometry': ['3D Polygon', 'Polygon'],
            'properties': OrderedDict()
        }
    else:
        assert infer_schema(df) == {
            'geometry': '3D Polygon',
            'properties': OrderedDict()
        }


def test_infer_schema_only_3D_Polygons(self):
    df = GeoDataFrame(geometry=[self.polygon_3D, self.polygon_3D])

    assert infer_schema(df) == {
        'geometry': '3D Polygon',
        'properties': OrderedDict()
    }


def test_infer_schema_null_geometry_and_2D_point(self):
    df = GeoDataFrame(geometry=[None, self.city_hall_entrance])

    # None geometry type is then omitted
    assert infer_schema(df) == {
        'geometry': 'Point',
        'properties': OrderedDict()
    }


def test_infer_schema_null_geometry_and_3D_point(self):
    df = GeoDataFrame(geometry=[None, self.point_3D])

    # None geometry type is then omitted
    assert infer_schema(df) == {
        'geometry': '3D Point',
        'properties': OrderedDict()
    }


def test_infer_schema_null_geometry_all(self):
    df = GeoDataFrame(geometry=[None, None])

    # None geometry type in then replaced by 'Unknown'
    # (default geometry type supported by Fiona)
    assert infer_schema(df) == {
        'geometry': 'Unknown',
        'properties': OrderedDict()
    }
