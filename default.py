#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import urllib.parse
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
from browser_detector import BrowserDetector
from url_manager import URLManager
from history_manager import HistoryManager
from bookmark_manager import BookmarkManager
from utils import Utils
import os

# Obtener información del addon
addon = xbmcaddon.Addon()
addon_handle = int(sys.argv[1])
addon_url = sys.argv[0]

def set_fanart():
    """Configurar fanart como fondo del plugin"""
    fanart_path = os.path.join(addon.getAddonInfo('path'), 'fanart.png')
    if os.path.exists(fanart_path):
        xbmcplugin.setPluginFanart(addon_handle, fanart_path)

def get_url(**kwargs):
    """Construir URL del plugin con parámetros"""
    return '{}?{}'.format(addon_url, urllib.parse.urlencode(kwargs))

def list_browsers():
    """Mostrar lista de navegadores detectados"""
    xbmcplugin.setPluginCategory(addon_handle, addon.getLocalizedString(30001))
    xbmcplugin.setContent(addon_handle, 'files')
    
    # Configurar fanart como fondo
    set_fanart()
    
    # Detectar navegadores instalados
    detector = BrowserDetector()
    browsers = detector.get_installed_browsers()
    
    if not browsers:
        # Mostrar mensaje si no se encontraron navegadores
        list_item = xbmcgui.ListItem(label=addon.getLocalizedString(30010))
        xbmcplugin.addDirectoryItem(addon_handle, '', list_item, False)
    else:
        # Mostrar navegadores encontrados
        for browser in browsers:
            list_item = xbmcgui.ListItem(label=browser['name'])
            list_item.setInfo('video', {'title': browser['name'], 'plot': browser['description']})
            list_item.setArt({'icon': browser.get('icon', 'DefaultProgram.png')})
            
            url = get_url(action='open_browser', browser=browser['executable'])
            xbmcplugin.addDirectoryItem(addon_handle, url, list_item, False)
    
    # Agregar opción para introducir URL personalizada
    list_item = xbmcgui.ListItem(label=addon.getLocalizedString(30011))
    list_item.setInfo('video', {'title': addon.getLocalizedString(30011), 'plot': addon.getLocalizedString(30012)})
    list_item.setArt({'icon': 'DefaultAddonsSearch.png'})
    url = get_url(action='custom_url')
    xbmcplugin.addDirectoryItem(addon_handle, url, list_item, False)
    
    # Agregar opción para gestionar URLs guardadas
    list_item = xbmcgui.ListItem(label=addon.getLocalizedString(30013))
    list_item.setInfo('video', {'title': addon.getLocalizedString(30013), 'plot': addon.getLocalizedString(30014)})
    list_item.setArt({'icon': 'DefaultAddonService.png'})
    url = get_url(action='manage_urls')
    xbmcplugin.addDirectoryItem(addon_handle, url, list_item, True)
    
    # Agregar opción para gestionar historial
    list_item = xbmcgui.ListItem(label=addon.getLocalizedString(30070))
    list_item.setInfo('video', {'title': addon.getLocalizedString(30070), 'plot': addon.getLocalizedString(30071)})
    list_item.setArt({'icon': 'DefaultVideo.png'})
    url = get_url(action='manage_history')
    xbmcplugin.addDirectoryItem(addon_handle, url, list_item, True)
    
    # Agregar opción para gestionar marcadores
    list_item = xbmcgui.ListItem(label=addon.getLocalizedString(30080))
    list_item.setInfo('video', {'title': addon.getLocalizedString(30080), 'plot': addon.getLocalizedString(30081)})
    list_item.setArt({'icon': 'DefaultFavourites.png'})
    url = get_url(action='manage_bookmarks')
    xbmcplugin.addDirectoryItem(addon_handle, url, list_item, True)
    
    # Agregar opción para abrir repositorio de GitHub
    list_item = xbmcgui.ListItem(label=addon.getLocalizedString(30170))
    list_item.setInfo('video', {'title': addon.getLocalizedString(30170), 'plot': addon.getLocalizedString(30171)})
    list_item.setArt({'icon': 'DefaultAddonWebSkin.png'})
    url = get_url(action='open_github')
    xbmcplugin.addDirectoryItem(addon_handle, url, list_item, False)
    
    xbmcplugin.endOfDirectory(addon_handle)

