# Prompt: rehacer el módulo de Automatizaciones de kapi

> **Cómo usar este archivo.** Pegalo completo como primer mensaje en Claude Code (o la herramienta de programación con IA que uses), abierto dentro del repositorio de la app de kapi. Adjuntá las siete imágenes de la carpeta `imagenes/` y, si podés, el PDF `kapi-automatizaciones-como-funciona.pdf`. Todo lo que sigue está escrito para la IA que va a programar.

---

## 1. Tu tarea

Vas a rehacer **Automatizaciones** en kapi, un CRM con chatbot para WhatsApp pensado para negocios chicos de servicios y productos. El objetivo del producto es **fidelizar**: que el cliente se quede. kapi tiene que acompañar a cada persona después de la compra sin que el dueño se acuerde de nada: agradecerle, preguntarle cómo le fue, ofrecerle algo más cuando corresponde y buscarla si deja de escribir.

El módulo cambia de raíz:

- **Las automatizaciones se piden en el chat con el Asistente**, en lenguaje natural. Ya no se arman a mano con un editor.
- **El módulo Automatizaciones queda solo para mirar**: qué está activo, qué base tiene cada una, qué va a salir y qué salió.

El trabajo tiene tres partes:

| Parte | Qué es |
|---|---|
| El motor | Decide a quién le toca cada mensaje, lo envía y registra qué pasó. |
| El Asistente | Entiende el pedido, propone la automatización y la activa solo con el OK del dueño. |
| Las pantallas | Cinco pantallas de solo lectura y su versión para celular. |

## 2. Reglas que no se negocian

1. **Solo lectura.** El módulo no tiene ningún control para crear, editar, borrar ni pausar. Todo cambio pasa por el Asistente y necesita el OK explícito del dueño.
2. **Ante la duda, no se envía.** Ningún mensaje sale sin permiso de la persona, sin texto aprobado por Meta o salteando un cuidado. Un mensaje de menos es un error menor; un mensaje de más le cuesta un cliente al negocio.
3. **Nunca dos veces.** El mismo mensaje no le llega dos veces a la misma persona por el mismo motivo, aunque el proceso se reinicie o corra en paralelo.
4. **Solo datos del CRM.** kapi no tiene ERP ni tienda conectada. «Compra» significa siempre: el día en que un chat se marcó como venta en el Kanban (pasó a una etapa con «Cuenta como venta ganada»). No hay plata, no hay ventas externas y **no hay nada de agenda ni de turnos**.
5. **Nada inventado.** Si un dato no existe en la base, no lo simules: aplicá el plan B de este documento y avisá en tu informe final.
6. **Solo por la API oficial de WhatsApp.** La app también permite conectar WhatsApp Web con QR; las automatizaciones nunca salen por ahí.

## 3. Qué es una automatización y qué no

**Sí es:** un mensaje que kapi manda por iniciativa propia, a las personas que cumplen una regla, en un momento definido. En esta versión, solo por WhatsApp.

**No es, y queda fuera de este trabajo:**

- Lo que kapi contesta cuando el cliente escribe. Eso es del Bot.
- Recordatorios de turno o cualquier cosa de agenda.
- Carrito abandonado: requiere una tienda conectada, que no existe.
- El módulo Marketing, que está en preparación.
- El editor visual de flujos: sale del menú.
- Instagram, Messenger y email. Dejá el modelo preparado para sumar email después, pero no lo construyas.

## 4. Antes de escribir código

Primero investigá el repositorio y contame lo que encontraste. No empieces a implementar hasta haber respondido esto:

- Cómo funciona hoy el motor de automatizaciones: disparadores, nodos, ejecuciones y límites. Qué partes sirven tal cual.
- Cómo crea y aplica cosas el Asistente hoy, qué herramientas tiene y cómo pide el OK del dueño.
- Cómo se envían hoy los mensajes aprobados de WhatsApp y cómo se descuentan los créditos.
- Cuántos flujos publicados existen hoy hechos con el editor visual. No los borres: proponeme qué hacer con ellos.
- Las seis preguntas de la tabla.

