"""
Partner domain entities implementation for HexaBuilders.
Implements Partner aggregate root with full business logic.
"""

from typing import Optional, List
from datetime import datetime

from ....seedwork.dominio.entidades import AggregateRoot, DomainEntity
from ....seedwork.dominio.excepciones import DomainException, BusinessRuleException
from .objetos_valor import (
    PartnerName, PartnerEmail, PartnerPhone, PartnerType, PartnerStatus,
    PartnerAddress, PartnerValidationData, PartnerMetrics
)
from .eventos import (
    PartnerCreated, PartnerStatusChanged, PartnerActivated, 
    PartnerDeactivated, PartnerUpdated, PartnerValidationCompleted
)
from .reglas import (
    PartnerMustHaveValidEmail, PartnerMustHaveValidPhone,
    PartnerCanOnlyBeActivatedIfValidated, PartnerCannotBeDeletedWithActiveCampaigns
)


class Partner(AggregateRoot):
    """
    Partner aggregate root.
    
    Represents a business partner in the HexaBuilders platform.
    Partners can create and manage campaigns, earn commissions,
    and participate in the partner ecosystem.
    """
    
    def __init__(
        self,
        nombre: PartnerName,
        email: PartnerEmail,
        telefono: PartnerPhone,
        tipo: PartnerType,
        partner_id: Optional[str] = None,
        direccion: Optional[PartnerAddress] = None,
        status: PartnerStatus = PartnerStatus.ACTIVO,
        validation_data: Optional[PartnerValidationData] = None,
        metrics: Optional[PartnerMetrics] = None
    ):
        super().__init__(partner_id)
        
        # Validate business rules
        rule_email = PartnerMustHaveValidEmail(email)
        rule_phone = PartnerMustHaveValidPhone(telefono)
        
        if not rule_email.is_valid():
            raise BusinessRuleException(rule_email)
        if not rule_phone.is_valid():
            raise BusinessRuleException(rule_phone)
        
        # Set attributes
        self._nombre = nombre
        self._email = email
        self._telefono = telefono
        self._tipo = tipo
        self._direccion = direccion
        self._status = status
        self._validation_data = validation_data or PartnerValidationData()
        self._metrics = metrics or PartnerMetrics()
        
        # Domain event
        self.agregar_evento(PartnerCreated(
            aggregate_id=self.id,
            business_name=self._nombre.value,
            email=self._email.value,
            partner_type=self._tipo.value,
            phone=self._telefono.value
        ))
    
    @property
    def nombre(self) -> PartnerName:
        return self._nombre
    
    @property
    def email(self) -> PartnerEmail:
        return self._email
    
    @property
    def telefono(self) -> PartnerPhone:
        return self._telefono
    
    @property
    def tipo(self) -> PartnerType:
        return self._tipo
    
    @property
    def direccion(self) -> Optional[PartnerAddress]:
        return self._direccion
    
    @property
    def status(self) -> PartnerStatus:
        return self._status
    
    @property
    def validation_data(self) -> PartnerValidationData:
        return self._validation_data
    
    @property
    def metrics(self) -> PartnerMetrics:
        return self._metrics
    
    def actualizar_informacion(
        self,
        nombre: Optional[PartnerName] = None,
        telefono: Optional[PartnerPhone] = None,
        direccion: Optional[PartnerAddress] = None
    ) -> None:
        """Update partner information."""
        
        old_data = {
            'nombre': self._nombre.value,
            'telefono': self._telefono.value,
            'direccion': self._direccion.direccion if self._direccion else None
        }
        
        if nombre and nombre != self._nombre:
            self._nombre = nombre
        
        if telefono and telefono != self._telefono:
            rule = PartnerMustHaveValidPhone(telefono)
            if not rule.is_valid():
                raise BusinessRuleException(rule)
            self._telefono = telefono
        
        if direccion:
            self._direccion = direccion
        
        self._mark_updated()
        
        # Domain event
        self.agregar_evento(PartnerUpdated(
            aggregate_id=self.id,
            old_data=old_data,
            new_data={
                'nombre': self._nombre.value,
                'telefono': self._telefono.value,
                'direccion': self._direccion.direccion if self._direccion else None
            }
        ))
    
    def activar(self) -> None:
        """Activate partner."""
        
        if self._status == PartnerStatus.ACTIVO:
            return  # Already active
        
        # Business rule: Partner must be validated to be activated
        if self._status == PartnerStatus.INACTIVO:
            rule = PartnerCanOnlyBeActivatedIfValidated(self._validation_data)
            if not rule.is_valid():
                raise BusinessRuleException(rule)
        
        old_status = self._status
        self._status = PartnerStatus.ACTIVO
        self._mark_updated()
        
        # Domain events
        self.agregar_evento(PartnerStatusChanged(
            aggregate_id=self.id,
            old_status=old_status.value,
            new_status=self._status.value,
            reason="Partner activated"
        ))
        
        self.agregar_evento(PartnerActivated(
            aggregate_id=self.id,
            partner_email=self._email.value,
            partner_name=self._nombre.value
        ))
    
    def desactivar(self, reason: Optional[str] = None) -> None:
        """Deactivate partner."""
        
        if self._status == PartnerStatus.INACTIVO:
            return  # Already inactive
        
        old_status = self._status
        self._status = PartnerStatus.INACTIVO
        self._mark_updated()
        
        # Domain events
        self.agregar_evento(PartnerStatusChanged(
            aggregate_id=self.id,
            old_status=old_status.value,
            new_status=self._status.value,
            reason=reason or "Partner deactivated"
        ))
        
        self.agregar_evento(PartnerDeactivated(
            aggregate_id=self.id,
            partner_email=self._email.value,
            partner_name=self._nombre.value,
            reason=reason
        ))
    
    def suspender(self, reason: str) -> None:
        """Suspend partner."""
        
        if not reason:
            raise DomainException("Suspension reason is required")
        
        if self._status == PartnerStatus.SUSPENDIDO:
            return  # Already suspended
        
        old_status = self._status
        self._status = PartnerStatus.SUSPENDIDO
        self._mark_updated()
        
        self.agregar_evento(PartnerStatusChanged(
            aggregate_id=self.id,
            old_status=old_status.value,
            new_status=self._status.value,
            reason=reason
        ))
    
    def validar_email(self) -> None:
        """Mark email as validated."""
        
        if self._validation_data.email_validated:
            return  # Already validated
        
        self._validation_data = PartnerValidationData(
            email_validated=True,
            phone_validated=self._validation_data.phone_validated,
            identity_validated=self._validation_data.identity_validated,
            business_validated=self._validation_data.business_validated
        )
        
        self._mark_updated()
        
        if self._validation_data.is_fully_validated():
            self._status = PartnerStatus.VALIDADO
            self.agregar_evento(PartnerValidationCompleted(
                aggregate_id=self.id,
                validation_type="complete",
                partner_email=self._email.value
            ))
    
    def validar_telefono(self) -> None:
        """Mark phone as validated."""
        
        if self._validation_data.phone_validated:
            return  # Already validated
        
        self._validation_data = PartnerValidationData(
            email_validated=self._validation_data.email_validated,
            phone_validated=True,
            identity_validated=self._validation_data.identity_validated,
            business_validated=self._validation_data.business_validated
        )
        
        self._mark_updated()
        
        if self._validation_data.is_fully_validated():
            self._status = PartnerStatus.VALIDADO
            self.agregar_evento(PartnerValidationCompleted(
                aggregate_id=self.id,
                validation_type="complete",
                partner_email=self._email.value
            ))
    
    def actualizar_metricas(self, nuevas_metricas: PartnerMetrics) -> None:
        """Update partner performance metrics."""
        
        self._metrics = nuevas_metricas
        self._mark_updated()
    
    def puede_crear_campanas(self) -> bool:
        """Check if partner can create campaigns."""
        return self._status in [PartnerStatus.ACTIVO, PartnerStatus.VALIDADO]
    
    def puede_recibir_comisiones(self) -> bool:
        """Check if partner can receive commissions."""
        return (
            self._status in [PartnerStatus.ACTIVO, PartnerStatus.VALIDADO] and
            self._validation_data.email_validated
        )
    
    def eliminar_suave(self, active_campaigns_count: int = 0) -> None:
        """Soft delete partner."""
        
        rule = PartnerCannotBeDeletedWithActiveCampaigns(active_campaigns_count)
        if not rule.is_valid():
            raise BusinessRuleException(rule)
        
        old_status = self._status
        self._status = PartnerStatus.ELIMINADO
        self.soft_delete()
        
        self.agregar_evento(PartnerStatusChanged(
            aggregate_id=self.id,
            old_status=old_status.value,
            new_status=self._status.value,
            reason="Partner deleted"
        ))
    
    def validate(self) -> None:
        """Validate partner state."""
        
        if not self._nombre or not self._email or not self._telefono:
            raise DomainException("Partner must have name, email and phone")
        
        if not self._tipo:
            raise DomainException("Partner must have a type")
        
        # Business rules validation
        rules = [
            PartnerMustHaveValidEmail(self._email),
            PartnerMustHaveValidPhone(self._telefono)
        ]
        
        for rule in rules:
            if not rule.is_valid():
                raise BusinessRuleException(rule)
    
    def get_profile_360(self) -> dict:
        """Get comprehensive partner profile."""
        
        return {
            'id': self.id,
            'nombre': self._nombre.value,
            'email': self._email.value,
            'telefono': self._telefono.value,
            'tipo': self._tipo.value,
            'status': self._status.value,
            'direccion': {
                'direccion': self._direccion.direccion,
                'ciudad': self._direccion.ciudad,
                'pais': self._direccion.pais,
                'codigo_postal': self._direccion.codigo_postal
            } if self._direccion else None,
            'validation': {
                'email_validated': self._validation_data.email_validated,
                'phone_validated': self._validation_data.phone_validated,
                'identity_validated': self._validation_data.identity_validated,
                'business_validated': self._validation_data.business_validated,
                'validation_percentage': self._validation_data.validation_percentage()
            },
            'metrics': {
                'total_campaigns': self._metrics.total_campaigns,
                'completed_campaigns': self._metrics.completed_campaigns,
                'success_rate': self._metrics.success_rate,
                'total_commissions': self._metrics.total_commissions,
                'average_rating': self._metrics.average_rating
            },
            'timestamps': {
                'created_at': self.created_at.isoformat(),
                'updated_at': self.updated_at.isoformat()
            },
            'version': self.version
        }
    
    def __repr__(self) -> str:
        return f"Partner(id={self.id}, name={self._nombre.value}, email={self._email.value}, status={self._status.value})"