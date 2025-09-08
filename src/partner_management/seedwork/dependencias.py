"""
"""

import logging
from typing import Dict, Any, Type, Callable

logger = logging.getLogger(__name__)


class DependencyContainer:
    """Simple dependency injection container."""
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, Callable] = {}
        self._singletons: Dict[str, Any] = {}
    
    def register_singleton(self, service_type: Type, instance: Any):
        """Register a singleton service instance."""
        key = self._get_service_key(service_type)
        self._singletons[key] = instance
        logger.debug(f"Registered singleton: {key}")
    
    def register_factory(self, service_type: Type, factory: Callable):
        """Register a factory function for a service type."""
        key = self._get_service_key(service_type)
        self._factories[key] = factory
        logger.debug(f"Registered factory: {key}")
    
    def register_instance(self, service_type: Type, instance: Any):
        """Register a service instance."""
        key = self._get_service_key(service_type)
        self._services[key] = instance
        logger.debug(f"Registered instance: {key}")
    
    def get(self, service_type: Type) -> Any:
        """Get service instance."""
        key = self._get_service_key(service_type)
        
        # Check singletons first
        if key in self._singletons:
            return self._singletons[key]
        
        # Check registered instances
        if key in self._services:
            return self._services[key]
        
        # Check factories
        if key in self._factories:
            factory = self._factories[key]
            instance = factory()
            return instance
        
        raise ValueError(f"Service not registered: {service_type}")
    
    def get_or_none(self, service_type: Type) -> Any:
        """Get service instance or None if not found."""
        try:
            return self.get(service_type)
        except ValueError:
            return None
    
    def is_registered(self, service_type: Type) -> bool:
        """Check if service type is registered."""
        key = self._get_service_key(service_type)
        return key in self._services or key in self._factories or key in self._singletons
    
    def clear(self):
        """Clear all registered services."""
        self._services.clear()
        self._factories.clear()
        self._singletons.clear()
    
    def _get_service_key(self, service_type: Type) -> str:
        """Get service key from type."""
        return f"{service_type.__module__}.{service_type.__name__}"


# Global container instance
_container = DependencyContainer()


def get_container() -> DependencyContainer:
    """Get global dependency container."""
    return _container


def setup_dependencies():
    """Setup dependency injection configuration."""
    from ..modulos.partners.dominio.repositorio import PartnerRepository
    from ..modulos.partners.infraestructura.repositorios_mock import MockPartnerRepository
    from ..modulos.partners.infraestructura.fabricas import FabricaPartner
    from ..seedwork.infraestructura.uow import UnitOfWorkInterface, UnitOfWork
    
    container = get_container()
    
    # Register repositories (using mocks for now)
    container.register_factory(PartnerRepository, lambda: MockPartnerRepository())
    
    # Register factories
    container.register_factory(FabricaPartner, lambda: FabricaPartner())
    
    # Register Unit of Work
    container.register_factory(UnitOfWorkInterface, lambda: UnitOfWork())
    
    logger.info("Dependency injection configured successfully")


def inject(service_type: Type):
    """Decorator for dependency injection."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            container = get_container()
            service_instance = container.get(service_type)
            return func(service_instance, *args, **kwargs)
        return wrapper
    return decorator


# Convenience functions for common services

def get_partner_repository():
    """Get partner repository instance."""
    from ..modulos.partners.dominio.repositorio import PartnerRepository
    return get_container().get(PartnerRepository)


def get_partner_factory():
    """Get partner factory instance."""
    from ..modulos.partners.infraestructura.fabricas import FabricaPartner
    return get_container().get(FabricaPartner)


def get_unit_of_work():
    """Get unit of work instance."""
    from ..seedwork.infraestructura.uow import UnitOfWorkInterface
    return get_container().get(UnitOfWorkInterface)


# Auto-setup dependencies when module is imported
try:
    setup_dependencies()
except Exception as e:
    logger.warning(f"Failed to auto-setup dependencies: {e}")
    # Dependencies can be setup manually later