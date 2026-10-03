"""Tests for configuration."""

from sqlalchemy import create_engine

from product_catalog.config import Settings


def test_database_url_pins_psycopg2_driver():
    url = Settings().database_url
    assert url.startswith("postgresql+psycopg2://")
    assert create_engine(url).dialect.driver == "psycopg2"
