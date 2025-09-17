import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Callable, Type, Union
from functools import wraps

from flask import Flask, request, jsonify, g, current_app
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

from ..dominio.excepciones import (
    DomainException, 
    ValidationException, 
    EntityNotFoundException,
    BusinessRuleViolationException,
    AuthorizationException
)
from ..aplicacion.dto import ResponseDTO, ErrorResponseDTO, ValidationErrorDTO

logger = logging.getLogger(__name__)


def create_app(config: Optional[Dict[str, Any]] = None) -> Flask:
    """
    Patrón de fábrica de aplicación Flask.
    
    Crea y configura aplicación Flask con:
    - Configuración CORS
    - Middleware de manejo de errores
    - Logging de peticiones/respuestas
    - Endpoints de verificación de salud
    - Soporte de versionado de API
    
    Args:
        config: Diccionario de configuración opcional
        
    Returns:
        Aplicación Flask configurada
    """
    app = Flask(__name__)
    
    # Aplicar configuración
    if config:
        app.config.update(config)
    
    # Configurar CORS para peticiones de origen cruzado
    CORS(app, 
         origins=app.config.get('CORS_ORIGINS', ['http://localhost:3000']),
         methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'],
         allow_headers=['Content-Type', 'Authorization', 'X-Correlation-ID'])
    
    # Registrar manejadores de errores
    register_error_handlers(app)
    
    # Registrar middleware
    register_middleware(app)
    
    # Registrar endpoints de verificación de salud
    register_health_endpoints(app)
    
    # Registrar blueprints CQRS
    register_cqrs_blueprints(app)
    
    # Configurar logging
    setup_logging(app)
    
    return app


def register_error_handlers(app: Flask) -> None:
    """Registrar manejadores de errores para excepciones de dominio y errores HTTP."""
    
    @app.errorhandler(ValidationException)
    def handle_validation_error(error: ValidationException) -> tuple:
        """Manejar excepciones de validación con errores de campo detallados."""
        correlation_id = getattr(g, 'correlation_id', None)
        
        response = ErrorResponseDTO.from_validation_exception(
            error, correlation_id=correlation_id
        )
        
        return jsonify(response.to_dict()), 400
    
    @app.errorhandler(EntityNotFoundException)
    def handle_not_found_error(error: EntityNotFoundException) -> tuple:
        """Manejar excepciones de entidad no encontrada."""
        correlation_id = getattr(g, 'correlation_id', None)
        
        response = ErrorResponseDTO(
            success=False,
            message=error.message,
            error_code=error.error_code,
            correlation_id=correlation_id
        )
        
        return jsonify(response.to_dict()), 404
    
    @app.errorhandler(BusinessRuleViolationException)
    def handle_business_rule_error(error: BusinessRuleViolationException) -> tuple:
        """Manejar excepciones de violación de reglas de negocio."""
        correlation_id = getattr(g, 'correlation_id', None)
        
        response = ErrorResponseDTO(
            success=False,
            message=error.message,
            error_code=error.error_code,
            correlation_id=correlation_id
        )
        
        # Agregar violaciones individuales como errores de campo
        for violation in error.violations:
            response.add_field_error("business_rule", violation)
        
        return jsonify(response.to_dict()), 422
    
    @app.errorhandler(AuthorizationException)
    def handle_authorization_error(error: AuthorizationException) -> tuple:
        """Manejar excepciones de autorización."""
        correlation_id = getattr(g, 'correlation_id', None)
        
        response = ErrorResponseDTO(
            success=False,
            message=error.message,
            error_code=error.error_code,
            correlation_id=correlation_id
        )
        
        return jsonify(response.to_dict()), 403
    
    @app.errorhandler(DomainException)
    def handle_domain_error(error: DomainException) -> tuple:
        """Manejar excepciones de dominio genéricas."""
        correlation_id = getattr(g, 'correlation_id', None)
        
        response = ErrorResponseDTO(
            success=False,
            message=error.message,
            error_code=error.error_code,
            correlation_id=correlation_id
        )
        
        return jsonify(response.to_dict()), 500
    
    @app.errorhandler(HTTPException)
    def handle_http_error(error: HTTPException) -> tuple:
        """Manejar excepciones HTTP."""
        correlation_id = getattr(g, 'correlation_id', None)
        
        response = ErrorResponseDTO(
            success=False,
            message=error.description or "Error HTTP",
            error_code=f"HTTP_{error.code}",
            correlation_id=correlation_id
        )
        
        return jsonify(response.to_dict()), error.code
    
    @app.errorhandler(Exception)
    def handle_unexpected_error(error: Exception) -> tuple:
        """Manejar excepciones inesperadas."""
        correlation_id = getattr(g, 'correlation_id', None)
        
        # Registrar el error para debugging
        app.logger.error(f"Unexpected error: {str(error)}", exc_info=True)
        
        # No exponer detalles internos de error en producción
        if app.config.get('DEBUG', False):
            message = str(error)
        else:
            message = "Ocurrió un error inesperado"
        
        response = ErrorResponseDTO(
            success=False,
            message=message,
            error_code="INTERNAL_SERVER_ERROR",
            correlation_id=correlation_id
        )
        
        return jsonify(response.to_dict()), 500