def open_browser(browser_path, url=None):
    """Abrir navegador con URL opcional"""
    detector = BrowserDetector()
    success = detector.launch_browser(browser_path, url)
    
    # Agregar al historial si está habilitado
    if url and success:
        history_manager = HistoryManager()
        browser_name = None
        
        # Intentar obtener el nombre del navegador
        browsers = detector.get_installed_browsers()
        for browser in browsers:
            if browser['executable'] == browser_path:
                browser_name = browser['name']
                break
        
        history_manager.add_to_history(url, browser_name=browser_name)
    
    if success:
        Utils.show_notification(addon.getLocalizedString(30020), addon.getLocalizedString(30021))
    else:
        Utils.show_notification(addon.getLocalizedString(30022), addon.getLocalizedString(30023), xbmcgui.NOTIFICATION_ERROR)

def custom_url():
    """Permitir al usuario introducir una URL personalizada"""
    keyboard = xbmc.Keyboard('', addon.getLocalizedString(30030))
    keyboard.doModal()
    
    if keyboard.isConfirmed():
        url = keyboard.getText()
        if url:
            # Validar URL
            if not url.startswith(('http://', 'https://')):
                url = 'http://' + url
            
            # Mostrar navegadores disponibles para abrir la URL
            detector = BrowserDetector()
            browsers = detector.get_installed_browsers()
            
            if browsers:
                # Crear lista de opciones
                options = [browser['name'] for browser in browsers]
                dialog = xbmcgui.Dialog()
                selected = dialog.select(addon.getLocalizedString(30031), options)
                
                if selected >= 0:
                    browser_path = browsers[selected]['executable']
                    open_browser(browser_path, url)
                    
                    # Preguntar si guardar la URL
                    if dialog.yesno(addon.getLocalizedString(30032), addon.getLocalizedString(30033)):
                        url_manager = URLManager()
                        name = dialog.input(addon.getLocalizedString(30034), url)
                        if name:
                            url_manager.save_url(name, url)
            else:
                Utils.show_notification(addon.getLocalizedString(30022), addon.getLocalizedString(30035), xbmcgui.NOTIFICATION_ERROR)

def manage_urls():
    """Gestionar URLs guardadas"""
    xbmcplugin.setPluginCategory(addon_handle, addon.getLocalizedString(30013))
    xbmcplugin.setContent(addon_handle, 'files')
    
    # Configurar fanart como fondo
    set_fanart()
    
    url_manager = URLManager()
    saved_urls = url_manager.get_saved_urls()
    
    if not saved_urls:
        # Mostrar mensaje si no hay URLs guardadas
        list_item = xbmcgui.ListItem(label=addon.getLocalizedString(30040))
        xbmcplugin.addDirectoryItem(addon_handle, '', list_item, False)
    else:
        # Mostrar URLs guardadas
        for url_data in saved_urls:
            list_item = xbmcgui.ListItem(label=url_data['name'])
            list_item.setInfo('video', {'title': url_data['name'], 'plot': url_data['url']})
            list_item.setArt({'icon': 'DefaultAddonsSearch.png'})
            
            # Menú contextual
            list_item.addContextMenuItems([
                (addon.getLocalizedString(30041), 'RunPlugin({})'.format(get_url(action='delete_url', url_id=url_data['id']))),
                (addon.getLocalizedString(30042), 'RunPlugin({})'.format(get_url(action='edit_url', url_id=url_data['id'])))
            ])
            
            url = get_url(action='open_saved_url', url_id=url_data['id'])
            xbmcplugin.addDirectoryItem(addon_handle, url, list_item, False)
    
    xbmcplugin.endOfDirectory(addon_handle)

