#!/bin/bash

# Script de configuración para pruebas de escenarios de calidad
# Ejecutar con: ./setup.sh

echo "🔧 Configurando entorno para pruebas de escenarios de calidad..."
echo "=============================================================="

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para verificar comando
check_command() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✅ $1 está instalado${NC}"
        return 0
    else
        echo -e "${RED}❌ $1 no está instalado${NC}"
        return 1
    fi
}

# Verificar prerequisitos
echo ""
echo "📋 Verificando prerequisitos..."
echo "-------------------------------"

# Python 3
if check_command python3; then
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    echo "  Versión: $PYTHON_VERSION"
else
    echo -e "${RED}Python 3 es requerido para ejecutar las pruebas${NC}"
    exit 1
fi

# pip
if check_command pip3; then
    echo -e "${GREEN}✅ pip3 está disponible${NC}"
else
    echo -e "${YELLOW}⚠️  pip3 no encontrado, intentando con pip...${NC}"
    if ! check_command pip; then
        echo -e "${RED}pip es requerido para instalar dependencias${NC}"
        exit 1
    fi
fi

# curl
if ! check_command curl; then
    echo -e "${RED}curl es requerido para las pruebas HTTP${NC}"
    exit 1
fi

# jq (opcional)
if check_command jq; then
    echo -e "${GREEN}✅ jq está disponible (opcional)${NC}"
else
    echo -e "${YELLOW}⚠️  jq no encontrado (opcional, para mejor formato de salida)${NC}"
fi

# Crear directorio de reportes
echo ""
echo "📁 Creando directorios..."
echo "-------------------------"
mkdir -p reports
mkdir -p logs
echo -e "${GREEN}✅ Directorios creados${NC}"

# Instalar dependencias de Python
echo ""
echo "📦 Instalando dependencias de Python..."
echo "---------------------------------------"
if [ -f "requirements.txt" ]; then
    if command -v pip3 &> /dev/null; then
        pip3 install -r requirements.txt
    else
        pip install -r requirements.txt
    fi
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Dependencias instaladas correctamente${NC}"
    else
        echo -e "${RED}❌ Error instalando dependencias${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠️  Archivo requirements.txt no encontrado${NC}"
fi

# Verificar servicios
echo ""
echo "🔍 Verificando servicios del sistema..."
echo "---------------------------------------"

# Función para verificar servicio
check_service() {
    local name=$1
    local url=$2
    
    echo -n "Verificando $name... "
    response=$(curl -s -o /dev/null -w "%{http_code}" "$url/health" 2>/dev/null)
    
    if [ "$response" = "200" ]; then
        echo -e "${GREEN}✅ OK${NC}"
        return 0
    else
        echo -e "${RED}❌ FAIL (HTTP $response)${NC}"
        return 1
    fi
}

# Verificar servicios
services_ok=0
check_service "Partner Management" "http://localhost:5000" && ((services_ok++))
check_service "BFF Web" "http://localhost:8000" && ((services_ok++))
check_service "Campaign Management" "http://localhost:5003" && ((services_ok++))
check_service "Onboarding" "http://localhost:5001" && ((services_ok++))
check_service "Recruitment" "http://localhost:5002" && ((services_ok++))
check_service "Notifications" "http://localhost:5004" && ((services_ok++))

echo ""
if [ $services_ok -eq 6 ]; then
    echo -e "${GREEN}✅ Todos los servicios están funcionando${NC}"
else
    echo -e "${YELLOW}⚠️  $services_ok/6 servicios están funcionando${NC}"
    echo -e "${YELLOW}   Algunas pruebas pueden fallar si los servicios no están disponibles${NC}"
fi

# Hacer scripts ejecutables
echo ""
echo "🔧 Configurando permisos..."
echo "---------------------------"
chmod +x run_all_tests.py
chmod +x load_tests/*.py
chmod +x availability_tests/*.py
chmod +x interoperability_tests/*.py
chmod +x recoverability_tests/*.py
chmod +x observability_tests/*.py
echo -e "${GREEN}✅ Permisos configurados${NC}"

# Mostrar resumen
echo ""
echo "📊 RESUMEN DE CONFIGURACIÓN"
echo "============================"
echo "✅ Python 3: $(python3 --version 2>&1 | cut -d' ' -f2)"
echo "✅ Servicios disponibles: $services_ok/6"
echo "✅ Directorios creados: reports/, logs/"
echo "✅ Dependencias instaladas"
echo "✅ Scripts configurados"

echo ""
echo "🚀 CONFIGURACIÓN COMPLETADA"
echo "==========================="
echo ""
echo "Para ejecutar las pruebas:"
echo "  python3 run_all_tests.py"
echo ""
echo "Para ejecutar pruebas específicas:"
echo "  python3 load_tests/scalability_test.py"
echo "  python3 availability_tests/service_failure_test.py"
echo ""
echo "Los reportes se guardarán en: reports/"
echo ""
