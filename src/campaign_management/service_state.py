"""
Control de estado del servicio Campaign Management.
Permite habilitar/deshabilitar el servicio para pruebas de compensación.
"""

import os
import json

# Archivo para persistir el estado del servicio
STATE_FILE = "/tmp/campaign_service_state.json"

def get_service_state() -> bool:
    """Obtiene el estado actual del servicio"""
    try:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, 'r') as f:
                data = json.load(f)
                return data.get('enabled', True)
        return True  # Por defecto habilitado
    except Exception:
        return True  # En caso de error, asumir habilitado

def set_service_state(enabled: bool) -> None:
    """Establece el estado del servicio"""
    try:
        data = {'enabled': enabled}
        with open(STATE_FILE, 'w') as f:
            json.dump(data, f)
    except Exception:
        pass  # Ignorar errores de escritura

def is_service_enabled() -> bool:
    """Verifica si el servicio está habilitado"""
    return get_service_state()
