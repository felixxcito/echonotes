**[Nombre Apellido] [Cédula]**

**[Nombre Apellido] [Cédula]**

# Unidad V - Taller de Sistemas de Información

**Caso de estudio: EchoNotes, sistema de transcripción musical automática**

Las cinco preguntas del taller se responden tomando como caso el desarrollo de EchoNotes, una aplicación web y de línea de comandos que convierte grabaciones de audio en MIDI, partituras y tablaturas.

## 1. Análisis de la Fase Crítica en el Ciclo de Vida. Caso: Una escuela de música encarga EchoNotes siguiendo el ciclo de vida clásico (en cascada). En la fase de implementación se instala el sistema y se capacita a los docentes. A la semana surgen quejas: la interfaz está en inglés y al buscar "guitarra" en el selector de instrumentos no aparece nada; las partituras de los alumnos, que graban sin metrónomo, salen con barras de compás incorrectas; y desde el celular la pantalla de transcripción es incómoda de usar. Pregunta: ¿En qué fase del ciclo de vida clásico se cometió el error fundamental? Justifica qué actividades de esa fase no se realizaron correctamente, cómo impactó las fases posteriores y propón una alternativa al modelo en cascada.

El error fundamental se cometió en la fase de Análisis de Requerimientos, aunque los síntomas aparecieron en la implementación. En esa fase no se estudió el contexto real de uso: no se entrevistó a los docentes ni se observó cómo trabajan en clase, por lo que no se registró que los usuarios hablan español y buscan los instrumentos por su nombre en español, que los alumnos graban sin metrónomo y que muchos usan el teléfono. Tampoco se validaron prototipos de pantalla con los usuarios finales antes de programar.

En cascada cada fase se construye sobre la anterior y no hay retroalimentación hacia atrás: el diseño definió una interfaz solo en inglés y pensada para escritorio; la programación implementó el selector de instrumentos con identificadores en inglés; y las pruebas verificaron que la transcripción funcionara técnicamente, pero no con grabaciones reales de alumnos ni en pantallas pequeñas. El resultado fue un sistema técnicamente correcto pero inadecuado para su contexto, detectado cuando corregirlo era más caro.

Como alternativa se recomienda un modelo iterativo e incremental con prototipos evolutivos. Así se hizo en el desarrollo de EchoNotes: primero se obtuvo una versión funcional con la pista de ejemplo, se probó visualmente en escritorio y en ancho de teléfono (375 px), y en iteraciones sucesivas se tradujo la interfaz, se agregó la búsqueda de instrumentos en español tolerante a tildes y errores, y se documentó la recomendación de grabar con tempo estable. Cada incremento se valida con usuarios antes de continuar.

## 2. Identificación de Requerimientos Funcionales y No Funcionales. Caso: En la reunión de levantamiento de requisitos, la coordinadora de la escuela de música dice: "Quiero que los profesores suban una grabación y el sistema les diga qué toca cada instrumento; que puedan elegir los instrumentos si ya los conocen, escucharlo y descargar la partitura en PDF y el MIDI. Tiene que ser rápido, que se vea el avance, que funcione en el celular, que no se caiga si dos profesores lo usan a la vez y que sea fácil para cualquiera." Pregunta: Identifica y clasifica al menos tres Requerimientos Funcionales y tres No Funcionales, redactando una especificación técnica y medible para cada uno.

**Requerimientos Funcionales:**

1. RF-01 Carga de audio: El sistema debe permitir cargar archivos de audio en formato MP3, WAV, FLAC, OGG, M4A, AAC, AIFF u Opus mediante un selector de archivos o arrastrando el archivo a la página, y debe rechazar con un mensaje descriptivo (respuesta HTTP 400) los archivos que no pueda decodificar.
2. RF-02 Transcripción por instrumento: El sistema debe generar, para cada nota detectada, un evento con su altura MIDI (0 a 127), su tiempo de inicio y de fin en segundos y su instrumento (uno de los 35 grupos soportados), y mostrarlo en el piano roll a medida que se transcribe.
3. RF-03 Restricción de instrumentos: El sistema debe permitir que el usuario indique los instrumentos presentes en la pista; cuando lo haga, no debe generar notas de ningún instrumento no indicado y debe marcar como "no detectado" los instrumentos indicados que no aparezcan en el resultado.
4. RF-04 Exportación: El sistema debe permitir descargar la transcripción como archivo MIDI, como audio WAV (solo síntesis o estéreo con el original) y como un archivo ZIP con la partitura en MusicXML, la partitura completa en PDF, un PDF por instrumento y una tablatura por cada instrumento de trastes.

