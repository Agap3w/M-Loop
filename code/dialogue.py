import pygame
import json
from settings import *

class DialogueManager:
    """
    Gestisce tutti i tipi di dialogo nel gioco.
    Supporta: basic, multiple_choice, open_input (futuro), llm_interrogation (futuro)
    """
    def __init__(self):
        self.active = False
        self.current_dialogue = None
        self.current_npc = None
        self.initiated_by = 'player'  # 'player' o 'npc'
        
        # Carica i dialoghi da JSON
        self.dialogues = self.load_dialogues()
        
        # Riferimento al DialogueBox (verrà impostato dopo)
        self.dialogue_box = None
        
        # Callback per quando il dialogo finisce
        self.on_dialogue_end = None
    
    def load_dialogues(self):
        """Carica tutti i dialoghi dal file JSON"""
        try:
            with open('../data/dialogues.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print("Warning: dialogues.json non trovato, creo struttura vuota")
            return {}
        except json.JSONDecodeError:
            print("Errore: dialogues.json non è un JSON valido")
            return {}
    
    def start_dialogue(self, npc, dialogue_id=None, initiated_by='player', **kwargs):
        """
        Inizia un dialogo con un NPC.
        
        Args:
            npc: L'oggetto NPC
            dialogue_id: ID del dialogo da usare (default: usa npc.dialogue_id)
            initiated_by: 'player' o 'npc'
            **kwargs: Parametri extra per condizioni (es: loop_count, time, has_item, ecc)
        """
        if self.active:
            return  # Dialogo già attivo
        
        # Usa dialogue_id dell'NPC se non specificato
        if dialogue_id is None:
            dialogue_id = npc.dialogue_id
        
        if dialogue_id is None or dialogue_id not in self.dialogues:
            print(f"Warning: Dialogo '{dialogue_id}' non trovato")
            return
        
        # Ottieni i dati del dialogo
        dialogue_data = self.dialogues[dialogue_id]
        
        # Applica condizioni se presenti
        dialogue_data = self._apply_conditions(dialogue_data, kwargs)
        
        # Attiva il dialogo
        self.active = True
        self.current_dialogue = dialogue_data
        self.current_npc = npc
        self.initiated_by = initiated_by
        
        # Crea il DialogueBox appropriato in base al tipo
        dialogue_type = dialogue_data.get('type', 'basic')
        
        if dialogue_type == 'basic':
            self.dialogue_box = BasicDialogueBox(dialogue_data, npc)
        elif dialogue_type == 'multiple_choice':
            self.dialogue_box = MultipleChoiceDialogueBox(dialogue_data, npc)
        elif dialogue_type == 'open_input':
            # TODO: Implementazione futura
            print("open_input non ancora implementato")
            self.dialogue_box = BasicDialogueBox(dialogue_data, npc)
        elif dialogue_type == 'llm_interrogation':
            # TODO: Implementazione futura per LLM
            print("llm_interrogation non ancora implementato")
            self.dialogue_box = BasicDialogueBox(dialogue_data, npc)
        else:
            self.dialogue_box = BasicDialogueBox(dialogue_data, npc)
    
    def _apply_conditions(self, dialogue_data, context):
        """
        Applica condizioni al dialogo in base al contesto del gioco.
        
        Es: Se loop_count > 3, usa un dialogo diverso
        """
        if 'conditions' not in dialogue_data:
            return dialogue_data
        
        conditions = dialogue_data['conditions']
        
        # Controlla ogni condizione
        for condition, alternative_text in conditions.items():
            if self._evaluate_condition(condition, context):
                # Crea una copia del dialogo con il testo alternativo
                modified_dialogue = dialogue_data.copy()
                if isinstance(alternative_text, str):
                    modified_dialogue['text'] = alternative_text
                elif isinstance(alternative_text, dict):
                    # Se alternative_text è un oggetto complesso, sostituisci completamente
                    modified_dialogue.update(alternative_text)
                return modified_dialogue
        
        return dialogue_data
    
    def _evaluate_condition(self, condition, context):
        """
        Valuta una condizione.
        
        Supporta:
        - Comparazioni: "loop_count > 3", "time >= 12:00"
        - Booleani: "has_item_key", "quest_completed"
        """
        # IMPORTANTE: Controlla prima gli operatori più lunghi (>=, <=)
        # poi quelli più corti (>, <) per evitare match errati!
        
        if '>=' in condition:
            key, value = condition.split('>=')
            key = key.strip()
            value = value.strip()
            return context.get(key, 0) >= self._parse_value(value)
        
        elif '<=' in condition:
            key, value = condition.split('<=')
            key = key.strip()
            value = value.strip()
            return context.get(key, 0) <= self._parse_value(value)
        
        elif '>' in condition:
            key, value = condition.split('>')
            key = key.strip()
            value = value.strip()
            return context.get(key, 0) > self._parse_value(value)
        
        elif '<' in condition:
            key, value = condition.split('<')
            key = key.strip()
            value = value.strip()
            return context.get(key, 0) < self._parse_value(value)
        
        elif '==' in condition:
            key, value = condition.split('==')
            key = key.strip()
            value = value.strip()
            return context.get(key) == self._parse_value(value)
        
        else:
            # Condizione booleana semplice (es: "has_item_key")
            return context.get(condition, False)

    
    def _parse_value(self, value):
        """Converte una stringa in int, float, time (HH:MM) o stringa"""
        # Prima rimuovi eventuali virgolette/spazi
        value = str(value).strip()
        
        try:
            # Controlla se è un formato HH:MM (es: "12:00", "18:30")
            if ':' in value:
                hours, minutes = value.split(':')
                return float(hours) + float(minutes) / 60.0
            
            # Altrimenti prova numero con decimale
            if '.' in value:
                return float(value)
            
            # Altrimenti prova intero
            return int(value)
        except ValueError:
            # È una stringa, restituiscila così
            return value
    
    def end_dialogue(self, choice_result=None):
        """
        Termina il dialogo corrente.
        
        Args:
            choice_result: Risultato della scelta (per multiple_choice)
        """
        self.active = False
        self.dialogue_box = None
        
        # Callback opzionale
        if self.on_dialogue_end:
            self.on_dialogue_end(self.current_npc, choice_result)
        
        self.current_dialogue = None
        self.current_npc = None
    
    def update(self):
        """Aggiorna il dialogo attivo"""
        if self.active and self.dialogue_box:
            result = self.dialogue_box.update()
            if result == 'end':
                self.end_dialogue()
            elif result is not None:
                # Risultato di una scelta
                self.end_dialogue(result)
    
    def draw(self, surface):
        """Disegna il dialogo attivo"""
        if self.active and self.dialogue_box:
            self.dialogue_box.draw(surface)
    
    def handle_input(self, event):
        """Gestisce l'input per il dialogo attivo"""
        if self.active and self.dialogue_box:
            return self.dialogue_box.handle_input(event)
        return False


class BasicDialogueBox:
    """
    Box di dialogo semplice - l'NPC parla e il player legge.
    """
    def __init__(self, dialogue_data, npc):
        self.npc = npc
        self.text = dialogue_data.get('text', 'Ciao!')
        self.npc_name = dialogue_data.get('npc_name', npc.name)
        
        # Box positioning e dimensioni
        self.screen = pygame.display.get_surface()
        self.box_width = 800
        self.box_height = 150
        self.box_x = (WIDTH - self.box_width) // 2
        self.box_y = HEIGTH - self.box_height - 40
        
        # Colori
        self.bg_color = (20, 20, 40)
        self.border_color = (200, 200, 220)
        self.text_color = (255, 255, 255)
        self.name_color = (255, 220, 100)
        
        # Font
        self.font = pygame.font.Font(None, 28)
        self.name_font = pygame.font.Font(None, 32)
        
        # Stato
        self.finished = False
        self.can_close = True
    
    def update(self):
        """Aggiorna il box - per ora è statico"""
        if self.finished:
            return 'end'
        return None
    
    def draw(self, surface):
        """Disegna il dialogue box"""
        # Box principale
        box_rect = pygame.Rect(self.box_x, self.box_y, self.box_width, self.box_height)
        pygame.draw.rect(surface, self.bg_color, box_rect)
        pygame.draw.rect(surface, self.border_color, box_rect, 3)
        
        # Nome NPC
        name_surf = self.name_font.render(self.npc_name, True, self.name_color)
        surface.blit(name_surf, (self.box_x + 20, self.box_y + 15))
        
        # Testo del dialogo (word wrap)
        self._draw_wrapped_text(surface, self.text, 
                                self.box_x + 20, 
                                self.box_y + 55,
                                self.box_width - 40)
        
        # Indicatore "Premi E per continuare"
        if self.can_close:
            indicator_font = pygame.font.Font(None, 22)
            indicator = indicator_font.render("Premi E per continuare", True, (150, 150, 150))
            surface.blit(indicator, 
                        (self.box_x + self.box_width - 200, 
                         self.box_y + self.box_height - 30))
    
    def _draw_wrapped_text(self, surface, text, x, y, max_width):
        """Disegna testo con word wrap"""
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_surf = self.font.render(test_line, True, self.text_color)
            
            if test_surf.get_width() <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Disegna le linee
        line_height = 32
        for i, line in enumerate(lines[:3]):  # Max 3 linee
            line_surf = self.font.render(line, True, self.text_color)
            surface.blit(line_surf, (x, y + i * line_height))
    
    def handle_input(self, event):
        """Gestisce input - premi E per chiudere"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e or event.key == pygame.K_SPACE:
                if self.can_close:
                    self.finished = True
                    return True
        return False


class MultipleChoiceDialogueBox(BasicDialogueBox):
    """
    Box di dialogo con scelte multiple.
    """
    def __init__(self, dialogue_data, npc):
        super().__init__(dialogue_data, npc)
        
        self.choices = dialogue_data.get('choices', [])
        self.selected_choice = 0
        self.can_close = False  # Non può chiudere finché non sceglie
        
        # Box più grande per le scelte
        self.box_height = 200
        self.box_y = HEIGTH - self.box_height - 40
        
        self.choice_made = None
    
    def draw(self, surface):
        """Disegna il dialogue box con scelte"""
        # Box principale
        box_rect = pygame.Rect(self.box_x, self.box_y, self.box_width, self.box_height)
        pygame.draw.rect(surface, self.bg_color, box_rect)
        pygame.draw.rect(surface, self.border_color, box_rect, 3)
        
        # Nome NPC
        name_surf = self.name_font.render(self.npc_name, True, self.name_color)
        surface.blit(name_surf, (self.box_x + 20, self.box_y + 15))
        
        # Testo del dialogo
        text_surf = self.font.render(self.text, True, self.text_color)
        surface.blit(text_surf, (self.box_x + 20, self.box_y + 55))
        
        # Scelte
        choice_y = self.box_y + 100
        for i, choice in enumerate(self.choices):
            choice_text = choice.get('text', f'Scelta {i+1}')
            
            # Colore diverso per scelta selezionata
            if i == self.selected_choice:
                color = (255, 255, 100)
                prefix = "▶ "
            else:
                color = (180, 180, 180)
                prefix = "  "
            
            choice_surf = self.font.render(f"{prefix}{choice_text}", True, color)
            surface.blit(choice_surf, (self.box_x + 40, choice_y + i * 35))
    
    def update(self):
        """Controlla se una scelta è stata fatta"""
        if self.choice_made is not None:
            return self.choices[self.choice_made]
        return None
    
    def handle_input(self, event):
        """Gestisce input per navigare e scegliere"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                self.selected_choice = (self.selected_choice - 1) % len(self.choices)
                return True
            
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.selected_choice = (self.selected_choice + 1) % len(self.choices)
                return True
            
            elif event.key == pygame.K_e or event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                self.choice_made = self.selected_choice
                return True
        
        return False