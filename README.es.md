<p align="center">
  <img src="assets/antigraf.png" width="160" height="160" alt="Icono de Antigraf: perfil grabado de una figura coronada de laurel sobre una teja verde">
</p>

<h1 align="center">Antigraf</h1>

<p align="center">
  <a href="README.md">English</a> ·
  <a href="README.ja.md">日本語</a> ·
  <a href="README.zh.md">简体中文</a> ·
  <a href="README.zh-hant.md">繁體中文</a> ·
  <a href="README.ko.md">한국어</a> ·
  <b>Español</b> ·
  <a href="README.fr.md">Français</a> ·
  <a href="README.vi.md">Tiếng Việt</a> ·
  <a href="README.pt.md">Português</a>
</p>

<p align="center">
  <b>Del griego <i>antígrafo</i> (αντίγραφο): una copia que responde al original.</b><br>
  Una habilidad de duplicado, clonado o estudio para agentes de código con IA.<br>
  Estudia una fuente, construye tu propia versión<br>
  y <b>demuestra</b> cuánto se acerca con comandos que puedes repetir.
</p>

<p align="center">
  <img alt="27 gates" src="https://img.shields.io/badge/gates-27-2d81ff?style=flat-square">
  <img alt="46 scripts, no installs" src="https://img.shields.io/badge/scripts-46%2C%20no%20installs-2d81ff?style=flat-square">
  <img alt="4 jobs" src="https://img.shields.io/badge/jobs-clone%20%C2%B7%20recreate%20%C2%B7%20improve%20%C2%B7%20study-2d81ff?style=flat-square">
  <img alt="Any model" src="https://img.shields.io/badge/works%20with-any%20model%20%C2%B7%20any%20harness-3a3a3a?style=flat-square">

  <img alt="Antigraf skill" src="https://img.shields.io/badge/skill-antigraf-1f883d?style=flat-square">
  <img alt="License: Apache-2.0 or MIT" src="https://img.shields.io/badge/license-Apache--2.0%20or%20MIT-2d81ff?style=flat-square">
</p>

<p align="center">
  <a href="#cómo-funciona">Cómo funciona</a> ·
<a href="#cuatro-trabajos">Cuatro trabajos</a> ·
<a href="#qué-lo-distingue">Qué lo distingue</a> ·
<a href="#dónde-está-cada-cosa">Dónde está cada cosa</a> ·
<a href="#instalación">Instalación</a> ·
<a href="#cómo-usarla">Cómo usarla</a> ·
<a href="#preguntas-que-hace-la-gente">Preguntas que hace la gente</a> ·
<a href="#estado-honesto">Estado honesto</a> ·
<a href="#licencia">Licencia</a> ·
<a href="#contribuir-y-seguridad">Contribuir y seguridad</a> ·
<a href="#la-línea-que-no-cruzamos">La línea que no cruzamos</a>
</p>

<br>

Antigraf vive dentro de tu agente como un paquete de instrucciones y un conjunto de herramientas
pequeñas. Recorre un sitio web, una app de móvil o un juego, apunta cada parte como un número,
construye tu propia copia y luego hace que ambos lados respondan a las mismas comprobaciones hasta
que nada falla y nada queda sin saber.

La idea no es decir "se ve igual". La idea es mostrar la fila que aún difiere, y el comando que lo
muestra.

<br>

<b>En palabras llanas:</b> Antigraf es una habilidad de replicación 1:1 para agentes de código con IA. Úsala para clonar un sitio web, copiar una app web o un juego, recrear un diseño como tuyo, o estudiar cómo está construido un sitio, de la interfaz al interior. Cubre todo el conjunto de páginas, no solo la portada: cada ruta, sección, control, estado abierto, animación, diseño de móvil, comportamiento sin conexión y escena 3D, cada uno comparado con el original y cada uno manteniendo el cierre al 100% hasta que coincida.

