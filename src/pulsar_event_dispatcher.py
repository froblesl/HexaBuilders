import json
import logging
import os
import time
import threading
import uuid
from typing import Dict, Any, List, Callable
from pulsar import Client, Consumer, Producer, Message
import traceback

class PulsarEventDispatcher:
    """Event dispatcher using Apache Pulsar for real distributed communication"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.logger = logging.getLogger(self.__class__.__name__)
        self._handlers: Dict[str, List[Callable]] = {}
        self._running = False
        
        # Pulsar configuration
        self.pulsar_url = os.getenv('PULSAR_BROKER_URL', 'pulsar://localhost:6650')
        self.admin_url = os.getenv('PULSAR_ADMIN_URL', 'http://localhost:8080')
        
        # Initialize Pulsar client
        self.client = None
        self.producer = None
        self.consumer = None
        self._init_pulsar()
        
        # Start event processing
        self._start_event_loop()
    
    def _init_pulsar(self):
        """Initialize Pulsar client and create producer/consumer"""
        try:
            self.client = Client(self.pulsar_url)
            self.logger.info(f"Pulsar client initialized for service {self.service_name}")
            
            # Create producer for publishing events
            self.producer = self.client.create_producer(
                topic=f"persistent://public/default/saga-events",
                producer_name=f"{self.service_name}-producer-{str(uuid.uuid4())[:8]}"
            )
            
            # Create consumer for subscribing to events
            self.consumer = self.client.subscribe(
                topic=f"persistent://public/default/saga-events",
                subscription_name=f"{self.service_name}-subscription-{str(uuid.uuid4())[:8]}"
            )
            
            self.logger.info(f"Pulsar producer and consumer created for service {self.service_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Pulsar: {str(e)}")
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            raise
    
    def _start_event_loop(self):
        """Start the event processing loop in a separate thread"""
        if self._running:
            return
        self._running = True
        thread = threading.Thread(target=self._event_loop_worker, daemon=True)
        thread.start()
        self.logger.info(f"Event loop started for service {self.service_name}")
    
    def _event_loop_worker(self):
        """Worker thread that processes incoming Pulsar messages"""
        while self._running:
            try:
                # Wait for messages with timeout
                msg = self.consumer.receive(timeout_millis=1000)
                if msg:
                    self._process_message(msg)
                    self.consumer.acknowledge(msg)
            except Exception as e:
                if "timeout" not in str(e).lower():
                    self.logger.error(f"Error in event loop: {str(e)}")
                time.sleep(0.1)  # Small delay to prevent busy waiting
    
    def _process_message(self, message: Message):
        """Process a received Pulsar message"""
        try:
            # Parse message data
            event_data = json.loads(message.data().decode('utf-8'))
            event_type = event_data.get('event_type')
            event_payload = event_data.get('event_data', {})
            source = event_data.get('source', 'unknown')
            
            # Skip messages from our own service to avoid loops
            if source == self.service_name:
                return
            
            self.logger.info(f"Service {self.service_name} received event: {event_type} from {source}")
            
            # Process event if we have handlers
            if event_type in self._handlers:
                for handler in self._handlers[event_type]:
                    try:
                        self.logger.info(f"Service {self.service_name} processing event: {event_type} with handler {handler.__name__}")
                        handler(event_payload)
                    except Exception as e:
                        self.logger.error(f"Error in event handler {handler.__name__}: {str(e)}")
                        self.logger.error(f"Traceback: {traceback.format_exc()}")
            
        except Exception as e:
            self.logger.error(f"Error processing message: {str(e)}")
            self.logger.error(f"Traceback: {traceback.format_exc()}")
    
    def subscribe(self, event_type: str, handler: Callable):
        """Subscribe to a specific event type"""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
        self.logger.info(f"Service {self.service_name} subscribed to {event_type}")
    
    def publish(self, event_type: str, event_data: Dict[str, Any]):
        """Publish an event to Pulsar"""
        try:
            self.logger.info(f"Service {self.service_name} publishing event: {event_type} for partner {event_data.get('partner_id', 'unknown')}")
            
            # Create event message
            event_message = {
                "event_type": event_type,
                "event_data": event_data,
                "timestamp": time.time(),
                "source": self.service_name
            }
            
            # Send to Pulsar
            message_data = json.dumps(event_message).encode('utf-8')
            self.producer.send(message_data)
            
            self.logger.info(f"Event {event_type} published to Pulsar successfully")
            
        except Exception as e:
            self.logger.error(f"Error publishing event to Pulsar: {str(e)}")
            self.logger.error(f"Traceback: {traceback.format_exc()}")
    
    def close(self):
        """Close Pulsar connections"""
        self._running = False
        try:
            if self.consumer:
                self.consumer.close()
            if self.producer:
                self.producer.close()
            if self.client:
                self.client.close()
            self.logger.info(f"Pulsar connections closed for service {self.service_name}")
        except Exception as e:
            self.logger.error(f"Error closing Pulsar connections: {str(e)}")
