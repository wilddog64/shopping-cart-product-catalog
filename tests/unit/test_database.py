"""Unit tests for database schema-mismatch guard."""

from unittest.mock import MagicMock, patch

from product_catalog.models import Product


class TestRecreateProductsIfSchemaMismatch:
    """Tests for _recreate_products_if_schema_mismatch."""

    def _call(self):
        from product_catalog.database import _recreate_products_if_schema_mismatch

        _recreate_products_if_schema_mismatch()

    def test_no_op_when_table_missing(self):
        """Should not DROP when products table does not exist yet."""
        mock_inspector = MagicMock()
        mock_inspector.has_table.return_value = False

        with patch("product_catalog.database.sa_inspect", return_value=mock_inspector), patch(
            "product_catalog.database.engine"
        ) as mock_engine:
            self._call()

        mock_engine.begin.assert_not_called()

    def test_no_op_when_schema_correct(self):
        """Should not DROP when all model columns are present."""
        all_cols = [{"name": c.name} for c in Product.__table__.columns]

        mock_inspector = MagicMock()
        mock_inspector.has_table.return_value = True
        mock_inspector.get_columns.return_value = all_cols

        with patch("product_catalog.database.sa_inspect", return_value=mock_inspector), patch(
            "product_catalog.database.engine"
        ) as mock_engine:
            self._call()

        mock_engine.begin.assert_not_called()

    def test_drops_table_when_columns_missing_in_sandbox(self):
        """Should DROP products when model columns are absent and env != production."""
        old_schema_cols = [
            {"name": "id"},
            {"name": "sku"},
            {"name": "name"},
            {"name": "price"},
            {"name": "inventory_count"},
        ]
        mock_inspector = MagicMock()
        mock_inspector.has_table.return_value = True
        mock_inspector.get_columns.return_value = old_schema_cols

        mock_conn = MagicMock()
        mock_ctx = MagicMock(
            __enter__=MagicMock(return_value=mock_conn),
            __exit__=MagicMock(return_value=False),
        )

        with (
            patch("product_catalog.database.sa_inspect", return_value=mock_inspector),
            patch("product_catalog.database.engine") as mock_engine,
            patch("product_catalog.database.settings") as mock_settings,
        ):
            mock_engine.begin.return_value = mock_ctx
            mock_settings.environment = "sandbox"
            self._call()

        mock_engine.begin.assert_called_once()
        executed_sql = mock_conn.execute.call_args[0][0].text
        assert "DROP TABLE" in executed_sql.upper()
        assert "products" in executed_sql

    def test_skips_drop_in_production(self):
        """Should NOT DROP even when columns are missing if env == production."""
        old_schema_cols = [{"name": "id"}, {"name": "sku"}]
        mock_inspector = MagicMock()
        mock_inspector.has_table.return_value = True
        mock_inspector.get_columns.return_value = old_schema_cols

        with patch("product_catalog.database.sa_inspect", return_value=mock_inspector), patch(
            "product_catalog.database.engine"
        ) as mock_engine, patch("product_catalog.database.settings") as mock_settings:
            mock_settings.environment = "production"
            self._call()

        mock_engine.begin.assert_not_called()
