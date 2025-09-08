"""
Mock repositories for Commission module in HexaBuilders.
Provides in-memory data persistence for development and testing.
"""

import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Optional, Any
from collections import defaultdict

from partner_management.seedwork.dominio.repositorio import Repositorio
from partner_management.seedwork.dominio.excepciones import DomainException

from ..dominio.entidades import Commission
from ..dominio.objetos_valor import (
    CommissionAmount, CommissionRate, CommissionPeriod, TransactionReference,
    CommissionType, CommissionStatus, CommissionCalculation
)
from .dto import CommissionDTO
from .fabricas import FabricaCommission


class RepositorioCommissionMock(Repositorio):
    """Mock repository for Commission entities."""
    
    def __init__(self):
        super().__init__()
        self._commissions: Dict[str, Commission] = {}
        self._fabrica = FabricaCommission()
        self._initialize_sample_data()
    
    def obtener_por_id(self, commission_id: str) -> Optional[Commission]:
        """Get commission by ID."""
        return self._commissions.get(commission_id)
    
    def obtener_por_transaction_id(self, transaction_id: str) -> Optional[Commission]:
        """Get commission by transaction ID."""
        for commission in self._commissions.values():
            if commission.transaction_reference.transaction_id == transaction_id:
                return commission
        return None
    
    def obtener_todos(self) -> List[Commission]:
        """Get all commissions."""
        return [c for c in self._commissions.values() if not c.is_deleted]
    
    def obtener_por_partner_id(self, partner_id: str) -> List[Commission]:
        """Get commissions by partner ID."""
        return [
            c for c in self._commissions.values() 
            if c.partner_id == partner_id and not c.is_deleted
        ]
    
    def obtener_por_status(self, status: CommissionStatus) -> List[Commission]:
        """Get commissions by status."""
        return [
            c for c in self._commissions.values() 
            if c.status == status and not c.is_deleted
        ]
    
    def obtener_todos_con_filtros(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Commission]:
        """Get commissions with filters and pagination."""
        
        commissions = [c for c in self._commissions.values() if not c.is_deleted]
        
        if filters:
            # Apply partner_id filter
            if 'partner_id' in filters:
                commissions = [c for c in commissions if c.partner_id == filters['partner_id']]
            
            # Apply status filter
            if 'status' in filters:
                status_filter = CommissionStatus(filters['status'])
                commissions = [c for c in commissions if c.status == status_filter]
            
            # Apply commission_type filter
            if 'commission_type' in filters:
                type_filter = CommissionType(filters['commission_type'])
                commissions = [c for c in commissions if c.commission_type == type_filter]
            
            # Apply date range filters
            if 'start_date' in filters:
                start_date = filters['start_date']
                commissions = [c for c in commissions if c.created_at >= start_date]
            
            if 'end_date' in filters:
                end_date = filters['end_date']
                commissions = [c for c in commissions if c.created_at <= end_date]
        
        # Sort by creation date (newest first)
        commissions.sort(key=lambda c: c.created_at, reverse=True)
        
        # Apply pagination
        return commissions[offset:offset + limit]
    
    def contar_con_filtros(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count commissions with filters."""
        return len(self.obtener_todos_con_filtros(filters, limit=10000, offset=0))
    
    def agregar(self, commission: Commission) -> None:
        """Add new commission."""
        if commission.id in self._commissions:
            raise DomainException(f"Commission with ID {commission.id} already exists")
        self._commissions[commission.id] = commission
    
    def actualizar(self, commission: Commission) -> None:
        """Update existing commission."""
        if commission.id not in self._commissions:
            raise DomainException(f"Commission with ID {commission.id} not found")
        self._commissions[commission.id] = commission
    
    def eliminar(self, commission: Commission) -> None:
        """Soft delete commission."""
        if commission.id in self._commissions:
            commission.soft_delete()
            self._commissions[commission.id] = commission
    
    def obtener_estadisticas_partner(self, partner_id: str) -> Dict[str, Any]:
        """Get commission statistics for partner."""
        partner_commissions = self.obtener_por_partner_id(partner_id)
        
        if not partner_commissions:
            return {
                'total_commissions': 0,
                'total_earned': Decimal('0'),
                'total_paid': Decimal('0'),
                'total_pending': Decimal('0'),
                'average_commission': Decimal('0')
            }
        
        total_earned = sum(c.commission_amount.amount for c in partner_commissions)
        total_paid = sum(
            c.commission_amount.amount for c in partner_commissions 
            if c.status == CommissionStatus.PAID
        )
        total_pending = sum(
            c.commission_amount.amount for c in partner_commissions 
            if c.status in [CommissionStatus.PENDING, CommissionStatus.APPROVED]
        )
        
        return {
            'total_commissions': len(partner_commissions),
            'total_earned': total_earned,
            'total_paid': total_paid,
            'total_pending': total_pending,
            'average_commission': total_earned / len(partner_commissions)
        }
    
    def _initialize_sample_data(self):
        """Initialize with sample commission data."""
        
        # Sample partner IDs (these should match partners in partner mock repo)
        sample_partner_ids = [
            "partner-001", "partner-002", "partner-003", 
            "partner-004", "partner-005"
        ]
        
        # Create sample commissions
        base_date = datetime.now() - timedelta(days=90)
        
        for i in range(20):
            partner_id = sample_partner_ids[i % len(sample_partner_ids)]
            
            # Vary commission types and amounts
            commission_types = ['SALE_COMMISSION', 'LEAD_COMMISSION', 'PERFORMANCE_BONUS', 'REFERRAL_BONUS']
            commission_type = commission_types[i % len(commission_types)]
            
            # Create transaction reference
            transaction_amount = Decimal(str(100 + (i * 50)))
            commission_rate = Decimal('0.05') + (Decimal(str(i % 3)) * Decimal('0.02'))  # 5-9%
            commission_amount = transaction_amount * commission_rate
            
            # Create value objects
            commission_amount_obj = CommissionAmount(commission_amount, "USD")
            commission_rate_obj = CommissionRate(commission_rate)
            commission_type_obj = CommissionType(commission_type)
            
            transaction_reference = TransactionReference(
                transaction_id=f"txn_{uuid.uuid4().hex[:8]}",
                transaction_type="SALE" if commission_type == "SALE_COMMISSION" else "LEAD",
                transaction_amount=transaction_amount,
                transaction_date=base_date + timedelta(days=i * 4)
            )
            
            # Create calculation period
            period_start = base_date + timedelta(days=i * 4)
            period_end = period_start + timedelta(days=30)
            calculation_period = CommissionPeriod(
                start_date=period_start,
                end_date=period_end,
                period_name=f"Period {i+1}"
            )
            
            # Vary status
            statuses = [
                CommissionStatus.PENDING, CommissionStatus.APPROVED, 
                CommissionStatus.PAID, CommissionStatus.PAID
            ]  # More paid commissions for realistic data
            status = statuses[i % len(statuses)]
            
            # Create calculation details
            calculation_details = CommissionCalculation(
                base_amount=transaction_amount,
                commission_rate=commission_rate_obj,
                commission_amount=commission_amount_obj,
                calculation_method="percentage",
                calculation_date=base_date + timedelta(days=i * 4)
            )
            
            # Create commission
            commission = self._fabrica.crear_commission(
                partner_id=partner_id,
                commission_amount=commission_amount_obj,
                commission_rate=commission_rate_obj,
                commission_type=commission_type_obj,
                transaction_reference=transaction_reference,
                calculation_period=calculation_period,
                status=status,
                calculation_details=calculation_details
            )
            
            # Set creation date
            commission._created_at = base_date + timedelta(days=i * 4)
            commission._updated_at = commission._created_at
            
            # Add approval and payment details for appropriate statuses
            if status in [CommissionStatus.APPROVED, CommissionStatus.PAID]:
                commission._approval_date = commission._created_at + timedelta(days=1)
                commission._approved_by = f"admin_{(i % 3) + 1}"
                commission._approval_notes = f"Approved commission #{i+1}"
            
            if status == CommissionStatus.PAID:
                commission._payment_date = commission._approval_date + timedelta(days=2)
                commission._payment_reference = f"pay_{uuid.uuid4().hex[:8]}"
            
            # Store commission
            self._commissions[commission.id] = commission