def register_middleware(app: Flask) -> None:
    """Registrar middleware para procesamiento de peticiones/respuestas."""
    
    @app.before_request
    def before_request():
        """Procesar petición antes de la ejecución del handler."""
        # Generar ID de correlación para trazabilidad
        correlation_id = request.headers.get('X-Correlation-ID')
        if not correlation_id:
            import uuid
            correlation_id = str(uuid.uuid4())
        
        g.correlation_id = correlation_id
        g.request_start_time = datetime.now(timezone.utc)
        
        # Extraer contexto de usuario
        g.user_id = request.headers.get('X-User-ID')
        g.tenant_id = request.headers.get('X-Tenant-ID')
        
        # Registrar petición
        app.logger.info(
            f"Request started - Method: {request.method}, "
            f"Path: {request.path}, "
            f"Correlation-ID: {correlation_id}, "
            f"User-ID: {g.user_id}"
        )
    
    @app.after_request
    def after_request(response):
        """Procesar respuesta después de la ejecución del handler."""
        if hasattr(g, 'correlation_id'):
            response.headers['X-Correlation-ID'] = g.correlation_id
        
        # Calcular duración de la petición
        if hasattr(g, 'request_start_time'):
            duration = (datetime.now(timezone.utc) - g.request_start_time).total_seconds() * 1000
            response.headers['X-Request-Duration-Ms'] = str(int(duration))
            
            # Registrar respuesta
            app.logger.info(
                f"Request completed - Status: {response.status_code}, "
                f"Duration: {duration:.2f}ms, "
                f"Correlation-ID: {getattr(g, 'correlation_id', 'unknown')}"
            )
        
        return response


def register_cqrs_blueprints(app: Flask) -> None:
    """Registrar blueprints CQRS de la aplicación."""
    try:
        from ...api.partners_cqrs import bp as partners_bp
        app.register_blueprint(partners_bp)
        logger.info("Partners CQRS blueprint registered successfully")
    except ImportError as e:
        logger.warning(f"Could not register Partners CQRS blueprint: {e}")
    except Exception as e:
        logger.error(f"Error registering CQRS blueprints: {e}")


