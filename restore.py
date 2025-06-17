#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import xbmc
import xbmcgui
import xbmcaddon
from backup import BackupManager
from utils import Utils

class RestoreManager:
    """Clase para gestionar la restauración del plugin"""
    
    def __init__(self):
        self.addon = xbmcaddon.Addon()
        self.backup_manager = BackupManager()
    
    def show_restore_dialog(self):
        """Mostrar diálogo de restauración"""
        try:
            # Obtener lista de respaldos disponibles
            backups = self.backup_manager.list_backups()
            
            if not backups:
                Utils.show_dialog(
                    self.addon.getLocalizedString(30022),  # Error
                    "No hay respaldos disponibles para restaurar"
                )
                return False
            
            # Crear lista de opciones para el diálogo
            options = []
            for backup in backups:
                date_formatted = Utils.format_datetime(backup['created_date'])
                option = f"{date_formatted} - {backup['url_count']} URLs ({backup['file_size']})"
                options.append(option)
            
            # Mostrar diálogo de selección
            dialog = xbmcgui.Dialog()
            selected = dialog.select("Seleccionar respaldo para restaurar", options)
            
            if selected >= 0:
                backup_to_restore = backups[selected]
                return self._confirm_and_restore(backup_to_restore)
            
            return False
            
        except Exception as e:
            Utils.log(f"Error en diálogo de restauración: {str(e)}", xbmc.LOGERROR)
            Utils.show_dialog(
                self.addon.getLocalizedString(30022),  # Error
                f"Error al mostrar diálogo de restauración: {str(e)}"
            )
            return False
    
    def _confirm_and_restore(self, backup_info):
        """Confirmar y realizar restauración"""
        try:
            # Mostrar información del respaldo
            date_formatted = Utils.format_datetime(backup_info['created_date'])
            message = (
                f"Respaldo: {date_formatted}\n"
                f"URLs: {backup_info['url_count']}\n"
                f"Tamaño: {backup_info['file_size']}\n"
                f"¿Confirmar restauración?"
            )
            
            dialog = xbmcgui.Dialog()
            if not dialog.yesno("Confirmar restauración", message):
                return False
            
            # Preguntar si restaurar configuraciones también
            restore_settings = False
            if backup_info['has_settings']:
                restore_settings = dialog.yesno(
                    "Restaurar configuraciones",
                    "¿También restaurar las configuraciones del plugin?"
                )
            
            # Mostrar progreso
            progress = Utils.create_progress_dialog("Restaurando respaldo")
            progress.update(0, "Iniciando restauración...")
            
            # Realizar restauración
            success = self.backup_manager.restore_backup(
                backup_info['path'],
                restore_settings
            )
            
            progress.update(100, "Restauración completada")
            Utils.close_progress_dialog(progress)
            
            if success:
                # Mostrar mensaje de éxito
                Utils.show_dialog(
                    "Restauración exitosa",
                    "El respaldo ha sido restaurado correctamente.\n"
                    "Se recomienda reiniciar Kodi para aplicar todos los cambios."
                )
                
                # Refrescar interfaz
                Utils.refresh_container()
                return True
            else:
                Utils.show_dialog(
                    self.addon.getLocalizedString(30022),  # Error
                    "Error al restaurar el respaldo"
                )
                return False
                
        except Exception as e:
            Utils.log(f"Error en restauración: {str(e)}", xbmc.LOGERROR)
            Utils.show_dialog(
                self.addon.getLocalizedString(30022),  # Error
                f"Error durante la restauración: {str(e)}"
            )
            return False
    
    def restore_from_file(self, file_path):
        """Restaurar desde un archivo específico"""
        try:
            if not os.path.exists(file_path):
                Utils.show_dialog(
                    self.addon.getLocalizedString(30022),  # Error
                    "El archivo de respaldo no existe"
                )
                return False
            
            # Validar archivo de respaldo
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    backup_data = json.load(f)
                
                if 'urls' not in backup_data and 'settings' not in backup_data:
                    Utils.show_dialog(
                        self.addon.getLocalizedString(30022),  # Error
                        "El archivo no es un respaldo válido"
                    )
                    return False
                    
            except (json.JSONDecodeError, IOError) as e:
                Utils.show_dialog(
                    self.addon.getLocalizedString(30022),  # Error
                    f"Error al leer el archivo de respaldo: {str(e)}"
                )
                return False
            
            # Importar respaldo
            imported_path = self.backup_manager.import_from_external(file_path)
            
            if imported_path:
                # Crear info del respaldo importado
                backup_info = {
                    'path': imported_path,
                    'created_date': backup_data.get('created_date', Utils.get_current_datetime()),
                    'url_count': len(backup_data.get('urls', [])),
                    'has_settings': 'settings' in backup_data,
                    'file_size': Utils.format_file_size(Utils.get_file_size(imported_path))
                }
                
                return self._confirm_and_restore(backup_info)
            else:
                Utils.show_dialog(
                    self.addon.getLocalizedString(30022),  # Error
                    "Error al importar el archivo de respaldo"
                )
                return False
                
        except Exception as e:
            Utils.log(f"Error al restaurar desde archivo: {str(e)}", xbmc.LOGERROR)
            Utils.show_dialog(
                self.addon.getLocalizedString(30022),  # Error
                f"Error al restaurar desde archivo: {str(e)}"
            )
            return False
    
    def show_backup_info(self, backup_path):
        """Mostrar información detallada de un respaldo"""
        try:
            if not os.path.exists(backup_path):
                return False
            
            with open(backup_path, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            # Construir información detallada
            info_lines = []
            info_lines.append(f"Fecha: {Utils.format_datetime(backup_data.get('created_date', 'N/A'))}")
            info_lines.append(f"Versión del addon: {backup_data.get('addon_version', 'N/A')}")
            info_lines.append(f"Versión de Kodi: {backup_data.get('kodi_version', 'N/A')}")
            info_lines.append(f"URLs guardadas: {len(backup_data.get('urls', []))}")
            info_lines.append(f"Configuraciones: {'Sí' if 'settings' in backup_data else 'No'}")
            
            # Información del sistema
            system_info = backup_data.get('system_info', {})
            if system_info:
                info_lines.append(f"Sistema: {system_info.get('system', 'N/A')}")
                info_lines.append(f"Arquitectura: {system_info.get('machine', 'N/A')}")
            
            # Tamaño del archivo
            file_size = Utils.format_file_size(Utils.get_file_size(backup_path))
            info_lines.append(f"Tamaño: {file_size}")
            
            # Mostrar información
            Utils.show_dialog("Información del respaldo", "\n".join(info_lines))
            return True
            
        except Exception as e:
            Utils.log(f"Error al mostrar información del respaldo: {str(e)}", xbmc.LOGERROR)
            Utils.show_dialog(
                self.addon.getLocalizedString(30022),  # Error
                f"Error al leer información del respaldo: {str(e)}"
            )
            return False
    
    def emergency_restore(self):
        """Restauración de emergencia - restaurar el respaldo más reciente"""
        try:
            backups = self.backup_manager.list_backups()
            
            if not backups:
                Utils.show_dialog(
                    self.addon.getLocalizedString(30022),  # Error
                    "No hay respaldos disponibles para restauración de emergencia"
                )
                return False
            
            # Tomar el respaldo más reciente
            latest_backup = backups[0]
            
            # Confirmar restauración de emergencia
            dialog = xbmcgui.Dialog()
            date_formatted = Utils.format_datetime(latest_backup['created_date'])
            message = (
                f"Restauración de emergencia\n"
                f"Respaldo más reciente: {date_formatted}\n"
                f"¿Continuar?"
            )
            
            if dialog.yesno("Restauración de emergencia", message):
                return self._confirm_and_restore(latest_backup)
            
            return False
            
        except Exception as e:
            Utils.log(f"Error en restauración de emergencia: {str(e)}", xbmc.LOGERROR)
            Utils.show_dialog(
                self.addon.getLocalizedString(30022),  # Error
                f"Error en restauración de emergencia: {str(e)}"
            )
            return False
    
    def cleanup_backups(self):
        """Limpiar respaldos antiguos"""
        try:
            dialog = xbmcgui.Dialog()
            
            # Preguntar cuántos respaldos mantener
            max_backups = dialog.numeric(0, "Número máximo de respaldos a mantener", "10")
            
            if max_backups > 0:
                deleted_count = self.backup_manager.cleanup_old_backups(max_backups)
                
                if deleted_count > 0:
                    Utils.show_dialog(
                        "Limpieza completada",
                        f"Se eliminaron {deleted_count} respaldos antiguos"
                    )
                else:
                    Utils.show_dialog(
                        "Limpieza completada",
                        "No se eliminaron respaldos"
                    )
                
                return True
            
            return False
            
        except Exception as e:
            Utils.log(f"Error en limpieza de respaldos: {str(e)}", xbmc.LOGERROR)
            Utils.show_dialog(
                self.addon.getLocalizedString(30022),  # Error
                f"Error en limpieza de respaldos: {str(e)}"
            )
            return False