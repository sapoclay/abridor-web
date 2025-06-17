#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import time
from datetime import datetime, timedelta
import xbmc
import xbmcaddon
import xbmcvfs
from utils import Utils

class HistoryManager:
    """Gestiona el historial de URLs visitadas"""
    
    def __init__(self):
        self.addon = xbmcaddon.Addon()
        
        # Usar xbmcvfs.translatePath para compatibilidad con Kodi 19+
        try:
            profile_path = xbmcvfs.translatePath(self.addon.getAddonInfo('profile'))
        except AttributeError:
            # Fallback para versiones anteriores
            profile_path = xbmc.translatePath(self.addon.getAddonInfo('profile'))
        
        if not os.path.exists(profile_path):
            os.makedirs(profile_path)
        
        self.history_file = os.path.join(profile_path, 'history.json')
        self.max_history_entries = int(self.addon.getSetting('max_history_entries') or '100')
        self.history_retention_days = int(self.addon.getSetting('history_retention_days') or '30')
    
    def add_to_history(self, url, title=None, browser_name=None):
        """Añadir una URL al historial"""
        if not self.addon.getSettingBool('enable_history'):
            return
        
        history = self.load_history()
        
        entry = {
            'url': url,
            'title': title or url,
            'browser': browser_name or 'Desconocido',
            'timestamp': time.time(),
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'access_count': 1
        }
        
        # Verificar si la URL ya existe
        existing_entry = None
        for i, hist_entry in enumerate(history):
            if hist_entry['url'] == url:
                existing_entry = i
                break
        
        if existing_entry is not None:
            # Actualizar entrada existente
            history[existing_entry]['timestamp'] = entry['timestamp']
            history[existing_entry]['date'] = entry['date']
            history[existing_entry]['browser'] = entry['browser']
            history[existing_entry]['access_count'] += 1
        else:
            # Añadir nueva entrada
            history.insert(0, entry)
        
        # Limpiar historial antiguo
        self._cleanup_history(history)
        
        # Limitar número de entradas
        if len(history) > self.max_history_entries:
            history = history[:self.max_history_entries]
        
        self.save_history(history)
        Utils.log(f"URL añadida al historial: {url}")
    
    def load_history(self):
        """Cargar historial desde archivo"""
        if not os.path.exists(self.history_file):
            return []
        
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            Utils.log(f"Error cargando historial: {str(e)}", xbmc.LOGERROR)
            return []
    
    def save_history(self, history):
        """Guardar historial a archivo"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            Utils.log(f"Error guardando historial: {str(e)}", xbmc.LOGERROR)
    
    def _cleanup_history(self, history):
        """Limpiar entradas antiguas del historial"""
        if self.history_retention_days <= 0:
            return history
        
        cutoff_time = time.time() - (self.history_retention_days * 24 * 60 * 60)
        return [entry for entry in history if entry['timestamp'] > cutoff_time]
    
    def get_recent_history(self, limit=20):
        """Obtener historial reciente"""
        history = self.load_history()
        return history[:limit]
    
    def get_most_visited(self, limit=10):
        """Obtener URLs más visitadas"""
        history = self.load_history()
        
        # Ordenar por número de accesos
        sorted_history = sorted(history, key=lambda x: x.get('access_count', 1), reverse=True)
        return sorted_history[:limit]
    
    def search_history(self, query):
        """Buscar en el historial"""
        history = self.load_history()
        query_lower = query.lower()
        
        results = []
        for entry in history:
            if (query_lower in entry['url'].lower() or 
                query_lower in entry.get('title', '').lower()):
                results.append(entry)
        
        return results
    
    def clear_history(self):
        """Limpiar todo el historial"""
        try:
            if os.path.exists(self.history_file):
                os.remove(self.history_file)
            Utils.log("Historial limpiado")
            return True
        except Exception as e:
            Utils.log(f"Error limpiando historial: {str(e)}", xbmc.LOGERROR)
            return False
    
    def remove_entry(self, url):
        """Eliminar una entrada específica del historial"""
        history = self.load_history()
        history = [entry for entry in history if entry['url'] != url]
        self.save_history(history)
        Utils.log(f"Entrada eliminada del historial: {url}")
    
    def get_history_stats(self):
        """Obtener estadísticas del historial"""
        history = self.load_history()
        
        if not history:
            return {
                'total_entries': 0,
                'total_visits': 0,
                'most_visited_url': None,
                'most_used_browser': None,
                'oldest_entry': None,
                'newest_entry': None
            }
        
        total_visits = sum(entry.get('access_count', 1) for entry in history)
        
        # URL más visitada
        most_visited = max(history, key=lambda x: x.get('access_count', 1))
        
        # Navegador más usado
        browser_counts = {}
        for entry in history:
            browser = entry.get('browser', 'Desconocido')
            browser_counts[browser] = browser_counts.get(browser, 0) + entry.get('access_count', 1)
        
        most_used_browser = max(browser_counts.keys(), key=lambda x: browser_counts[x]) if browser_counts else None
        
        # Entradas más antigua y reciente
        oldest_entry = min(history, key=lambda x: x['timestamp'])
        newest_entry = max(history, key=lambda x: x['timestamp'])
        
        return {
            'total_entries': len(history),
            'total_visits': total_visits,
            'most_visited_url': most_visited['url'],
            'most_visited_count': most_visited.get('access_count', 1),
            'most_used_browser': most_used_browser,
            'oldest_entry': oldest_entry['date'],
            'newest_entry': newest_entry['date']
        }
    
    def export_history(self, export_path):
        """Exportar historial a archivo"""
        history = self.load_history()
        
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            Utils.log(f"Error exportando historial: {str(e)}", xbmc.LOGERROR)
            return False
