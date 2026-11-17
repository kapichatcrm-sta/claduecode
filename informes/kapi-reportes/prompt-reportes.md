# Prompt: rehacer el módulo de Reportes de kapi

> **Cómo usar este archivo.** Pegalo completo como primer mensaje en Claude Code (o la herramienta de programación con IA que uses), abierto dentro del repositorio de la app de kapi. Adjuntá las siete imágenes de la carpeta `imagenes/` y, si podés, el PDF `kapi-reportes-como-funciona.pdf`. Todo lo que sigue está escrito para la IA que va a programar.

---

## 1. Tu tarea

Vas a rehacer la sección **Reportes** de kapi (ruta `/reports`), un CRM con chatbot para WhatsApp, Instagram, Messenger y email, pensado para negocios chicos de servicios y productos.

El módulo nuevo tiene cinco pestañas y un botón:

| Pestaña | Pregunta que responde |
|---|---|
| Resumen | ¿Cómo viene la atención y qué miro hoy? |
| Respuesta | ¿Estoy contestando a tiempo, cuándo fallo y quién atiende? |
| Embudo | ¿En qué etapa se frenan los chats y qué tan ordenado está mi Kanban? |
| Contactos | ¿Cómo crece mi base, qué tan interesada está y qué tan completa? |
| Cliente ideal | ¿Qué tipo de persona llega más a venta en mi CRM? |
| Botón «Analizar con IA» | Llevar los números a Claude o ChatGPT |

Quien usa esto es el dueño de un negocio, no un analista. Cada pantalla tiene que entenderse en diez segundos y cada bloque tiene que terminar en una acción.

## 2. Tres reglas que no se negocian

1. **Solo datos del CRM.** Todo número sale de lo que pasa dentro de kapi: conversaciones, mensajes, etapas del Kanban, contactos, etiquetas y seguimientos. kapi no tiene ERP ni sistema de ventas conectado, así que **no se muestra plata, ingresos, ticket ni «ventas reales»**. Lo único que existe es «chats marcados como venta»: los que están en una etapa del Kanban con «Cuenta como venta ganada». Usá siempre esa expresión.
2. **Nada de agenda.** No incluyas turnos, faltas, cancelaciones, ocupación ni profesionales. Esos datos quedan en Calendario.
3. **Nada inventado.** Si un dato no existe en la base, no lo simules ni lo estimes: aplicá el plan B que indica este documento y avisá en tu informe final.

Tampoco va una barra de preguntas en lenguaje natural: eso ya existe en el Asistente.

## 3. Antes de escribir código

Primero investigá el repositorio y contame lo que encontraste. No empieces a implementar hasta haber respondido esto:

- Dónde vive hoy el módulo de Reportes, qué pestañas tiene y qué consultas hace. Hoy existen los indicadores «Conversaciones», «Primera respuesta típica», «Respuesta típica», «Cerradas» y «Esperan respuesta», y los gráficos por canal, por día y hora, embudo por etapa y rendimiento por persona. **Reutilizá esas cuentas, no las dupliques.**
- Cómo es el modelo de datos de conversaciones, mensajes, etapas del Kanban, contactos, etiquetas y seguimientos.
- Qué componentes de interfaz ya existen (tarjetas, tablas, pestañas, selectores, esqueletos de carga) y qué tokens de color y tipografía usa la app.
- Las cuatro preguntas de la tabla siguiente.

| N.º | Pregunta | Métricas que dependen | Plan B si la respuesta es no |
|---|---|---|---|
| 1 | ¿Se guarda la fecha de cada cambio de etapa del Kanban y de cada cierre de conversación? | Marcados como venta del período, Días hasta marcarse como venta, Tiempo típico por etapa, Cuánto tardás en cerrar, Decide en, Escribe antes de decidir | «Marcados como venta» cuenta los chats del período que hoy están en esa etapa. Las métricas de tiempo se ocultan. No las aproximes. |
| 2 | ¿Cada mensaje guarda si lo envió el bot o una persona? | El bot y tu equipo, fila del bot en Quién atendió, aviso de Dentro y fuera de horario | Esos bloques se ocultan. |
| 3 | ¿Qué valores guarda el campo Origen del contacto? | Opción «Origen» del selector de «Qué grupo llega más a venta» | El selector queda solo con Etiqueta y Canal. |
| 4 | ¿El puntaje «Salud del cliente» se calcula con historial real? | Bloque «Cómo están tus clientes» | El bloque se oculta. |

