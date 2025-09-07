import json
import logging
import os
import pickle
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type, Callable, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from contextlib import contextmanager
from threading import Lock
import time

from pydispatcher import dispatcher
from ..dominio.eventos import DomainEvent, IntegrationEvent
from ..dominio.excepciones import DomainException


class EventDispatcher:
    """
    Event dispatcher using PyDispatcher (from tutorial).
    
    Provides:
    - Event publishing and subscription
    - Decoupled event handling
    - Thread-safe operations
    - Error handling for event handlers
    """
    
    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = {}
        self._lock = Lock()
        self._logger = logging.getLogger(__name__ + ".EventDispatcher")
    
    def subscribe(self, event_type: Union[str, Type], handler: Callable) -> None:
        """
        Suscribirse a eventos de tipo específico.
        
        Args:
            event_type: Tipo de evento al cual suscribirse (clase o string)
            handler: Función para manejar el evento
        """
        event_key = self._get_event_key(event_type)
        
        with self._lock:
            if event_key not in self._handlers:
                self._handlers[event_key] = []
            
            if handler not in self._handlers[event_key]:
                self._handlers[event_key].append(handler)
                
        # Also register with PyDispatcher
        dispatcher.connect(handler, signal=event_key)
        
        self._logger.debug(f"Subscribed handler {handler.__name__} to event {event_key}")
    
    def unsubscribe(self, event_type: Union[str, Type], handler: Callable) -> None:
        """
        Unsubscribe from events.
        
        Args:
            event_type: Event type to unsubscribe from
            handler: Handler to remove
        """
        event_key = self._get_event_key(event_type)
        
        with self._lock:
            if event_key in self._handlers and handler in self._handlers[event_key]:
                self._handlers[event_key].remove(handler)
                
                if not self._handlers[event_key]:
                    del self._handlers[event_key]
        
        # Also disconnect from PyDispatcher
        try:
            dispatcher.disconnect(handler, signal=event_key)
        except Exception:
            pass  # Handler might not be connected
        
        self._logger.debug(f"Unsubscribed handler {handler.__name__} from event {event_key}")
    
    def publish(self, event: Union[DomainEvent, IntegrationEvent, str], data: Any = None) -> None:
        """
        Publish event to all subscribers.
        
        Args:
            event: Event object or event type string
            data: Optional data for string events
        """
        if isinstance(event, str):
            event_key = event
            event_data = data
        else:
            event_key = self._get_event_key(type(event))
            event_data = event
        
        self._logger.info(f"Publishing event: {event_key}")
        
        # Get handlers safely
        handlers = []
        with self._lock:
            handlers = self._handlers.get(event_key, []).copy()
        
        # Execute handlers
        for handler in handlers:
            try:
                if isinstance(event_data, str):
                    handler(event_data)
                else:
                    handler(event_data)
                    
            except Exception as e:
                self._logger.error(f"Error in event handler {handler.__name__}: {str(e)}")
                # Continue with other handlers even if one fails
        
        # Also send through PyDispatcher
        try:
            dispatcher.send(signal=event_key, event=event_data)
        except Exception as e:
            self._logger.error(f"Error in PyDispatcher send: {str(e)}")
    
    def get_handlers(self, event_type: Union[str, Type]) -> List[Callable]:
        """Get all handlers for event type."""
        event_key = self._get_event_key(event_type)
        with self._lock:
            return self._handlers.get(event_key, []).copy()
    
    def clear_handlers(self, event_type: Optional[Union[str, Type]] = None) -> None:
        """Clear handlers for specific event type or all handlers."""
        with self._lock:
            if event_type:
                event_key = self._get_event_key(event_type)
                self._handlers.pop(event_key, None)
                
                # Disconnect from PyDispatcher
                try:
                    dispatcher.disconnect(signal=event_key)
                except Exception:
                    pass
            else:
                self._handlers.clear()
                # Clear all PyDispatcher connections would require tracking all signals
    
    def _get_event_key(self, event_type: Union[str, Type]) -> str:
        """Get string key for event type."""
        if isinstance(event_type, str):
            return event_type
        elif isinstance(event_type, type):
            return event_type.__name__
        else:
            return str(type(event_type).__name__)