def open_saved_url(url_id):
    """Abrir URL guardada"""
    url_manager = URLManager()
    url_data = url_manager.get_url_by_id(url_id)
    
    if url_data:
        # Mostrar navegadores disponibles
        detector = BrowserDetector()
        browsers = detector.get_installed_browsers()
        
        if browsers:
            options = [browser['name'] for browser in browsers]
            dialog = xbmcgui.Dialog()
            selected = dialog.select(addon.getLocalizedString(30031), options)
            
            if selected >= 0:
                browser_path = browsers[selected]['executable']
                open_browser(browser_path, url_data['url'])

def delete_url(url_id):
    """Eliminar URL guardada"""
    dialog = xbmcgui.Dialog()
    if dialog.yesno(addon.getLocalizedString(30050), addon.getLocalizedString(30051)):
        url_manager = URLManager()
        url_manager.delete_url(url_id)
        Utils.show_notification(addon.getLocalizedString(30052), addon.getLocalizedString(30053))
        xbmc.executebuiltin('Container.Refresh')

def edit_url(url_id):
    """Editar URL guardada"""
    url_manager = URLManager()
    url_data = url_manager.get_url_by_id(url_id)
    
    if url_data:
        dialog = xbmcgui.Dialog()
        
        # Editar nombre
        new_name = dialog.input(addon.getLocalizedString(30060), url_data['name'])
        if new_name:
            # Editar URL
            new_url = dialog.input(addon.getLocalizedString(30061), url_data['url'])
            if new_url:
                url_manager.update_url(url_id, new_name, new_url)
                Utils.show_notification(addon.getLocalizedString(30062), addon.getLocalizedString(30063))
                xbmc.executebuiltin('Container.Refresh')

def manage_history():
    """Gestionar historial de navegación"""
    xbmcplugin.setPluginCategory(addon_handle, addon.getLocalizedString(30070))
    xbmcplugin.setContent(addon_handle, 'files')
    
    # Configurar fanart como fondo
    set_fanart()
    
    history_manager = HistoryManager()
    
    # Agregar opciones de gestión del historial
    options = [
        (addon.getLocalizedString(30072), 'recent_history'),  # "Ver historial reciente"
        (addon.getLocalizedString(30073), 'most_visited'),    # "URLs más visitadas"
        (addon.getLocalizedString(30074), 'search_history'),  # "Buscar en historial"
        (addon.getLocalizedString(30075), 'history_stats'),   # "Estadísticas"
        (addon.getLocalizedString(30076), 'clear_history')    # "Limpiar historial"
    ]
    
    for title, action in options:
        list_item = xbmcgui.ListItem(label=title)
        list_item.setArt({'icon': 'DefaultVideo.png'})
        url = get_url(action=action)
        xbmcplugin.addDirectoryItem(addon_handle, url, list_item, action != 'clear_history')
    
    xbmcplugin.endOfDirectory(addon_handle)

def recent_history():
    """Mostrar historial reciente"""
    xbmcplugin.setPluginCategory(addon_handle, addon.getLocalizedString(30072))
    xbmcplugin.setContent(addon_handle, 'files')
    
    # Configurar fanart como fondo
    set_fanart()
    
    history_manager = HistoryManager()
    history = history_manager.get_recent_history()
    
    if not history:
        list_item = xbmcgui.ListItem(label=addon.getLocalizedString(30077))  # "No hay historial"
        xbmcplugin.addDirectoryItem(addon_handle, '', list_item, False)
    else:
        for i, entry in enumerate(history):
            title = f"{entry.get('title', entry['url'])} ({entry['date']})"
            list_item = xbmcgui.ListItem(label=title)
            list_item.setInfo('video', {
                'title': entry.get('title', entry['url']),
                'plot': f"URL: {entry['url']}\nNavegador: {entry.get('browser', 'Desconocido')}\nVisitas: {entry.get('access_count', 1)}"
            })
            list_item.setArt({'icon': 'DefaultVideo.png'})
            
            # Menú contextual
            list_item.addContextMenuItems([
                (addon.getLocalizedString(30051), f'RunPlugin({get_url(action="delete_history", history_id=i)})')
            ])
            
            url = get_url(action='open_history_item', history_id=i)
            xbmcplugin.addDirectoryItem(addon_handle, url, list_item, False)
    
    xbmcplugin.endOfDirectory(addon_handle)

