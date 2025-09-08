
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, fields, asdict
from typing import Any, Dict, List, Optional, Type, TypeVar, Union, Callable, Generic
from datetime import datetime, date
from enum import Enum

from ..dominio.excepciones import ValidationException


T = TypeVar('T')


class SerializationFormat(Enum):
    JSON = "json"
    XML = "xml"
    YAML = "yaml"


@dataclass
class DTO(ABC):    
    version: str = field(default="1.0", init=False)
    
    def validate(self) -> None:
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self, dict_factory=self._dict_factory)
    
    def to_json(self, indent: Optional[int] = None) -> str:
        return json.dumps(
            self.to_dict(), 
            default=self._json_serializer, 
            indent=indent,
            ensure_ascii=False
        )
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DTO':
        # Filter only fields that exist in the DTO
        field_names = {f.name for f in fields(cls)}
        filtered_data = {k: v for k, v in data.items() if k in field_names}
        
        return cls(**filtered_data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'DTO':
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def _dict_factory(self, field_list) -> Dict[str, Any]:
        result = {}
        for key, value in field_list:
            if value is not None:
                if isinstance(value, Enum):
                    result[key] = value.value
                elif isinstance(value, (datetime, date)):
                    result[key] = value.isoformat()
                elif hasattr(value, 'to_dict'):
                    result[key] = value.to_dict()
                else:
                    result[key] = value
        return result
    
    def _json_serializer(self, obj: Any) -> Any:
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        elif isinstance(obj, Enum):
            return obj.value
        elif hasattr(obj, 'to_dict'):
            return obj.to_dict()
        else:
            return str(obj)
    
    def __post_init__(self):
        self.validate()


@dataclass
class RequestDTO(DTO):
    correlation_id: Optional[str] = None
    user_id: Optional[str] = None
    tenant_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_metadata(self, key: str, value: Any) -> None:
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        return self.metadata.get(key, default)


@dataclass
class ResponseDTO(DTO):
    success: bool = True
    message: Optional[str] = None
    error_code: Optional[str] = None
    correlation_id: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    @classmethod
    def success_response(
        cls, 
        data: Optional[Any] = None, 
        message: Optional[str] = None,
        correlation_id: Optional[str] = None
    ) -> 'ResponseDTO':
        response = cls(
            success=True,
            message=message,
            correlation_id=correlation_id
        )
        
        if data is not None and hasattr(response, 'data'):
            response.data = data
        
        return response
    
    @classmethod
    def error_response(
        cls,
        message: str,
        error_code: Optional[str] = None,
        correlation_id: Optional[str] = None
    ) -> 'ResponseDTO':
        return cls(
            success=False,
            message=message,
            error_code=error_code,
            correlation_id=correlation_id
        )


@dataclass
class PagedResponseDTO(ResponseDTO):
    
    items: List[Any] = field(default_factory=list)
    pagination: Optional['PaginationMetadataDTO'] = None
    
    @classmethod
    def create(
        cls,
        items: List[Any],
        total_count: int,
        page_number: int,
        page_size: int,
        correlation_id: Optional[str] = None
    ) -> 'PagedResponseDTO':
        total_pages = (total_count + page_size - 1) // page_size
        
        pagination = PaginationMetadataDTO(
            total_count=total_count,
            page_number=page_number,
            page_size=page_size,
            total_pages=total_pages,
            has_next_page=page_number < total_pages,
            has_previous_page=page_number > 1
        )
        
        return cls(
            success=True,
            items=items,
            pagination=pagination,
            correlation_id=correlation_id
        )


@dataclass
class PaginationMetadataDTO(DTO):    
    total_count: int
    page_number: int
    page_size: int
    total_pages: int
    has_next_page: bool
    has_previous_page: bool


@dataclass
class ValidationErrorDTO(DTO):    
    field: str
    message: str
    rejected_value: Optional[Any] = None
    error_code: Optional[str] = None


@dataclass
class ErrorResponseDTO(ResponseDTO):    
    errors: List[ValidationErrorDTO] = field(default_factory=list)
    
    def add_field_error(self, field: str, message: str, rejected_value: Any = None) -> None:
        error = ValidationErrorDTO(
            field=field,
            message=message,
            rejected_value=rejected_value
        )
        self.errors.append(error)
    
    @classmethod
    def from_validation_exception(
        cls, 
        exception: ValidationException,
        correlation_id: Optional[str] = None
    ) -> 'ErrorResponseDTO':
        response = cls(
            success=False,
            message=exception.message,
            error_code=exception.error_code,
            correlation_id=correlation_id
        )
        
        for field, messages in exception.field_errors.items():
            for message in messages:
                response.add_field_error(field, message)
        
        return response


class DTOMapper(ABC, Generic[T]):
    @abstractmethod
    def to_dto(self, domain_object: T) -> DTO:
        pass
    
    @abstractmethod
    def from_dto(self, dto: DTO) -> T:
        pass
    
    def to_dto_list(self, domain_objects: List[T]) -> List[DTO]:
        return [self.to_dto(obj) for obj in domain_objects]
    
    def from_dto_list(self, dtos: List[DTO]) -> List[T]:
        return [self.from_dto(dto) for dto in dtos]


class AutoMapper:    
    @staticmethod
    def map_to_dto(domain_object: Any, dto_class: Type[DTO]) -> DTO:
        if domain_object is None:
            return None
        
        dto_fields = {f.name: f.type for f in fields(dto_class)}
        
        dto_data = {}
        for field_name, field_type in dto_fields.items():
            if hasattr(domain_object, field_name):
                value = getattr(domain_object, field_name)
                dto_data[field_name] = AutoMapper._convert_value(value, field_type)
        
        return dto_class(**dto_data)
    
    @staticmethod
    def map_from_dto(dto: DTO, domain_class: Type[T]) -> T:
        if dto is None:
            return None
        
        import inspect
        sig = inspect.signature(domain_class.__init__)
        params = list(sig.parameters.keys())[1:]
        
        domain_data = {}
        for param in params:
            if hasattr(dto, param):
                value = getattr(dto, param)
                domain_data[param] = value
        
        return domain_class(**domain_data)
    
    @staticmethod
    def _convert_value(value: Any, target_type: Type) -> Any:
        if value is None:
            return None
        
        if target_type in (str, int, float, bool):
            return target_type(value)
        
        if target_type == datetime and isinstance(value, str):
            return datetime.fromisoformat(value.replace('Z', '+00:00'))
        
        if hasattr(target_type, '__origin__') and target_type.__origin__ == list:
            if isinstance(value, list):
                item_type = target_type.__args__[0]
                return [AutoMapper._convert_value(item, item_type) for item in value]
        
        return value


class DTOFactory:
    def __init__(self):
        self._converters: Dict[str, Callable] = {}
        self._validators: Dict[Type[DTO], List[Callable]] = {}
    
    def register_converter(self, source_type: str, converter: Callable) -> None:
        self._converters[source_type] = converter
    
    def register_validator(self, dto_type: Type[DTO], validator: Callable) -> None:
        if dto_type not in self._validators:
            self._validators[dto_type] = []
        self._validators[dto_type].append(validator)
    
    def create_dto(
        self, 
        dto_type: Type[DTO], 
        data: Any, 
        source_type: Optional[str] = None
    ) -> DTO:
        if source_type and source_type in self._converters:
            converter = self._converters[source_type]
            converted_data = converter(data)
        else:
            converted_data = data
        
        if isinstance(converted_data, dict):
            dto = dto_type.from_dict(converted_data)
        else:
            dto = AutoMapper.map_to_dto(converted_data, dto_type)
        
        if dto_type in self._validators:
            for validator in self._validators[dto_type]:
                validator(dto)
        
        return dto


class DTOVersionManager:
    def __init__(self):
        self._migrators: Dict[str, Dict[str, Callable]] = {}
    
    def register_migrator(
        self, 
        dto_type: str, 
        from_version: str, 
        to_version: str,
        migrator: Callable
    ) -> None:
        if dto_type not in self._migrators:
            self._migrators[dto_type] = {}
        
        key = f"{from_version}->{to_version}"
        self._migrators[dto_type][key] = migrator
    
    def migrate_dto(
        self, 
        dto_dict: Dict[str, Any], 
        dto_type: str, 
        target_version: str
    ) -> Dict[str, Any]:
        current_version = dto_dict.get('version', '1.0')
        
        if current_version == target_version:
            return dto_dict
        
        if dto_type not in self._migrators:
            raise ValidationException(
                message=f"No migrators available for DTO type: {dto_type}",
                field_errors={"version": ["Migration not supported"]}
            )
        
        # Find migration path
        migration_key = f"{current_version}->{target_version}"
        
        if migration_key in self._migrators[dto_type]:
            migrator = self._migrators[dto_type][migration_key]
            migrated_data = migrator(dto_dict)
            migrated_data['version'] = target_version
            return migrated_data
        
        raise ValidationException(
            message=f"No migration path from {current_version} to {target_version}",
            field_errors={"version": [f"Migration from {current_version} to {target_version} not supported"]}
        )


def validate_required_fields(*field_names: str):
    def decorator(dto_class):
        original_validate = getattr(dto_class, 'validate', lambda self: None)
        
        def validate(self):
            original_validate(self)
            
            missing_fields = []
            for field_name in field_names:
                if not hasattr(self, field_name) or getattr(self, field_name) is None:
                    missing_fields.append(field_name)
            
            if missing_fields:
                raise ValidationException(
                    message=f"Required fields missing: {', '.join(missing_fields)}",
                    field_errors={field: ["Field is required"] for field in missing_fields}
                )
        
        dto_class.validate = validate
        return dto_class
    
    return decorator


def validate_field_range(field_name: str, min_value: Any = None, max_value: Any = None):
    def decorator(dto_class):
        original_validate = getattr(dto_class, 'validate', lambda self: None)
        
        def validate(self):
            original_validate(self)
            
            if hasattr(self, field_name):
                value = getattr(self, field_name)
                if value is not None:
                    if min_value is not None and value < min_value:
                        raise ValidationException(
                            message=f"Field '{field_name}' is below minimum value",
                            field_errors={field_name: [f"Must be >= {min_value}"]}
                        )
                    if max_value is not None and value > max_value:
                        raise ValidationException(
                            message=f"Field '{field_name}' exceeds maximum value",
                            field_errors={field_name: [f"Must be <= {max_value}"]}
                        )
        
        dto_class.validate = validate
        return dto_class
    
    return decorator


def validate_field_length(field_name: str, min_length: int = 0, max_length: Optional[int] = None):
    def decorator(dto_class):
        original_validate = getattr(dto_class, 'validate', lambda self: None)
        
        def validate(self):
            original_validate(self)
            
            if hasattr(self, field_name):
                value = getattr(self, field_name)
                if value is not None and hasattr(value, '__len__'):
                    length = len(value)
                    if length < min_length:
                        raise ValidationException(
                            message=f"Field '{field_name}' is too short",
                            field_errors={field_name: [f"Must be at least {min_length} characters"]}
                        )
                    if max_length is not None and length > max_length:
                        raise ValidationException(
                            message=f"Field '{field_name}' is too long",
                            field_errors={field_name: [f"Must be at most {max_length} characters"]}
                        )
        
        dto_class.validate = validate
        return dto_class
    
    return decorator
