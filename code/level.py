import pygame
import json
from settings import *
from tile import Tile
from player import Player
from npc import NPC
from support import *
from dialogue import DialogueManager

class Level:
    def __init__(self, time_manager, map_name='npc_world'):
        """map_name: nome della mappa da caricare (es: 'world', 'house1', 'church')"""
        
        # get the display surface
        self.display_surface = pygame.display.get_surface()

        # Nome mappa corrente
        self.map_name = map_name

        # Time manager
        self.time_manager = time_manager

        # sprite group setup
        self.visible_sprites = YSortCameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()
        self.npc_sprites = pygame.sprite.Group()

        # Dialogue system
        self.dialogue_manager = DialogueManager()

        # sprite setup
        self.create_map()
        self.player_spawn = (self.player.rect.x, self.player.rect.y)

    def create_map(self):
        """Carica la mappa usando approccio IBRIDO: CSV per tiles + JSON per NPC"""

        layouts = {
            'boundary': import_csv_layout('../map/collision.csv'),
            'walkable_objects': import_csv_layout('../map/walkable_objects.csv'),
            'obstacle_objects': import_csv_layout('../map/obstacle_objects.csv')
        }

        graphics = {
            'walkable_objects' : import_folder('../graphics/walkable_objects'),
            'obstacle_objects' : import_folder('../graphics/obstacle_objects')
        }
        for style, layout in layouts.items():
            for row_index, row in enumerate(layout):
                for col_index, col in enumerate(row):
                    if col != '-1':
                        x = col_index * TILESIZE
                        y = row_index * TILESIZE
                        if style == 'boundary':
                            Tile((x,y), [self.obstacle_sprites], 'invisible')
                        if style == 'walkable_objects':
                            surf = graphics['walkable_objects'][int(col)]
                            Tile((x,y), [self.visible_sprites], 'walkable_objects', surf)
                        if style == 'obstacle_objects':
                            surf = graphics['obstacle_objects'][int(col)]
                            Tile((x,y), [self.visible_sprites, self.obstacle_sprites], 'obstacle_objects', surf)

        self.load_npcs_from_json()

        self.player = Player((685,210), [self.visible_sprites], self.obstacle_sprites)

    def load_npcs_from_json(self):
        """Carica SOLO gli NPC dal JSON"""

        try:
            # Carica il file JSON
            with open(f'../map/{self.map_name}.json') as f:
                map_data = json.load(f)
            
            # Cerca il layer 'npc'
            for layer in map_data['layers']:
                if layer['type'] == 'objectgroup' and layer['name'] == 'npc':
                    # Crea gli NPC
                    for obj in layer['objects']:
                        pos = (obj['x'], obj['y'])
                        
                        npc_type = obj.get('class', obj.get('type', 'unknown')) # Tiled può usare 'class' o 'type' a seconda della versione
                        
                        # Dati base NPC
                        npc_data = {
                            'type': npc_type,
                            'name': obj.get('name', f'NPC_{obj.get("id", 0)}'),
                            'movement': 'static', #leggo il campo 'movement', se non esite uso static come default
                            'dialogue_id': None,
                            'waypoints': [],
                            'speed': 2
                        }
                        
                        # Se in futuro aggiungi properties, le legge da qui
                        if 'properties' in obj:
                            for prop in obj['properties']:
                                prop_name = prop['name']
                                prop_value = prop['value']
                                
                                if prop_name == 'movement':
                                    npc_data['movement'] = prop_value
                                elif prop_name == 'dialogue_id':
                                    npc_data['dialogue_id'] = prop_value
                                elif prop_name == 'speed':
                                    npc_data['speed'] = int(prop_value)
                        
                        # Crea NPC
                        NPC(pos, [self.visible_sprites, self.obstacle_sprites, self.npc_sprites], npc_data)
                                          
                    break  # Layer NPC trovato, esci dal loop
        
        except FileNotFoundError:
            print(f"Warning: {self.map_name}.json non trovato, nessun NPC caricato")
        except json.JSONDecodeError:
            print(f"Errore: {self.map_name}.json non è un JSON valido")

    def handle_interaction(self):
        """Gestisce l'interazione del player con gli NPC"""
        if self.player.nearby_npc and not self.dialogue_manager.active:
            # Avvia il dialogo
            # In futuro qui passeremo anche loop_count, time, ecc.
            self.dialogue_manager.start_dialogue(
                self.player.nearby_npc,
                initiated_by='player',
                loop_count=self.time_manager.loop_count,
                time=self.time_manager.current_time,
                has_item_newspaper=False  # TODO: Collegare all'inventario
            )
            
            # Blocca il movimento del player durante il dialogo
            self.player.can_move = False

    def run(self):

        # Check se il loop è appena resetato
        if self.time_manager.just_reset:
            # Riporta il player allo spawn
            self.player.rect.x, self.player.rect.y = self.player_spawn
            self.player.hitbox.center = self.player.rect.center
            
            # Resetta il flag
            self.time_manager.just_reset = False
            
        # Controlla NPC vicini per interazione
        self.player.check_nearby_npcs(self.npc_sprites)
        
        # update and draw the game
        self.visible_sprites.custom_draw(self.player)
        self.visible_sprites.update()
        
        # Aggiorna e disegna il dialogo se attivo
        if self.dialogue_manager.active:
            self.time_manager.pause()
            self.dialogue_manager.update()
            self.dialogue_manager.draw(self.display_surface)
        else:
            # Sblocca il movimento quando il dialogo finisce
            self.time_manager.resume()
            self.player.can_move = True


class YSortCameraGroup(pygame.sprite.Group):
    def __init__(self):

        # general setup
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.half_width = self.display_surface.get_size()[0] // 2
        self.half_heigth = self.display_surface.get_size()[1] // 2
        self.offset = pygame.math.Vector2()

        #create the floor
        self.floor_surface = pygame.image.load("../map/floor_map.png").convert()
        self.floor_rect = self.floor_surface.get_rect(topleft =(0,0))

    def custom_draw(self, player):

        # getting the offset
        self.offset.x = player.rect.centerx - self.half_width
        self.offset.y = player.rect.centery - self.half_heigth

        # drawing the floor
        floor_offset_pos = self.floor_rect.topleft - self.offset
        self.display_surface.blit(self.floor_surface, floor_offset_pos)

        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)

            # Disegna indicatore di interazione per NPC
            if hasattr(sprite, 'draw_interaction_indicator'):
                sprite.draw_interaction_indicator(self.display_surface, self.offset)