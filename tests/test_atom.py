from os.path import dirname, join
from datetime import datetime, timezone

from opynsearch.atom import parse_atom_feed
from opynsearch.result import SearchResultPage, SearchResultItem


def test_parse():
    parsed = parse_atom_feed(open(join(dirname(__file__), "data/atom.xml")))
    assert parsed == SearchResultPage(
        title="EUMETSAT Product Navigator COLOS Adaptor results feed",
        id="http://46.51.189.235:80/atom",
        source="",
        total_results=58,
        start_index=1,
        items_per_page=10,
        items=[
            SearchResultItem(
                title="ASCAT AHRPT - Metop",
                id="EO:EUM:DAT:METOP:ASCATAHRPT",
                identifier="EO:EUM:DAT:METOP:ASCATAHRPT",
                creator=None,
                subjects=[
                    "climatologyMeteorologyAtmosphere",
                    "Observation",
                    "Marine",
                    "Satellite_Data",
                    "Sea_Ice"
                ],
                abstract="The prime objective of the Advanced SCATterometer (ASCAT) is to measure wind speed and direction over the oceans, and the main operational application is the assimilation of ocean winds in NWP models. Other operational applications, based on the use of measurements of the backscattering coefficient, are sea ice edge detection and monitoring, monitoring sea ice, snow cover, soil moisture and land surface parameters.",
                contributors=[],
                modified=datetime(2010, 9, 21, 0, 0, tzinfo=timezone.utc),
                date=None,
                sources=[],
                language=None,
                rights="-",
                envelope={
                    "type":
                    "Polygon",
                    "coordinates": [
                        [
                            (90.0, -180.0),
                            (-90.0, -180.0),
                            (-90.0, 180.0),
                            (90.0, 180.0),
                            (90.0, -180.0)
                        ]
                    ],
                    "crs": {
                        "type": "name",
                        "properties": {"name": "urn:ogc:def:crs:EPSG:6.7:4326"}
                    }
                }
            )
        ],
        creator=None,
        subjects=["climatologyMeteorologyAtmosphere"],
        abstract=None,
        publisher="EUMETSAT Product Navigator",
        contributors=["con terra GmbH"],
        modified=datetime(2014, 3, 14, 11, 23, 28, tzinfo=timezone.utc),
        identifier=None,
        language=None,
        rights="Copyright",
        envelopes=[]
    )