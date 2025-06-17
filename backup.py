#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import shutil
import xbmc
import xbmcgui
import xbmcaddon
from utils import Utils
from url_manager import URLManager

class BackupManager:
    """Clase para gestionar respaldos del plugin"""
    
    def __init__(self):
        self.addon = xbmcaddon.Addon()
        # Usar xbmcvfs.translatePath para compatibilidad con Kodi 19+
        try:
            import xbmcvfs
            self.data_dir = xbmcvfs.translatePath(self.addon.getAddonInfo('profile'))
        except (ImportError, AttributeError):
            # Fallback para versiones anteriores de Kodi
            self.data_dir = xbmc.translatePath(self.addon.getAddonInfo('profile'))
        
        self.backup_dir = os.path.join(self.data_dir, 'backups')
        
        # Crear directorio de respaldos si no existe
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
    
    def create_backup(self, include_settings=True):
        """Crear respaldo completo del plugin"""
        try:
            backup_data = {
                'created_date': Utils.get_current_datetime(),
                'addon_version': self.addon.getAddonInfo('version'),
                'kodi_version': xbmc.getInfoLabel('System.BuildVersion'),
                'system_info': Utils.get_system_info()
            }
            
            # Respaldar URLs guardadas
            url_manager = URLManager()
            urls = url_manager.get_saved_urls()
            backup_data['urls'] = urls
            
            # Respaldar configuraciones si se solicita
            if include_settings:
                settings = self._get_all_settings()
                backup_data['settings'] = settings
            
            # Generar nombre de archivo
            timestamp = Utils.get_current_datetime().replace(':', '-').replace('.', '-')
            backup_filename = f"plugin_backup_{timestamp}.json"
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            # Guardar respaldo
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            
            Utils.log(f"Respaldo creado: {backup_path}")
            return backup_path
            
        except Exception as e:
            Utils.log(f"Error al crear respaldo: {str(e)}", xbmc.LOGERROR)
            return None
    
    def restore_backup(self, backup_path, restore_settings=True):
        """Restaurar desde archivo de respaldo"""
        try:
            if not os.path.exists(backup_path):
                Utils.log(f"Archivo de respaldo no encontrado: {backup_path}", xbmc.LOGERROR)
                return False
            
            with open(backup_path, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            # Restaurar URLs
            if 'urls' in backup_data:
                url_manager = URLManager()
                # Limpiar URLs existentes
                current_urls = url_manager.get_saved_urls()
                for url in current_urls:
                    url_manager.delete_url(url['id'])
                
                # Restaurar URLs del respaldo
                for url_data in backup_data['urls']:
                    url_manager.save_url(
                        url_data['name'],
                        url_data['url'],
                        url_data.get('description', '')
                    )
            
            # Restaurar configuraciones si se solicita
            if restore_settings and 'settings' in backup_data:
                self._restore_settings(backup_data['settings'])
            
            Utils.log(f"Respaldo restaurado desde: {backup_path}")
            return True
            
        except Exception as e:
            Utils.log(f"Error al restaurar respaldo: {str(e)}", xbmc.LOGERROR)
            return False
    
    def _get_all_settings(self):
        """Obtener todas las configuraciones del addon"""
        settings = {}
        
        # Lista de configuraciones a respaldar
        setting_keys = [
            'auto_detect_browsers', 'show_browser_descriptions', 'show_notifications',
            'default_browser', 'remember_last_browser', 'enable_url_history',
            'max_saved_urls', 'auto_backup_urls', 'backup_frequency',
            'enable_debug_logging', 'log_level', 'show_system_info',
            'enable_custom_browsers', 'custom_browser_name', 'custom_browser_path',
            'custom_browser_args', 'enable_url_validation', 'auto_add_http',
            'warn_external_urls', 'url_open_mode', 'enable_incognito_mode'
        ]
        
        for key in setting_keys:
            try:
                value = self.addon.getSetting(key)
                settings[key] = value
            except Exception:
                pass
        
        return settings
    
    def _restore_settings(self, settings):
        """Restaurar configuraciones del addon"""
        for key, value in settings.items():
            try:
                self.addon.setSetting(key, value)
            except Exception as e:
                Utils.log(f"Error al restaurar configuración {key}: {str(e)}", xbmc.LOGWARNING)
    
    def list_backups(self):
        """Listar archivos de respaldo disponibles"""
        try:
            backups = []
            
            if os.path.exists(self.backup_dir):
                for filename in os.listdir(self.backup_dir):
                    if filename.endswith('.json') and filename.startswith('plugin_backup_'):
                        backup_path = os.path.join(self.backup_dir, filename)
                        
                        # Obtener información del respaldo
                        try:
                            with open(backup_path, 'r', encoding='utf-8') as f:
                                backup_data = json.load(f)
                            
                            backup_info = {
                                'filename': filename,
                                'path': backup_path,
                                'created_date': backup_data.get('created_date', 'Unknown'),
                                'addon_version': backup_data.get('addon_version', 'Unknown'),
                                'url_count': len(backup_data.get('urls', [])),
                                'has_settings': 'settings' in backup_data,
                                'file_size': Utils.format_file_size(Utils.get_file_size(backup_path))
                            }
                            
                            backups.append(backup_info)
                            
                        except (json.JSONDecodeError, IOError):
                            # Archivo corrupto, ignorar
                            pass
            
            # Ordenar por fecha de creación (más recientes primero)
            backups.sort(key=lambda x: x['created_date'], reverse=True)
            return backups
            
        except Exception as e:
            Utils.log(f"Error al listar respaldos: {str(e)}", xbmc.LOGERROR)
            return []
    
    def delete_backup(self, backup_path):
        """Eliminar archivo de respaldo"""
        try:
            if os.path.exists(backup_path):
                os.remove(backup_path)
                Utils.log(f"Respaldo eliminado: {backup_path}")
                return True
            return False
        except Exception as e:
            Utils.log(f"Error al eliminar respaldo: {str(e)}", xbmc.LOGERROR)
            return False
    
    def cleanup_old_backups(self, max_backups=10):
        """Limpiar respaldos antiguos manteniendo solo los más recientes"""
        try:
            backups = self.list_backups()
            
            if len(backups) > max_backups:
                # Eliminar respaldos antiguos
                backups_to_delete = backups[max_backups:]
                
                for backup in backups_to_delete:
                    self.delete_backup(backup['path'])
                
                Utils.log(f"Respaldos antiguos eliminados: {len(backups_to_delete)}")
                return len(backups_to_delete)
            
            return 0
            
        except Exception as e:
            Utils.log(f"Error al limpiar respaldos: {str(e)}", xbmc.LOGERROR)
            return 0
    
    def auto_backup(self):
        """Realizar respaldo automático según configuración"""
        try:
            if not Utils.get_addon_setting('auto_backup_urls', False):
                return False
            
            frequency = Utils.get_addon_setting('backup_frequency', '0')
            last_backup = Utils.get_addon_setting('last_auto_backup', '')
            
            # Determinar si es necesario hacer respaldo
            should_backup = False
            
            if not last_backup:
                should_backup = True
            else:
                try:
                    import datetime
                    last_backup_date = datetime.datetime.fromisoformat(last_backup)
                    now = datetime.datetime.now()
                    
                    if frequency == '0':  # Diario
                        should_backup = (now - last_backup_date).days >= 1
                    elif frequency == '1':  # Semanal
                        should_backup = (now - last_backup_date).days >= 7
                    elif frequency == '2':  # Mensual
                        should_backup = (now - last_backup_date).days >= 30
                        
                except (ValueError, TypeError):
                    should_backup = True
            
            if should_backup:
                backup_path = self.create_backup(include_settings=False)
                if backup_path:
                    Utils.set_addon_setting('last_auto_backup', Utils.get_current_datetime())
                    self.cleanup_old_backups()
                    Utils.log("Respaldo automático completado")
                    return True
            
            return False
            
        except Exception as e:
            Utils.log(f"Error en respaldo automático: {str(e)}", xbmc.LOGERROR)
            return False