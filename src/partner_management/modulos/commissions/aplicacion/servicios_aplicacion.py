"""
Application services for Commission module in HexaBuilders.
Implements CQRS pattern with command and query separation.
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal

from ....seedwork.aplicacion.servicios import ServicioAplicacion
from ....seedwork.infraestructura.uow import UnitOfWork
from ....seedwork.dominio.excepciones import DomainException

from .comandos.crear_commission import CrearCommission, handle_crear_commission
from .comandos.actualizar_commission import ActualizarCommission, handle_actualizar_commission
from .comandos.aprobar_commission import AprobarCommission, handle_aprobar_commission
from .comandos.cancelar_commission import CancelarCommission, handle_cancelar_commission
from .comandos.procesar_pago_commission import ProcesarPagoCommission, handle_procesar_pago_commission

from .queries.obtener_commission import ObtenerCommission, handle_obtener_commission
from .queries.obtener_todos_commissions import ObtenerTodosCommissions, handle_obtener_todos_commissions
from .queries.obtener_comisiones_partner import ObtenerComisionesPartner, handle_obtener_comisiones_partner

logger = logging.getLogger(__name__)


class ServicioCommission(ServicioAplicacion):
    """
    Application service for Commission operations.
    Coordinates CQRS operations and business workflows.
    """
    
    def __init__(self):
        super().__init__()
        self._logger = logging.getLogger(self.__class__.__name__)
    
    # Command operations
    
    def crear_commission(
        self,
        partner_id: str,
        commission_amount: Decimal,
        commission_rate: Decimal,
        commission_type: str,
        transaction_id: str,
        transaction_type: str,
        transaction_amount: Decimal,
        transaction_date: datetime,
        calculation_period_start: datetime,
        calculation_period_end: datetime,
        period_name: str,
        currency: str = "USD",
        calculation_method: str = "percentage"
    ) -> str:
        """
        Create a new commission.
        """
        self._logger.info(f"Creating commission for partner: {partner_id}")
        
        comando = CrearCommission(
            partner_id=partner_id,
            commission_amount=commission_amount,
            commission_rate=commission_rate,
            commission_type=commission_type,
            transaction_id=transaction_id,
            transaction_type=transaction_type,
            transaction_amount=transaction_amount,
            transaction_date=transaction_date,
            calculation_period_start=calculation_period_start,
            calculation_period_end=calculation_period_end,
            period_name=period_name,
            currency=currency,
            calculation_method=calculation_method
        )
        
        return handle_crear_commission(comando)
    
    def actualizar_commission(
        self,
        commission_id: str,
        nuevo_monto: Optional[Decimal] = None,
        nueva_rate: Optional[Decimal] = None,
        adjustment_reason: Optional[str] = None,
        adjusted_by: str = "system",
        currency: str = "USD"
    ) -> str:
        """
        Update a commission.
        """
        self._logger.info(f"Updating commission: {commission_id}")
        
        comando = ActualizarCommission(
            commission_id=commission_id,
            nuevo_monto=nuevo_monto,
            nueva_rate=nueva_rate,
            adjustment_reason=adjustment_reason,
            adjusted_by=adjusted_by,
            currency=currency
        )
        
        return handle_actualizar_commission(comando)
    
    def aprobar_commission(
        self,
        commission_id: str,
        approved_by: str,
        approval_notes: Optional[str] = None
    ) -> str:
        """
        Approve a commission for payment.
        """
        self._logger.info(f"Approving commission: {commission_id}")
        
        comando = AprobarCommission(
            commission_id=commission_id,
            approved_by=approved_by,
            approval_notes=approval_notes
        )
        
        return handle_aprobar_commission(comando)
    
    def cancelar_commission(
        self,
        commission_id: str,
        cancellation_reason: str,
        cancelled_by: str
    ) -> str:
        """
        Cancel a commission.
        """
        self._logger.info(f"Cancelling commission: {commission_id}")
        
        comando = CancelarCommission(
            commission_id=commission_id,
            cancellation_reason=cancellation_reason,
            cancelled_by=cancelled_by
        )
        
        return handle_cancelar_commission(comando)
    
    def procesar_pago_commission(
        self,
        commission_id: str,
        payment_method: str,
        payment_reference: str,
        payment_fee: Decimal = Decimal('0.00'),
        bank_details: Optional[str] = None
    ) -> str:
        """
        Process payment for a commission.
        """
        self._logger.info(f"Processing payment for commission: {commission_id}")
        
        comando = ProcesarPagoCommission(
            commission_id=commission_id,
            payment_method=payment_method,
            payment_reference=payment_reference,
            payment_fee=payment_fee,
            bank_details=bank_details
        )
        
        return handle_procesar_pago_commission(comando)
    
    # Query operations
    
    def obtener_commission(self, commission_id: str) -> Dict[str, Any]:
        """
        Get commission by ID.
        """
        self._logger.info(f"Getting commission: {commission_id}")
        
        query = ObtenerCommission(commission_id=commission_id)
        result = handle_obtener_commission(query)
        
        return result.commission_data
    
    def obtener_todos_commissions(
        self,
        partner_id: Optional[str] = None,
        status: Optional[str] = None,
        commission_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Get all commissions with optional filtering.
        """
        self._logger.info(f"Getting commissions with filters - partner_id: {partner_id}, status: {status}")
        
        query = ObtenerTodosCommissions(
            partner_id=partner_id,
            status=status,
            commission_type=commission_type,
            limit=limit,
            offset=offset
        )
        result = handle_obtener_todos_commissions(query)
        
        return {
            'commissions': result.commissions,
            'total_count': result.total_count,
            'count': result.count
        }
    
    def obtener_comisiones_partner(
        self,
        partner_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        status: Optional[str] = None,
        include_analytics: bool = True
    ) -> Dict[str, Any]:
        """
        Get commissions for a specific partner with analytics.
        """
        self._logger.info(f"Getting commissions for partner: {partner_id}")
        
        query = ObtenerComisionesPartner(
            partner_id=partner_id,
            start_date=start_date,
            end_date=end_date,
            status=status,
            include_analytics=include_analytics
        )
        result = handle_obtener_comisiones_partner(query)
        
        return {
            'partner_id': result.partner_id,
            'commissions': result.commissions,
            'count': result.count,
            'analytics': result.analytics
        }
    
    # Business workflows
    
    def procesar_comision_automatica(
        self,
        partner_id: str,
        transaction_data: Dict[str, Any],
        commission_rules: Dict[str, Any]
    ) -> str:
        """
        Process automatic commission based on transaction data and rules.
        """
        self._logger.info(f"Processing automatic commission for partner: {partner_id}")
        
        try:
            # Calculate commission based on rules
            commission_amount = self._calculate_automatic_commission(
                transaction_data, commission_rules
            )
            
            # Create commission
            return self.crear_commission(
                partner_id=partner_id,
                commission_amount=commission_amount,
                commission_rate=Decimal(str(commission_rules.get('rate', 0.05))),
                commission_type=commission_rules.get('type', 'SALE_COMMISSION'),
                transaction_id=transaction_data['transaction_id'],
                transaction_type=transaction_data['transaction_type'],
                transaction_amount=Decimal(str(transaction_data['amount'])),
                transaction_date=transaction_data['transaction_date'],
                calculation_period_start=datetime.now().replace(day=1),  # Start of month
                calculation_period_end=datetime.now(),
                period_name=f"Auto Commission - {datetime.now().strftime('%Y-%m')}"
            )
            
        except Exception as e:
            self._logger.error(f"Failed to process automatic commission: {str(e)}")
            raise DomainException(f"Automatic commission processing failed: {str(e)}")
    
    def aprobar_comisiones_batch(
        self,
        commission_ids: List[str],
        approved_by: str,
        approval_notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Approve multiple commissions in batch.
        """
        self._logger.info(f"Batch approving {len(commission_ids)} commissions")
        
        approved = []
        failed = []
        
        for commission_id in commission_ids:
            try:
                self.aprobar_commission(commission_id, approved_by, approval_notes)
                approved.append(commission_id)
            except Exception as e:
                failed.append({
                    'commission_id': commission_id,
                    'error': str(e)
                })
                self._logger.error(f"Failed to approve commission {commission_id}: {str(e)}")
        
        return {
            'approved': approved,
            'failed': failed,
            'success_count': len(approved),
            'failure_count': len(failed)
        }
    
    def generar_reporte_comisiones(
        self,
        start_date: datetime,
        end_date: datetime,
        partner_id: Optional[str] = None,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate commission report for specified period.
        """
        self._logger.info(f"Generating commission report from {start_date} to {end_date}")
        
        # Get commissions data
        commissions_data = self.obtener_todos_commissions(
            partner_id=partner_id,
            status=status,
            limit=10000  # Large limit for report
        )
        
        # Filter by date range (this would be better done at repository level)
        filtered_commissions = []
        for commission in commissions_data['commissions']:
            commission_date = datetime.fromisoformat(commission['timestamps']['created_at'])
            if start_date <= commission_date <= end_date:
                filtered_commissions.append(commission)
        
        # Calculate report metrics
        total_amount = sum(Decimal(c['commission_amount']) for c in filtered_commissions)
        status_breakdown = {}
        type_breakdown = {}
        
        for commission in filtered_commissions:
            status = commission['status']
            comm_type = commission['commission_type']
            
            status_breakdown[status] = status_breakdown.get(status, 0) + 1
            type_breakdown[comm_type] = type_breakdown.get(comm_type, 0) + 1
        
        return {
            'report_period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'total_commissions': len(filtered_commissions),
            'total_amount': str(total_amount),
            'status_breakdown': status_breakdown,
            'type_breakdown': type_breakdown,
            'commissions': filtered_commissions
        }
    
    def _calculate_automatic_commission(
        self,
        transaction_data: Dict[str, Any],
        commission_rules: Dict[str, Any]
    ) -> Decimal:
        """
        Calculate commission amount based on transaction and rules.
        """
        transaction_amount = Decimal(str(transaction_data['amount']))
        commission_rate = Decimal(str(commission_rules.get('rate', 0.05)))
        
        # Apply any business rules for calculation
        min_commission = Decimal(str(commission_rules.get('min_amount', 1.0)))
        max_commission = Decimal(str(commission_rules.get('max_amount', 10000.0)))
        
        calculated_commission = transaction_amount * commission_rate
        
        # Apply bounds
        if calculated_commission < min_commission:
            calculated_commission = min_commission
        elif calculated_commission > max_commission:
            calculated_commission = max_commission
        
        return calculated_commission