<table>
  <tr>
    <td width="25%" valign="top">
      <h3>Estudia cualquier cosa</h3>
      Páginas, pantallas, menús, controles y lo que hay detrás de un clic. Cada número lleva su origen, así que una suposición no puede hacerse pasar por una medición.
    </td>
    <td width="25%" valign="top">
      <h3>Construye la tuya</h3>
      Tu copia vive en tu proyecto, con la tecnología que elijas. Nada de la fuente viaja con ella salvo lo que tienes derecho a usar.
    </td>
    <td width="25%" valign="top">
      <h3>Comprobado, no adivinado</h3>
      27 comprobaciones corren en ambos lados cada ronda. Una que nunca corrió, o que respondió sin saber, bloquea el cierre y nunca cuenta como aprobada.
    </td>
    <td width="25%" valign="top">
      <h3>Listo para agentes</h3>
      Un archivo de habilidad y scripts simples, para que cualquier modelo y entorno mueva las mismas comprobaciones. Medir no necesita IA.
    </td>
  </tr>
</table>

<br>

## Cómo funciona

Señala una fuente, elige un trabajo, y avanza en cinco etapas:

1. **Estudiar:** recorrer la fuente, abrir lo que se esconde tras un clic y registrarlo como números.
2. **Planear:** una fila por página, sección, control, estado y ruta, cada una con la comprobación que la juzga.
3. **Construir:** escribe tu copia, primero la parte visible. Las piezas de servidor se nombran, nunca se copian.
4. **Comprobar:** las mismas comprobaciones corren en el original y en tu copia, ronda tras ronda.
5. **Refinar:** cada fila fallida vuelve como el siguiente mensaje de construcción, hasta que el cierre se complete.

## Cuatro trabajos

`/antigraf` hace una sola pregunta antes de que ocurra cualquier cosa.

| # | Trabajo | Qué hace |
|---|---|---|
| **1** | **Clonar** | Copia la fuente 1:1. No pregunta nada más y fija el objetivo en 100%. |
| **2** | **Recrear** | Copia como tu propia versión. Pregunta qué debe cambiar: colores, marca, iconos, textos. |
| **3** | **Mejorar** | Pone una fuente frente a tu proyecto, muestra qué hace mejor y termina con una lista corta de próximos pasos. |
| **4** | **Estudiar** | Solo lectura, nada se ejecuta, los secretos se tapan. Con qué está construido, de arriba abajo. |

Todo trabajo terminado acaba con una tabla honesta de 1 a 100 por área, qué frena cada área y tus
opciones para seguir.

## Qué lo distingue

| | **Antigraf** | Una habilidad de clonado típica |
|---|---|---|
| Dónde corre | Cualquier entorno y modelo. Solo librerías estándar de Python 3 y Node | Atada a un bucle de agente |
| Cómo decide "terminado" | 27 comprobaciones, cada una con su código de salida, todas en cada ronda | El modelo dice que se ve bien |
| "No comparado" | Siempre bloquea el cierre | Suele contarse como aprobado |
| Diferencias que aceptas | Solo tuyas, escritas por ti, nunca descartadas en silencio | No contemplado |
| Trabajos grandes | Se dividen en carriles, 3 ayudantes como máximo, regla de 60 minutos | Una corrida larga que se desvía poco a poco |
| Lo que afirma de sí misma | Un bloque de progreso generado de registros reales | Lo que diga la página |

Ningún puntaje global esconde qué fila falló. Las imágenes nunca aprueban nada por sí solas. Un modelo
más débil, o que no puede ver imágenes, nunca baja el listón: gasta menos y lo dice.

## Dónde está cada cosa

| Ruta | Qué es |
|---|---|
| `skills/antigraf/SKILL.md` | la habilidad misma: trabajos, etapas, niveles, espacio de trabajo, rondas, reglas |
| `skills/antigraf/README.md` | el documento completo: comprobaciones, tolerancias, progreso, disposición |
| `skills/antigraf/references/` | 12 guías: comprobaciones, planificación, fidelidad, escena, entrega, evidencia |
| `skills/antigraf/scripts/` | 46 herramientas: 39 Python, 7 de navegador, una lista de dispositivos |
| `assets/` | el icono, en 512 y 128 píxeles |