| N.º | Pregunta | Qué depende | Plan B si la respuesta es no |
|---|---|---|---|
| 1 | ¿Se guarda la fecha en que un chat pasa a una etapa marcada como venta? | Toda automatización que cuenta días desde la compra | Empezá a guardarla. Esas automatizaciones funcionan solo para ventas marcadas desde ese día; no reconstruyas fechas viejas. |
| 2 | ¿El motor puede calcular por adelantado a quién le toca cada día, o solo reacciona cuando algo pasa? | La pantalla Próximos envíos y todos los números de «salen hoy» y «próximos 7 días» | Hay que construir el calendario de envíos de la sección 8. Es la pieza central: sin ella no hay módulo. |
| 3 | ¿kapi puede crear un mensaje y mandarlo a aprobar a Meta, o solo cargar los ya aprobados? | El paso de aprobación en el chat | El Asistente usa solo mensajes ya aprobados y, si no hay uno que sirva, le explica al dueño cómo crearlo en Meta. |
| 4 | ¿Funcionan hoy los disparadores «Inactividad detectada» y «Fecha programada»? | Mensajes por falta de actividad, por fecha y envíos únicos | No dependas de ellos: el calendario de envíos calcula esas fechas por su cuenta. |
| 5 | ¿Se guardan los avisos de WhatsApp sobre cada mensaje: enviado, entregado, leído o fallido? | Entregados, Leídos y el motivo «WhatsApp no pudo entregarlo» | Empezá a guardarlos. Hasta entonces, el Historial muestra solo enviados y respondidos. |
| 6 | ¿Hay hoy una forma de registrar que alguien pidió no recibir más mensajes? | El cuidado «Baja inmediata» | Construila antes que cualquier otra cosa. Sin baja no se activa ninguna automatización. |

Si encontrás algo que contradice este documento, frená y preguntame antes de seguir.

## 5. Contexto técnico observado desde afuera

Esto se vio desde el navegador, sin acceso al código. **Verificalo en el repositorio antes de asumirlo.**

- Frontend en Next.js con App Router y React; componentes de estilo Radix. Base de datos MySQL (sin verificar).
- IA con Gemini, a través de un servicio interno llamado `ai-agent`, que tiene «skills».
- El módulo actual vive en `/workflows` y `/workflows/{id}`, con un editor hecho con React Flow.
- El editor actual lista disparadores como mensaje recibido, etiqueta asignada, etapa del Kanban modificada, oportunidad ganada, inactividad detectada y fecha programada. **Varios figuran pero no se emiten.**
- Hay pasos que te sirven: verificar consentimiento, control de frecuencia, horario comercial, enviar plantilla, esperar respuesta, escalar a humano, agregar etiqueta, crear tarea.
- Límite actual de 10 ejecuciones por minuto.
- Cada mensaje de WhatsApp consume 4 créditos.
- Los mensajes aprobados se cargan desde Meta.
- La ficha del contacto tiene un campo de consentimiento.
- Canales muestra el nivel del número (cuántas personas puede contactar por día) y su calidad.
- El Asistente vive en `/asistente` y muestra el texto «usa tus permisos y nada se aplica sin tu OK».
- **Problemas conocidos del Asistente que este trabajo tiene que resolver:** falló al crear una regla porque usó campos que no existen, le pidió al usuario «el ID del tag» y mezcla «tú» con «vos».

## 6. Cómo está hecha una automatización

Toda automatización tiene las mismas cinco partes. Usá estos nombres en el código, en el chat y en las pantallas.

### 6.1 A quién: la base

Una base es **una regla, no una lista guardada**. Se recalcula cada vez que se necesita. La regla combina condiciones con «y». Condiciones permitidas, y solo estas:

| Condición | Ejemplos |
|---|---|
| Etapa del Kanban | Está marcado como venta. No está marcado como venta. |
| Fecha en que se marcó como venta | Hace menos de 15 días. Hace más de 6 meses. |
| Etiquetas | Tiene «Clase de prueba». No tiene «Compró». |
| Interés que asigna la IA | Caliente. Frío. |
| Canal | WhatsApp. |
| Último mensaje del contacto | Hace más de 60 días. |
| Último mensaje del negocio sin respuesta | Hace 15 días. |
| Fecha de alta del contacto | Hace más de 30 días. |
| Campo propio de tipo fecha | Cumpleaños. Vencimiento de la cuota. |

Tres condiciones van siempre, aunque nadie las pida: la persona dio permiso, no pidió la baja y tiene WhatsApp.

Un negocio que no usa el Kanban puede usar una etiqueta, por ejemplo «Compró», como señal de compra. En ese caso la fecha es la del día en que se puso la etiqueta.

### 6.2 Cuándo

| Forma | Ejemplo | Qué define una «ocurrencia» |
|---|---|---|
| Días después de algo que pasó | A los 15 días de la compra | La fecha del hecho |
| Se repite | Cada 6 meses como cliente | El número de repetición |
| Una fecha de cada año | El día del cumpleaños | El año |
| Tiempo sin actividad | 60 días sin escribir · 15 días sin responder | La fecha del último mensaje que inició el plazo |
| Fecha y hora puntual (solo envío único) | El lunes 30 a las 10:00 | Única |

Cada automatización tiene una hora de envío. Por defecto, las 10:00. Los envíos solo salen dentro del horario permitido: por defecto, de lunes a sábado de 9 a 20, en la zona horaria de la empresa. Si un envío cae fuera, pasa al siguiente momento válido.

La «ocurrencia» es lo que impide repetir: **automatización + contacto + ocurrencia** es una clave única.

### 6.3 Qué se manda

- Un mensaje de WhatsApp aprobado por Meta.
- Datos que se completan solos con cada persona: nombre, nombre del negocio y campos de la ficha.
- Hasta tres botones de respuesta.
- Si falta un dato de la persona (por ejemplo, no tiene nombre cargado), usá un texto de reemplazo definido en la automatización. Si no hay reemplazo, ese envío no sale y queda registrado con el motivo.

### 6.4 Qué pasa después

Una rama por cada respuesta posible:

| Respuesta | Cómo se detecta |
|---|---|
| Un botón | Por el botón que tocó. |
| Texto libre | La IA lo clasifica en: conforme, duda o queja, pide la baja, otro. |
| Silencio | Pasaron N días sin respuesta. Por defecto, 3. |

Acciones permitidas en cada rama, todas ya existentes en la app: responder con un mensaje, abrir el chat y avisar a una persona del equipo, poner o quitar una etiqueta, crear un seguimiento, mover de etapa, o no hacer nada.

Cuando la persona responde, la conversación sigue su curso normal con el Bot o el equipo. La automatización no insiste nunca más de una vez.

### 6.5 Cuidados

Son fijos, iguales para todas, y **no se pueden apagar ni desde el chat**:

| Cuidado | Regla |
|---|---|
| Permiso | Solo a quien tiene el consentimiento marcado. |
| Tope semanal | Un mensaje automático por persona cada 7 días, como máximo. |
| Horario | Solo dentro del horario permitido. |
| Baja inmediata | Quien pide no recibir más queda afuera para siempre. |
| Chat abierto | No sale si la persona tiene una conversación abierta en la que alguien del equipo escribió en las últimas 48 horas. |
| Límite diario | No se supera el máximo diario que kapi muestra en Canales. Usá como techo el 80 % de ese máximo. |
| Créditos | No sale si no alcanzan los créditos. |

## 7. Tipos y estados

**Tipos:** *continua* (queda funcionando y le llega a cada persona cuando le toca) y *envío único* (sale una sola vez, a una base, en una fecha y hora).

| Estado | Qué significa | Se ve en el módulo |
|---|---|---|
| Propuesta | El Asistente la armó y espera el OK del dueño. | No. Solo en el chat. |
| Espera a Meta | El mensaje está en revisión. | Sí |
| Activa | Continua, funcionando. | Sí |
| Programada | Envío único con fecha, sin salir. | Sí |
| En pausa | El dueño pidió frenarla. Conserva su base, no envía. | Sí |
| Con problema | No puede enviar. Muestra el motivo y qué hacer. | Sí |
| Terminada | Envío único que ya salió. | Solo en Historial |