**Requerimientos No Funcionales:**

1. RNF-01 Rendimiento y retroalimentación: El sistema deberá mostrar las primeras notas en pantalla en menos de 10 segundos desde que el servidor acepta el archivo (equipo con GPU y modelo medium) y deberá actualizar la barra de progreso y el tiempo restante estimado al menos una vez por cada fragmento de 5 segundos de audio procesado.
2. RNF-02 Concurrencia: El servidor deberá procesar una transcripción a la vez; ante una solicitud simultánea deberá responder con el código HTTP 503 en menos de 1 segundo, y la interfaz deberá reintentar automáticamente mostrando una cuenta regresiva, sin que el servidor se bloquee ni pierda la transcripción en curso.
3. RNF-03 Usabilidad y accesibilidad: La interfaz deberá estar completamente en español, funcionar sin desplazamiento horizontal en pantallas desde 375 píxeles de ancho, tener un contraste de texto mínimo de 4,5:1 (WCAG 2.1 nivel AA) y permitir transcribir la pista de ejemplo con un máximo de 2 clics.
4. RNF-04 Portabilidad: El sistema deberá ejecutarse en Linux, macOS y Windows con Python 3.10 a 3.12, y también como contenedor Docker, sin cambios en el código.
5. RNF-05 Privacidad y licencias: El sistema no deberá almacenar el audio subido una vez terminada la transcripción y deberá usarse solo con fines no comerciales, de acuerdo con la licencia CC BY-NC 4.0 de los pesos del modelo.

## 3. Justificación del Modelo de Desarrollo. Caso: El equipo de EchoNotes tiene 15 semanas para el proyecto. La base técnica (el modelo de transcripción) ya existe, pero no se sabe qué funcionalidades valorarán más los músicos y docentes: un historial de transcripciones, cuentas de usuario, un editor para corregir notas o la detección de acordes. Se quiere tener pronto una versión usable y mejorarla según la opinión de los usuarios. Pregunta: ¿Qué modelo o metodología de desarrollo es el más adecuado? Explica dos características que se alineen con las necesidades del proyecto y contrasta con una desventaja del ciclo de vida clásico en este caso.

El modelo más adecuado es una metodología Ágil, específicamente Scrum, con sprints de una semana que coinciden con las 15 semanas del cronograma de implementación del proyecto.

Primera característica: la entrega incremental de valor. En lugar de esperar a tener todas las funcionalidades, se entrega primero un producto mínimo viable (EchoNotes renombrado, con tema claro, en español y documentado, semanas 1 a 7) y luego se agregan incrementos como el despliegue en servidor, el historial o el editor de notas. Los usuarios pueden usar el sistema desde las primeras semanas.

Segunda característica: la adaptación al cambio mediante retroalimentación continua. Al final de cada sprint se hace una revisión con docentes y músicos, y el Product Backlog se reordena según lo que pidan. Si los docentes valoran más corregir notas que tener cuentas de usuario, el editor de notas sube de prioridad sin afectar lo ya entregado.

En contraste, el ciclo de vida en cascada exigiría definir y congelar todos los requerimientos al inicio, cuando todavía no se sabe qué funcionalidades serán útiles, y no habría producto que mostrar hasta el final de las 15 semanas. El riesgo sería invertir el tiempo del semestre en funcionalidades que los usuarios no valoran y descubrirlo cuando ya no queda tiempo para corregir el rumbo.

## 4. Especificación Funcional Detallada a partir de un Problema. Caso: Hoy, para obtener la partitura de una canción, un profesor debe escucharla muchas veces y escribir las notas a mano, lo que le toma horas. Con EchoNotes se quiere automatizar este proceso. Pregunta: Redacta la especificación funcional del caso de uso "Transcribir audio a partitura", incluyendo actores, precondiciones, flujo básico, flujos alternativos y poscondiciones.

Caso de uso: CU-01 Transcribir audio a partitura.

**Actores:**

Actor principal: el Usuario (músico, docente o estudiante), que inicia el proceso desde la interfaz web. Actores secundarios: el Servidor EchoNotes con el modelo de transcripción, que procesa el audio; MuseScore, sistema externo que genera las partituras y tablaturas; y HuggingFace, proveedor de los pesos del modelo, que interviene solo al iniciar el servidor por primera vez.

**Precondiciones:**

El servidor de EchoNotes está iniciado y el modelo está cargado en memoria. MuseScore 4 o superior está instalado en el servidor (necesario para los PDF). El usuario dispone de un archivo de audio en un formato soportado. El navegador del usuario tiene conexión con el servidor.

