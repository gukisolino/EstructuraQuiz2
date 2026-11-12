# Un día en el parque

Aplicación de escritorio con interfaz gráfica (**tkinter**) que simula una visita a un parque de diversiones. Cada atracción sirve para practicar un concepto distinto de **Estructuras de Datos**, y todo se ve animado en pantalla.

Solo usa la librería estándar de Python: no hay que instalar nada extra.

## Requisitos

- Python 3.8 o superior, con **tkinter** incluido.
  - Windows y macOS (instalador de python.org): ya viene incluido.
  - macOS con Homebrew: `brew install python-tk`
  - Ubuntu/Debian: `sudo apt install python3-tk`

## Cómo ejecutarlo

```bash
python3 Parque_De_Diversiones.py
```

Se abre una ventana de 900 × 600 con un menú de cuatro atracciones. Cada pantalla tiene un botón **< Menú** para volver.

## Las atracciones

| Atracción | Concepto | Idea |
|---|---|---|
| Montaña rusa | **Cola** (FIFO) + recursión | El primero en llegar a la fila es el primero en subir al carro. |
| Reclamos | **Pila** (LIFO) | El último reclamo registrado es el primero en deshacerse. |
| Fuegos artificiales | **Recursividad** | Cada explosión nace de otra explosión más pequeña. |
| Rueda de Chicago | **Lista circular enlazada** | El último nodo apunta de nuevo al primero. |

### 1. Montaña rusa (cola)

- **Llega una persona:** se forma al final de la fila (`encolar`).
- **Llegan 3 personas:** llegan varias seguidas, una tras otra (recursivo).
- **Subir carro:** las primeras 3 de la fila (el frente) suben y el carro recorre los rieles (`desencolar`). Sube despacio y baja rápido, según la pendiente.
- Abajo se dibujan los nodos reales de la cola con los punteros `frente` y `final`.
- La fila admite hasta 6 personas; se muestra el total de visitantes y de viajes.

### 2. Registro de reclamos (pila)

- Escribí un reclamo (o usá una idea rápida) y presioná **Registrar reclamo**: cae encima de la pila (`apilar`).
- **Deshacer el último:** saca el reclamo del tope (`desapilar`).
- La pila admite hasta 8 reclamos y marca cuál es el **TOPE**.

### 3. Fuegos artificiales (recursividad)

- **Iniciar cierre del parque:** cuenta regresiva y un show de 6 cohetes. El primero explota con profundidad 2 y los demás con profundidad aleatoria entre 2 y 3.
- **Botones 1-4:** eligen la profundidad de la recursión. Un clic en el cielo lanza un cohete con esa profundidad.
- Cada nivel de la explosión tiene su color y aparece un instante después del anterior. El punto de la punta de cada chispa es donde nace la siguiente llamada recursiva.
- Funciones recursivas: `cuenta_regresiva`, `espectaculo`, `subir_cohete` y `explosion`. Todas tienen **caso base** y **caso recursivo**, y están marcadas en el código.

### 4. Rueda de Chicago (lista circular)

- **Subir persona / Bajar persona:** operan sobre la cabina que está en el andén (el nodo `actual`).
- **Girar un paso:** la rueda avanza una cabina (`actual = actual.siguiente`).
- **Dar una vuelta completa:** gira 8 veces seguidas (recursivo) y `actual` vuelve al nodo de salida.
- Abajo se dibujan los 8 nodos; la etiqueta `actual` salta de nodo en nodo y, al llegar al último, vuelve al primero.

## Estructuras de datos del proyecto

Todas están hechas **a mano con nodos enlazados**, sin usar listas de Python como estructura principal.

| Clase | Punteros | Operaciones |
|---|---|---|
| `Nodo` | `dato`, `siguiente` | Eslabón base de todas las estructuras. |
| `Cola` | `frente`, `final` | `encolar`, `desencolar`, `esta_vacia`, `recorrer` |
| `Pila` | `tope` | `apilar`, `desapilar`, `esta_vacia`, `recorrer` |
| `ListaCircular` | `cabeza`, `ultimo`, `actual` | `agregar`, `girar`, `recorrer` |

En `ListaCircular` el último nodo apunta a la cabeza, así que nunca hay `None`. Por eso no se puede recorrer con `while nodo:` (sería infinito): se recorre exactamente `tamano` veces.

## Cómo está organizado el código

Todo está en un solo archivo, `Parque_De_Diversiones.py`:

1. **Estructuras de datos:** `Nodo`, `Cola`, `Pila`, `ListaCircular`.
2. **Utilidades de dibujo:** `rect_redondo`, `boton`, `persona`.
3. **`Pantalla`:** clase base con el canvas, la barra superior, la barra de mensajes y `animar`.
4. **Pantallas:** `MontanaRusa`, `Reclamos`, `Fuegos`, `RuedaChicago`.
5. **Menú y aplicación:** lista `PANTALLAS`, `Menu` y `App`.

Para encontrar cada concepto, buscá estas marcas en el código:

```
<<< COLA    <<< PILA    <<< LISTA CIRCULAR    <<< RECURSIÓN
```

Cada pantalla abre con un bloque **FUNCIONALIDAD** (qué hace) y otro **CONCEPTOS** (qué conceptos usa).

## Cómo agregar una atracción nueva

1. Crear una clase que herede de `Pantalla` e implemente `construir()` (y opcionalmente `dibujar_fondo()`).
2. Agregar un diccionario nuevo a la lista `PANTALLAS`, al final del archivo, con `titulo`, `estructura`, `color`, `clase` y `descr`.

El menú genera la tarjeta automáticamente.
