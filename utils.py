#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import xbmc
import xbmcgui
import xbmcaddon

class Utils:
    """Clase de utilidades para el plugin"""
    
    @staticmethod
    def log(message, level=xbmc.LOGDEBUG):
        """Escribir mensaje en el log de Kodi"""
        addon = xbmcaddon.Addon()
        addon_name = addon.getAddonInfo('name')
        xbmc.log(f"[{addon_name}] {message}", level)
    
    @staticmethod
    def show_notification(title, message, icon=xbmcgui.NOTIFICATION_INFO, time=5000):
        """Mostrar notificación en Kodi"""
        xbmcgui.Dialog().notification(title, message, icon, time)
    
    @staticmethod
    def show_dialog(title, message):
        """Mostrar diálogo modal"""
        xbmcgui.Dialog().ok(title, message)
    
    @staticmethod
    def show_confirmation(title, message):
        """Mostrar diálogo de confirmación"""
        return xbmcgui.Dialog().yesno(title, message)
    
    @staticmethod
    def get_user_input(title, default_text=""):
        """Obtener entrada de texto del usuario"""
        keyboard = xbmc.Keyboard(default_text, title)
        keyboard.doModal()
        
        if keyboard.isConfirmed():
            return keyboard.getText()
        return None
    
    @staticmethod
    def get_current_datetime():
        """Obtener fecha y hora actual en formato ISO"""
        return datetime.datetime.now().isoformat()
    
    @staticmethod
    def format_datetime(iso_datetime):
        """Formatear fecha ISO a formato legible"""
        try:
            dt = datetime.datetime.fromisoformat(iso_datetime)
            return dt.strftime("%d/%m/%Y %H:%M")
        except (ValueError, TypeError):
            return iso_datetime or "N/A"
    
    @staticmethod
    def validate_url(url):
        """Validar si una URL es válida"""
        if not url:
            return False
        
        # Agregar protocolo si no existe
        if not url.startswith(('http://', 'https://', 'ftp://', 'file://')):
            url = 'http://' + url
        
        # Verificación básica de formato
        import re
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        return bool(url_pattern.match(url))
    
    @staticmethod
    def sanitize_filename(filename):
        """Sanitizar nombre de archivo eliminando caracteres no válidos"""
        import re
        # Reemplazar caracteres no válidos con guiones bajos
        return re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    @staticmethod
    def get_file_size(file_path):
        """Obtener tamaño de archivo en bytes"""
        try:
            import os
            return os.path.getsize(file_path)
        except OSError:
            return 0
    
    @staticmethod
    def format_file_size(size_bytes):
        """Formatear tamaño de archivo en formato legible"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        import math
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"
    
    @staticmethod
    def is_network_available():
        """Verificar si hay conexión de red disponible"""
        try:
            import socket
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except OSError:
            return False
    
    @staticmethod
    def get_system_info():
        """Obtener información del sistema"""
        import platform
        return {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'python_version': platform.python_version()
        }
    
    @staticmethod
    def create_progress_dialog(title):
        """Crear diálogo de progreso"""
        progress = xbmcgui.DialogProgress()
        progress.create(title)
        return progress
    
    @staticmethod
    def update_progress_dialog(progress, percent, message=""):
        """Actualizar diálogo de progreso"""
        if progress:
            progress.update(percent, message)
            return not progress.iscanceled()
        return True
    
    @staticmethod
    def close_progress_dialog(progress):
        """Cerrar diálogo de progreso"""
        if progress:
            progress.close()
    
    @staticmethod
    def get_addon_setting(setting_id, default_value=None):
        """Obtener configuración del addon"""
        addon = xbmcaddon.Addon()
        try:
            value = addon.getSetting(setting_id)
            return value if value else default_value
        except Exception:
            return default_value
    
    @staticmethod
    def set_addon_setting(setting_id, value):
        """Establecer configuración del addon"""
        addon = xbmcaddon.Addon()
        try:
            addon.setSetting(setting_id, str(value))
            return True
        except Exception as e:
            Utils.log(f"Error al establecer configuración {setting_id}: {str(e)}", xbmc.LOGERROR)
            return False
    
    @staticmethod
    def show_select_dialog(title, options):
        """Mostrar diálogo de selección"""
        dialog = xbmcgui.Dialog()
        selected = dialog.select(title, options)
        return selected if selected >= 0 else None
    
    @staticmethod
    def show_multiselect_dialog(title, options):
        """Mostrar diálogo de selección múltiple"""
        dialog = xbmcgui.Dialog()
        selected = dialog.multiselect(title, options)
        return selected if selected else []
    
    @staticmethod
    def execute_builtin(command):
        """Ejecutar comando builtin de Kodi"""
        try:
            xbmc.executebuiltin(command)
            return True
        except Exception as e:
            Utils.log(f"Error al ejecutar comando builtin: {str(e)}", xbmc.LOGERROR)
            return False
    
    @staticmethod
    def refresh_container():
        """Refrescar el contenedor actual"""
        return Utils.execute_builtin('Container.Refresh')
    
    @staticmethod
    def go_back():
        """Volver atrás en la navegación"""
        return Utils.execute_builtin('Action(Back)')
    
    @staticmethod
    def play_sound(sound_file):
        """Reproducir archivo de sonido"""
        try:
            xbmc.playSFX(sound_file)
            return True
        except Exception as e:
            Utils.log(f"Error al reproducir sonido: {str(e)}", xbmc.LOGERROR)
            return False
    
    @staticmethod
    def get_localized_string(string_id):
        """Obtener cadena localizada"""
        addon = xbmcaddon.Addon()
        try:
            return addon.getLocalizedString(string_id)
        except Exception:
            return f"String ID: {string_id}"
    
    @staticmethod
    def check_dependencies():
        """Verificar dependencias del addon"""
        try:
            import subprocess
            import json
            import uuid
            import urllib.parse
            import platform
            return True
        except ImportError as e:
            Utils.log(f"Dependencia faltante: {str(e)}", xbmc.LOGERROR)
            return False