Si encontrás algo que contradice este documento (por ejemplo, una tabla que no existe o un campo con otro significado), frená y preguntame antes de seguir.

## 4. Contexto técnico observado desde afuera

Esto se vio desde el navegador, sin acceso al código. **Verificalo en el repositorio antes de asumirlo.**

- Frontend en Next.js con App Router y React; componentes de estilo Radix.
- Base de datos MySQL (sin verificar).
- IA con Gemini, a través de un servicio interno llamado `ai-agent`.
- Colores definidos en `oklch(...)`, con un acento naranja óxido.
- Clases con prefijos `mcrm-`, `nexo` y `v-`; esqueletos de carga `kapi-skeleton` y `v-skel`.
- Configuración por pestañas con `?tab=`.

## 5. Estructura general

- **Ruta:** `/reports?tab=resumen|respuesta|embudo|contactos|cliente-ideal`. Sin `tab`, abre Resumen. El botón «Analizar con IA» abre `/reports/ia`.
- **Encabezado, igual en todas las pestañas:** título «Reportes», selector de período, texto «comparado con los N días anteriores», botón «Descargar» y botón principal «Analizar con IA».
- **Período:** hoy, ayer, esta semana, 7, 30 y 90 días, y mes. Por defecto, 30 días. El período elegido se mantiene al cambiar de pestaña y queda en la URL.
- **Orden dentro de cada pestaña:** indicadores arriba, gráficos al medio, tablas abajo.
- **Cada bloque termina en una acción:** un enlace que abre el módulo correspondiente (Chat, Kanban, Contactos, Seguimientos o Bot) ya filtrado con los casos de ese bloque.
- **Las pestañas viejas** (Demanda, Equipo, Kanban, Etiquetas, Consumidor ideal, Consultas) se eliminan. Si alguien entra por una URL vieja, redirigilo a la pestaña nueva equivalente.

## 6. Reglas de cálculo que valen para todo

| Término | Definición |
|---|---|
| Consulta | Una conversación. Empieza con el primer mensaje del contacto y cuenta una sola vez. Pertenece al período si ese primer mensaje cae dentro. |
| Marcado como venta | Chat en una etapa del Kanban con «Cuenta como venta ganada». No es facturación. |
| Comparación | Contra el período anterior del mismo largo. Flecha hacia arriba o abajo más la diferencia. Verde cuando mejora; en tiempos de espera, bajar es mejorar. Sin cambio: signo igual y texto «Igual que antes», en gris. |
| Típico | La mediana, nunca el promedio. |
| Horario de atención | Los tiempos de respuesta cuentan solo las horas del horario cargado en Configuración, Empresa. Donde este documento dice «tiempo de reloj», se cuenta todo el tiempo. |
| Zona horaria | La de la empresa. |
| Puntos | Diferencia entre dos porcentajes. |
| Pocos datos | Con menos de 10 casos en un bloque, se muestra la cantidad, no el porcentaje, y el texto «Todavía hay pocos datos». |
| Foto del momento | Números que no dependen del período porque muestran el estado actual. Se indican en cada caso. |
| Redondeo | Porcentajes sin decimales. Tiempos: en minutos hasta 59, en horas y minutos hasta 23 h, en días después. |

## 7. Pestaña por pestaña

En cada tabla, **Tipo** es `D` (cuenta directa sobre datos guardados) o `IA` (lectura con IA, ver sección 8). **Dep.** indica de cuál de las cuatro preguntas depende.

### 7.1 Resumen (`imagenes/1-resumen.png`)

Bloques, en orden: frase «Lo importante»; cinco indicadores; «De la consulta al cierre» (dos tercios del ancho) junto a «Para mirar hoy» (un tercio); «Por dónde te escriben» junto a «Qué te preguntan».

