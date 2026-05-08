# 🦅 Nodos Biológicos Invisibles — ZMG
 
Detección de corredores de biodiversidad ocultos en la Zona Metropolitana de Guadalajara mediante K-Means clustering sobre datos de eBird.
 
**Pipeline:** API eBird → Java ETL → MySQL → Python K-Means → Mapa interactivo
 
---
 
## 📋 Requisitos previos
 
Antes de empezar, necesitas tener instalado:
 
| Herramienta | Versión mínima | Descarga |
|---|---|---|
| Java JDK | 17+ | https://adoptium.net |
| Apache Maven | 3.8+ | https://maven.apache.org/download.cgi |
| MySQL Community | 8.0+ | https://dev.mysql.com/downloads/mysql |
| Python | 3.10+ | https://www.python.org/downloads |
| Git | cualquiera | https://git-scm.com |
 
---
 
## ⚙️ Instalación paso a paso
 
### 1. Clonar el repositorio
 
```bash
git clone https://github.com/TU_USUARIO/nodos-biologicos.git
cd nodos-biologicos
```
 
### 2. Obtener la API Key de eBird (gratis, 2 minutos)
 
1. Entra a https://ebird.org/api/keygen
2. Inicia sesión (o crea cuenta gratis)
3. Copia la key que te generan
### 3. Configurar variables de entorno
 
Estas variables guardan tus credenciales sin hardcodearlas en el código.
 
**macOS / Linux** — agrega al final de tu `~/.zshrc` o `~/.bashrc`:
```bash
export EBIRD_API_KEY="pega_tu_key_aqui"
export DB_PASSWORD="tu_password_de_mysql"   # déjalo vacío si MySQL no tiene contraseña
```
Después ejecuta:
```bash
source ~/.zshrc   # o source ~/.bashrc
```
 
**Windows (PowerShell como administrador):**
```powershell
[System.Environment]::SetEnvironmentVariable("EBIRD_API_KEY","pega_tu_key_aqui","User")
[System.Environment]::SetEnvironmentVariable("DB_PASSWORD","tu_password_mysql","User")
```
Cierra y vuelve a abrir la terminal para que tome efecto.
 
**Verificar que funcionó:**
```bash
echo $EBIRD_API_KEY   # debe mostrar tu key
```
 
### 4. Crear la base de datos
 
Abre MySQL desde terminal:
```bash
mysql -u root -p
```
Luego ejecuta:
```sql
source schema.sql
```
O copia y pega el contenido de `schema.sql` directamente.
 
### 5. Instalar dependencias Java
 
```bash
mvn dependency:resolve
```
 
### 6. Configurar entorno Python
 
```bash
# Crear entorno virtual
python3 -m venv venv
 
# Activar
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
 
# Instalar dependencias
pip install -r requirements.txt
```
 
---
 
## 🚀 Ejecución del pipeline
 
Sigue estos pasos **en orden**:
 
### Paso 1 — ETL Java (descarga datos de eBird y los guarda en MySQL)
 
```bash
mvn compile
mvn exec:java -Dexec.mainClass="mx.zmg.Main"
```
 
Verás en la consola mensajes como:
```
📡 Fetching observaciones recientes MX-JAL...
📡 Fetching radio 50km desde Guadalajara...
📡 Fetching histórico: 2024-11-01
✅ Total registros únicos: 4832
[CARGAR] ✅ Total insertado: 4832 registros
```
 
### Paso 2 — K-Means clustering
 
```bash
# Asegúrate de tener el entorno virtual activo
source venv/bin/activate
 
python 01_kmeans.py
```
 
Se abrirá la gráfica `elbow_method.png`. Observa el "codo" de la curva y **ajusta la variable `K_OPTIMO`** en `01_kmeans.py` (línea ~45) según lo que veas. Luego vuelve a correr el script.
 
### Paso 3 — Análisis estadístico
 
```bash
python 02_estadistica.py
```
 
Genera `estadistica_por_zona.csv` y la gráfica de distribución de Poisson.
 
### Paso 4 — Mapa interactivo
 
```bash
python 03_mapa.py
```
 
Genera `nodos_biologicos_zmg.html`. Ábrelo en tu navegador para ver los nodos detectados.
 
---
 
## 📁 Estructura del proyecto
 
```
nodos-biologicos/
├── src/main/java/mx/zmg/
│   ├── Avistamiento.java           # Entidad principal
│   ├── EBirdAPIClient.java         # Cliente HTTP para la API de eBird
│   ├── ETLService.java             # Carga datos a MySQL en lotes
│   ├── DataAccumulatorService.java # Orquesta las llamadas a la API
│   └── Main.java                   # Punto de entrada
├── 01_kmeans.py                    # K-Means + Método del Codo
├── 02_estadistica.py               # Estadística descriptiva + Poisson
├── 03_mapa.py                      # Mapa Folium interactivo
├── schema.sql                      # Script de base de datos
├── requirements.txt                # Dependencias Python
├── pom.xml                         # Dependencias Java (Maven)
└── README.md
```
 
---
 
## 🔧 Solución de problemas frecuentes
 
**`EBIRD_API_KEY` no encontrada**
Asegúrate de haber cerrado y reabierto la terminal después de setear las variables. Verifica con `echo $EBIRD_API_KEY`.
 
**Error de conexión a MySQL**
Verifica que MySQL esté corriendo:
```bash
# macOS
brew services list | grep mysql
 
# Windows
Get-Service -Name MySQL*
```
 
**Pocos registros en K-Means (< 500)**
El Paso 1 puede haber fallado silenciosamente. Revisa la consola buscando errores de red. Puedes aumentar el rango de fechas históricas en `DataAccumulatorService.java`.
 
**`ModuleNotFoundError` en Python**
Asegúrate de tener el entorno virtual activado (`source venv/bin/activate`) antes de correr cualquier script Python.
 
---
 
## 📊 Outputs esperados
 
| Archivo | Descripción |
|---|---|
| `elbow_method.png` | Gráfica para elegir K óptimo |
| `poisson_zona_top.png` | Distribución de Poisson de la zona más activa |
| `estadistica_por_zona.csv` | Estadística descriptiva por clúster |
| `nodos_biologicos_zmg.html` | Mapa interactivo con los nodos detectados |
 
---
 
## 👥 Equipo
Proyecto desarrollado para [Martin, Ramses, nombre, nombre].