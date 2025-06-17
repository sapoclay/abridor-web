#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import sqlite3
import xbmc
import xbmcaddon
import xbmcgui
from utils import Utils

class BookmarkManager:
    """Gestiona la importación de marcadores desde navegadores"""
    
    def __init__(self):
        self.addon = xbmcaddon.Addon()
        self.system = Utils.get_system()
        
    def find_chrome_bookmarks(self):
        """Encontrar archivo de marcadores de Chrome"""
        chrome_paths = {
            'windows': [
                os.path.expandvars(r'%LOCALAPPDATA%\Google\Chrome\User Data\Default\Bookmarks'),
                os.path.expandvars(r'%APPDATA%\Google\Chrome\User Data\Default\Bookmarks')
            ],
            'linux': [
                os.path.expanduser('~/.config/google-chrome/Default/Bookmarks'),
                os.path.expanduser('~/.config/chromium/Default/Bookmarks')
            ]
        }
        
        paths = chrome_paths.get(self.system, [])
        for path in paths:
            if os.path.exists(path):
                return path
        return None
    
    def find_firefox_bookmarks(self):
        """Encontrar base de datos de marcadores de Firefox"""
        firefox_paths = {
            'windows': [
                os.path.expandvars(r'%APPDATA%\Mozilla\Firefox\Profiles'),
            ],
            'linux': [
                os.path.expanduser('~/.mozilla/firefox')
            ]
        }
        
        base_paths = firefox_paths.get(self.system, [])
        for base_path in base_paths:
            if os.path.exists(base_path):
                for profile_dir in os.listdir(base_path):
                    if profile_dir.endswith('.default') or profile_dir.endswith('.default-release'):
                        bookmarks_path = os.path.join(base_path, profile_dir, 'places.sqlite')
                        if os.path.exists(bookmarks_path):
                            return bookmarks_path
        return None
    
    def import_chrome_bookmarks(self):
        """Importar marcadores de Chrome"""
        bookmarks_file = self.find_chrome_bookmarks()
        if not bookmarks_file:
            return []
        
        try:
            with open(bookmarks_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            bookmarks = []
            
            def extract_bookmarks(node):
                if node.get('type') == 'url':
                    bookmarks.append({
                        'name': node.get('name', ''),
                        'url': node.get('url', ''),
                        'source': 'Chrome'
                    })
                elif node.get('type') == 'folder':
                    for child in node.get('children', []):
                        extract_bookmarks(child)
            
            # Extraer de la barra de marcadores
            bookmark_bar = data.get('roots', {}).get('bookmark_bar', {})
            if bookmark_bar:
                extract_bookmarks(bookmark_bar)
            
            # Extraer de otros marcadores
            other_bookmarks = data.get('roots', {}).get('other', {})
            if other_bookmarks:
                extract_bookmarks(other_bookmarks)
            
            Utils.log(f"Importados {len(bookmarks)} marcadores de Chrome")
            return bookmarks
            
        except Exception as e:
            Utils.log(f"Error importando marcadores de Chrome: {str(e)}", xbmc.LOGERROR)
            return []
    
    def import_firefox_bookmarks(self):
        """Importar marcadores de Firefox"""
        bookmarks_db = self.find_firefox_bookmarks()
        if not bookmarks_db:
            return []
        
        try:
            # Hacer una copia temporal para evitar bloqueos
            temp_db = bookmarks_db + '.temp'
            import shutil
            shutil.copy2(bookmarks_db, temp_db)
            
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            
            # Consulta para obtener marcadores
            query = """
                SELECT moz_bookmarks.title, moz_places.url
                FROM moz_bookmarks
                INNER JOIN moz_places ON moz_bookmarks.fk = moz_places.id
                WHERE moz_bookmarks.type = 1 AND moz_places.url IS NOT NULL
                AND moz_places.url NOT LIKE 'place:%'
            """
            
            cursor.execute(query)
            results = cursor.fetchall()
            
            bookmarks = []
            for title, url in results:
                if title and url:
                    bookmarks.append({
                        'name': title,
                        'url': url,
                        'source': 'Firefox'
                    })
            
            conn.close()
            os.remove(temp_db)
            
            Utils.log(f"Importados {len(bookmarks)} marcadores de Firefox")
            return bookmarks
            
        except Exception as e:
            Utils.log(f"Error importando marcadores de Firefox: {str(e)}", xbmc.LOGERROR)
            if os.path.exists(temp_db):
                os.remove(temp_db)
            return []
    
    def import_all_bookmarks(self):
        """Importar marcadores de todos los navegadores disponibles"""
        all_bookmarks = []
        
        # Importar de Chrome
        chrome_bookmarks = self.import_chrome_bookmarks()
        all_bookmarks.extend(chrome_bookmarks)
        
        # Importar de Firefox
        firefox_bookmarks = self.import_firefox_bookmarks()
        all_bookmarks.extend(firefox_bookmarks)
        
        return all_bookmarks
    
    def show_import_dialog(self):
        """Mostrar diálogo para seleccionar marcadores a importar"""
        bookmarks = self.import_all_bookmarks()
        
        if not bookmarks:
            xbmcgui.Dialog().notification(
                self.addon.getAddonInfo('name'),
                self.addon.getLocalizedString(30040),  # "No se encontraron marcadores"
                xbmcgui.NOTIFICATION_INFO,
                3000
            )
            return []
        
        # Crear lista para el diálogo de selección múltiple
        bookmark_list = []
        for bookmark in bookmarks:
            label = f"{bookmark['name']} ({bookmark['source']})"
            bookmark_list.append(label)
        
        # Mostrar diálogo de selección múltiple
        dialog = xbmcgui.Dialog()
        selected_indices = dialog.multiselect(
            self.addon.getLocalizedString(30041),  # "Seleccionar marcadores a importar"
            bookmark_list
        )
        
        if selected_indices:
            selected_bookmarks = [bookmarks[i] for i in selected_indices]
            Utils.log(f"Usuario seleccionó {len(selected_bookmarks)} marcadores para importar")
            return selected_bookmarks
        
        return []