Lee esta página para saber qué promete. Lee el documento completo para la tolerancia exacta de cada comprobación.

## Instalación

Sin gestor de paquetes, sin `pip install`, sin cuenta. Es una carpeta de texto y scripts simples.

**Opción 1: copiar la carpeta (recomendada)**

```bash
git clone https://github.com/xC3FFF0E/Antigraf.git
```

Luego mueve `Antigraf/skills/antigraf/` a donde tu agente carga habilidades. La carpeta conserva su
nombre, mantiene `SKILL.md` arriba y viaja con sus carpetas `references/` y `scripts/`.

| Entorno | Dónde va la carpeta |
|---|---|
| La carpeta de habilidades de un proyecto | `<tu proyecto>/.claude/skills/antigraf/` |
| Todos los proyectos de la máquina | `~/.claude/skills/antigraf/` |
| Cualquier otro | la carpeta de habilidades que lee tu entorno |

**Opción 2: sin acceso a carpetas**

Pega el texto de `skills/antigraf/SKILL.md` en el campo de instrucciones personalizadas de tu agente.
La habilidad funciona solo con ese texto, sin las herramientas: las comprobaciones las hace el modelo
a mano, y la tabla final dice cuáles se hicieron así.

**Opción 3: sin agente**

Las herramientas son scripts normales.

```bash
cd skills/antigraf
python scripts/antigraf_mode.py --choose 1 --target https://example.com
```

Requisitos: **Python 3.8 o superior** (solo librería estándar), **Node 18 o superior** para las
herramientas de navegador, y un navegador basado en Chromium (Edge o Chrome) para recorrer y pulsar.
Cada pieza es opcional: si falta una, la habilidad baja un nivel y lo dice en la tabla final en vez de
adivinar.

## Cómo usarla

Una línea basta:

```
/antigraf https://example.com
```

Desde ahí corre en seis pasos.

| Paso | Qué ocurre |
|---|---|
| **1. Preguntar el trabajo** | 1 Clonar, 2 Recrear, 3 Mejorar, 4 Estudiar. Nada se copia hasta que respondas. |
| **2. Preguntar solo lo necesario** | Clonar no pregunta más. Recrear pregunta qué cambiar. Mejorar pide tu proyecto y lo que de verdad quieres. Estudiar pregunta la profundidad y qué parte importa. |
| **3. Escribir un plan que ves** | Como mucho siete pasos en tus palabras, uno marcado *se detiene aquí*, guardado en disco para que otro modelo retome el mismo paso. |
| **4. Estudiar, planear, construir, medir** | Las mismas comprobaciones corren en el original y en tu copia, ronda tras ronda. |
| **5. Cerrar huecos** | Cada fila fallida vuelve como el siguiente mensaje, y una fila que antes pasaba y ahora falla se marca como regresión. |
| **6. Mostrar la tabla** | Ocho áreas, cada una sobre 100, nombrando qué la frena. Luego tus opciones. |

La tabla final se ve así, y se calcula con la prueba registrada, nunca la escribe el modelo:

```
Area                    Score  pass  fail  unknown  What holds it
----------------------  -----  ----  ----  -------  -----------------------------------
Words & layout           100%     3     0        0
Design, icons             50%     1     1        0  failing: G4 contrast
Behaviour, flows           0%     0     0        5  not measured: G6, G7, G23, G24, G19
Phone & PWA                0%     0     1        1  failing: G14 tap targets
Motion & 3D               33%     1     0        2  not measured: G25, G26
Media & speed            100%     2     0        0
Sources, repairs          50%     2     0        2  not measured: G22, G16
Evidence, proof, pages    60%     3     1        1  failing: G12
```

Una comprobación que nunca corrió, o que respondió sin saber, cuenta como **cero**, así que el total
nunca puede adular la copia. Todo trabajo termina con esta tabla y tres ofertas: seguir empujando,
aceptar una diferencia como tuya con una renuncia firmada, o parar.