Motivos de «Con problema»: Meta rechazó o dio de baja el mensaje, no hay créditos, el número llegó a su límite, o el canal se desconectó.

## 8. El motor

### 8.1 El calendario de envíos

Es la pieza central. Es una lista de envíos programados: automatización, contacto, ocurrencia, fecha y hora prevista, y estado.

- **Se arma una vez por día**, de madrugada, para los próximos 7 días.
- **Se actualiza en el momento** cuando: un chat se marca como venta, se pone o se quita una etiqueta usada por alguna base, una persona responde, una persona pide la baja, o una automatización se activa, se pausa o cambia.
- Para cada automatización activa: calculá quién cumple la regla y en qué fecha le toca, y creá o actualizá su envío programado.
- **Es una previsión.** Los mensajes del día siguiente a una compra recién se conocen cuando se marca la venta, así que no pueden aparecer a más de un día de distancia.

### 8.2 Al activar, nada hacia atrás

Cuando una automatización continua se activa, entra solo quien todavía no llegó a su fecha. Si alguien compró hace 40 días y se activa «a los 15 días de la compra», no recibe nada. Lo mismo vale para las de falta de actividad: quien ya había pasado el plazo antes de activarla, no entra. Para escribirle a toda esa gente existe el envío único.

### 8.3 Tope semanal y prioridad

Cuando a una persona le tocan dos mensajes dentro de los mismos 7 días:

1. Sale el de mayor prioridad, en este orden: (1) respuesta a algo que la persona hizo hace poco, como «Gracias por tu compra»; (2) recorrido por días; (3) fechas, como cumpleaños o cada 6 meses; (4) recuperación; (5) envíos únicos.
2. El otro se corre al primer día libre, hasta 7 días después de su fecha original.
3. Si en ese plazo no pudo salir, o era de fecha exacta como un cumpleaños, se descarta y se registra con el motivo «ya había recibido otro mensaje esa semana».

### 8.4 El envío

A la hora prevista, **volvé a revisar todo** antes de enviar: que la persona siga cumpliendo la regla, permiso, baja, chat abierto, tope semanal, estado del mensaje en Meta, límite diario y créditos. Si algo falla, el envío no sale y queda registrado con su motivo.

Si pasa todo: enviá por la API oficial, descontá los créditos, registrá el envío y respetá el límite de velocidad que ya tiene la app.

Si el límite diario no alcanza para todos los envíos del día, salen primero los de mayor prioridad y el resto pasa al día siguiente.

### 8.5 El resultado

- Guardá los avisos de WhatsApp: enviado, entregado, leído, fallido con su motivo.
- «Respondió» es cualquier mensaje de la persona dentro de los 3 días siguientes al envío.
- Clasificá la respuesta y ejecutá la rama que corresponda.
- Un envío único pasa a «Terminada» cuando salió el último mensaje.

### 8.6 La baja

- La persona puede pedirla con una palabra («baja», «no quiero recibir más», «stop») o con un botón. La IA también detecta la intención en un texto libre.
- kapi la registra, le confirma con un mensaje corto y la excluye para siempre de todas las automatizaciones.
- La baja no impide que la persona escriba ni que el negocio le responda sus consultas.
- El dueño puede revertir una baja solo si la persona lo pide.

### 8.7 Pausar, reanudar y cambiar

- **Pausar:** no sale nada. La base sigue funcionando. Al reanudar, a quien se le pasó la fecha por más de 7 días no le llega.
- **Cambiar el mensaje:** hay que volver a aprobarlo en Meta. Mientras tanto sigue saliendo el anterior.
- **Cambiar la base o el momento:** se recalcula el calendario. Los envíos ya hechos no se tocan.

### 8.8 Calidad del número

Si la calidad del número baja, avisale al dueño en el chat y frená los envíos únicos hasta que él decida. Las continuas siguen.

