# Scripts de HexaBuilders para GCP

Esta carpeta contiene scripts para facilitar el despliegue y control de costos en Google Cloud Platform.

## 📋 Scripts Disponibles

### 🏗️ Scripts de Despliegue Original
- **`create-gke-cluster.sh`** - Crear cluster de Kubernetes
- **`build-and-push-images.sh`** - Construir y subir imágenes Docker 
- **`deploy-to-gke.sh`** - Desplegar aplicación completa
- **`cleanup-gke.sh`** - Limpiar todos los recursos

### 💰 Nuevo: Control de Costos
- **`gcp-cost-control.sh`** - ⭐ **RECOMENDADO** - Control inteligente de costos

## 🚀 Uso Rápido del Control de Costos

```bash
# Una sola vez: dar permisos
chmod +x scripts/gcp-cost-control.sh

# Comandos diarios
./scripts/gcp-cost-control.sh shutdown    # 🛑 Apagar (fin de día)
./scripts/gcp-cost-control.sh startup     # ✅ Encender (inicio de día)
./scripts/gcp-cost-control.sh status      # 📊 Ver estado actual
./scripts/gcp-cost-control.sh costs       # 💰 Ver desglose de costos
```

## 💰 Ahorro de Costos

| Estado | Costo/mes | Cuándo usar |
|--------|-----------|-------------|
| 🟢 **Encendido** | ~$46 | Trabajando activamente |
| 🟡 **Solo cluster off** | ~$21 | Pausa corta (almuerzo) |
| 🔴 **Todo off** | ~$3 | Fin de semana/vacaciones |

## 📚 Guías Completas

- **Para consola web**: `../GUIA_DESPLIEGUE_GCP_CONSOLA.md`
- **Para línea de comandos**: `../README-K8S-GCP.md`

## ⚡ Comandos de Emergencia

```bash
# Si algo se rompe - reiniciar todo
./scripts/gcp-cost-control.sh shutdown
sleep 60
./scripts/gcp-cost-control.sh startup

# Si quieres eliminar TODO (cuidado!)
./scripts/gcp-cost-control.sh destroy
```