El cierre se completa en **100%** y solo entonces: cada fila aprobada, nada sin saber, ninguna
diferencia sin explicación. Hasta ese momento la tabla dice qué está abierto, por comprobación y por
fila, por ejemplo `G5 @1440 hero pad 16 12 -4 +-4`.

## Preguntas que hace la gente

**¿Puede copiar un sitio entero, o solo la portada?**
Recorre todos los enlaces del mismo sitio y captura cada página en tres anchos, móviles y tabletas. Lo que no alcanzó, las páginas que no recorrió y los controles que no pulsó, queda escrito como *no explorado* y mantiene el cierre. Siempre ves la cuenta: páginas encontradas frente a páginas recorridas.

**¿Me entrega el código fuente del original?**
No. Mide el original y tú construyes tu propia copia con tu tecnología. Lo que se entrega es tu código, no una copia del suyo.

**¿Funciona con un modelo que no ve imágenes?**
Sí. El diseño viaja como números: tamaños, colores, espaciado, tipografía, zonas pulsables. Las imágenes se usan para comparar, nunca para aprender, así que un modelo solo de texto igual construye desde medidas.

**¿Qué se niega a copiar?**
Lógica de servidor, credenciales, tokens de sesión, pagos y datos contables. Un campo con esa forma detiene la ejecución y se escribe en `HANDOVER.md`, para que sepas qué conectar tú.

**¿Cómo sé que de verdad funcionó?**
Cada comprobación deja un archivo con su propio código de salida, y la tabla final se calcula de esos registros. Una comprobación que nunca corrió, o que respondió sin saber, vale cero. El modelo no puede escribir su propia nota.

**¿Qué tipos de fuentes maneja?**
Sitios web y apps web de varias páginas, apps de móvil y comportamiento PWA, interfaces de streaming con reproductor, tiendas y catálogos, sitios de documentación, y escenas 3D con sus llamadas de dibujo, shaders y movimiento.

**¿Qué necesita para funcionar?**
Python 3.8 o superior solo con la librería estándar, Node 18 o superior para las herramientas de navegador, y un navegador Chromium. Sin instalar paquetes, sin cuenta, sin clave.

## Estado honesto

Aqui se muestran dos numeros distintos a proposito: la puntuacion es lo que las compuertas dicen de un par real original-copia, y lo probado es cuantos pares pasaron todas las compuertas. El segundo decide si la herramienta esta terminada.

**Capacidad medida, no declarada.** Todas las compuertas existen y se ejecutan. Lo que realmente paso se cuenta aparte de lo que puntuo un solo par.

<!-- ANTIGRAF:SCORE (written by scripts/antigraf_registry.py - do not edit by hand) -->

**Measured: 54.0% out of 100 - the three-page test pair (round 1)**

| Area | Score | Passing | Failing | Not measured | What holds it down |
|---|---|---|---|---|---|
| Words & layout | 100% | 3 | 0 | 0 | - |
| Design, icons | 100% | 2 | 0 | 0 | - |
| Behaviour, flows | 0% | 0 | 5 | 0 | failing: G6, G7, G23, G24, G19 |
| Phone & PWA | 0% | 0 | 2 | 0 | failing: G14, G18 |
| Motion & 3D | 33% | 1 | 2 | 0 | failing: G25, G26 |
| Media & speed | 100% | 2 | 0 | 0 | - |
| Sources, repairs | 50% | 2 | 1 | 1 | failing: G16 |
| Evidence, proof, pages | 60% | 3 | 2 | 0 | failing: G1, G12 |
| **Total** | **54.0%** | 13 | 13 | 1 | 14 gate(s) not passing |

The lock needs 100%: every gate passing, nothing unknown. A gate that never ran counts as zero, not as a pass.

<!-- /ANTIGRAF:SCORE -->

### Compuerta por compuerta

<!-- ANTIGRAF:PROGRESS (written by scripts/antigraf_registry.py - do not edit by hand) -->

**27 gates  ·  0 proven on a real original-to-copy pair  ·  1 measured so far**