class SerializationUtils:
    """
    Serialization utilities for events and commands.
    
    Supports:
    - JSON serialization with custom types
    - Pickle serialization for complex objects
    - Schema-based validation
    - Compression for large payloads
    """
    
    @staticmethod
    def to_json(obj: Any, indent: Optional[int] = None) -> str:
        """
        Serialize object to JSON with custom type handling.
        
        Args:
            obj: Object to serialize
            indent: JSON indentation
            
        Returns:
            JSON string
        """
        return json.dumps(obj, default=SerializationUtils._json_serializer, indent=indent, ensure_ascii=False)
    
    @staticmethod
    def from_json(json_str: str, target_type: Optional[Type] = None) -> Any:
        """
        Deserialize JSON string to object.
        
        Args:
            json_str: JSON string to deserialize
            target_type: Optional target type for conversion
            
        Returns:
            Deserialized object
        """
        data = json.loads(json_str)
        
        if target_type and hasattr(target_type, 'from_dict'):
            return target_type.from_dict(data)
        
        return data
    
    @staticmethod
    def to_pickle(obj: Any) -> bytes:
        """Serialize object to pickle bytes."""
        return pickle.dumps(obj)
    
    @staticmethod
    def from_pickle(data: bytes) -> Any:
        """Deserialize pickle bytes to object."""
        return pickle.loads(data)
    
    @staticmethod
    def to_dict(obj: Any) -> Dict[str, Any]:
        """Convert object to dictionary."""
        if hasattr(obj, 'to_dict'):
            return obj.to_dict()
        elif hasattr(obj, '__dict__'):
            return asdict(obj) if hasattr(obj, '__dataclass_fields__') else obj.__dict__
        else:
            return {'value': obj}
    
    @staticmethod
    def _json_serializer(obj: Any) -> Any:
        """Custom JSON serializer for complex types."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif hasattr(obj, 'to_dict'):
            return obj.to_dict()
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        else:
            return str(obj)


class ConfigurationManager:
    """
    Configuration management for different environments.
    
    Features:
    - Environment-based configuration
    - Configuration validation
    - Hot reloading
    - Default values and overrides
    """
    
    def __init__(self, config_file: Optional[str] = None, environment: Optional[str] = None):
        self._config_file = config_file
        self._environment = environment or os.getenv('ENVIRONMENT', 'development')
        self._config: Dict[str, Any] = {}
        self._defaults: Dict[str, Any] = {}
        self._validators: Dict[str, Callable] = {}
        self._load_config()
    
    def set_default(self, key: str, value: Any) -> None:
        """Set default value for configuration key."""
        self._defaults[key] = value
    
    def set_validator(self, key: str, validator: Callable[[Any], bool]) -> None:
        """Set validator for configuration key."""
        self._validators[key] = validator
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.
        
        Args:
            key: Configuration key (supports dot notation)
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        # Check environment variable first
        env_key = key.upper().replace('.', '_')
        env_value = os.getenv(env_key)
        if env_value is not None:
            return self._parse_env_value(env_value)
        
        # Check loaded configuration
        value = self._get_nested_value(self._config, key)
        if value is not None:
            return value
        
        # Check defaults
        if key in self._defaults:
            return self._defaults[key]
        
        return default
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""
        # Validate if validator exists
        if key in self._validators and not self._validators[key](value):
            raise DomainException(
                message=f"Configuration validation failed for key: {key}",
                error_code="CONFIGURATION_VALIDATION_FAILED"
            )
        
        self._set_nested_value(self._config, key, value)
    
    def reload(self) -> None:
        """Reload configuration from file."""
        self._load_config()
    
    def get_environment(self) -> str:
        """Get current environment."""
        return self._environment
    
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self._environment.lower() in ('dev', 'development')
    
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self._environment.lower() in ('prod', 'production')
    
    def _load_config(self) -> None:
        """Load configuration from file and environment."""
        self._config = {}
        
        if self._config_file and os.path.exists(self._config_file):
            try:
                with open(self._config_file, 'r') as f:
                    if self._config_file.endswith('.json'):
                        self._config = json.load(f)
                    elif self._config_file.endswith(('.yml', '.yaml')):
                        import yaml
                        self._config = yaml.safe_load(f)
            except Exception as e:
                logging.warning(f"Failed to load config file {self._config_file}: {str(e)}")
        
        # Load environment-specific section
        if self._environment in self._config:
            env_config = self._config[self._environment]
            self._config.update(env_config)
    
    def _get_nested_value(self, config: Dict[str, Any], key: str) -> Any:
        """Get nested configuration value using dot notation."""
        keys = key.split('.')
        value = config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return None
        
        return value
    
    def _set_nested_value(self, config: Dict[str, Any], key: str, value: Any) -> None:
        """Set nested configuration value using dot notation."""
        keys = key.split('.')
        current = config
        
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        current[keys[-1]] = value
    
    def _parse_env_value(self, value: str) -> Any:
        """Parse environment variable value to appropriate type."""
        # Try to parse as JSON first
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            pass
        
        # Try boolean
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'
        
        # Try integer
        try:
            return int(value)
        except ValueError:
            pass
        
        # Try float
        try:
            return float(value)
        except ValueError:
            pass
        
        # Return as string
        return value


class PerformanceMonitor:
    """
    Performance monitoring utilities.
    
    Features:
    - Method execution timing
    - Memory usage tracking
    - Performance metrics collection
    - Alert thresholds
    """
    
    def __init__(self):
        self._metrics: Dict[str, List[float]] = {}
        self._thresholds: Dict[str, float] = {}
        self._lock = Lock()
        self._logger = logging.getLogger(__name__ + ".PerformanceMonitor")
    
    def set_threshold(self, metric_name: str, threshold_ms: float) -> None:
        """Set performance threshold for metric."""
        self._thresholds[metric_name] = threshold_ms
    
    @contextmanager
    def measure(self, operation_name: str):
        """Context manager to measure operation time."""
        start_time = time.time()
        try:
            yield
        finally:
            execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            self.record_metric(operation_name, execution_time)
    
    def record_metric(self, metric_name: str, value: float) -> None:
        """Record performance metric."""
        with self._lock:
            if metric_name not in self._metrics:
                self._metrics[metric_name] = []
            
            self._metrics[metric_name].append(value)
            
            # Keep only last 1000 measurements
            if len(self._metrics[metric_name]) > 1000:
                self._metrics[metric_name] = self._metrics[metric_name][-1000:]
        
        # Check threshold
        if metric_name in self._thresholds and value > self._thresholds[metric_name]:
            self._logger.warning(f"Performance threshold exceeded for {metric_name}: {value:.2f}ms > {self._thresholds[metric_name]:.2f}ms")
    
    def get_statistics(self, metric_name: str) -> Dict[str, float]:
        """Get statistics for metric."""
        with self._lock:
            if metric_name not in self._metrics or not self._metrics[metric_name]:
                return {}
            
            values = self._metrics[metric_name]
            return {
                'count': len(values),
                'avg': sum(values) / len(values),
                'min': min(values),
                'max': max(values),
                'latest': values[-1]
            }
    
    def get_all_metrics(self) -> Dict[str, Dict[str, float]]:
        """Get statistics for all metrics."""
        return {name: self.get_statistics(name) for name in self._metrics.keys()}
    
    def clear_metrics(self, metric_name: Optional[str] = None) -> None:
        """Clear metrics."""
        with self._lock:
            if metric_name:
                self._metrics.pop(metric_name, None)
            else:
                self._metrics.clear()


class HealthChecker:
    """
    Health check implementations for monitoring system health.
    
    Features:
    - Component health checks
    - Dependency validation
    - Health status aggregation
    - Custom health checks
    """
    
    def __init__(self):
        self._checks: Dict[str, Callable[[], bool]] = {}
        self._check_results: Dict[str, Dict[str, Any]] = {}
        self._logger = logging.getLogger(__name__ + ".HealthChecker")
    
    def register_check(self, name: str, check_func: Callable[[], bool]) -> None:
        """Register health check function."""
        self._checks[name] = check_func
    
    def run_check(self, check_name: str) -> Dict[str, Any]:
        """Run specific health check."""
        if check_name not in self._checks:
            return {
                'name': check_name,
                'healthy': False,
                'message': 'Check not found',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
        
        start_time = time.time()
        try:
            result = self._checks[check_name]()
            execution_time = (time.time() - start_time) * 1000
            
            check_result = {
                'name': check_name,
                'healthy': bool(result),
                'message': 'OK' if result else 'Check failed',
                'execution_time_ms': execution_time,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            check_result = {
                'name': check_name,
                'healthy': False,
                'message': f'Check error: {str(e)}',
                'execution_time_ms': execution_time,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            self._logger.error(f"Health check {check_name} failed: {str(e)}")
        
        self._check_results[check_name] = check_result
        return check_result
    
    def run_all_checks(self) -> Dict[str, Any]:
        """Run all registered health checks."""
        results = {}
        overall_healthy = True
        
        for check_name in self._checks:
            result = self.run_check(check_name)
            results[check_name] = result
            
            if not result['healthy']:
                overall_healthy = False
        
        return {
            'healthy': overall_healthy,
            'checks': results,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    
    def is_healthy(self) -> bool:
        """Check overall system health."""
        health_result = self.run_all_checks()
        return health_result['healthy']


class ConnectionPoolManager:
    """
    Connection pooling and resource management.
    
    Features:
    - Connection pool management
    - Resource cleanup
    - Connection health monitoring
    - Automatic reconnection
    """
    
    def __init__(self, max_connections: int = 10):
        self._max_connections = max_connections
        self._pools: Dict[str, List[Any]] = {}
        self._factories: Dict[str, Callable] = {}
        self._validators: Dict[str, Callable] = {}
        self._lock = Lock()
        self._logger = logging.getLogger(__name__ + ".ConnectionPoolManager")
    
    def register_factory(self, pool_name: str, factory: Callable, validator: Optional[Callable] = None) -> None:
        """Register connection factory for pool."""
        self._factories[pool_name] = factory
        if validator:
            self._validators[pool_name] = validator
        
        with self._lock:
            if pool_name not in self._pools:
                self._pools[pool_name] = []
    
    @contextmanager
    def get_connection(self, pool_name: str):
        """Get connection from pool with automatic cleanup."""
        if pool_name not in self._factories:
            raise DomainException(
                message=f"Connection factory not registered for pool: {pool_name}",
                error_code="POOL_NOT_REGISTERED"
            )
        
        connection = self._acquire_connection(pool_name)
        try:
            yield connection
        finally:
            self._release_connection(pool_name, connection)
    
    def _acquire_connection(self, pool_name: str) -> Any:
        """Acquire connection from pool."""
        with self._lock:
            pool = self._pools[pool_name]
            
            # Try to get existing connection
            while pool:
                connection = pool.pop()
                
                # Validate connection if validator exists
                if pool_name in self._validators:
                    try:
                        if self._validators[pool_name](connection):
                            return connection
                        else:
                            # Invalid connection, try next one or create new
                            continue
                    except Exception:
                        continue
                else:
                    return connection
            
            # Create new connection if pool is empty
            try:
                connection = self._factories[pool_name]()
                self._logger.debug(f"Created new connection for pool: {pool_name}")
                return connection
            except Exception as e:
                raise DomainException(
                    message=f"Failed to create connection for pool {pool_name}: {str(e)}",
                    error_code="CONNECTION_CREATION_FAILED"
                )
    
    def _release_connection(self, pool_name: str, connection: Any) -> None:
        """Release connection back to pool."""
        with self._lock:
            pool = self._pools[pool_name]
            
            # Add back to pool if under limit
            if len(pool) < self._max_connections:
                pool.append(connection)
            else:
                # Close connection if pool is full
                try:
                    if hasattr(connection, 'close'):
                        connection.close()
                except Exception:
                    pass  # Ignore close errors
    
    def clear_pool(self, pool_name: str) -> None:
        """Clear all connections in pool."""
        with self._lock:
            if pool_name in self._pools:
                pool = self._pools[pool_name]
                
                # Close all connections
                for connection in pool:
                    try:
                        if hasattr(connection, 'close'):
                            connection.close()
                    except Exception:
                        pass
                
                pool.clear()
                self._logger.info(f"Cleared connection pool: {pool_name}")
    
    def get_pool_stats(self) -> Dict[str, Dict[str, int]]:
        """Get statistics for all pools."""
        with self._lock:
            return {
                name: {
                    'active_connections': len(pool),
                    'max_connections': self._max_connections
                }
                for name, pool in self._pools.items()
            }


# Global instances for easy access
event_dispatcher = EventDispatcher()
performance_monitor = PerformanceMonitor()
health_checker = HealthChecker()
connection_pool_manager = ConnectionPoolManager()

# Configuration manager with environment detection
config = ConfigurationManager(
    config_file=os.getenv('CONFIG_FILE', 'config.json'),
    environment=os.getenv('ENVIRONMENT', 'development')
)


# Utility decorators
def monitor_performance(operation_name: Optional[str] = None):
    """Decorator to monitor method performance."""
    def decorator(func):
        name = operation_name or f"{func.__module__}.{func.__name__}"
        
        def wrapper(*args, **kwargs):
            with performance_monitor.measure(name):
                return func(*args, **kwargs)
        
        return wrapper
    return decorator


def handle_errors(logger: Optional[logging.Logger] = None, reraise: bool = True):
    """Decorator to handle and log errors."""
    def decorator(func):
        log = logger or logging.getLogger(func.__module__)
        
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                log.error(f"Error in {func.__name__}: {str(e)}")
                if reraise:
                    raise
                return None
        
        return wrapper
    return decorator
