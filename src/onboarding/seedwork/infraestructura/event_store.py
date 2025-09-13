import json
from datetime import datetime
from typing import List, Dict, Any, Type
from sqlalchemy import Column, String, Integer, DateTime, Text, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

from onboarding.seedwork.dominio.entidades import DomainEvent, EventStore
from onboarding.seedwork.dominio.eventos import EventEnvelope


Base = declarative_base()


class EventRecord(Base):
    __tablename__ = 'event_store'
    
    id = Column(String, primary_key=True)
    aggregate_id = Column(String, nullable=False, index=True)
    event_type = Column(String, nullable=False)
    event_data = Column(Text, nullable=False)
    version = Column(Integer, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    correlation_id = Column(String, nullable=True)
    
    __table_args__ = (
        Index('ix_aggregate_version', 'aggregate_id', 'version'),
        Index('ix_event_type', 'event_type'),
        Index('ix_timestamp', 'timestamp'),
    )


class SqlAlchemyEventStore(EventStore):
    def __init__(self, session: Session, event_registry: Dict[str, Type[DomainEvent]]):
        self.session = session
        self.event_registry = event_registry
    
    async def save_events(self, aggregate_id: str, events: List[DomainEvent], expected_version: int):
        """Save events to the event store"""
        try:
            for i, event in enumerate(events):
                event_record = EventRecord(
                    id=event.id,
                    aggregate_id=aggregate_id,
                    event_type=event.__class__.__name__,
                    event_data=json.dumps(event.to_dict()),
                    version=expected_version + i + 1,
                    timestamp=event.timestamp,
                    correlation_id=getattr(event, 'correlation_id', None)
                )
                self.session.add(event_record)
            
            self.session.commit()
            
        except Exception as e:
            self.session.rollback()
            raise Exception(f"Failed to save events: {str(e)}")
    
    async def get_events(self, aggregate_id: str, from_version: int = 0) -> List[DomainEvent]:
        """Retrieve events for an aggregate from the event store"""
        try:
            records = self.session.query(EventRecord).filter(
                EventRecord.aggregate_id == aggregate_id,
                EventRecord.version > from_version
            ).order_by(EventRecord.version).all()
            
            events = []
            for record in records:
                event_class = self.event_registry.get(record.event_type)
                if event_class:
                    event_data = json.loads(record.event_data)
                    # Remove the base event fields to avoid duplication
                    event_data.pop('id', None)
                    event_data.pop('timestamp', None)
                    event_data.pop('event_type', None)
                    
                    # Create event instance
                    event = event_class(**event_data)
                    event.id = record.id
                    event.timestamp = record.timestamp
                    events.append(event)
            
            return events
            
        except Exception as e:
            raise Exception(f"Failed to retrieve events: {str(e)}")
    
    async def get_all_events(
        self, 
        from_timestamp: datetime = None, 
        to_timestamp: datetime = None,
        event_types: List[str] = None
    ) -> List[EventEnvelope]:
        """Get all events with optional filtering"""
        try:
            query = self.session.query(EventRecord)
            
            if from_timestamp:
                query = query.filter(EventRecord.timestamp >= from_timestamp)
            
            if to_timestamp:
                query = query.filter(EventRecord.timestamp <= to_timestamp)
            
            if event_types:
                query = query.filter(EventRecord.event_type.in_(event_types))
            
            records = query.order_by(EventRecord.timestamp).all()
            
            envelopes = []
            for record in records:
                envelope = EventEnvelope(
                    event_id=record.id,
                    aggregate_id=record.aggregate_id,
                    event_type=record.event_type,
                    event_data=json.loads(record.event_data),
                    version=record.version,
                    timestamp=record.timestamp,
                    correlation_id=record.correlation_id
                )
                envelopes.append(envelope)
            
            return envelopes
            
        except Exception as e:
            raise Exception(f"Failed to retrieve all events: {str(e)}")
    
    async def get_aggregate_version(self, aggregate_id: str) -> int:
        """Get the current version of an aggregate"""
        try:
            result = self.session.query(EventRecord.version).filter(
                EventRecord.aggregate_id == aggregate_id
            ).order_by(EventRecord.version.desc()).first()
            
            return result.version if result else 0
            
        except Exception as e:
            raise Exception(f"Failed to get aggregate version: {str(e)}")
    
    def create_snapshot(self, aggregate_id: str, version: int, data: Dict[str, Any]):
        """Create a snapshot of an aggregate state"""
        # TODO: Implement snapshot functionality for performance optimization
        pass
    
    def get_snapshot(self, aggregate_id: str) -> Dict[str, Any]:
        """Retrieve the latest snapshot for an aggregate"""
        # TODO: Implement snapshot retrieval
        return None


class EventPublisher:
    """Publishes events to external systems (Pulsar, etc.)"""
    
    def __init__(self, event_bus=None):
        self.event_bus = event_bus
        self.failed_events = []
    
    async def publish_events(self, events: List[EventEnvelope]):
        """Publish events to external message broker"""
        for event in events:
            try:
                if self.event_bus:
                    await self.event_bus.publish(
                        topic=f"onboarding.{event.event_type.lower()}",
                        message=event.to_cloud_event()
                    )
            except Exception as e:
                # Store failed events for retry
                self.failed_events.append({
                    'event': event,
                    'error': str(e),
                    'timestamp': datetime.utcnow()
                })
                print(f"Failed to publish event {event.event_id}: {str(e)}")
    
    async def retry_failed_events(self):
        """Retry publishing failed events"""
        retry_events = self.failed_events.copy()
        self.failed_events.clear()
        
        for failed_event in retry_events:
            try:
                if self.event_bus:
                    await self.event_bus.publish(
                        topic=f"onboarding.{failed_event['event'].event_type.lower()}",
                        message=failed_event['event'].to_cloud_event()
                    )
            except Exception as e:
                # Add back to failed events if retry fails
                self.failed_events.append(failed_event)


# Event Registry for deserialization
def create_event_registry():
    """Create a registry of all domain events for deserialization"""
    from onboarding.seedwork.dominio.eventos import (
        ContractCreated,
        ContractTermsUpdated,
        ContractSubmittedForLegalReview,
        ContractSigned,
        ContractActivated,
        NegotiationStarted,
        ProposalSubmitted,
        ProposalAccepted,
        NegotiationCompleted,
        LegalValidationRequested,
        LegalValidationCompleted,
        DocumentUploaded,
        DocumentSigned
    )
    
    return {
        'ContractCreated': ContractCreated,
        'ContractTermsUpdated': ContractTermsUpdated,
        'ContractSubmittedForLegalReview': ContractSubmittedForLegalReview,
        'ContractSigned': ContractSigned,
        'ContractActivated': ContractActivated,
        'NegotiationStarted': NegotiationStarted,
        'ProposalSubmitted': ProposalSubmitted,
        'ProposalAccepted': ProposalAccepted,
        'NegotiationCompleted': NegotiationCompleted,
        'LegalValidationRequested': LegalValidationRequested,
        'LegalValidationCompleted': LegalValidationCompleted,
        'DocumentUploaded': DocumentUploaded,
        'DocumentSigned': DocumentSigned,
    }