| Métrica | Tipo | Cómo se calcula | Gráfico | Dep. |
|---|---|---|---|---|
| Lo importante | IA | Elegí el indicador que más mejoró y el que más empeoró frente al período anterior y redactá dos oraciones. Solo podés usar números que ya estén en la pantalla. | Texto | |
| Consultas nuevas | D | Conversaciones cuyo primer mensaje del contacto cae en el período. | Tarjeta | |
| Primera respuesta | D | Mediana de los minutos entre el primer mensaje del contacto y la primera respuesta (bot o persona), dentro del horario de atención. | Tarjeta | |
| En menos de 5 min | D | Consultas con primera respuesta en 5 minutos o menos, sobre consultas del período. | Tarjeta | |
| Contactos nuevos | D | Contactos dados de alta en el período. | Tarjeta | |
| Esperan respuesta ahora | D | Conversaciones abiertas cuyo último mensaje es del contacto. Foto del momento. | Tarjeta con enlace | |
| De la consulta al cierre | D | Sobre las consultas del período: «Te escribieron» (todas), «Les respondiste» (con al menos una respuesta) y una barra por etapa del Kanban, en su orden, con los chats que hoy están en esa etapa o en una posterior. Porcentaje sobre «Te escribieron». No dibujes la primera etapa. La última barra se llama «Marcados como venta». Debajo, «Dónde más se pierde»: el par de pasos seguidos con mayor caída en personas. | Barras horizontales | |
| Para mirar hoy | D | Reglas en este orden; mostrá las tres primeras con casos: (1) conversaciones abiertas con el último mensaje del contacto hace más de 24 h; (2) franja de día y hora con la espera típica más alta, entre las que tienen 10 consultas o más; (3) etapa con más chats sin mensajes hace más de 7 días; (4) seguimientos vencidos; (5) contactos calientes sin mensajes del equipo hace más de 7 días. | Lista de avisos | |
| Por dónde te escriben | D | Consultas por canal y, de cada canal, qué porcentaje está marcado como venta. | Barras horizontales | |
| Qué te preguntan | IA | Tema principal de cada chat cerrado, de una lista de hasta seis temas más «Otros». Porcentaje sobre chats clasificados del período. | Barras horizontales, en el color secundario | |

### 7.2 Respuesta (`imagenes/2-respuesta.png`)

Bloques, en orden: cinco indicadores; «Cuánto esperan la primera respuesta» junto a «Dentro y fuera de horario»; «Cuándo te escriben» con las franjas lentas; «Quién atendió» junto a «El bot y tu equipo»; «Cuánto tardás en cerrar una conversación».

| Métrica | Tipo | Cómo se calcula | Gráfico | Dep. |
|---|---|---|---|---|
| Primera respuesta típica | D | Igual que en Resumen. | Tarjeta | |
| En menos de 5 min | D | Igual que en Resumen. | Tarjeta | |
| Respuesta típica | D | Para cada mensaje del contacto que tuvo respuesta: minutos hasta la respuesta siguiente, dentro del horario. Mediana de todos esos tiempos. | Tarjeta | |
| Esperan respuesta ahora | D | Igual que en Resumen. | Tarjeta con enlace | |
| Nunca tuvieron respuesta | D | Consultas del período sin ninguna respuesta, sobre consultas del período. | Tarjeta | |
| Cuánto esperan la primera respuesta | D | Cada consulta cae en un tramo: menos de 5 min, de 5 a 15 min, de 15 min a 1 h, de 1 a 4 h, más de 4 h, sin respuesta. Suman 100. | Barras horizontales; «Sin respuesta» en gris | |
| Dentro y fuera de horario | D | Una consulta es «dentro» si su primer mensaje llegó en el horario de atención. Para cada grupo: porcentaje del total y primera respuesta típica. En «fuera», en tiempo de reloj. El aviso: porcentaje de consultas de fuera de horario cuya primera respuesta fue del bot. | Tabla de dos filas | 2 (solo el aviso) |
| Cuándo te escriben | D | Consultas del período por día de la semana y hora de inicio. Cinco tonos repartidos en partes iguales entre el mínimo y el máximo. | Mapa de calor | |
| Franjas donde más hacés esperar | D | Bloques de tres horas por día. Para cada bloque con 10 consultas o más: cantidad de consultas y espera típica en tiempo de reloj. Los tres con más espera. | Lista | |
| Quién atendió | D | Por persona: chats con al menos un mensaje suyo en el período; su primera respuesta típica; su respuesta típica; de esos chats, los cerrados; y las conversaciones abiertas que tiene asignadas ahora. Una fila para el bot. Debajo, conversaciones abiertas sin agente. | Tabla | 2 (fila del bot) |
| El bot y tu equipo | D | Conversaciones cerradas del período en tres grupos: solo bot, bot y después persona, solo personas. Suman 100. | Barra única en tres partes, con leyenda | 2 |
| Cuánto tardás en cerrar | D | Mediana entre el primer mensaje y el paso a Cerrada; porcentaje de conversaciones cerradas el mismo día en que empezaron; conversaciones abiertas con más de 7 días (foto del momento). | Tres tarjetas chicas | 1 (las dos primeras) |