### 8.9 El registro de envíos

Un registro por cada envío, incluso los que no salieron: automatización, contacto, ocurrencia, fecha prevista, fecha real, estado (enviado, entregado, leído, respondió, no salió), motivo si no salió, clasificación de la respuesta, acción ejecutada y créditos usados. De acá salen el Historial y todos los números de resultado.

## 9. El Asistente

### 9.1 Qué tiene que poder hacer

Adaptá estos nombres a como ya estén hechas las herramientas del Asistente:

| Herramienta | Qué hace |
|---|---|
| Buscar una base | Recibe una regla y devuelve cuántas personas la cumplen hoy y una muestra con nombres. |
| Proponer una automatización | Arma las cinco partes y la deja en estado Propuesta. No envía nada. |
| Activar | Solo después del OK explícito del dueño. |
| Crear un mensaje para aprobar | Lo envía a revisión de Meta y sigue su estado. |
| Cambiar, pausar y reanudar | Siempre con OK. |
| Listar y explicar | Responde qué hay activo, qué sale hoy y qué le va a llegar a una persona. |

### 9.2 Cómo tiene que conversar

1. **Entender el pedido tal como viene.** El dueño habla con sus palabras y casi nunca da todos los datos.
2. **Completar con valores sensatos:** las 10:00 como hora, los cuidados fijos, y «si responde con un problema, avisar a una persona».
3. **Preguntar solo lo imprescindible, de a una pregunta y con opciones.** La más importante: si un pedido como «mandales a los que compraron en los últimos 15 días» es para **una sola vez** o **de ahora en más**. Mostrá las dos opciones con la cantidad de personas de cada una.
4. **Nunca pedir identificadores, códigos ni nombres internos.** Buscá las etiquetas, las etapas y las personas por su nombre. Si hay dos parecidas, mostralas por nombre y que el dueño elija.
5. **Usar solo campos que existen.** Antes de proponer, verificá cada condición contra la lista de la sección 6.1.
6. **Mostrar siempre la tarjeta de propuesta** con las cinco partes, a cuántas personas les llegaría hoy y un enlace para ver la lista.
7. **No activar sin un sí claro.** Un «dale», un «activala» o el botón «Activar» valen. Una pregunta o un silencio, no.
8. **Avisar lo que viene:** que Meta tiene que aprobar el mensaje y cuánto suele tardar. Cuando aprueba o rechaza, avisar en el chat. Si rechaza, explicar por qué y proponer un texto corregido.
9. **Decir que no cuando corresponde.** Si el pedido necesita un dato que no existe (cumpleaños sin cargar, tienda sin conectar, algo de agenda), explicalo y ofrecé la alternativa más cercana.
10. **Advertir antes de un riesgo:** una base más grande que el límite diario, un texto que Meta suele rechazar, o un envío a gente que no escribe hace mucho.
11. **Hablar bien:** español rioplatense con voseo, sin inglés y sin jerga. Nunca mezclar «tú» y «vos».
12. **Dejar rastro:** cada automatización guarda quién la pidió, cuándo, y el enlace a la conversación.

La imagen `imagenes/6-en-el-chat.png` muestra una conversación completa de ejemplo.

## 10. Las pantallas

Todas son de solo lectura. Ruta sugerida: `/workflows?tab=activas|bases|envios|historial` y `/workflows/{id}` para el detalle. El encabezado es igual en todas: título «Automatizaciones», la línea «Se crean y se cambian hablando con kapi en el chat. Acá ves qué está activo, a quién le llega y cuándo.» y el botón «Pedir una automatización en el chat», que abre el Asistente.

### 10.1 Activas (`imagenes/1-activas.png`)

