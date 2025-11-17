import pytest
import os
import sys
from pathlib import Path
from pyspark.sql import SparkSession
import pygeohash as ghsh

# to run tests and generate html report:
# pytest src/test/etl_tests.py -v --html=src/test/report.html


sys.path.insert(0, str(Path(__file__).parent.parent / "main" / "python"))
from geocoding import GeocoderService
from encryption import PIIEncryptionService


@pytest.fixture(scope="session")
def spark():
    session = SparkSession.builder \
        .master("local[1]") \
        .appName("etl_tests") \
        .config("spark.driver.host", "127.0.0.1") \
        .getOrCreate()
    yield session
    session.stop()


@pytest.fixture(scope="session")
def geocoder():
    api_key = os.getenv("OPENCAGE_API_KEY")
    if not api_key:
        pytest.skip("OPENCAGE_API_KEY env var not set")
    return GeocoderService(api_key=api_key)


@pytest.fixture(scope="session")
def pii_encryption():
    """Initialize PII encryption service"""
    encryption_key = "3dd960b7ae92c14e3a4070d222000111" # For testing purposes FAKE key is hardcoded
    return PIIEncryptionService(encryption_key)


### main_etl code snippets needed for tests start ###
@pytest.fixture
def ghsh_4_func():
    """Geohash function"""
    def ghsh_4(cord_list):
        try:
            lat, lng = cord_list
            if lat is not None and lng is not None:
                return ghsh.encode(lat, lng, precision=4)
            return None
        except Exception as e:
            return None
    return ghsh_4


@pytest.fixture
def get_lat_lng_func(geocoder):
    """Get lat/lng function"""
    def get_lat_lng(address, city, country):
        lat, lng = geocoder.get_cord(f"{address} {city}, {country}")
        return [float(lat), float(lng)]
    return get_lat_lng

### main_etl code snippets needed for tests end ###


#GEOCODING API TESTS

class TestGeocodingAPI:
    
    def test_geocode_nyc_address(self, geocoder):
        """Real API call: should geocode NYC address"""
        lat, lng = geocoder.get_cord("1600 Broadway, New York, USA")
        
        assert lat is not None
        assert lng is not None
        assert isinstance(lat, (int, float))
        assert isinstance(lng, (int, float))
        # NYC is roughly around 40.7 latitude and -74 longitude
        assert 40.0 < lat < 41.0
        assert -75.0 < lng < -73.0
    
    def test_geocode_london_address(self, geocoder):
        """Real API call: should geocode London address"""
        lat, lng = geocoder.get_cord("10 Downing Street, London, UK")
        
        assert lat is not None
        assert lng is not None
        # London is roughly around 51.5 latitude and -0.1 longitude
        assert 51.0 < lat < 52.0
        assert -1.0 < lng < 0.5
    
    def test_geocode_tokyo_address(self, geocoder):
        """Real API call: should geocode Tokyo address"""
        lat, lng = geocoder.get_cord("Shibuya, Tokyo, Japan")
        
        assert lat is not None
        assert lng is not None
        # Tokyo is roughly around 35.6 latitude and 139.7 longitude
        assert 35.0 < lat < 36.0
        assert 139.0 < lng < 140.0


# LAT/LNG TRANSFORMATION

class TestLatLngWithAPI:
    
    def test_get_lat_lng_with_real_api(self, get_lat_lng_func):
        """Real API: should get coordinates from address components"""
        result = get_lat_lng_func("Times Square", "New York", "USA")
        
        assert result is not None
        assert len(result) == 2
        assert all(isinstance(x, float) for x in result)
        # Times Square is in NYC area
        assert 40.0 < result[0] < 41.0
        assert -75.0 < result[1] < -73.0
    
    def test_get_lat_lng_london_with_real_api(self, get_lat_lng_func):
        """Real API: should get coordinates for London"""
        result = get_lat_lng_func("Big Ben", "London", "UK")
        
        assert result is not None
        assert len(result) == 2
        assert 51.0 < result[0] < 52.0
        assert -1.0 < result[1] < 0.5


# ======================== GEOHASH TESTS ========================

class TestGeohash:
    
    def test_generates_geohash_from_valid_coordinates(self, ghsh_4_func):
        """Should generate 4-char geohash from coordinates"""
        result = ghsh_4_func([40.7128, -74.0060])
        
        assert result is not None
        assert len(result) == 4
        assert all(c.isalnum() for c in result)
    
    def test_returns_none_for_null_latitude(self, ghsh_4_func):
        """Should return None if latitude is null"""
        result = ghsh_4_func([None, -74.0060])
        assert result is None
    
    def test_returns_none_for_null_longitude(self, ghsh_4_func):
        """Should return None if longitude is null"""
        result = ghsh_4_func([40.7128, None])
        assert result is None
    
    def test_returns_none_for_both_null(self, ghsh_4_func):
        """Should return None if both coordinates are null"""
        result = ghsh_4_func([None, None])
        assert result is None
    
    def test_handles_invalid_input_gracefully(self, ghsh_4_func):
        """Should return None for invalid input"""
        assert ghsh_4_func("invalid") is None
        assert ghsh_4_func([1]) is None
    
    def test_different_locations_produce_different_hashes(self, ghsh_4_func):
        """Should produce unique geohashes for different locations"""
        nyc = ghsh_4_func([40.7128, -74.0060])
        london = ghsh_4_func([51.5074, -0.1278])
        tokyo = ghsh_4_func([35.6762, 139.6503])
        
        assert nyc != london
        assert london != tokyo


# ======================== ENCRYPTION TESTS ========================

class TestEncryption:
    
    def test_encrypts_specified_pii_fields(self, spark):
        """Should encrypt specified PII fields"""
        service = PIIEncryptionService(encryption_key="secret_key_123")
        df = spark.createDataFrame([
            {"name": "John", "email": "john@test.com", "age": 30}
        ])
        
        result = service.encrypt_pii_fields(df, ["name", "email"])
        
        assert "name" in result.columns
        assert "email" in result.columns
        assert "__encryption_key__" not in result.columns
    
    
    def test_raises_error_for_invalid_fields(self, spark):
        """Should raise error when field doesn't exist"""
        service = PIIEncryptionService(encryption_key="secret_key_123")
        df = spark.createDataFrame([
            {"name": "John", "email": "john@test.com"}
        ])
        
        with pytest.raises(ValueError, match="Fields not found"):
            service.encrypt_pii_fields(df, ["nonexistent"])
    

if __name__ == "__main__":
    pytest.main([__file__, "-v"])