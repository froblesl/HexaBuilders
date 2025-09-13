# Módulos del Onboarding Service - HexaBuilders

## 📋 Contracts Module

### **Responsabilidad**
Gestión del ciclo de vida completo de contratos legales entre HexaBuilders y partners.

### **Entidades Principales**
- `Contract` (Aggregate Root): Contrato principal con términos y estados
- `ContractVersion`: Versiones del contrato para auditoría
- `ContractTemplate`: Plantillas predefinidas por tipo de partner

### **Estados del Contrato**
```
DRAFT → IN_NEGOTIATION → LEGAL_REVIEW → PENDING_SIGNATURE → SIGNED → ACTIVE
                     ↓                                              ↓
                 CANCELLED                                      EXPIRED/TERMINATED
```

### **Comandos Principales**
- `CreateContract`: Crear nuevo contrato
- `UpdateContractTerms`: Modificar términos
- `SubmitForLegalReview`: Enviar a revisión legal
- `SignContract`: Firmar digitalmente
- `ActivateContract`: Activar contrato firmado

---

## 🤝 Negotiations Module

### **Responsabilidad**
Gestión del proceso estructurado de negociación de términos contractuales.

### **Entidades Principales**
- `Negotiation` (Aggregate Root): Proceso de negociación
- `NegotiationRound`: Rondas individuales de negociación
- `Proposal`: Propuestas específicas de términos

### **Flujo de Negociación**
```
Proposal Inicial → Contrapropuesta → Revisión → Acuerdo/Rechazo
                        ↓
                   Nueva Ronda ←
```

### **Comandos Principales**
- `StartNegotiation`: Iniciar proceso
- `SubmitProposal`: Enviar propuesta
- `RespondToProposal`: Responder propuesta
- `AcceptTerms`: Aceptar términos finales

---

## ⚖️ Legal Module

### **Responsabilidad**
Validación legal y compliance de contratos y términos.

### **Entidades Principales**
- `LegalValidation` (Aggregate Root): Proceso de validación legal
- `ComplianceCheck`: Verificaciones de cumplimiento normativo
- `LegalOpinion`: Opiniones legales detalladas

### **Tipos de Validación**
- **Compliance Regulatorio**: Cumplimiento de leyes locales
- **Términos Contractuales**: Validez de cláusulas
- **Protección de Datos**: GDPR, CCPA compliance
- **Propiedad Intelectual**: Verificación de derechos

### **Comandos Principales**
- `RequestLegalValidation`: Solicitar validación
- `PerformComplianceCheck`: Ejecutar verificación
- `ProvideeLegalOpinion`: Emitir opinión legal
- `ApproveLegalTerms`: Aprobar términos

---

## 📋 Documents Module

### **Responsabilidad**
Gestión documental completa con firmas digitales y versionado.

### **Entidades Principales**
- `Document` (Aggregate Root): Documento principal
- `DocumentVersion`: Versiones para control de cambios
- `DigitalSignature`: Firmas electrónicas verificables

### **Tipos de Documentos**
- **Contract Documents**: Contratos principales
- **Addendums**: Anexos y modificaciones
- **Legal Evidence**: Evidencia legal
- **Supporting Documents**: Documentos de soporte

### **Comandos Principales**
- `UploadDocument`: Subir documento
- `CreateDocumentVersion`: Nueva versión
- `RequestDigitalSignature`: Solicitar firma
- `ValidateSignature`: Validar autenticidad

---

## 🔄 Interacciones Entre Módulos

### **Contracts ↔ Negotiations**
- Contracts inicia Negotiations para términos complejos
- Negotiations actualiza Contract con términos acordados

### **Contracts ↔ Legal**
- Contracts solicita validación a Legal antes de firma
- Legal aprueba/rechaza términos contractuales

### **Contracts ↔ Documents**
- Contracts genera Documents para firma
- Documents notifica a Contracts cuando está firmado

### **Legal ↔ Documents**
- Legal valida Documents antes de aprobación
- Documents proporciona evidencia legal a Legal

---

## 📊 Métricas de Módulos

### **Contracts KPIs**
- Tiempo promedio de creación a activación
- Tasa de contratos completados vs iniciados
- Número de modificaciones por contrato

### **Negotiations KPIs**
- Número promedio de rondas por negociación
- Tiempo promedio de negociación
- Tasa de éxito de negociaciones

### **Legal KPIs**
- Tiempo promedio de validación legal
- Tasa de aprobación en primera revisión
- Número de issues de compliance detectados

### **Documents KPIs**
- Tiempo promedio hasta primera firma
- Tasa de documentos firmados completamente
- Número de versiones promedio por documento