def most_visited():
    """Mostrar URLs más visitadas"""
    xbmcplugin.setPluginCategory(addon_handle, addon.getLocalizedString(30073))
    xbmcplugin.setContent(addon_handle, 'files')
    
    # Configurar fanart como fondo
    set_fanart()
    
    history_manager = HistoryManager()
    most_visited = history_manager.get_most_visited()
    
    if not most_visited:
        list_item = xbmcgui.ListItem(label=addon.getLocalizedString(30077))
        xbmcplugin.addDirectoryItem(addon_handle, '', list_item, False)
    else:
        for i, entry in enumerate(most_visited):
            title = f"{entry.get('title', entry['url'])} ({entry.get('access_count', 1)} visitas)"
            list_item = xbmcgui.ListItem(label=title)
            list_item.setInfo('video', {
                'title': entry.get('title', entry['url']),
                'plot': f"URL: {entry['url']}\nVisitas: {entry.get('access_count', 1)}\nÚltima visita: {entry['date']}"
            })
            list_item.setArt({'icon': 'DefaultVideo.png'})
            
            url = get_url(action='open_history_item', history_id=i, list_type='most_visited')
            xbmcplugin.addDirectoryItem(addon_handle, url, list_item, False)
    
    xbmcplugin.endOfDirectory(addon_handle)

def open_history_item(history_id, list_type='recent'):
    """Abrir item del historial"""
    history_manager = HistoryManager()
    
    if list_type == 'most_visited':
        history = history_manager.get_most_visited()
    else:
        history = history_manager.get_recent_history()
    
    if history and int(history_id) < len(history):
        entry = history[int(history_id)]
        url = entry['url']
        
        # Mostrar navegadores disponibles
        detector = BrowserDetector()
        browsers = detector.get_installed_browsers()
        
        if browsers:
            options = [browser['name'] for browser in browsers]
            dialog = xbmcgui.Dialog()
            selected = dialog.select(addon.getLocalizedString(30031), options)
            
            if selected >= 0:
                browser_path = browsers[selected]['executable']
                open_browser(browser_path, url)

def delete_history(history_id):
    """Eliminar entrada del historial"""
    history_manager = HistoryManager()
    history = history_manager.get_recent_history()
    
    if history and int(history_id) < len(history):
        entry = history[int(history_id)]
        dialog = xbmcgui.Dialog()
        
        if dialog.yesno(addon.getLocalizedString(30078), 
                       addon.getLocalizedString(30079).format(entry.get('title', entry['url']))):
            history_manager.remove_entry(entry['url'])
            Utils.show_notification(addon.getLocalizedString(30055), addon.getLocalizedString(30056))
            xbmc.executebuiltin('Container.Refresh')

def clear_history():
    """Limpiar todo el historial"""
    dialog = xbmcgui.Dialog()
    if dialog.yesno(addon.getLocalizedString(30076), addon.getLocalizedString(30080)):
        history_manager = HistoryManager()
        if history_manager.clear_history():
            Utils.show_notification(addon.getLocalizedString(30055), addon.getLocalizedString(30081))
        else:
            Utils.show_notification(addon.getLocalizedString(30022), addon.getLocalizedString(30082), xbmcgui.NOTIFICATION_ERROR)

def manage_bookmarks():
    """Gestionar marcadores importados"""
    xbmcplugin.setPluginCategory(addon_handle, addon.getLocalizedString(30080))
    xbmcplugin.setContent(addon_handle, 'files')
    
    # Configurar fanart como fondo
    set_fanart()
    
    # Opciones de gestión de marcadores
    options = [
        (addon.getLocalizedString(30083), 'import_bookmarks'),  # "Importar marcadores"
        (addon.getLocalizedString(30084), 'view_bookmarks')     # "Ver marcadores importados"
    ]
    
    for title, action in options:
        list_item = xbmcgui.ListItem(label=title)
        list_item.setArt({'icon': 'DefaultFavourites.png'})
        url = get_url(action=action)
        xbmcplugin.addDirectoryItem(addon_handle, url, list_item, True)
    
    xbmcplugin.endOfDirectory(addon_handle)

