"""RabbitMQ messaging integration for Product Catalog service."""

from functools import lru_cache
from typing import Optional

import structlog

# Try to import from the rabbitmq-client-python library
try:
    from rabbitmq_client.config import Config as RabbitMQConfig
    from rabbitmq_client.connection import Connection
    from rabbitmq_client.publisher import Publisher
    from rabbitmq_client.vault import VaultCredentialManager

    RABBITMQ_AVAILABLE = True
except ImportError:
    RABBITMQ_AVAILABLE = False
    RabbitMQConfig = None
    Connection = None
    Publisher = None
    VaultCredentialManager = None

from .config import get_settings
from .events import (
    InventoryLowEvent,
    InventoryUpdatedEvent,
)

logger = structlog.get_logger(__name__)

EVENTS_EXCHANGE = "events"
LOW_STOCK_THRESHOLD = 10


class ProductEventPublisher:
    """Publisher for product catalog events."""

    def __init__(self, publisher: Optional["Publisher"] = None):
        """Initialize the event publisher.

        Args:
            publisher: RabbitMQ publisher instance. If None, publishing is disabled.
        """
        self._publisher = publisher

        if self._publisher:
            logger.info("product_event_publisher_initialized")
        else:
            logger.warning("product_event_publisher_disabled", reason="no_publisher")

    @property
    def enabled(self) -> bool:
        """Check if publishing is enabled."""
        return self._publisher is not None

    def publish_inventory_updated(
        self,
        product_id: str,
        sku: str,
        previous_quantity: int,
        new_quantity: int,
        reason: str,
        correlation_id: str | None = None,
    ) -> bool:
        """Publish an inventory.updated event.

        Args:
            product_id: Product UUID
            sku: Product SKU
            previous_quantity: Previous inventory quantity
            new_quantity: New inventory quantity
            reason: Reason for the change

        Returns:
            True if published successfully, False otherwise.
        """
        publisher = self._publisher
        if not publisher:
            logger.debug("publish_skipped", event="inventory.updated", reason="disabled")
            return False

        event = InventoryUpdatedEvent.create(
            product_id=product_id,
            sku=sku,
            previous_quantity=previous_quantity,
            new_quantity=new_quantity,
            reason=reason,
            correlation_id=correlation_id,
        )

        try:
            result = publisher.publish(
                exchange=EVENTS_EXCHANGE,
                routing_key=InventoryUpdatedEvent.TYPE,
                body=event.model_dump(mode="json", by_alias=True),
            )

            logger.info(
                "event_published",
                event_type=InventoryUpdatedEvent.TYPE,
                product_id=product_id,
                correlation_id=event.correlation_id,
            )

            # Check if we should also publish a low stock warning
            if new_quantity <= LOW_STOCK_THRESHOLD and new_quantity < previous_quantity:
                self._publish_inventory_low(product_id, sku, new_quantity, event.correlation_id)

            return result

        except Exception as e:
            logger.error(
                "event_publish_failed",
                event_type=InventoryUpdatedEvent.TYPE,
                product_id=product_id,
                error=str(e),
            )
            return False

    def _publish_inventory_low(
        self,
        product_id: str,
        sku: str,
        current_quantity: int,
        correlation_id: str,
    ) -> bool:
        """Publish an inventory.low event (internal)."""
        publisher = self._publisher
        if not publisher:
            return False

        # Note: We'd need product_name here - in real implementation would fetch it
        event = InventoryLowEvent.create(
            product_id=product_id,
            sku=sku,
            current_quantity=current_quantity,
            product_name=f"Product {sku}",  # Would typically fetch from DB
            threshold=LOW_STOCK_THRESHOLD,
            correlation_id=correlation_id,
        )

        try:
            result = publisher.publish(
                exchange=EVENTS_EXCHANGE,
                routing_key=InventoryLowEvent.TYPE,
                body=event.model_dump(mode="json", by_alias=True),
            )

            logger.warning(
                "low_stock_alert",
                event_type=InventoryLowEvent.TYPE,
                product_id=product_id,
                sku=sku,
                quantity=current_quantity,
            )

            return result

        except Exception as e:
            logger.error(
                "event_publish_failed",
                event_type=InventoryLowEvent.TYPE,
                product_id=product_id,
                error=str(e),
            )
            return False


@lru_cache
def get_rabbitmq_config() -> Optional["RabbitMQConfig"]:
    """Get RabbitMQ configuration from settings."""
    if not RABBITMQ_AVAILABLE:
        return None

    settings = get_settings()

    return RabbitMQConfig(
        host=settings.rabbitmq_host,
        port=settings.rabbitmq_port,
        vhost=settings.rabbitmq_vhost,
        username=settings.rabbitmq_username,
        password=settings.rabbitmq_password,
        use_tls=settings.rabbitmq_use_tls,
    )


def create_publisher() -> Optional["Publisher"]:
    """Create a RabbitMQ publisher.

    Returns:
        Publisher instance if connection successful, None otherwise.
    """
    if not RABBITMQ_AVAILABLE:
        logger.warning("rabbitmq_not_available", reason="library_not_installed")
        return None

    config = get_rabbitmq_config()
    if config is None:
        return None

    settings = get_settings()

    try:
        # Create connection (with or without Vault)
        if settings.vault_enabled:
            vault_manager = VaultCredentialManager(
                vault_addr=settings.vault_addr,
                vault_role=settings.vault_role,
                mount_path=settings.vault_rabbitmq_path,
            )
            connection = Connection(config, vault_manager=vault_manager)
        else:
            connection = Connection(config)

        connection.connect()

        publisher = Publisher(connection)

        # Ensure events exchange exists
        publisher.declare_exchange(EVENTS_EXCHANGE, exchange_type="topic", durable=True)

        logger.info("rabbitmq_publisher_created", host=config.host, port=config.port)

        return publisher

    except Exception as e:
        logger.error("rabbitmq_connection_failed", error=str(e))
        return None


@lru_cache
def get_event_publisher() -> ProductEventPublisher:
    """Get or create the product event publisher singleton."""
    publisher = create_publisher()
    return ProductEventPublisher(publisher)