### 7.3 Embudo (`imagenes/3-embudo.png`)

Arriba de todo va un aviso fijo: *«Estos números salen de tu Kanban. kapi no ve lo que se cobra ni lo que se vende por fuera: cuenta los chats que alguien del equipo, o la IA, movió a una etapa de venta.»*

Bloques, en orden: aviso; cuatro indicadores; «Etapa por etapa»; «Por qué se cerraron sin venta» junto a «El orden de tu embudo»; «Qué grupo llega más a venta».

| Métrica | Tipo | Cómo se calcula | Gráfico | Dep. |
|---|---|---|---|---|
| Marcados como venta | D | Chats que pasaron en el período a una etapa marcada como venta. | Tarjeta | 1 |
| De cada 100 consultas, llegan a venta | D | Consultas del período que hoy están marcadas como venta, sobre consultas del período. | Tarjeta | |
| Días hasta marcarse como venta | D | Mediana de días entre el primer mensaje y el paso a la etapa de venta. | Tarjeta | 1 |
| Frenados más de 7 días | D | Chats abiertos en etapas anteriores a la venta sin mensajes de ninguna de las dos partes en 7 días. Foto del momento. | Tarjeta con enlace | |
| Etapa por etapa | D | Por etapa: chats del período que están en esa etapa o en una posterior; avance (chats de la etapa siguiente sobre los de esta); tiempo típico en la etapa; frenados más de 7 días. Resaltá la etapa con menor avance. | Tabla con barra por fila | 1 (tiempo típico) |
| Por qué se cerraron sin venta | IA | Sobre conversaciones cerradas en el período que no están marcadas como venta: motivo de una lista fija (precio, horarios, eligió otro lugar, otro). «Dejó de responder» va por regla, sin IA: el último mensaje es del negocio y no hubo respuesta. | Barras horizontales, en el color secundario | |
| El orden de tu embudo | D | Consultas del período que siguen en la primera etapa; chats frenados más de 7 días; chats abiertos del embudo sin agente asignado. | Tres números | |
| Quién mueve los chats | D | De los chats que cambiaron de etapa en el período, porcentaje movido por la IA y porcentaje movido a mano. Usá la marca «Movida por IA» que ya existe. | Barra única en dos partes | |
| Qué grupo llega más a venta | D | Por etiqueta: chats del período con esa etiqueta, cuántos están marcados como venta y la división entre ambos. Un chat con dos etiquetas cuenta en las dos; «Sin etiqueta» agrupa al resto. Selector para repetir la cuenta por Canal o por Origen. | Tabla con barra y selector | 3 (Origen) |

### 7.4 Contactos (`imagenes/4-contactos.png`)

Bloques, en orden: cinco indicadores; «Cómo crece tu base» junto a «Por dónde entraron»; «Qué tan interesados están» junto a «Cómo están tus clientes»; «Qué tan completa está tu base» junto a «Etiquetas más usadas».