def import_bookmarks():
    """Importar marcadores de navegadores"""
    bookmark_manager = BookmarkManager()
    selected_bookmarks = bookmark_manager.show_import_dialog()
    
    if selected_bookmarks:
        # Guardar marcadores seleccionados como URLs guardadas
        url_manager = URLManager()
        imported_count = 0
        
        for bookmark in selected_bookmarks:
            name = f"{bookmark['name']} ({bookmark['source']})"
            if url_manager.save_url(name, bookmark['url']):
                imported_count += 1
        
        if imported_count > 0:
            Utils.show_notification(
                addon.getLocalizedString(30085),
                addon.getLocalizedString(30086).format(imported_count)
            )
        else:
            Utils.show_notification(
                addon.getLocalizedString(30022),
                addon.getLocalizedString(30087),
                xbmcgui.NOTIFICATION_ERROR
            )

def open_github():
    """Abrir repositorio de GitHub del proyecto"""
    github_url = "https://github.com/sapoclay/abridor-web"
    
    # Detectar navegadores disponibles
    detector = BrowserDetector()
    browsers = detector.get_installed_browsers()
    
    if not browsers:
        # Si no hay navegadores detectados, mostrar error
        Utils.show_notification(
            addon.getLocalizedString(30022), 
            addon.getLocalizedString(30035), 
            xbmcgui.NOTIFICATION_ERROR
        )
        return
    
    # Intentar obtener el navegador predeterminado del sistema
    default_browser = detector.get_default_browser()
    selected_browser = None
    
    # Buscar el navegador predeterminado en la lista de detectados
    if default_browser:
        for browser in browsers:
            if default_browser.lower() in browser['name'].lower():
                selected_browser = browser
                break
    
    # Si no se encontró el predeterminado, usar el primero de la lista
    if not selected_browser:
        selected_browser = browsers[0]
    
    # Abrir GitHub en el navegador seleccionado
    success = detector.launch_browser(selected_browser['executable'], github_url)
    
    if success:
        Utils.show_notification(
            addon.getLocalizedString(30172), 
            addon.getLocalizedString(30173).format(selected_browser['name'])
        )
        
        # Agregar al historial si está habilitado
        history_manager = HistoryManager()
        history_manager.add_to_history(github_url, "Repositorio Abridor Web", selected_browser['name'])
    else:
        Utils.show_notification(
            addon.getLocalizedString(30022), 
            addon.getLocalizedString(30174), 
            xbmcgui.NOTIFICATION_ERROR
        )

def router(paramstring):
    """Enrutador principal del plugin"""
    params = dict(urllib.parse.parse_qsl(paramstring))
    
    if params:
        action = params.get('action')
        
        if action == 'open_browser':
            open_browser(params.get('browser'))
        elif action == 'custom_url':
            custom_url()
        elif action == 'manage_urls':
            manage_urls()
        elif action == 'open_saved_url':
            open_saved_url(params.get('url_id'))
        elif action == 'delete_url':
            delete_url(params.get('url_id'))
        elif action == 'edit_url':
            edit_url(params.get('url_id'))
        elif action == 'manage_history':
            manage_history()
        elif action == 'recent_history':
            recent_history()
        elif action == 'most_visited':
            most_visited()
        elif action == 'open_history_item':
            open_history_item(params.get('history_id'), params.get('list_type', 'recent'))
        elif action == 'delete_history':
            delete_history(params.get('history_id'))
        elif action == 'clear_history':
            clear_history()
        elif action == 'manage_bookmarks':
            manage_bookmarks()
        elif action == 'import_bookmarks':
            import_bookmarks()
        elif action == 'view_bookmarks':
            manage_urls()  # Reutilizar la función existente
        elif action == 'open_github':
            open_github()
        else:
            raise ValueError('Acción inválida: {}'.format(action))
    else:
        list_browsers()

if __name__ == '__main__':
    router(sys.argv[2][1:])  # Omitir el primer '?'