| Elemento | Qué muestra y cómo se calcula |
|---|---|
| Automatizaciones activas | Cantidad en estado Activa. Debajo, cuántas esperan a Meta y cuántos envíos únicos hay programados. |
| Mensajes que salen hoy | Envíos programados para hoy, entre todas. Enlace a Próximos envíos. |
| En los próximos 7 días | Envíos programados de los próximos 7 días. Debajo, cuántos se corrieron por el tope semanal. |
| Respondieron este mes | Mensajes de los últimos 30 días con respuesta dentro de los 3 días, sobre los enviados. |
| Clientes recuperados | Personas que en los últimos 30 días recibieron un mensaje de falta de actividad y volvieron a escribir dentro de los 14 días. |
| El recorrido de tu cliente | Arriba, en orden de tiempo, las automatizaciones que cuentan desde la compra o son una fecha del año. Abajo, «Si se aleja»: las de falta de actividad. Punto lleno si está activa, vacío si no. El subtítulo aclara qué se toma como compra. |
| Todas las automatizaciones | Una fila por automatización: nombre y momento, base, próximo envío, porcentaje de respuesta y estado. El nombre abre el detalle. |
| Cuidados que valen para todas | Cuatro textos fijos: permiso, una por semana, en horario y baja inmediata. |

Al pie: «Esta pantalla es solo para mirar. Para crear, cambiar o pausar una automatización, pedíselo a kapi en el chat.»

### 10.2 Detalle (`imagenes/2-detalle.png`)

| Elemento | Qué muestra y cómo se calcula |
|---|---|
| Título | Nombre, estado, tipo, quién la pidió y cuándo. Botón «Pedir un cambio en el chat», que abre el Asistente con esa automatización como contexto. |
| La frase | Toda la automatización en una oración, redactada con las cinco partes. Debajo, qué se toma como compra. |
| A quién | Cantidad en espera, la regla como etiquetas y una frase con la cuenta: cumplen la regla, menos sin permiso, menos con baja. Tabla de personas ordenadas por fecha de envío. Enlace a Contactos con ese filtro. |
| Cuándo | El momento en palabras y barras con los envíos de los próximos días. |
| Qué se manda | El mensaje como lo ve el cliente, con los datos variables en negrita y los botones. Debajo: estado en Meta, canal y créditos por envío. |
| Qué pasa después | Una fila por rama. |
| Cuidados | Las reglas fijas. |
| Cómo viene | Últimos 30 días: enviados, entregados, leídos, respondieron, con duda o queja y pidieron no recibir más. Enlace a la conversación donde se pidió. |

### 10.3 Bases (`imagenes/3-bases.png`)

| Elemento | Qué muestra y cómo se calcula |
|---|---|
| Contactos en tu base | Contactos activos. |
| Pueden recibir mensajes | Contactos con permiso y sin baja, y su porcentaje sobre el total. |
| Están en alguna automatización | Personas distintas que hoy están en la base de al menos una automatización activa o programada. |
| Pidieron no recibir más | Contactos con baja. |
| Las bases de tus automatizaciones | Una fila por base: nombre, cómo se arma en una línea, personas que hoy cumplen la regla y pueden recibir, cuántas tienen un envío en los próximos 7 días y qué automatización la usa. Debajo, cuántas personas están en dos bases o más. |
| Quiénes pueden recibir | Tres barras que suman el total: dieron permiso, no dieron permiso y pidieron la baja. |
| Con qué se arma una base | Texto fijo con los datos de la sección 6.1, en lenguaje simple. |

### 10.4 Próximos envíos (`imagenes/4-proximos-envios.png`)

| Elemento | Qué muestra y cómo se calcula |
|---|---|
| Salen hoy · Próximos 7 días | Envíos programados. El segundo lleva el texto «si nada cambia». |
| Límite diario de WhatsApp | Personas a contactar hoy sobre el nivel del número, con una barra, y la calidad del número. |
| Créditos de la semana | Envíos de 7 días por los créditos de cada mensaje. |
| Qué sale y a qué hora | Lista agrupada por día y ordenada por hora. Cada fila: hora, automatización, cantidad de personas, hasta dos nombres y «Ver quiénes». |
| Mensajes por día | Barras con el total por día, relativas al día con más envíos. Aviso de que es una previsión. |
| Corridos por el tope semanal | Cuántos envíos de esta semana se movieron más adelante. |
| ¿Qué le va a llegar a un cliente? | Buscador por nombre o teléfono. Muestra todos los envíos futuros de esa persona, ordenados por fecha. |