def register_health_endpoints(app: Flask) -> None:
    """Registrar endpoints de verificación de salud y métricas."""
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """Endpoint básico de verificación de salud."""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'service': 'partner-management',
            'version': app.config.get('VERSION', '1.0.0')
        })
    
    @app.route('/health/ready', methods=['GET'])
    def readiness_check():
        """Verificación de preparación para Kubernetes."""
        # Agregar verificaciones para dependencias (base de datos, cola de mensajes, etc.)
        checks = {
            'database': True,  # Reemplazar con verificación real de base de datos
            'message_queue': True,  # Reemplazar con verificación real de cola
            'external_services': True  # Reemplazar con verificaciones reales de servicios externos
        }
        
        all_ready = all(checks.values())
        status_code = 200 if all_ready else 503
        
        return jsonify({
            'ready': all_ready,
            'checks': checks,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), status_code
    
    @app.route('/health/live', methods=['GET'])
    def liveness_check():
        """Verificación de actividad para Kubernetes."""
        return jsonify({
            'alive': True,
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
    
    @app.route('/metrics', methods=['GET'])
    def metrics():
        """Endpoint básico de métricas."""
        # Esto se integraría con colección real de métricas
        return jsonify({
            'requests_total': 0,  # Reemplazar con métrica real
            'requests_duration_seconds': 0,  # Reemplazar con métrica real
            'active_connections': 0,  # Reemplazar con métrica real
            'timestamp': datetime.now(timezone.utc).isoformat()
        })


def setup_logging(app: Flask) -> None:
    """Configurar logging estructurado para la aplicación."""
    if not app.debug:
        # Configurar logging de producción
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s %(levelname)s [%(name)s] %(message)s'
        )
        
        # Establecer niveles de log para librerías de terceros
        logging.getLogger('werkzeug').setLevel(logging.WARNING)


class BaseController:
    """
    Clase controlador base con funcionalidad común.
    
    Proporciona:
    - Acceso al contexto de petición
    - Patrones de respuesta comunes
    - Utilidades de manejo de errores
    - Helpers de autenticación/autorización
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @property
    def correlation_id(self) -> Optional[str]:
        """Obtener ID de correlación del contexto de petición."""
        return getattr(g, 'correlation_id', None)
    
    @property
    def user_id(self) -> Optional[str]:
        """Obtener ID de usuario del contexto de petición."""
        return getattr(g, 'user_id', None)
    
    @property
    def tenant_id(self) -> Optional[str]:
        """Obtener ID de inquilino del contexto de petición."""
        return getattr(g, 'tenant_id', None)
    
    def success_response(self, data: Any = None, message: str = None) -> Dict[str, Any]:
        """Crear respuesta exitosa."""
        response = ResponseDTO.success_response(
            data=data,
            message=message,
            correlation_id=self.correlation_id
        )
        return response.to_dict()
    
    def error_response(self, message: str, error_code: str = None) -> Dict[str, Any]:
        """Crear respuesta de error."""
        response = ErrorResponseDTO.error_response(
            message=message,
            error_code=error_code,
            correlation_id=self.correlation_id
        )
        return response.to_dict()
    
    def get_json_data(self, required_fields: List[str] = None) -> Dict[str, Any]:
        """
        Obtener datos JSON de la petición con validación.
        
        Args:
            required_fields: Lista de nombres de campos requeridos
            
        Returns:
            Diccionario de datos JSON
            
        Raises:
            ValidationException: Si faltan campos requeridos
        """
        if not request.is_json:
            raise ValidationException(
                message="La petición debe contener datos JSON",
                field_errors={"content_type": ["Debe ser application/json"]}
            )
        
        data = request.get_json()
        if not data:
            raise ValidationException(
                message="El cuerpo de la petición no puede estar vacío",
                field_errors={"body": ["No puede estar vacío"]}
            )
        
        if required_fields:
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                raise ValidationException(
                    message=f"Faltan campos requeridos: {', '.join(missing_fields)}",
                    field_errors={field: ["Falta campo requerido"] for field in missing_fields}
                )
        
        return data
    
    def require_authentication(self) -> str:
        """
        Requerir autenticación de usuario.
        
        Returns:
            ID de usuario
            
        Raises:
            AuthorizationException: Si el usuario no está autenticado
        """
        if not self.user_id:
            raise AuthorizationException(
                message="Autenticación requerida",
                user_id=None,
                action="access_resource"
            )
        
        return self.user_id
    
    def require_authorization(self, required_roles: List[str] = None) -> str:
        """
        Requerir autorización de usuario con verificación opcional de roles.
        
        Args:
            required_roles: Lista de roles requeridos
            
        Returns:
            ID de usuario
            
        Raises:
            AuthorizationException: Si el usuario carece de autorización requerida
        """
        user_id = self.require_authentication()
        
        if required_roles:
            # Esto se integraría con el sistema real de verificación de roles
            user_roles = request.headers.get('X-User-Roles', '').split(',')
            
            if not any(role in user_roles for role in required_roles):
                raise AuthorizationException(
                    message=f"Roles requeridos: {', '.join(required_roles)}",
                    user_id=user_id,
                    action="access_resource"
                )
        
        return user_id


def api_route(path: str, methods: List[str] = None, **options):
    """
    Decorador para rutas de API con funcionalidad común.
    
    Agrega:
    - Manejo de errores
    - Formateo de respuestas
    - Monitoreo de rendimiento
    - Autenticación/autorización (si se requiere)
    """
    methods = methods or ['GET']
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = datetime.now(timezone.utc)
            
            try:
                # Ejecutar el handler de la ruta
                result = func(*args, **kwargs)
                
                # Si el resultado ya es un objeto Response, retornar tal como está
                if hasattr(result, 'status_code'):
                    return result
                
                # Si el resultado es una tupla (data, status_code), desempaquetarla
                if isinstance(result, tuple) and len(result) == 2:
                    data, status_code = result
                    return jsonify(data), status_code
                
                # En caso contrario, asumir que son datos exitosos
                return jsonify(result)
                
            except Exception as e:
                # Dejar que los manejadores de errores se encarguen de las excepciones
                raise
            
            finally:
                # Registrar métricas de rendimiento
                duration = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
                current_app.logger.debug(f"Route {path} executed in {duration:.2f}ms")
        
        # Registrar ruta con Flask
        return current_app.route(path, methods=methods, **options)(wrapper)
    
    return decorator


def require_auth(roles: List[str] = None):
    """
    Decorador para requerir autenticación y autorización opcional basada en roles.
    
    Args:
        roles: Lista opcional de roles requeridos
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Verificar autenticación
            user_id = g.get('user_id')
            if not user_id:
                raise AuthorizationException(
                    message="Autenticación requerida",
                    user_id=None,
                    action=func.__name__
                )
            
            # Verificar autorización si se especificaron roles
            if roles:
                user_roles = request.headers.get('X-User-Roles', '').split(',')
                if not any(role in user_roles for role in roles):
                    raise AuthorizationException(
                        message=f"Roles requeridos: {', '.join(roles)}",
                        user_id=user_id,
                        action=func.__name__
                    )
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def validate_json(schema: Dict[str, Any]):
    """
    Decorador para validar el cuerpo de petición JSON contra esquema.
    
    Args:
        schema: Esquema JSON para validación
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not request.is_json:
                raise ValidationException(
                    message="La petición debe contener datos JSON",
                    field_errors={"content_type": ["Debe ser application/json"]}
                )
            
            data = request.get_json()
            if not data:
                raise ValidationException(
                    message="El cuerpo de la petición no puede estar vacío",
                    field_errors={"body": ["No puede estar vacío"]}
                )
            
            # Validación básica de esquema (en producción, usar librería jsonschema)
            required_fields = schema.get('required', [])
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                raise ValidationException(
                    message=f"Faltan campos requeridos: {', '.join(missing_fields)}",
                    field_errors={field: ["Falta campo requerido"] for field in missing_fields}
                )
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def api_versioning(version: str):
    """
    Decorador para soporte de versionado de API.
    
    Args:
        version: Versión de API (ej., "v1", "v2")
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Agregar versión a los headers de respuesta
            g.api_version = version
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


# Funciones de utilidad para patrones comunes de API
def paginate_response(items: List[Any], page: int, page_size: int, total_count: int) -> Dict[str, Any]:
    """
    Crear respuesta paginada con metadatos.
    
    Args:
        items: Lista de elementos para la página actual
        page: Número de página actual
        page_size: Elementos por página
        total_count: Número total de elementos
        
    Returns:
        Diccionario de respuesta paginada
    """
    from ..aplicacion.dto import PagedResponseDTO
    
    response = PagedResponseDTO.create(
        items=items,
        total_count=total_count,
        page_number=page,
        page_size=page_size,
        correlation_id=getattr(g, 'correlation_id', None)
    )
    
    return response.to_dict()


def extract_pagination_params() -> tuple[int, int]:
    """
    Extraer parámetros de paginación de la petición.
    
    Returns:
        Tupla de (page, page_size)
    """
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)
    
    # Validar parámetros de paginación
    if page < 1:
        raise ValidationException(
            message="El número de página debe ser mayor que 0",
            field_errors={"page": ["Debe ser mayor que 0"]}
        )
    
    if page_size < 1 or page_size > 100:
        raise ValidationException(
            message="El tamaño de página debe estar entre 1 y 100",
            field_errors={"page_size": ["Debe estar entre 1 y 100"]}
        )
    
    return page, page_size


def extract_sort_params() -> List[tuple[str, str]]:
    """
    Extraer parámetros de ordenamiento de la petición.
    
    Returns:
        Lista de tuplas (field, direction)
    """
    sort_param = request.args.get('sort', '')
    if not sort_param:
        return []
    
    sort_fields = []
    for sort_item in sort_param.split(','):
        if sort_item.startswith('-'):
            field = sort_item[1:]
            direction = 'desc'
        else:
            field = sort_item
            direction = 'asc'
        
        sort_fields.append((field, direction))
    
    return sort_fields


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
