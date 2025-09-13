import pytest
import asyncio
import json
import time
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from uuid import uuid4

from partner_management.seedwork.dominio.eventos_integracion import (
    ContractSignedIntegrationEvent,
    ContractActivatedIntegrationEvent,
    CandidateMatchedIntegrationEvent,
    CandidateHiredIntegrationEvent,
    CampaignPerformanceReportIntegrationEvent,
    BudgetAlertIntegrationEvent
)
from partner_management.seedwork.aplicacion.handlers_integracion import (
    IntegrationEventHandler,
    IntegrationEventDispatcher
)


class TestEventIntegration:
    """Tests for integration event handling across services"""
    
    @pytest.fixture
    def mock_partner_repository(self):
        """Mock partner repository for testing"""
        repository = Mock()
        
        # Mock partner with required methods
        mock_partner = Mock()
        mock_partner.id = str(uuid4())
        mock_partner.tier = "GOLD"
        
        # Mock methods that handlers call
        mock_partner.actualizar_estado_contrato = Mock()
        mock_partner.agregar_metadatos = Mock()
        mock_partner.actualizar_permisos = Mock()
        mock_partner.habilitar_funcionalidad = Mock()
        mock_partner.actualizar_metricas_reclutamiento = Mock()
        mock_partner.agregar_comision = Mock()
        mock_partner.actualizar_metricas_campanas = Mock()
        mock_partner.agregar_alerta = Mock()
        
        repository.get_by_id.return_value = mock_partner
        repository.save = Mock()
        
        return repository, mock_partner
    
    @pytest.fixture
    def mock_uow(self):
        """Mock unit of work for testing"""
        uow = Mock()
        uow.__enter__ = Mock(return_value=uow)
        uow.__exit__ = Mock(return_value=None)
        uow.commit = Mock()
        return uow
    
    @pytest.fixture
    def mock_notification_service(self):
        """Mock notification service for testing"""
        service = Mock()
        service.send_notification = Mock()
        return service
    
    @pytest.fixture
    def integration_handler(self, mock_partner_repository, mock_uow, mock_notification_service):
        """Integration event handler with mocked dependencies"""
        repository, partner = mock_partner_repository
        return IntegrationEventHandler(
            partner_repository=repository,
            uow=mock_uow,
            notification_service=mock_notification_service
        ), partner
    
    @pytest.fixture
    def event_dispatcher(self, integration_handler):
        """Integration event dispatcher"""
        handler, partner = integration_handler
        return IntegrationEventDispatcher(handler), partner
    
    @pytest.mark.asyncio
    async def test_contract_signed_event_handling(self, integration_handler):
        """Test handling of contract signed events from Onboarding service"""
        handler, mock_partner = integration_handler
        
        # Create test event
        event = ContractSignedIntegrationEvent(
            event_id=str(uuid4()),
            occurred_on=datetime.utcnow(),
            contract_id=str(uuid4()),
            partner_id=mock_partner.id,
            contract_type="STANDARD",
            effective_date=datetime.utcnow()
        )
        
        # Handle the event
        await handler.handle_contract_signed(event)
        
        # Verify partner was updated
        mock_partner.actualizar_estado_contrato.assert_called_once_with("SIGNED")
        mock_partner.agregar_metadatos.assert_called_once()
        
        # Verify metadata contains contract information
        call_args = mock_partner.agregar_metadatos.call_args[0][0]
        assert call_args["contract_id"] == event.contract_id
        assert call_args["contract_type"] == event.contract_type
    
    @pytest.mark.asyncio
    async def test_contract_activated_event_handling(self, integration_handler):
        """Test handling of contract activated events"""
        handler, mock_partner = integration_handler
        
        # Create test event with permissions
        permissions = {
            "can_create_campaigns": True,
            "max_campaign_budget": 50000.0,
            "can_post_jobs": True
        }
        
        event = ContractActivatedIntegrationEvent(
            event_id=str(uuid4()),
            occurred_on=datetime.utcnow(),
            contract_id=str(uuid4()),
            partner_id=mock_partner.id,
            contract_type="PREMIUM",
            permissions=permissions
        )
        
        # Handle the event
        await handler.handle_contract_activated(event)
        
        # Verify partner status and permissions updated
        mock_partner.actualizar_estado_contrato.assert_called_once_with("ACTIVE")
        mock_partner.actualizar_permisos.assert_called_once_with(permissions)
        mock_partner.habilitar_funcionalidad.assert_called_once_with("CAMPAIGNS")
    
    @pytest.mark.asyncio
    async def test_candidate_matched_event_handling(self, integration_handler):
        """Test handling of candidate matched events from Recruitment service"""
        handler, mock_partner = integration_handler
        
        event = CandidateMatchedIntegrationEvent(
            event_id=str(uuid4()),
            occurred_on=datetime.utcnow(),
            job_id=str(uuid4()),
            candidate_id=str(uuid4()),
            partner_id=mock_partner.id,
            match_score=85.5,
            candidate_profile={
                "name": "John Doe",
                "skills": ["Python", "Flask", "PostgreSQL"],
                "experience": 5
            }
        )
        
        # Handle the event
        await handler.handle_candidate_matched(event)
        
        # Verify recruitment metrics updated
        mock_partner.actualizar_metricas_reclutamiento.assert_called_once()
        call_args = mock_partner.actualizar_metricas_reclutamiento.call_args[0][0]
        assert call_args["candidates_matched"] == 1
        assert call_args["last_match_score"] == 85.5
    
    @pytest.mark.asyncio
    async def test_candidate_hired_event_handling(self, integration_handler):
        """Test handling of candidate hired events with commission calculation"""
        handler, mock_partner = integration_handler
        
        event = CandidateHiredIntegrationEvent(
            event_id=str(uuid4()),
            occurred_on=datetime.utcnow(),
            job_id=str(uuid4()),
            candidate_id=str(uuid4()),
            partner_id=mock_partner.id,
            position="Senior Software Engineer",
            start_date=datetime.utcnow() + timedelta(days=30),
            salary=100000.0
        )
        
        # Handle the event
        await handler.handle_candidate_hired(event)
        
        # Verify metrics and commission updated
        mock_partner.actualizar_metricas_reclutamiento.assert_called_once()
        mock_partner.agregar_comision.assert_called_once()
        
        # Verify commission calculation (15% base rate * 1.2 GOLD multiplier = 18%)
        commission_call = mock_partner.agregar_comision.call_args[0][0]
        expected_commission = 100000.0 * 0.15 * 1.2  # 18000.0
        assert commission_call["amount"] == expected_commission
        assert commission_call["type"] == "hiring"
    
    @pytest.mark.asyncio
    async def test_campaign_performance_report_handling(self, integration_handler):
        """Test handling of campaign performance reports"""
        handler, mock_partner = integration_handler
        
        performance_data = {
            "impressions": 50000,
            "clicks": 1250,
            "conversions": 75,
            "cost": 2500.0,
            "ctr": 2.5,
            "conversion_rate": 6.0
        }
        
        event = CampaignPerformanceReportIntegrationEvent(
            event_id=str(uuid4()),
            occurred_on=datetime.utcnow(),
            campaign_id=str(uuid4()),
            partner_id=mock_partner.id,
            performance_data=performance_data,
            period="weekly"
        )
        
        # Handle the event
        await handler.handle_campaign_performance_report(event)
        
        # Verify campaign metrics updated
        mock_partner.actualizar_metricas_campanas.assert_called_once()
        call_args = mock_partner.actualizar_metricas_campanas.call_args[0][0]
        assert call_args["impressions"] == 50000
        assert call_args["clicks"] == 1250
        assert call_args["conversions"] == 75
        assert call_args["period"] == "weekly"
    
    @pytest.mark.asyncio
    async def test_budget_alert_handling(self, integration_handler):
        """Test handling of budget alerts from Campaign Management"""
        handler, mock_partner = integration_handler
        
        event = BudgetAlertIntegrationEvent(
            event_id=str(uuid4()),
            occurred_on=datetime.utcnow(),
            campaign_id=str(uuid4()),
            partner_id=mock_partner.id,
            alert_type="threshold_reached",
            current_spend=8500.0,
            budget_limit=10000.0,
            threshold_percentage=85.0
        )
        
        # Handle the event
        await handler.handle_budget_alert(event)
        
        # Verify alert was added to partner
        mock_partner.agregar_alerta.assert_called_once()
        call_args = mock_partner.agregar_alerta.call_args[0][0]
        assert call_args["type"] == "budget_alert"
        assert call_args["alert_type"] == "threshold_reached"
        assert call_args["current_spend"] == 8500.0
    
    @pytest.mark.asyncio
    async def test_event_dispatcher_routing(self, event_dispatcher):
        """Test that event dispatcher routes events to correct handlers"""
        dispatcher, mock_partner = event_dispatcher
        
        # Test contract signed event dispatch
        event_data = {
            "event_id": str(uuid4()),
            "occurred_on": datetime.utcnow().isoformat(),
            "contract_id": str(uuid4()),
            "partner_id": mock_partner.id,
            "contract_type": "STANDARD",
            "effective_date": datetime.utcnow().isoformat()
        }
        
        await dispatcher.dispatch("ContractSigned", event_data)
        
        # Verify the correct handler method was called
        mock_partner.actualizar_estado_contrato.assert_called_once_with("SIGNED")
    
    @pytest.mark.asyncio
    async def test_event_dispatcher_unknown_event_type(self, event_dispatcher):
        """Test dispatcher handles unknown event types gracefully"""
        dispatcher, mock_partner = event_dispatcher
        
        # This should not raise an exception
        await dispatcher.dispatch("UnknownEventType", {"some": "data"})
        
        # No handler methods should have been called
        mock_partner.actualizar_estado_contrato.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_notification_service_integration(self, integration_handler, mock_notification_service):
        """Test that notifications are sent for appropriate events"""
        handler, mock_partner = integration_handler
        
        # Test contract signed notification
        event = ContractSignedIntegrationEvent(
            event_id=str(uuid4()),
            occurred_on=datetime.utcnow(),
            contract_id=str(uuid4()),
            partner_id=mock_partner.id,
            contract_type="STANDARD",
            effective_date=datetime.utcnow()
        )
        
        await handler.handle_contract_signed(event)
        
        # Verify notification was sent
        mock_notification_service.send_notification.assert_called_once()
        call_args = mock_notification_service.send_notification.call_args[1]
        assert call_args["partner_id"] == mock_partner.id
        assert call_args["type"] == "contract_signed"
    
    @pytest.mark.asyncio
    async def test_budget_alert_urgent_notification(self, integration_handler, mock_notification_service):
        """Test that urgent notifications are sent for budget exhaustion"""
        handler, mock_partner = integration_handler
        
        # Test budget exhausted alert (should be high urgency)
        event = BudgetAlertIntegrationEvent(
            event_id=str(uuid4()),
            occurred_on=datetime.utcnow(),
            campaign_id=str(uuid4()),
            partner_id=mock_partner.id,
            alert_type="exhausted",
            current_spend=10000.0,
            budget_limit=10000.0,
            threshold_percentage=100.0
        )
        
        await handler.handle_budget_alert(event)
        
        # Verify high urgency notification was sent
        mock_notification_service.send_notification.assert_called_once()
        call_args = mock_notification_service.send_notification.call_args[1]
        assert call_args["urgency"] == "high"
        assert call_args["type"] == "budget_alert"
    
    @pytest.mark.asyncio
    async def test_commission_calculation_by_tier(self, mock_partner_repository, mock_uow, mock_notification_service):
        """Test commission calculation varies by partner tier"""
        repository, mock_partner = mock_partner_repository
        
        test_cases = [
            ("BRONZE", 1.0, 15000.0),  # Base rate
            ("SILVER", 1.1, 16500.0),  # 10% bonus
            ("GOLD", 1.2, 18000.0),    # 20% bonus
            ("PLATINUM", 1.3, 19500.0) # 30% bonus
        ]
        
        for tier, multiplier, expected_commission in test_cases:
            # Reset mock for each test
            mock_partner.reset_mock()
            mock_partner.tier = tier
            
            handler = IntegrationEventHandler(
                partner_repository=repository,
                uow=mock_uow,
                notification_service=mock_notification_service
            )
            
            event = CandidateHiredIntegrationEvent(
                event_id=str(uuid4()),
                occurred_on=datetime.utcnow(),
                job_id=str(uuid4()),
                candidate_id=str(uuid4()),
                partner_id=mock_partner.id,
                position="Test Position",
                start_date=datetime.utcnow(),
                salary=100000.0
            )
            
            await handler.handle_candidate_hired(event)
            
            # Verify commission calculation
            commission_call = mock_partner.agregar_comision.call_args[0][0]
            assert commission_call["amount"] == expected_commission
    
    @pytest.mark.asyncio
    async def test_error_handling_in_event_processing(self, integration_handler):
        """Test error handling when event processing fails"""
        handler, mock_partner = integration_handler
        
        # Make the partner repository raise an exception
        handler.partner_repository.get_by_id.side_effect = Exception("Database error")
        
        event = ContractSignedIntegrationEvent(
            event_id=str(uuid4()),
            occurred_on=datetime.utcnow(),
            contract_id=str(uuid4()),
            partner_id=str(uuid4()),
            contract_type="STANDARD",
            effective_date=datetime.utcnow()
        )
        
        # Should raise the exception
        with pytest.raises(Exception, match="Database error"):
            await handler.handle_contract_signed(event)
    
    @pytest.mark.asyncio
    async def test_concurrent_event_processing(self, integration_handler):
        """Test that multiple events can be processed concurrently"""
        handler, mock_partner = integration_handler
        
        # Create multiple events
        events = []
        for i in range(5):
            event = ContractSignedIntegrationEvent(
                event_id=str(uuid4()),
                occurred_on=datetime.utcnow(),
                contract_id=str(uuid4()),
                partner_id=mock_partner.id,
                contract_type=f"TYPE_{i}",
                effective_date=datetime.utcnow()
            )
            events.append(handler.handle_contract_signed(event))
        
        # Process all events concurrently
        await asyncio.gather(*events)
        
        # Verify all events were processed
        assert mock_partner.actualizar_estado_contrato.call_count == 5
        assert mock_partner.agregar_metadatos.call_count == 5