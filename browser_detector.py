#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import platform
import subprocess
import xbmc
import xbmcaddon
from utils import Utils

class BrowserDetector:
    """Clase para detectar navegadores web instalados en el sistema"""
    
    def __init__(self):
        self.addon = xbmcaddon.Addon()
        self.system = platform.system().lower()
        self.addon_path = self.addon.getAddonInfo('path')
        self.icons_path = os.path.join(self.addon_path, 'resources', 'images')
        
        # Definir navegadores conocidos por sistema operativo
        self.browsers_config = {
            'windows': [
                {
                    'name': 'Google Chrome',
                    'executable': 'chrome.exe',
                    'paths': [
                        r'C:\Program Files\Google\Chrome\Application\chrome.exe',
                        r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
                        r'%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe'
                    ],
                    'description': 'Navegador web de Google',
                    'icon': 'chrome.png'
                },
                {
                    'name': 'Mozilla Firefox',
                    'executable': 'firefox.exe',
                    'paths': [
                        r'C:\Program Files\Mozilla Firefox\firefox.exe',
                        r'C:\Program Files (x86)\Mozilla Firefox\firefox.exe'
                    ],
                    'description': 'Navegador web de Mozilla',
                    'icon': 'firefox.png'
                },
                {
                    'name': 'Microsoft Edge',
                    'executable': 'msedge.exe',
                    'paths': [
                        r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
                        r'C:\Program Files\Microsoft\Edge\Application\msedge.exe'
                    ],
                    'description': 'Navegador web de Microsoft',
                    'icon': 'edge.png'
                },
                {
                    'name': 'Opera',
                    'executable': 'opera.exe',
                    'paths': [
                        r'C:\Users\%USERNAME%\AppData\Local\Programs\Opera\opera.exe',
                        r'C:\Program Files\Opera\opera.exe'
                    ],
                    'description': 'Navegador web Opera',
                    'icon': 'opera.png'
                },
                {
                    'name': 'Internet Explorer',
                    'executable': 'iexplore.exe',
                    'paths': [
                        r'C:\Program Files\Internet Explorer\iexplore.exe',
                        r'C:\Program Files (x86)\Internet Explorer\iexplore.exe'
                    ],
                    'description': 'Navegador web de Microsoft (legacy)',
                    'icon': 'ie.png'
                }
            ],
            'linux': [
                {
                    'name': 'Google Chrome',
                    'executable': 'google-chrome',
                    'paths': [
                        '/usr/bin/google-chrome',
                        '/usr/bin/google-chrome-stable',
                        '/opt/google/chrome/google-chrome',
                        '/snap/bin/google-chrome'
                    ],
                    'description': 'Navegador web de Google',
                    'icon': 'chrome.png'
                },
                {
                    'name': 'Chromium',
                    'executable': 'chromium-browser',
                    'paths': [
                        '/usr/bin/chromium-browser',
                        '/usr/bin/chromium',
                        '/snap/bin/chromium'
                    ],
                    'description': 'Navegador web de código abierto',
                    'icon': 'chromium.png'
                },
                {
                    'name': 'Mozilla Firefox',
                    'executable': 'firefox',
                    'paths': [
                        '/usr/bin/firefox',
                        '/usr/bin/firefox-esr',
                        '/opt/firefox/firefox',
                        '/snap/bin/firefox'
                    ],
                    'description': 'Navegador web de Mozilla',
                    'icon': 'firefox.png'
                },
                {
                    'name': 'Microsoft Edge',
                    'executable': 'microsoft-edge',
                    'paths': [
                        '/usr/bin/microsoft-edge',
                        '/usr/bin/microsoft-edge-stable',
                        '/opt/microsoft/msedge/microsoft-edge',
                        '/opt/microsoft/msedge/msedge'
                    ],
                    'description': 'Navegador web de Microsoft',
                    'icon': 'edge.png'
                },
                {
                    'name': 'Opera',
                    'executable': 'opera',
                    'paths': [
                        '/usr/bin/opera',
                        '/usr/bin/opera-stable',
                        '/opt/opera/opera'
                    ],
                    'description': 'Navegador web Opera',
                    'icon': 'opera.png'
                },
                {
                    'name': 'Brave Browser',
                    'executable': 'brave-browser',
                    'paths': [
                        '/usr/bin/brave-browser',
                        '/usr/bin/brave',
                        '/opt/brave.com/brave/brave-browser'
                    ],
                    'description': 'Navegador web Brave',
                    'icon': 'brave.png'
                },
                {
                    'name': 'Vivaldi',
                    'executable': 'vivaldi',
                    'paths': [
                        '/usr/bin/vivaldi',
                        '/usr/bin/vivaldi-stable',
                        '/opt/vivaldi/vivaldi'
                    ],
                    'description': 'Navegador web Vivaldi',
                    'icon': 'vivaldi.png'
                }
            ]
        }
    
    def _get_icon_path(self, icon_filename):
        """Obtener ruta completa del icono del navegador"""
        if not icon_filename:
            return 'DefaultProgram.png'
        
        # Ruta completa del icono
        icon_path = os.path.join(self.icons_path, icon_filename)
        
        # Verificar si el icono existe
        if os.path.exists(icon_path):
            return icon_path
        else:
            # Si no existe, usar icono por defecto
            Utils.log(f"Icono no encontrado: {icon_path}, usando por defecto", xbmc.LOGWARNING)
            return 'DefaultProgram.png'
    
    def get_installed_browsers(self):
        """Obtener lista de navegadores instalados en el sistema"""
        installed_browsers = []
        
        # Obtener configuración de navegadores para el sistema actual
        browsers = self.browsers_config.get(self.system, [])
        
        for browser in browsers:
            browser_path = self._find_browser_executable(browser)
            if browser_path:
                installed_browser = browser.copy()
                installed_browser['executable'] = browser_path
                installed_browser['icon'] = self._get_icon_path(browser.get('icon'))
                installed_browsers.append(installed_browser)
        
        # Intentar detectar navegadores adicionales
        additional_browsers = self._detect_additional_browsers()
        installed_browsers.extend(additional_browsers)
        
        Utils.log(f"Navegadores detectados: {len(installed_browsers)}")
        return installed_browsers
    
    def _find_browser_executable(self, browser):
        """Encontrar el ejecutable de un navegador específico"""
        for path in browser['paths']:
            # Expandir variables de entorno en Windows
            if self.system == 'windows':
                path = os.path.expandvars(path)
            
            if os.path.isfile(path) and os.access(path, os.X_OK):
                Utils.log(f"Navegador encontrado: {browser['name']} en {path}")
                return path
        
        # Intentar encontrar en PATH
        if self.system == 'linux':
            try:
                result = subprocess.run(['which', browser['executable']], 
                                     capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    path = result.stdout.strip()
                    if path:
                        Utils.log(f"Navegador encontrado en PATH: {browser['name']} en {path}")
                        return path
            except (subprocess.TimeoutExpired, subprocess.SubprocessError):
                pass
        
        return None
    
    def _detect_additional_browsers(self):
        """Detectar navegadores adicionales no incluidos en la configuración"""
        additional_browsers = []
        
        if self.system == 'linux':
            # Buscar en aplicaciones del sistema
            desktop_paths = [
                '/usr/share/applications/',
                '/usr/local/share/applications/',
                '~/.local/share/applications/'
            ]
            
            for desktop_path in desktop_paths:
                expanded_path = os.path.expanduser(desktop_path)
                if os.path.exists(expanded_path):
                    for filename in os.listdir(expanded_path):
                        if filename.endswith('.desktop'):
                            browser_info = self._parse_desktop_file(os.path.join(expanded_path, filename))
                            if browser_info:
                                additional_browsers.append(browser_info)
        
        return additional_browsers
    
    def _parse_desktop_file(self, desktop_file):
        """Parsear archivo .desktop para extraer información del navegador"""
        try:
            with open(desktop_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Buscar aplicaciones que parezcan navegadores
            browser_keywords = ['browser', 'web browser', 'internet', 'chrome', 'firefox', 'opera', 'safari', 'edge']
            # Excluir aplicaciones que NO son navegadores
            exclude_keywords = ['connector', 'extension', 'plugin', 'helper', 'manager', 'settings', 'preferences']
            
            name = None
            exec_command = None
            comment = None
            
            for line in content.split('\n'):
                line = line.strip()
                if line.startswith('Name='):
                    name = line.split('=', 1)[1]
                elif line.startswith('Exec='):
                    exec_command = line.split('=', 1)[1]
                elif line.startswith('Comment='):
                    comment = line.split('=', 1)[1]
            
            # Verificar si parece un navegador
            if name and exec_command:
                name_lower = name.lower()
                
                # Verificar que contiene palabras clave de navegador
                is_browser = any(keyword in name_lower for keyword in browser_keywords)
                
                # Verificar que NO contiene palabras clave excluidas
                is_excluded = any(keyword in name_lower for keyword in exclude_keywords)
                
                if is_browser and not is_excluded:
                    # Extraer el comando ejecutable
                    exec_parts = exec_command.split()
                    if exec_parts:
                        executable = exec_parts[0]
                        
                        # Verificar si el ejecutable existe
                        if os.path.isfile(executable) and os.access(executable, os.X_OK):
                            return {
                                'name': name,
                                'executable': executable,
                                'description': comment or f'Navegador web {name}',
                                'icon': 'DefaultProgram.png'
                            }
        
        except (IOError, UnicodeDecodeError):
            pass
        
        return None
    
    def launch_browser(self, browser_path, url=None):
        """Lanzar navegador con URL opcional"""
        try:
            command = [browser_path]
            
            if url:
                command.append(url)
            
            # Configurar el proceso según el sistema operativo
            if self.system == 'windows':
                # En Windows, usar subprocess con shell=True
                subprocess.Popen(command, shell=True)
            else:
                # En Linux, usar subprocess normal
                subprocess.Popen(command, 
                               stdout=subprocess.DEVNULL, 
                               stderr=subprocess.DEVNULL)
            
            Utils.log(f"Navegador lanzado: {browser_path} {url or ''}")
            return True
            
        except Exception as e:
            Utils.log(f"Error al lanzar navegador: {str(e)}", xbmc.LOGERROR)
            return False
    
    def get_default_browser(self):
        """Obtener el navegador predeterminado del sistema"""
        try:
            if self.system == 'windows':
                # En Windows, usar registro o comando
                import winreg
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                   r'Software\Microsoft\Windows\Shell\Associations\UrlAssociations\http\UserChoice')
                prog_id = winreg.QueryValueEx(key, 'ProgId')[0]
                winreg.CloseKey(key)
                return prog_id
            
            elif self.system == 'linux':
                # En Linux, usar xdg-settings
                result = subprocess.run(['xdg-settings', 'get', 'default-web-browser'],
                                     capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    return result.stdout.strip()
            
        except Exception as e:
            Utils.log(f"Error al obtener navegador predeterminado: {str(e)}", xbmc.LOGWARNING)
        
        return None