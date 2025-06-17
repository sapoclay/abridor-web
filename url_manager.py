#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import uuid
import xbmc
import xbmcaddon
import xbmcvfs
from utils import Utils

class URLManager:
    """Clase para gestionar URLs guardadas por el usuario"""
    
    def __init__(self):
        self.addon = xbmcaddon.Addon()
        # Usar xbmcvfs.translatePath para compatibilidad con Kodi 19+
        try:
            import xbmcvfs
            self.data_dir = xbmcvfs.translatePath(self.addon.getAddonInfo('profile'))
        except (ImportError, AttributeError):
            # Fallback para versiones anteriores de Kodi
            self.data_dir = xbmc.translatePath(self.addon.getAddonInfo('profile'))
        
        self.urls_file = os.path.join(self.data_dir, 'saved_urls.json')
        
        # Crear directorio de datos si no existe
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            Utils.log(f"Directorio de datos creado: {self.data_dir}")
    
    def _load_urls(self):
        """Cargar URLs desde el archivo JSON"""
        try:
            if os.path.exists(self.urls_file):
                with open(self.urls_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('urls', [])
            return []
        except (json.JSONDecodeError, IOError) as e:
            Utils.log(f"Error al cargar URLs: {str(e)}", xbmc.LOGERROR)
            return []
    
    def _save_urls(self, urls):
        """Guardar URLs en el archivo JSON"""
        try:
            data = {
                'urls': urls,
                'version': '1.0'
            }
            with open(self.urls_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            Utils.log(f"URLs guardadas: {len(urls)} elementos")
            return True
        except IOError as e:
            Utils.log(f"Error al guardar URLs: {str(e)}", xbmc.LOGERROR)
            return False
    
    def save_url(self, name, url, description=None):
        """Guardar una nueva URL"""
        urls = self._load_urls()
        
        # Verificar si ya existe una URL con el mismo nombre
        for existing_url in urls:
            if existing_url['name'].lower() == name.lower():
                Utils.log(f"URL con nombre '{name}' ya existe")
                return False
        
        # Crear nueva entrada
        new_url = {
            'id': str(uuid.uuid4()),
            'name': name,
            'url': url,
            'description': description or '',
            'created_date': Utils.get_current_datetime(),
            'access_count': 0,
            'last_accessed': None
        }
        
        urls.append(new_url)
        
        if self._save_urls(urls):
            Utils.log(f"URL guardada: {name} -> {url}")
            return True
        return False
    
    def get_saved_urls(self):
        """Obtener todas las URLs guardadas"""
        urls = self._load_urls()
        # Ordenar por fecha de creación (más recientes primero)
        return sorted(urls, key=lambda x: x.get('created_date', ''), reverse=True)
    
    def get_url_by_id(self, url_id):
        """Obtener URL específica por ID"""
        urls = self._load_urls()
        for url in urls:
            if url['id'] == url_id:
                return url
        return None
    
    def update_url(self, url_id, name=None, url=None, description=None):
        """Actualizar URL existente"""
        urls = self._load_urls()
        
        for i, existing_url in enumerate(urls):
            if existing_url['id'] == url_id:
                if name is not None:
                    existing_url['name'] = name
                if url is not None:
                    existing_url['url'] = url
                if description is not None:
                    existing_url['description'] = description
                
                existing_url['modified_date'] = Utils.get_current_datetime()
                
                if self._save_urls(urls):
                    Utils.log(f"URL actualizada: {existing_url['name']}")
                    return True
                return False
        
        Utils.log(f"URL no encontrada para actualizar: {url_id}")
        return False
    
    def delete_url(self, url_id):
        """Eliminar URL por ID"""
        urls = self._load_urls()
        
        for i, url in enumerate(urls):
            if url['id'] == url_id:
                deleted_url = urls.pop(i)
                if self._save_urls(urls):
                    Utils.log(f"URL eliminada: {deleted_url['name']}")
                    return True
                return False
        
        Utils.log(f"URL no encontrada para eliminar: {url_id}")
        return False
    
    def increment_access_count(self, url_id):
        """Incrementar contador de accesos de una URL"""
        urls = self._load_urls()
        
        for url in urls:
            if url['id'] == url_id:
                url['access_count'] = url.get('access_count', 0) + 1
                url['last_accessed'] = Utils.get_current_datetime()
                
                if self._save_urls(urls):
                    Utils.log(f"Contador de accesos actualizado para: {url['name']}")
                    return True
                return False
        
        return False
    
    def get_most_accessed_urls(self, limit=10):
        """Obtener URLs más accedidas"""
        urls = self._load_urls()
        # Ordenar por número de accesos (mayor a menor)
        sorted_urls = sorted(urls, key=lambda x: x.get('access_count', 0), reverse=True)
        return sorted_urls[:limit]
    
    def search_urls(self, query):
        """Buscar URLs por nombre o URL"""
        urls = self._load_urls()
        query_lower = query.lower()
        
        matching_urls = []
        for url in urls:
            if (query_lower in url['name'].lower() or 
                query_lower in url['url'].lower() or 
                query_lower in url.get('description', '').lower()):
                matching_urls.append(url)
        
        return matching_urls
    
    def export_urls(self, export_path):
        """Exportar URLs a un archivo"""
        try:
            urls = self._load_urls()
            export_data = {
                'export_date': Utils.get_current_datetime(),
                'addon_version': self.addon.getAddonInfo('version'),
                'urls': urls
            }
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            Utils.log(f"URLs exportadas a: {export_path}")
            return True
        except IOError as e:
            Utils.log(f"Error al exportar URLs: {str(e)}", xbmc.LOGERROR)
            return False
    
    def import_urls(self, import_path, merge=True):
        """Importar URLs desde un archivo"""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            imported_urls = import_data.get('urls', [])
            
            if merge:
                # Fusionar con URLs existentes
                existing_urls = self._load_urls()
                existing_names = {url['name'].lower() for url in existing_urls}
                
                # Agregar solo URLs que no existan
                new_urls = []
                for url in imported_urls:
                    if url['name'].lower() not in existing_names:
                        # Generar nuevo ID para evitar conflictos
                        url['id'] = str(uuid.uuid4())
                        new_urls.append(url)
                
                all_urls = existing_urls + new_urls
            else:
                # Reemplazar todas las URLs
                all_urls = imported_urls
            
            if self._save_urls(all_urls):
                Utils.log(f"URLs importadas: {len(imported_urls)} elementos")
                return True
            return False
            
        except (json.JSONDecodeError, IOError) as e:
            Utils.log(f"Error al importar URLs: {str(e)}", xbmc.LOGERROR)
            return False
    
    def backup_urls(self):
        """Crear copia de seguridad de URLs"""
        try:
            backup_filename = f"urls_backup_{Utils.get_current_datetime().replace(':', '-')}.json"
            backup_path = os.path.join(self.data_dir, backup_filename)
            
            return self.export_urls(backup_path)
        except Exception as e:
            Utils.log(f"Error al crear backup: {str(e)}", xbmc.LOGERROR)
            return False
    
    def restore_urls(self, backup_path):
        """Restaurar URLs desde copia de seguridad"""
        return self.import_urls(backup_path, merge=False)
    
    def get_statistics(self):
        """Obtener estadísticas de URLs"""
        urls = self._load_urls()
        
        total_urls = len(urls)
        total_accesses = sum(url.get('access_count', 0) for url in urls)
        
        # URL más accedida
        most_accessed = None
        if urls:
            most_accessed = max(urls, key=lambda x: x.get('access_count', 0))
        
        # URL más reciente
        most_recent = None
        if urls:
            most_recent = max(urls, key=lambda x: x.get('created_date', ''))
        
        return {
            'total_urls': total_urls,
            'total_accesses': total_accesses,
            'most_accessed': most_accessed,
            'most_recent': most_recent,
            'average_accesses': total_accesses / total_urls if total_urls > 0 else 0
        }