| What the gates check | Gates | State | Where it was measured |
|---|---|---|---|
| Look: sections, words, colours, spacing | G2, G3, G4, G5 | measured | the three-page test pair round 1 |
| Icons and pictures, one partner each | G8, G17 | measured | the three-page test pair round 1 |
| Every page walked, planned and shipped | G11 | measured | the three-page test pair round 1 |
| Behaviour: pressed, and the same result | G7, G23, G24 | measured | the three-page test pair round 1 |
| States: hover, focus, open, empty, error | G6 | measured | the three-page test pair round 1 |
| Motion: durations, easings, scroll | G13 | measured | the three-page test pair round 1 |
| Phone, install and offline (PWA) | G9, G14, G18 | measured | the three-page test pair round 1 |
| Speed and weight budgets | G15 | measured | the three-page test pair round 1 |
| Logic: same input, same answer, no secrets | G19 | measured | the three-page test pair round 1 |
| Defects found, and the copy repaired | G20, G21 | measured | the three-page test pair round 1 |
| 3D scene read as numbers | G25 | measured | the three-page test pair round 1 |
| 3D motion compared frame by frame | G26 | measured | the three-page test pair round 1 |
| Server seams listed for you to hook up | G16 | measured | the three-page test pair round 1 |
| Evidence, proof and a frozen plan | G0, G1, G10, G12 | measured | the three-page test pair round 1 |

| Target | Family | Kind | Gates passed | Failed | Unknown | Verdict |
|---|---|---|---|---|---|---|
| the three-page test pair | unknown | round 1 | 13 of 27 | 13 | 0 | measured |

`proven` means every gate ran, passed, and nothing was unknown. `measured` means the gates ran and left a real exit code. Anything else is `not proven`, and is not being claimed.

<!-- /ANTIGRAF:PROGRESS -->



**La mitad que mide funciona. La mitad que construye aún no ha producido una copia que apruebe todas
las comprobaciones.**

El bloque de progreso del documento completo se escribe desde los registros en disco, nunca a mano.
Hoy dice 27 comprobaciones, 0 probadas en un par real original-copia. Preferimos mostrarte un cero y
la razón antes que un cien y una mentira.

## Licencia

Dos licencias, tú eliges: **Apache License 2.0** ([LICENSE-APACHE](LICENSE-APACHE)) o **MIT** ([LICENSE-MIT](LICENSE-MIT)). La versión corta, y lo que las licencias no cubren, está en [LICENSE.md](LICENSE.md). El icono y el nombre se quedan con el proyecto; un fork está bien siempre que diga que es un fork.

## Contribuir y seguridad

Cómo proponer un cambio, y la regla que importa (una comprobación nueva debe mostrarse fallando primero), está en [CONTRIBUTING.md](CONTRIBUTING.md). Cómo avisar de un fallo de seguridad en privado, y de qué te protege Antigraf y de qué no, está en [SECURITY.md](SECURITY.md).

## La línea que no cruzamos

Antigraf copia cómo se ve una página y cómo se comporta en tu navegador. **No** copia lógica de
servidor, credenciales, tokens de sesión, datos de pago o contables, y se detiene y rechaza cuando
encuentra un campo con esa forma. Esas piezas se escriben en `HANDOVER.md`, así sabes exactamente qué
conectar a tu propio backend, legalmente y en tus términos.

**No condonamos la piratería, compartir cuentas, evadir muros de pago, DRM o inicio de sesión,
extraer datos privados, ni reproducir el contenido, la marca o los recursos de otros sin permiso.**
Usa Antigraf con lo que es tuyo, lo que tiene licencia abierta, o lo que tienes permiso de estudiar.
Las imágenes, fuentes, logos y textos sin derechos se reemplazan por los tuyos, y una licencia que
nadie aclaró mantiene el cierre bloqueado hasta que la aclares o la cambies.

<br>

<p align="center">
  <img src="assets/antigraf-128.png" width="36" height="36" alt="Antigraf"><br>
  <sub>Antigraf. Una habilidad de duplicado, clonado o estudio para agentes de código con IA.</sub>
</p>