### 10.5 Historial (`imagenes/5-historial.png`)

| Elemento | Qué muestra y cómo se calcula |
|---|---|
| Enviados · Entregados · Leídos · Respondieron | Últimos 30 días, con el porcentaje sobre los enviados. |
| No salieron | Envíos que estaban programados y no se hicieron. |
| Por qué no salieron | Los que no salieron, agrupados por motivo. |
| Envíos únicos terminados | Una fila por envío único: fecha, enviados y porcentaje de respuesta. |
| Mensaje por mensaje | Una fila por envío, del más nuevo al más viejo: cuándo, persona, automatización y el último estado conocido. Filtros por automatización, resultado y fecha, y buscador de personas. |

Los filtros y los buscadores no cambian nada: solo eligen qué se ve.

### 10.6 Celular (`imagenes/7-celular.png`)

Una sola columna: los cuatro números de a dos, «Hoy salen N mensajes» y cada automatización como una tarjeta. Las pestañas se desplazan de costado.

## 11. Diseño

Seguí las imágenes como referencia de distribución y jerarquía, y **usá los tokens de color y tipografía que ya tiene la app**. Valores de las maquetas, solo como referencia:

| Elemento | Valor en la maqueta |
|---|---|
| Fondo de página | `#F6F5F2` |
| Tarjeta | `#FFFFFF`, borde `#E8E5E0`, radio 14 px, relleno 20 px |
| Texto | `#1C1917`; secundario `#57534E`; apagado `#6B665F` |
| Acento | `#BC4F1B`; fondo suave `#FBEEE6` |
| Estado Activa | fondo `#E7F1EA`, texto `#1B5E3A` |
| Estado Programada | fondo `#FBEEE6`, texto `#9A3F12` |
| Estados Espera a Meta, Entregado, Leído | fondo `#EEF0F3`, texto `#3A4654` |
| Estados No salió, Pidió la baja, Con problema | fondo `#FBE9E7`, texto `#9B2C1F` |
| Títulos | Fuente redondeada en peso 800 |
| Texto | Fuente del sistema, 14 px; etiquetas de 13 px |

- Los títulos hoy usan una fuente que solo existe en Mac. Cargá una fuente web redondeada equivalente (en las maquetas, Nunito).
- Todo estado lleva su texto: el color nunca es la única señal.
- Barras horizontales con el número al lado. Sin tortas ni líneas.
- Botones y enlaces reales, contraste de 4,5 a 1 como mínimo y zonas táctiles de 44 px.
- Español rioplatense con voseo, sin inglés ni jerga. Usá exactamente los nombres de este documento.
- En los listados se muestra el nombre de la persona, no su teléfono.

## 12. Estados de cada pantalla

- **Sin automatizaciones:** «Todavía no tenés automatizaciones. Pedile la primera a kapi en el chat.» Con tres ejemplos de pedido para copiar y el botón al Asistente.
- **Cargando:** el esqueleto de carga que ya usa la app.
- **Sin envíos próximos:** «No hay nada programado para los próximos 7 días.»
- **Error:** «No pudimos cargar este bloque» y un botón para reintentar. Un bloque con error no rompe los demás.
- **Automatización con problema:** el motivo en una línea y qué hacer, con un enlace al chat.

## 13. Permisos y seguridad

- Respetá los permisos existentes. Quien no puede ver contactos no ve nombres en estas pantallas.
- El Asistente actúa con los permisos del usuario que le habla. Solo quien puede enviar mensajes a clientes puede aprobar una automatización.
- Guardá quién pidió y quién aprobó cada automatización y cada cambio.
- Las bajas y el consentimiento no se pueden modificar desde el Asistente por pedido del dueño, salvo revertir una baja cuando la persona lo pidió.

## 14. Rendimiento