| Métrica | Tipo | Cómo se calcula | Gráfico | Dep. |
|---|---|---|---|---|
| Contactos en tu base | D | Contactos activos. Valor anterior: ese total menos los contactos nuevos del período. | Tarjeta | |
| Contactos nuevos | D | Contactos dados de alta en el período. | Tarjeta | |
| Volvieron a escribir | D | Contactos dados de alta antes del período que iniciaron una conversación en el período. | Tarjeta | |
| Con permiso para mensajes | D | Contactos con consentimiento, sobre el total. | Tarjeta | |
| Sin actividad hace 60 días | D | Contactos cuyo último mensaje, enviado o recibido, tiene más de 60 días. Foto del momento. | Tarjeta con enlace | |
| Cómo crece tu base | D | Contactos nuevos por semana (por día si el período tiene 14 días o menos). Debajo, una frase que reparte las consultas entre contactos nuevos y contactos que ya existían. | Barras horizontales; la última, en tono oscuro | |
| Por dónde entraron | D | Canal de la primera conversación de cada contacto nuevo. | Barras horizontales | |
| Qué tan interesados están | D | Contactos según el campo Interés que la IA ya asigna: calientes, fríos, sin clasificar. Aviso: calientes sin mensajes del equipo en 7 días. | Barras horizontales | |
| Cómo están tus clientes | D | Solo contactos con un chat marcado como venta, según el puntaje de salud de la ficha: bien (70 a 100), para cuidar (40 a 69), en riesgo (0 a 39). Sin historial suficiente, el contacto no entra. | Barras horizontales | 4 |
| Qué tan completa está tu base | D | Porcentaje de contactos con cada dato: teléfono, nombre y apellido, agente asignado, alguna etiqueta, email. Aviso: cantidad de contactos sin ninguna etiqueta. | Barras horizontales | |
| Etiquetas más usadas | D | Por etiqueta: contactos que la tienen y cuántos de ellos son nuevos del período. Debajo, cuántas etiquetas se usan sobre el máximo de 25. | Tabla | |

### 7.5 Cliente ideal (`imagenes/5-cliente-ideal.png`)

**Cómo se arma.** Compará dos grupos de los últimos 6 meses: contactos con un chat marcado como venta («llegaron a venta») y contactos que consultaron y cerraron sin venta («no llegaron»). Recalculalo una vez por semana y guardá el resultado. Con menos de 20 chats marcados como venta, no muestres el perfil: mostrá cuántos faltan.

Bloques, en orden: selector de perfil (tu cliente ideal, el ocasional, el que más tiempo te lleva) con la base usada; frase del perfil con cuatro datos y dos botones; seis tarjetas; «Qué hacer con este perfil».

| Métrica | Tipo | Cómo se calcula | Dep. |
|---|---|---|---|
| El perfil en una frase | IA | Redactala con el canal más frecuente, el tema más frecuente del primer mensaje y los días que tarda en decidir. | |
| Decide en | D | Mediana de días entre el primer mensaje y el paso a la etapa de venta. | 1 |
| Escribe antes de decidir | D | Mediana de mensajes del contacto antes del paso a la etapa de venta. | 1 |
| Vuelve a escribirte | D | Para contactos con dos conversaciones o más: mediana de días entre el inicio de una y el de la siguiente. | |
| Sigue en contacto | D | Mediana de meses entre el primer y el último mensaje. | |
| Por dónde te escribe | D | Canal de la primera conversación; porcentaje por canal. Más las dos etiquetas más frecuentes. | |
| Qué busca | IA | Hasta cuatro motivos; cada uno debe aparecer en al menos 1 de cada 10 chats. | |
| Cómo decide | D e IA | Etiqueta con mayor porcentaje de llegada a venta, entre las que tienen 10 chats o más. Porcentaje de llegada a venta de las consultas respondidas en 10 minutos o menos, frente al resto. Tema más frecuente del primer mensaje (IA). | |
| Qué lo frena y qué responderle | IA | Las tres dudas más repetidas y la respuesta que dio el equipo en chats que llegaron a venta. | |
| Con qué palabras lo pide | IA | Tres frases textuales, sin nombres ni datos personales. | |
| En qué se nota la diferencia | D | Para cada rasgo de una lista fija (respondido en menos de 10 minutos, canal, etiqueta, tema del primer mensaje), porcentaje de cada grupo que lo cumple. Mostrá los tres con mayor diferencia. | |
| Contactos parecidos | D | Contactos que no llegaron a venta y cumplen al menos dos de esos tres rasgos. El botón les pone una etiqueta. | |
| Los otros dos perfiles | D | Ocasional: llegó a venta y tiene una sola conversación. El que más tiempo te lleva: no llegó a venta y está en la cuarta parte con más mensajes. | |