**Flujo básico:**

1. El usuario abre la aplicación; el sistema verifica que el servidor esté disponible y carga la lista de instrumentos.
2. El usuario selecciona o arrastra un archivo de audio; el sistema muestra el nombre del archivo.
3. Opcionalmente, el usuario indica los instrumentos presentes en la pista.
4. El usuario presiona "Transcribir".
5. El sistema decodifica el audio, reserva el turno de procesamiento y muestra la vista de transcripción.
6. El modelo procesa el audio en fragmentos de 5 segundos y envía cada nota al navegador en tiempo real; el sistema la dibuja en el piano roll y actualiza el progreso.
7. Al terminar, el sistema detecta el tempo y el compás, genera el MIDI ajustado a la cuadrícula de pulsos, habilita el botón "Descargar" y libera el turno de procesamiento.
8. El usuario elige "Descargar" y luego "Partituras".
9. El sistema envía el MIDI a MuseScore, que genera el MusicXML, la partitura completa, un PDF por instrumento y las tablaturas, y devuelve todo en un archivo ZIP.
10. El sistema muestra la lista de archivos generados y el usuario descarga los que necesita o todos juntos.

**Flujos alternativos:**

A1 - Servidor ocupado (paso 5): si otro usuario está transcribiendo, el servidor responde HTTP 503; el sistema muestra "Servidor ocupado, reintentando en N s" y reintenta automáticamente. El usuario puede presionar "Cancelar" para desistir.

A2 - Archivo inválido (paso 5): si el audio no se puede decodificar, el sistema vuelve a la pantalla de bienvenida con un mensaje de error en rojo y el usuario puede elegir otro archivo.

A3 - Instrumento no detectado (paso 6): si un instrumento indicado por el usuario no aparece en el audio, el sistema lo muestra tachado con la etiqueta "no detectado".

A4 - Sin tempo estable (paso 7): si no se encuentra un pulso estable, el sistema genera el MIDI sin cuantizar y, en el paso 10, advierte que las barras de compás son aproximadas y que la partitura puede ser difícil de leer.

A5 - MuseScore no disponible (paso 9): si MuseScore no está instalado, el servidor responde HTTP 503 con instrucciones de instalación; el usuario conserva la opción de descargar el MIDI y el audio WAV.

**Poscondiciones:**

El usuario obtiene la transcripción en MIDI y las partituras en PDF y MusicXML (y tablaturas cuando corresponde). El audio subido no queda almacenado en el servidor. El turno de procesamiento queda libre para otro usuario.

## 5. Gestión del Cambio en la Fase de Implementación. Caso: Un conservatorio con muchos años de tradición decide incorporar EchoNotes en sus clases. El sistema funciona correctamente y pasó todas las pruebas, pero varios profesores con larga trayectoria se resisten a usarlo: dicen que el dictado musical se aprende transcribiendo a oído, desconfían de la precisión de la herramienta y sienten que el sistema los hace prescindibles. Pregunta: ¿A qué fase del ciclo de vida corresponde este problema? Más allá de la capacitación técnica, propón dos estrategias concretas que aborden las preocupaciones humanas y culturales.

Es un problema típico de la fase de Implementación, en particular de la gestión del cambio organizacional. Implementar no consiste solo en instalar el sistema y capacitar sobre su uso, sino en lograr que las personas lo adopten; aquí falló la dimensión humana, no la técnica.

Primera estrategia: involucrar a los profesores como co-diseñadores y "usuarios campeones". Se les invita a definir cómo se usará EchoNotes en clase, por ejemplo como herramienta de verificación: el alumno transcribe a oído y luego compara su trabajo con el resultado del sistema, lo que refuerza el entrenamiento auditivo en lugar de reemplazarlo. Los profesores más reconocidos lideran un piloto en su cátedra y comparten su experiencia con sus colegas. Así la herramienta se percibe como propia y no como una imposición.

Segunda estrategia: comunicar con honestidad el propósito y los límites del sistema y hacer una adopción gradual. En reuniones abiertas se explica que EchoNotes ahorra el trabajo mecánico de pasar notas a limpio, pero que no es perfecto: comete errores, no detecta acordes y su partitura necesita la revisión de un músico experto, de modo que el criterio del profesor sigue siendo indispensable. El uso empieza siendo voluntario y convive con el método tradicional durante un periodo, y se reconocen públicamente los aportes de quienes proponen mejoras. Esto reduce el temor a ser reemplazados y construye confianza con evidencia.