- El calendario de envíos se calcula en segundo plano. Las pantallas leen el calendario ya armado; nunca lo calculan al abrir.
- El conteo de una base tiene que responder en menos de dos segundos con 10.000 contactos, porque el Asistente lo usa en plena conversación.
- El proceso de envío tiene que ser seguro ante reinicios: usá la clave única de la sección 6.2 para no repetir.

## 15. Orden de trabajo

1. Investigación e informe (sección 4). Esperá mi OK.
2. La baja y su registro (pregunta 6).
3. El modelo de las cinco partes, los tipos y los estados.
4. El calendario de envíos, la regla de no ir hacia atrás, el tope semanal y la prioridad. Con pruebas.
5. El envío, con todas las revisiones previas y el registro.
6. El resultado: avisos de WhatsApp, respuestas y ramas.
7. Las herramientas del Asistente y la conversación.
8. Las pantallas, en este orden: Activas, Detalle, Próximos envíos, Bases, Historial.
9. Celular, estados vacíos, accesibilidad y textos.
10. Sacar el editor visual del menú, según lo que acordemos sobre los flujos existentes.

Mostrame el resultado al terminar cada paso. **No actives ninguna automatización contra clientes reales durante el desarrollo:** usá el número de prueba.

## 16. Criterios de aceptación

- [ ] El módulo no tiene ningún control que cree, edite, borre o pause una automatización.
- [ ] Una automatización se puede pedir, revisar y activar completa desde el chat, sin que el Asistente pida ningún identificador.
- [ ] Ante un pedido ambiguo, el Asistente pregunta si es una sola vez o de ahora en más.
- [ ] Nada se activa sin un OK explícito.
- [ ] Ningún mensaje sale sin permiso, con baja, fuera de horario, con un chat abierto con el equipo o por encima del tope semanal.
- [ ] La misma persona no recibe dos veces el mismo mensaje por el mismo motivo, aun reiniciando el proceso.
- [ ] Al activar una continua, no le llega a nadie cuya fecha ya pasó.
- [ ] Cuando a una persona le tocan dos mensajes, sale el de mayor prioridad y el otro se corre o se descarta según la regla.
- [ ] La baja funciona con palabra, con botón y con texto libre, y excluye a la persona de todo.
- [ ] Próximos envíos coincide con lo que efectivamente sale, salvo los cambios previstos: compras nuevas, respuestas y bajas.
- [ ] Cada envío, salga o no, queda en el Historial con su resultado o su motivo.
- [ ] «Compra» se calcula siempre con la fecha en que el chat se marcó como venta, y la pantalla lo dice.
- [ ] No aparece nada de agenda, de turnos ni de dinero.
- [ ] Las automatizaciones solo salen por la API oficial de WhatsApp.
- [ ] Las seis preguntas están respondidas y el plan B está aplicado donde corresponde.
- [ ] No queda texto en inglés, jerga interna ni mezcla de «tú» y «vos».

## 17. Qué me tenés que entregar al final

1. La respuesta a las seis preguntas, con el archivo o la tabla donde lo verificaste.
2. Qué partes del motor actual reutilizaste y cuáles reemplazaste.
3. Qué hiciste con los flujos que ya existían.
4. Todo lo que encontraste distinto a lo que dice este documento.
5. Un resumen de los archivos que cambiaste.
6. Lo que quedó pendiente y por qué.

**Una decisión que todavía no está tomada:** sumar un único botón «Pausar» en el detalle de cada automatización. No lo construyas. Dejá el estado «En pausa» funcionando desde el chat, que es lo que hace falta para agregarlo después.

## 18. Imágenes de referencia

| Archivo | Pantalla |
|---|---|
| `imagenes/1-activas.png` | Activas |
| `imagenes/2-detalle.png` | Detalle de una automatización |
| `imagenes/3-bases.png` | Bases |
| `imagenes/4-proximos-envios.png` | Próximos envíos |
| `imagenes/5-historial.png` | Historial |
| `imagenes/6-en-el-chat.png` | Cómo se pide en el chat |
| `imagenes/7-celular.png` | Activas en el celular |

Los números y los nombres de las imágenes son de ejemplo (una empresa de prueba). No los copies al código.