Las cuatro acciones de «Qué hacer con este perfil» usan módulos que ya existen: etiquetar contactos, agregar un contexto al bot, guardar respuestas rápidas y abrir «Analizar con IA».

### 7.6 Analizar con IA (`imagenes/6-analizar-con-ia.png`)

Hacelo en dos fases:

- **Fase 1, incluida en este trabajo:** «Copiar informe» (un texto con todos los números del período, listo para pegar en una IA), «Descargar en PDF» y «Descargar en Excel».
- **Fase 2, no la construyas todavía:** el conector de solo lectura para Claude y ChatGPT, los cuatro permisos y el registro de consultas. Dejá la pantalla armada con esas partes marcadas como «Próximamente» y contame qué haría falta.

## 8. Lectura con IA

Usá el mismo servicio de IA que la app ya tiene para el Resumen IA y las etiquetas automáticas.

- **Cuándo corre.** Una vez por chat, al cerrarse. Nunca al cargar la pantalla.
- **Qué guarda.** Tema principal y, si el chat cerró sin venta, el motivo. Los reportes leen esos valores guardados.
- **Listas cerradas.** Temas: hasta seis más «Otros», editables por el dueño. Motivos: precio, horarios, eligió otro lugar, otro.
- **Cliente ideal.** Una tarea semanal que guarda el perfil completo.
- **Transparencia.** Todo bloque de IA lleva un enlace para leer los chats detrás del número.
- **Privacidad.** Las citas textuales van sin nombres, teléfonos ni datos personales.
- **Si la IA falla o no hay crédito.** El bloque muestra «Todavía no pudimos leer estos chats» y el resto de la pestaña funciona igual.

## 9. Diseño

Seguí las imágenes de `imagenes/` como referencia de distribución y jerarquía. **Usá los tokens de color y tipografía que ya tiene la app.** Los valores de abajo son los de las maquetas y sirven solo como referencia.

| Elemento | Valor en la maqueta |
|---|---|
| Fondo de página | `#F6F5F2` |
| Tarjeta | `#FFFFFF`, borde `#E8E5E0`, radio 14 px, relleno 20 px |
| Texto | `#1C1917`; secundario `#57534E`; apagado `#6B665F` |
| Acento | `#BC4F1B`; acento oscuro `#7A300C`; fondo suave de aviso `#FBEEE6` |
| Color secundario de gráficos | `#2B6CB0` (solo en bloques de IA: temas y motivos) |
| Gris de comparación | `#857F78` |
| Mapa de calor | `#F4EEE9`, `#F1D3C0`, `#E3A27F`, `#CC6E3F`, `#A9471A` |
| Mejora y empeora | `#1B6E45` y `#B42318`, siempre con flecha y texto |
| Títulos | Fuente redondeada en peso 800: 28 px el título, 17 px los bloques, 28 px los números |
| Texto | Fuente del sistema, 14 px; etiquetas de 13 px |
| Separación | 20 px entre bloques, 16 px entre indicadores |

**Los títulos hoy usan «Arial Rounded MT Bold», que solo existe en Mac.** Cargá una fuente web redondeada equivalente (en las maquetas, Nunito) para que se vea igual en Windows y Android.

Reglas de gráficos:

- Solo cuatro tipos: tarjeta con número, barras horizontales, mapa de calor y tabla. Sin tortas, líneas ni dos ejes.
- Toda barra lleva su número al lado. El texto nunca toma el color de la barra.
- Extremos de barra redondeados 4 px; 2 px de separación entre partes de una barra partida.
- Un solo color por gráfico, salvo las barras partidas, que llevan leyenda.
- El color nunca es la única señal: flecha más texto en las comparaciones, etiqueta en cada barra.

Otras reglas:

