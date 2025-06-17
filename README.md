# Abridor Web - Plugin para Kodi

[![Version](https://img.shields.io/badge/version-1.1.2-blue.svg)](https://github.com/sapoclay/abridor-web)
[![Kodi Version](https://img.shields.io/badge/kodi-19%2B-green.svg)](https://kodi.tv)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux-lightgrey.svg)](https://github.com/sapoclay/abridor-web)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)

![abridor-web](https://github.com/user-attachments/assets/988c7af3-fe74-4035-9296-b9ca0e67cabb)

**Abridor Web** es un plugin para Kodi que permite detectar automáticamente navegadores web instalados en el sistema y abrirlos directamente desde la interfaz de Kodi. El plugin también incluye funcionalidades avanzadas de gestión de URLs, historial de navegación e importación de marcadores.

## 🚀 ¿Qué hace este plugin?

El plugin **Abridor Web** actúa como un puente entre Kodi y los navegadores web de tu sistema, ofreciendo:

- **Detección automática** de navegadores instalados en Windows y Linux
- **Lanzamiento directo** de navegadores desde Kodi con URLs personalizadas
- **Gestión completa** de URLs favoritas con estadísticas de uso
- **Historial de navegación** integrado con búsqueda y análisis
- **Importación de marcadores** desde Chrome, Chromium y Firefox
- **Interfaz multiidioma** en español e inglés

## ✨ Características principales

### 🌐 Detección inteligente de navegadores
- **Windows**: Chrome, Firefox, Edge, Opera, Internet Explorer
- **Linux**: Chrome, Chromium, Firefox, Opera, Brave, Vivaldi, Edge
- Búsqueda automática en rutas comunes del sistema
- Soporte para navegadores personalizados y portables
- Filtrado de falsos positivos y detección mediante archivos .desktop (Linux)

### 📱 Gestión avanzada de URLs
- Introducir y abrir URLs personalizadas al instante
- Guardar URLs favoritas con nombres descriptivos
- Sistema completo de edición y eliminación de URLs
- Contador de accesos y estadísticas detalladas de uso
- Respaldo automático y restauración de datos

### 📋 Historial de navegación integrado
- Registro automático de todas las URLs visitadas
- Visualización de historial reciente y URLs más visitadas
- Búsqueda avanzada en el historial de navegación
- Estadísticas detalladas de uso y patrones de navegación
- Limpieza automática configurable y manual del historial
- Exportación del historial a archivos externos

### 🔖 Importación de marcadores
- Importación completa desde Chrome/Chromium (formato JSON)
- Importación desde Firefox (base de datos SQLite)
- Interfaz de selección interactiva para elegir marcadores
- Integración automática con el sistema de URLs guardadas
- Soporte para múltiples perfiles de navegador

### ⚙️ Configuración profesional
- 6 categorías de configuración detalladas
- Navegador predeterminado configurable
- Soporte para navegadores personalizados con argumentos
- Validación automática de URLs con notificaciones
- Modo incógnito y opciones de privacidad
- Sistema de logging para depuración avanzada

### 🌍 Experiencia multiidioma
- Interfaz completamente localizada en español e inglés
- 185+ cadenas de texto traducidas
- Mensajes de error y notificaciones localizados
- Documentación en ambos idiomas

## 🛠️ ¿Cómo funciona?

### Flujo de funcionamiento

#### 1. **Detección de navegadores**
```python
# El sistema analiza el SO y busca navegadores en:
# Windows: Registro de Windows + rutas comunes
# Linux: Comandos which + archivos .desktop + rutas estándar

navegadores_detectados = detector.detect_browsers()
# Resultado: Lista de navegadores con nombre, ruta y icono
```

#### 2. **Gestión de URLs**
```python
# Sistema JSON para persistencia de datos
{
    "urls": [
        {
            "name": "Mi sitio favorito",
            "url": "https://ejemplo.com",
            "access_count": 15,
            "last_accessed": "2025-06-17 10:30:00"
        }
    ]
}
```

#### 3. **Lanzamiento de navegadores**
```python
# Ejecución segura con subprocess
subprocess.Popen([
    ruta_navegador,
    url_destino,
    *argumentos_adicionales
], shell=False)
```

#### 4. **Importación de marcadores**
- **Chrome/Chromium**: Lee el archivo `Bookmarks` (JSON)
- **Firefox**: Consulta la base de datos `places.sqlite`
- **Procesamiento**: Extrae URLs y nombres, los integra al sistema

### Componentes técnicos clave

#### `browser_detector.py` - Motor de detección
- **Windows**: Utiliza el registro de Windows y rutas predefinidas
- **Linux**: Combina comandos `which`, archivos `.desktop` y rutas estándar
- **Filtrado inteligente**: Elimina falsos positivos y duplicados
- **Iconos dinámicos**: Asigna iconos específicos a cada navegador detectado

#### `url_manager.py` - Gestión de datos
- **Persistencia JSON**: Almacena URLs de forma estructurada
- **Validación**: Verifica formato y accesibilidad de URLs
- **Estadísticas**: Cuenta accesos y rastrea patrones de uso
- **Respaldos automáticos**: Crea copias de seguridad programadas

#### `history_manager.py` - Historial inteligente
- **Registro automático**: Cada URL visitada se almacena con timestamp
- **Análisis de patrones**: Identifica URLs más visitadas y recientes
- **Búsqueda avanzada**: Permite encontrar URLs por texto parcial
- **Limpieza inteligente**: Elimina entradas antiguas basándose en configuración

#### `bookmark_manager.py` - Importación de marcadores
- **Chrome/Chromium**: Parser JSON nativo para archivos de marcadores
- **Firefox**: Conexión SQLite para leer la base de datos places.sqlite
- **Interfaz selectiva**: Permite elegir qué marcadores importar
- **Integración**: Convierte marcadores en URLs guardadas del sistema

## 📋 Requisitos del sistema

### Compatibilidad de Sistemas Operativos
- ✅ **Windows 10/11** - Detección vía registro y rutas comunes
- ✅ **Linux** (Ubuntu, Debian, Fedora, Arch, etc.) - Detección vía archivos .desktop
- ❌ **macOS** - No soportado en esta versión
- ❌ **Android** - No compatible con la arquitectura del plugin

### Requisitos de Kodi
- **Kodi 19.x (Matrix)** o superior
- **Python 3.0+** requerido por Kodi
- **Permisos de ejecución** para lanzar aplicaciones externas

### Navegadores Soportados

![navegadores-detectables](https://github.com/user-attachments/assets/bf48368b-f225-419a-b1ea-50d094bd871f)

| Sistema | Navegador | Detección | Estado |
|---------|-----------|-----------|--------|
| Windows | Google Chrome | ✅ Registro + Rutas | Completo |
| Windows | Mozilla Firefox | ✅ Registro + Rutas | Completo |
| Windows | Microsoft Edge | ✅ Registro + Rutas | Completo |
| Windows | Opera | ✅ Registro + Rutas | Completo |
| Windows | Internet Explorer | ✅ Registro | Completo |
| Linux | Google Chrome | ✅ which + .desktop | Completo |
| Linux | Chromium | ✅ which + .desktop | Completo |
| Linux | Mozilla Firefox | ✅ which + .desktop | Completo |
| Linux | Opera | ✅ which + .desktop | Completo |
| Linux | Brave Browser | ✅ which + .desktop | Completo |
| Linux | Vivaldi | ✅ which + .desktop | Completo |
| Linux | Microsoft Edge | ✅ which + .desktop | Completo |

## 📥 Instalación

### Método 1: Instalación desde ZIP (Recomendado)
1. **Descarga** el archivo `plugin.navegador.kodi-1.1.2.zip` desde [Releases](https://github.com/sapoclay/abridor-web/releases)
2. En Kodi, navega a **Complementos > Instalar desde archivo ZIP**
3. **Selecciona** el archivo ZIP descargado
4. **Confirma** la instalación cuando Kodi lo solicite
5. El plugin aparecerá en **Complementos > Complementos de programa**

### Método 2: Instalación manual (Desarrollo)
```bash
# Clona el repositorio
git clone https://github.com/sapoclay/abridor-web.git

# Copia el plugin al directorio de addons de Kodi
cp -r abridor-web ~/.kodi/addons/plugin.navegador.kodi

# Reinicia Kodi para que detecte el plugin
```

### Verificación de la instalación
1. Abre Kodi y ve a **Complementos > Complementos de programa**
2. Busca **"Abridor Web"** en la lista
3. Si aparece, la instalación fue exitosa

## 🚀 Guía de uso

### Primer uso
1. **Inicia** el plugin desde **Complementos > Complementos de programa > Abridor Web**
2. El plugin **detectará automáticamente** los navegadores instalados
3. Verás una lista de navegadores disponibles con sus iconos correspondientes

### Funcionalidades principales

#### 🌐 Abrir navegadores
```
Menú Principal > [Seleccionar Navegador]
```
- Haz clic en cualquier navegador detectado para abrirlo
- El navegador se ejecutará con su página de inicio predeterminada

#### 📱 URLs personalizadas
```
Menú Principal > "Introducir URL personalizada"
```
1. **Introduce** la URL que deseas abrir
2. **Selecciona** el navegador (o usa el predeterminado)
3. La URL se abrirá inmediatamente

#### 💾 Gestión de URLs guardadas
```
Menú Principal > "Gestionar URLs guardadas"
```
- **Ver URLs**: Lista todas las URLs guardadas con estadísticas
- **Editar**: Modifica nombre o URL de entradas existentes
- **Eliminar**: Borra URLs que ya no necesites
- **Estadísticas**: Ve cuántas veces has visitado cada URL

#### 📋 Historial de navegación
```
Menú Principal > "Gestionar historial"
```
- **Historial reciente**: URLs visitadas recientemente
- **Más visitadas**: URLs ordenadas por frecuencia de acceso
- **Buscar**: Encuentra URLs específicas en tu historial
- **Limpiar**: Elimina entradas antiguas del historial

#### 🔖 Importar marcadores
```
Menú Principal > "Gestionar marcadores" > "Importar marcadores"
```
1. **Selecciona** el navegador fuente (Chrome/Firefox)
2. **Elige** qué marcadores importar de la lista interactiva
3. Los marcadores se **integran automáticamente** como URLs guardadas

#### ⚙️ Configuración avanzada
```
Kodi > Complementos > Abridor Web > Configurar
```

**Categorías de configuración disponibles:**
- **Detección de navegadores**: Habilitar/deshabilitar navegadores específicos
- **Gestión de URLs**: Configurar respaldos automáticos y validación
- **Historial**: Configurar retención y limpieza automática
- **Marcadores**: Opciones de importación y sincronización
- **Navegador personalizado**: Agregar navegadores no detectados automáticamente
- **Opciones de URL**: Configurar modo incógnito y argumentos adicionales

### Navegación por menús

#### Menú principal
```
🌐 Abridor Web
├── 🔍 [Navegadores Detectados]
│   ├── 🟢 Google Chrome
│   ├── 🟠 Mozilla Firefox
│   ├── 🔵 Microsoft Edge
│   └── ⚪ [Otros navegadores...]
├── 📝 Introducir URL personalizada
├── 💾 Gestionar URLs guardadas
├── 📋 Gestionar historial
├── 🔖 Gestionar marcadores
├── 💾 Crear respaldo
├── 🔄 Restaurar respaldo
└── 🌐 Abrir repositorio de GitHub
```

#### Gestión de URLs
```
💾 URLs Guardadas
├── 📊 Ver estadísticas generales
├── 📝 Añadir nueva URL
├── 📂 [URLs guardadas]
│   ├── 📄 Mi sitio favorito (15 visitas)
│   ├── 📄 Portal de noticias (8 visitas)
│   └── 📄 [Más URLs...]
└── 🗑️ Limpiar URLs sin usar
```

## 🏗️ Arquitectura y desarrollo

### Estructura del proyecto
```
plugin.navegador.kodi/
├── 📄 addon.xml                    # Metadatos y configuración del plugin
├── 🎯 default.py                   # Punto de entrada principal
├── 🔍 browser_detector.py          # Motor de detección de navegadores
├── 📊 url_manager.py              # Sistema de gestión de URLs
├── 📋 history_manager.py          # Gestión de historial
├── 🔖 bookmark_manager.py         # Importación de marcadores
├── 💾 backup.py                   # Sistema de respaldos
├── 🔄 restore.py                  # Sistema de restauración
├── 🛠️ utils.py                   # Utilidades comunes
├── 🎨 logo.png                    # Icono del plugin
├── 🖼️ fanart.png                  # Imagen de fondo
└── 📁 resources/
    ├── ⚙️ settings.xml            # Configuración de ajustes
    ├── 🖼️ images/                 # Iconos de navegadores
    │   ├── chrome.png
    │   ├── firefox.png
    │   ├── edge.png
    │   └── [otros iconos...]
    └── 🌍 language/               # Traducciones
        ├── English/strings.po
        └── Spanish/strings.po
```

### Componentes principales

#### `default.py` - Coordinador principal
```python
# Funciones principales del controlador
def main_menu()           # Menú principal con fanart
def list_browsers()       # Lista navegadores detectados
def manage_urls()         # Gestión de URLs guardadas
def manage_history()      # Gestión de historial
def manage_bookmarks()    # Gestión de marcadores
def open_custom_url()     # Entrada de URL personalizada
```

#### `browser_detector.py` - Detección inteligente
```python
class BrowserDetector:
    def detect_browsers(self)                    # Detecta todos los navegadores
    def _detect_windows_browsers(self)           # Detección específica Windows
    def _detect_linux_browsers(self)             # Detección específica Linux
    def _check_desktop_files(self)               # Lee archivos .desktop (Linux)
    def launch_browser(self, browser, url)       # Lanza navegador con URL
```

#### `url_manager.py` - Gestión de datos
```python
class URLManager:
    def load_urls(self)                         # Carga URLs desde JSON
    def save_urls(self)                         # Guarda URLs a JSON
    def add_url(self, name, url)                # Añade nueva URL
    def edit_url(self, index, name, url)        # Edita URL existente
    def delete_url(self, index)                 # Elimina URL
    def increment_access_count(self, index)     # Cuenta accesos
```

### APIs y dependencias

#### APIs de Kodi utilizadas
```python
import xbmc                    # Logging y sistema
import xbmcgui                 # Interfaz de usuario
import xbmcplugin             # Funcionalidad de plugin
import xbmcaddon              # Configuración del addon
import xbmcvfs                # Sistema de archivos virtual
```

#### Librerías Python estándar
```python
import os                     # Operaciones del sistema
import sys                    # Sistema Python
import json                   # Manejo de datos JSON
import sqlite3                # Base de datos Firefox
import subprocess             # Ejecución de procesos
import urllib.parse           # Validación de URLs
import datetime               # Manejo de fechas
```

### Almacenamiento de datos

#### Estructura de Archivos de datos
```
~/.kodi/userdata/addon_data/plugin.navegador.kodi/
├── 📄 saved_urls.json         # URLs guardadas principales
├── 📄 history.json           # Historial de navegación
├── 📄 urls_backup_*.json     # Respaldos automáticos
└── 📁 cache/                 # Caché temporal
    └── 📄 detected_browsers.json
```

#### Formato de datos JSON
```json
{
  "version": "1.1.2",
  "urls": [
    {
      "name": "Mi sitio favorito",
      "url": "https://ejemplo.com",
      "access_count": 15,
      "last_accessed": "2025-06-17T10:30:00",
      "date_added": "2025-06-01T15:20:00"
    }
  ],
  "settings": {
    "auto_backup": true,
    "backup_frequency": "weekly"
  }
}
```

## 🔧 Solución de problemas

### Problemas comunes y soluciones

#### ❌ No se detectan navegadores
**Síntomas**: El plugin no muestra ningún navegador en la lista
**Causas posibles**:
- Navegadores no instalados correctamente
- Permisos insuficientes
- Rutas de instalación no estándar

**Soluciones**:
1. **Verifica la instalación** de los navegadores manualmente
2. **Revisa los logs** de Kodi en `Configuración > Sistema > Logging`
3. **Configura un navegador personalizado** en la configuración del plugin
4. **Ejecuta Kodi con permisos elevados** (temporal para diagnóstico)

```bash
# Linux: Verificar navegadores instalados
which google-chrome firefox chromium-browser opera brave-browser

# Windows: Verificar en el registro
reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe"
```

#### 🌐 Error al abrir URLs
**Síntomas**: El navegador no se abre o muestra error
**Causas posibles**:
- URL malformada o inválida
- Navegador corrupto o mal configurado
- Problemas de red

**Soluciones**:
1. **Valida la URL** manualmente en un navegador
2. **Prueba con un navegador diferente** desde el plugin
3. **Verifica la configuración de red** del sistema
4. **Revisa los argumentos del navegador** en configuración avanzada

#### 🔒 Problemas de permisos (Linux)
**Síntomas**: Error "Permiso denegado" al abrir navegadores
**Causas posibles**:
- Kodi sin permisos para ejecutar aplicaciones
- Navegadores sin permisos de ejecución
- Políticas de seguridad restrictivas

**Soluciones**:
```bash
# Dar permisos de ejecución a los navegadores
chmod +x /usr/bin/google-chrome
chmod +x /usr/bin/firefox

# Ejecutar Kodi desde terminal para ver errores
kodi

# Verificar permisos del directorio de Kodi
ls -la ~/.kodi/userdata/addon_data/plugin.navegador.kodi/
```

#### 📱 URLs no se guardan
**Síntomas**: Las URLs guardadas no persisten entre sesiones
**Causas posibles**:
- Permisos de escritura insuficientes
- Directorio de datos corrupto
- Espacio insuficiente en disco

**Soluciones**:
1. **Verifica permisos** del directorio de datos de Kodi
2. **Crea un respaldo manual** desde el plugin
3. **Limpia la caché** del plugin y reinicia Kodi
4. **Reinstala el plugin** si el problema persiste

### Diagnóstico avanzado

#### Activar logging detallado
```python
# En la configuración del plugin, habilita:
# "Registro de depuración" = Habilitado
# "Nivel de registro" = Debug

# Los logs aparecerán en:
# ~/.kodi/temp/kodi.log (Linux)
# %APPDATA%\Kodi\kodi.log (Windows)
```

#### Comandos de diagnóstico
```bash
# Linux: Verificar estado del sistema
ps aux | grep kodi
lsof -p $(pgrep kodi)
strace -p $(pgrep kodi) 2>&1 | grep -E "open|exec"

# Verificar integridad de archivos del plugin
find ~/.kodi/addons/plugin.navegador.kodi -name "*.py" -exec python3 -m py_compile {} \;
```

#### Archivo de diagnóstico automático
El plugin incluye una función de diagnóstico que puedes activar:
```
Plugin > Configuración > Avanzado > "Generar informe de diagnóstico"
```

Este informe incluye:
- Navegadores detectados
- Rutas del sistema
- Configuración actual
- Estados de archivos de datos
- Versiones de componentes

## 🤝 Contribuir al proyecto

### ¿Cómo puedes ayudar?

#### 🐛 Reportar bugs
1. **Revisa** si el bug ya fue reportado en [Issues](https://github.com/sapoclay/abridor-web/issues)
2. **Crea un nuevo issue** con:
   - Descripción detallada del problema
   - Pasos para reproducir el bug
   - Información del sistema (OS, versión de Kodi)
   - Logs relevantes del plugin

#### 💡 Sugerir mejoras
- **Ideas de nuevas funcionalidades**
- **Mejoras de interfaz de usuario**
- **Optimizaciones de rendimiento**
- **Soporte para nuevos navegadores**

#### 🔧 Contribuir con código
```bash
# 1. Fork del repositorio
git clone https://github.com/TU_USUARIO/abridor-web.git
cd abridor-web

# 2. Crear rama para nueva funcionalidad
git checkout -b feature/nueva-funcionalidad

# 3. Realizar cambios
# ... editar código ...

# 4. Commit con mensaje descriptivo
git add .
git commit -m "Añadir soporte para navegador X"

# 5. Push y crear Pull Request
git push origin feature/nueva-funcionalidad
```

#### 🌍 Traducciones
**Idiomas necesarios**:
- Francés (fr)
- Alemán (de)
- Italiano (it)
- Portugués (pt)
- Ruso (ru)

**Proceso**:
1. Copia `resources/language/English/strings.po`
2. Traduce las cadenas de texto
3. Crea una carpeta con el código del idioma
4. Envía un Pull Request

### Estándares de desarrollo

#### Estilo de código Python
```python
# Seguir PEP 8
# Documentación en español para funciones principales
# Logging estructurado

def detectar_navegadores(self):
    """
    Detecta navegadores instalados en el sistema.
    
    Returns:
        list: Lista de diccionarios con información de navegadores
    """
    xbmc.log("[Abridor Web] Iniciando detección de navegadores", xbmc.LOGINFO)
    # ... implementación ...
```

#### Estructura de commits
```
tipo(scope): descripción breve

descripción detallada del cambio realizado

Fixes #numero_issue
```

**Tipos de commit**:
- `feat`: Nueva funcionalidad
- `fix`: Corrección de bug
- `docs`: Cambios en documentación
- `style`: Cambios de formato/estilo
- `refactor`: Refactorización de código
- `test`: Añadir o modificar tests

### Desarrollador 
**EntrUnosYCeros**
- 📧 Email: [contacto disponible en GitHub]
- 🌐 GitHub: [@sapoclay](https://github.com/sapoclay)
- 💬 Blog: [Entre Unos y Ceros](https://entreunosyceros.net)

### Tecnologías utilizadas
- **Kodi API** - Framework de medios de código abierto
- **Python 3** - Lenguaje de programación principal
- **SQLite** - Base de datos para importación de marcadores Firefox
- **JSON** - Formato de almacenamiento de datos
- **GNU gettext** - Sistema de internacionalización

---
<div align="center">

**Abridor Web** - Llevando la web a tu experiencia Kodi - **entreunosyceros.net**

</div>
