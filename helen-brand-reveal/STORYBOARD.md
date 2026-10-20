# Helen — brand reveal · storyboard sincronizado

**Formato:** 1920×1080, 30 fps, 48,17 s (`index.html`) · reencuadre 1080×1920 (`vertical/index.html`)
**Tema:** `assets/bgm.mp3`, original y compuesto para esta pieza (funk/soul acústico, Fa mayor, 108 BPM, palmas en 2 y 4, sin voces). Generador: `tools/compose_bgm.py`.
**Grilla:** 1 beat = 0,556 s · 1 corchea = 0,278 s · 1 compás = 2,222 s. Todos los cortes caen en el tiempo 1 o 3 de un compás (bombo) y están redondeados al cuadro más cercano (30 fps).
`hyperframes beats` detecta 108,2 BPM y coincide con la partitura en ±20 ms en los compases 1–9 y 19–22. En los compases 10–18 se corre media corchea por el bombo sincopado, así que los cortes usan la partitura exacta del tema.

| # | Escena | Ventana | Compases | Qué cae en el golpe |
|---|---|---|---|---|
| 1 | Intro: el gorro se dibuja en trazo naranja sobre crema | 0,00–4,43 | 1–2 | Un tramo del trazo por golpe (bombo/palma); redoble en c2 t4: el relleno se completa en semicorcheas y el gorro vuela hacia la "e" |
| 2 | Logo reveal | 4,43–8,90 | 3–4 | **Crash c3:** el gorro aterriza sobre la "e" con un rebote; H‑e‑l‑e‑n suben en corcheas con overshoot. c4 t3: el fondo verde se abre detrás del logo |
| → | Zoom‑through (push en Z) por el ojo de la primera "e" | corte 8,90 | c5 t1 | La escena sale creciendo con blur de 18 px y el concepto entra creciendo |
| 3 | Concepto (verde) | 8,90–15,57 | 5–7 | "Mucho más que buena *comida.*" palabra por corchea, con máscara de línea; c6–7: cercana · cálida · casera · alegre · auténtica · familiar, una por beat; c7 t3: subrayado |
| → | Barrido de paneles de marca (naranja · beige · crema), diagonal, `expo.inOut` | corte 15,57 | c8 t1 | La pantalla queda cubierta justo en el golpe |
| 4 | Paleta | 15,57–20,00 | 8–9 | **Crash c8:** #FEA300, después #072305, #E3D8C5, #000000 y #F7F4ED, uno por golpe; los códigos giran como split‑flap y forman el bloque de la página 12. c9 t3½: el naranja se expande a pantalla completa |
| → | Match por color (el naranja pasa a ser el fondo) | corte 20,00 | c10 t1 | — |
| 5 | Tipografía (break del tema) | 20,00–22,23 | 10 | "Aa" gigante; el abecedario se revela en persiana, una línea por corchea |
| → | Barrido de paneles (verde · crema · verde) | corte 22,23 | c11 t1 | — |
| 6a | Patrón de gorros (naranja sobre verde) en diagonal infinita, plano 2.5D | 22,23–24,43 | 11 | **Crash c11** |
| 6b | Corte al patrón del wordmark sobre beige, misma velocidad diagonal | 24,43–28,90 | 12–13 | Corte en el bombo de c12; c12 t3: la grilla de íconos de la página 7 se arma celda por corchea (11 celdas) mientras la cámara la endereza |
| → | Zoom hacia la empanada de línea → tarjeta redondeada que se abre a pantalla completa | corte 28,90 | c14 t1 | El dibujo de la empanada se convierte en las empanadas reales |
| 7 | Comida y apetito (lo más enérgico) | 28,90–37,77 | 14–17 | Un revelado con máscara cada medio compás (wipe hacia la izquierda; iris circular en los punch‑ins), con el punto más rápido de cada transición en el golpe: empanadas, pizza, relleno, canelones en tarjeta, split, tríptico, queso, empanadas. "Hecho con amor, *como en casa.*" entra palabra por corchea y se mantiene entre los cortes |
| → | Barrido de paneles (naranja · verde · beige) | corte 37,77 | c18 t1 | — |
| 8 | Aplicaciones: muro bento de mockups (cartel, vidriera, laptop, caja de pizza, bolsa, menú, delantal) | 37,77–44,43 | 18–20 | Columnas con esquinas redondeadas que se deslizan en direcciones opuestas (parallax) sobre un plano 2.5D que se endereza; los mockups se abren con máscara en fusas. **c20:** la cámara vuela hacia la vidriera hasta llenar el cuadro (aterriza en c20 t3) |
| → | Iris verde que se abre desde el logo de la vidriera | corte 44,43 | c21 t1 | — |
| 9 | Cierre (verde) | 44,43–48,17 | 21–22 | **Crash c21:** el logo llega; "Catering a medida" en corcheas y "Sabores que hacen momentos especiales". Remates de la banda en c21 t4 y t4½ (el logo se recoge). **Último golpe c22 = 46,67 s:** pulso del logo + glow. Hold de 1,5 s mientras resuena el acorde final |

**Identidad:** el logo es el vector original del PDF (página 1), sin deformar ni recolorear; el isotipo solo se separa durante el dibujo de la intro y aterriza en su posición exacta. Los textos van en Fraunces (soft) como reemplazo de Recoleta. Colores: solo los cinco de la paleta.
**Terminación (v2, más moderna):** color plano limpio, sin grano ni viñeta. Texto con máscaras de línea (cada palabra sube desde atrás de su línea), easing `expo`, tarjetas con esquinas redondeadas.
**Reencuadre 9:16:** misma grilla de tiempos. La paleta usa el bloque exacto de la página 12, la grilla de íconos el 3×4 original y las tomas de comida van en ventana o en bandas apiladas (sin escalar las fotos de más).

Hoja visual: `storyboard/storyboard-16x9.jpg`.