- **Celular** (`imagenes/7-celular.png`): una sola columna, indicadores de a dos, pestañas con desplazamiento horizontal. Las tablas anchas se desplazan dentro de su caja.
- **Accesibilidad:** botones y enlaces reales, contraste de texto de 4,5 a 1 como mínimo, zonas táctiles de 44 px, y texto alternativo en el mapa de calor y en las barras partidas.
- **Textos:** español rioplatense con voseo, coma decimal, espacio antes del signo de porcentaje. Sin inglés ni jerga. Usá exactamente los nombres de este documento; no mezcles «Cerrada» con «Resuelta» ni «Bot» con «Agente».

## 10. Estados de cada bloque

- **Cargando:** el esqueleto de carga que ya usa la app.
- **Sin datos en el período:** una línea que diga qué falta, por ejemplo «Todavía no hay consultas en este período».
- **Pocos datos:** cantidad sin porcentaje y el aviso de la sección 6.
- **Dato no disponible** (plan B aplicado): el bloque no se muestra. No dejes una tarjeta vacía.
- **Error:** «No pudimos cargar este bloque» y un botón para reintentar. Un bloque con error no rompe los demás.

## 11. Rendimiento

- Calculá en la base de datos, con consultas agregadas. No traigas mensajes al navegador para sumarlos.
- Cada pestaña pide solo sus datos. Los bloques cargan en paralelo.
- Guardá en caché los resultados por empresa y período; los números de «foto del momento» se refrescan en cada carga.
- La pestaña tiene que mostrarse en menos de dos segundos con una empresa de 10.000 conversaciones.
- Respetá los permisos existentes: un agente sin permiso de reportes no ve el módulo.

## 12. Orden de trabajo

1. Investigación e informe (sección 3). Esperá mi OK.
2. Capa de cálculo: una función por métrica, con pruebas. Empezá por las que no dependen de ninguna pregunta.
3. Estructura: ruta, encabezado, selector de período y pestañas.
4. Pestañas en este orden: Respuesta, Resumen, Embudo, Contactos.
5. Tareas de IA (temas y motivos) y los bloques que las usan.
6. Cliente ideal.
7. Analizar con IA, fase 1.
8. Celular, estados vacíos, accesibilidad y textos.

Mostrame el resultado al terminar cada paso.

## 13. Criterios de aceptación

- [ ] Las cinco pestañas existen, con los bloques en el orden indicado.
- [ ] No aparece ningún dato de agenda ni ningún importe en dinero.
- [ ] La palabra «venta» aparece siempre como «marcado como venta» o «llegan a venta», y el aviso del Embudo está visible.
- [ ] Cada métrica coincide con su fórmula y tiene al menos una prueba con datos conocidos.
- [ ] Los tiempos usan mediana y respetan el horario de atención, salvo donde se indica tiempo de reloj.
- [ ] Las cuatro preguntas están respondidas y el plan B está aplicado donde corresponde.
- [ ] Ningún bloque de IA se calcula al cargar la pantalla.
- [ ] Cada bloque tiene su enlace de acción y abre el módulo ya filtrado.
- [ ] Funciona en celular sin desplazamiento horizontal de la página.
- [ ] Los títulos se ven con la misma fuente en Mac, Windows y Android.
- [ ] No queda texto en inglés ni jerga interna a la vista del usuario.

## 14. Qué me tenés que entregar al final

1. La respuesta a las cuatro preguntas, con el archivo o la tabla donde lo verificaste.
2. La lista de métricas a las que les aplicaste el plan B.
3. Todo lo que encontraste distinto a lo que dice este documento.
4. Un resumen de los archivos que cambiaste.
5. Lo que quedó pendiente y por qué.

## 15. Imágenes de referencia

| Archivo | Pantalla |
|---|---|
| `imagenes/1-resumen.png` | Resumen |
| `imagenes/2-respuesta.png` | Respuesta |
| `imagenes/3-embudo.png` | Embudo |
| `imagenes/4-contactos.png` | Contactos |
| `imagenes/5-cliente-ideal.png` | Cliente ideal |
| `imagenes/6-analizar-con-ia.png` | Analizar con IA |
| `imagenes/7-celular.png` | Resumen en el celular |

Los números de las imágenes son de ejemplo (una empresa de prueba). No los copies al código.
