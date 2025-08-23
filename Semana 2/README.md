# Entrega 2 - Diseño tactico

## Miembros

- Francisco Robles [@froblesl](github.com/froblesl)
- Hernán Álvarez [@hernanHawk](github.com/hernanHawk)
- Nicolás Escobar [@nicolasuniandes](github.com/nicolasuniandes)
- Javier barrera [@j4vierb](github.com/j4vierb)

# Atributos de calidad

## 1. Escalabilidad
- **Definición:**  
  Capacidad de la arquitectura para soportar un aumento significativo de usuarios, transacciones y equipos de desarrollo sin degradar el rendimiento.

- **Justificación:**  
  - El sistema hoy procesa +80.000 transacciones por minuto y maneja $50B USD al año.  
  - Con la salida a bolsa (IPO) se espera crecimiento acelerado de clientes y transacciones.  
  - Una arquitectura de microservicios reactivos debe escalar horizontalmente, evitando que un servicio afecte al resto.  

---

## 2. Disponibilidad
- **Definición:**  
  Capacidad del sistema para operar de manera continua, cumpliendo con SLA de alta disponibilidad y tolerancia a fallos.

- **Justificación:**  
  - El negocio exige SLA de activación de campañas en 24 horas y pagos en 48 horas.  
  - Un incidente en un servicio no debe impactar al resto (problema actual del monolito).  
  - Al operar globalmente (20 oficinas y clientes internacionales), el downtime implica pérdidas millonarias y afecta la confianza de los socios.  

---

## 3. Interoperabilidad
- **Definición:**  
  Capacidad de la arquitectura para integrar componentes y servicios construidos con diferentes tecnologías, lenguajes y plataformas, garantizando comunicación fluida y eficiente.

- **Justificación:**  
  - Las limitantes del stack actual han frenado la innovación y la nueva arquitectura debe permitir servicios con tecnologías heterogéneas.  
  - Cada equipo podrá seleccionar el stack más adecuado al problema, pero esto exige mecanismos comunes de integración.  
  - Los microservicios podrán colaborar sin importar el lenguaje o framework elegido.  


# Vista de contexto

# Vista funcional

## Diagrama de componentes

## Diagrama de modulos

# Vista de información

