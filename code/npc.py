import pygame
from settings import *

class NPC(pygame.sprite.Sprite):
    def __init__(self, pos, groups, npc_data):
        """
        npc_data è un dict che contiene:
        - type: tipo di NPC (es: 'merchant', 'guard')
        - name: nome dell'NPC (opzionale)
        - movement: tipo di movimento ('static', 'patrol', 'wander')
        - waypoints: lista di punti per patrol (opzionale)
        - dialogue_id: ID del dialogo associato (opzionale)
        - speed: velocità movimento (default: 2)
        """
        super().__init__(groups)
        
        # Dati base dell'NPC
        self.npc_type = npc_data.get('type', 'villager')
        self.name = npc_data.get('name', 'NPC')
        
        # Carica grafica
        self.image = pygame.image.load(f'../graphics/npc/{self.npc_type}.png').convert_alpha()
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(-10, -20)
        
        # Sistema di movimento (per future fasi)
        self.movement_type = npc_data.get('movement', 'static')
        self.speed = npc_data.get('speed', 2)
        self.direction = pygame.math.Vector2()
        
        # Waypoints per pattugliamento (se presenti)
        self.waypoints = npc_data.get('waypoints', [])
        self.current_waypoint = 0
        
        # Dialoghi
        self.dialogue_id = npc_data.get('dialogue_id', None)
        self.can_interact = False # Viene impostato dal player quando è nel raggio
        
        # Schedule (orari - per future fasi)
        self.schedule = npc_data.get('schedule', None)

        # Indicator grafico
        self.indicator_font = pygame.font.Font(None, 24)
        
    def draw_interaction_indicator(self, surface, offset):
        """Disegna l'indicatore 'E' sopra l'NPC quando il player può interagire"""
        if self.can_interact:
            # Posizione dell'indicatore (sopra la testa dell'NPC)
            indicator_pos = (
                self.rect.centerx - offset.x,
                self.rect.top - offset.y - 20
            )
            
            # Disegna un piccolo cerchio di sfondo
            pygame.draw.circle(surface, (50, 50, 50), indicator_pos, 12)
            pygame.draw.circle(surface, (255, 255, 255), indicator_pos, 12, 2)
            
            # Disegna la lettera 'E'
            text = self.indicator_font.render('E', True, (255, 255, 100))
            text_rect = text.get_rect(center=indicator_pos)
            surface.blit(text, text_rect)
        
    def move(self):
        """Gestisce il movimento dell'NPC (da implementare in Fase 6)"""
        if self.movement_type == 'static':
            return  # NPC fermo
        
        elif self.movement_type == 'patrol':
            # TODO: Implementare logica di pattugliamento
            pass
        
        elif self.movement_type == 'wander':
            # TODO: Implementare movimento casuale
            pass
    
    def update(self):
        """Chiamato ogni frame"""
        # Per ora non fa nulla, ma è pronto per movimento futuro
        self.move()