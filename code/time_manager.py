import pygame
from settings import *

class TimeManager:
    """
    Gestisce il sistema temporale del gioco e il loop temporale.
    
    Il tempo avanza da 9:00 a 21:00, poi resetta.
    """
    
    def __init__(self, time_speed=5.0, start_time=9.0, end_time=21.0):
        """
        Inizializza il time manager.
        
        Args:
            time_speed: Secondi reali per ogni ora di gioco (default: 5)
            start_time: Ora di inizio del loop (default: 9.0 = 09:00)
            end_time: Ora di fine del loop (default: 21.0 = 21:00)
        """
        self.time_speed = time_speed  # Secondi reali per ora di gioco
        self.start_time = start_time
        self.end_time = end_time
        
        # Stato attuale
        self.current_time = start_time
        self.loop_count = 0
        self.paused = False
        
        # Variabili per timer
        self.accumulated_time = 0.0
        self.just_reset = False
    
    def update(self, delta_time):
        """
        Aggiorna il tempo di gioco.
        
        Args:
            delta_time: Tempo trascorso in secondi (dal clock)
        """
        if self.paused:
            return
        
        # Accumula tempo reale
        self.accumulated_time += delta_time
        
        # Avanza di 1 ora quando abbiamo accumulato abbastanza tempo
        # Uso while per gestire lag spikes
        while self.accumulated_time >= self.time_speed:
            self.current_time += 1.0  # Avanza sempre di 1 ora esatta
            self.accumulated_time -= self.time_speed  # Mantieni l'eccesso
            
            # Check se abbiamo raggiunto la fine del loop
            if self.current_time >= self.end_time:
                self.reset_loop()
                break  # Esci dopo il reset

    def reset_loop(self):
        """
        Resetta il loop temporale.
        Riporta il tempo all'inizio e incrementa il contatore loop.
        """
        self.current_time = self.start_time
        self.loop_count += 1
        self.accumulated_time = 0.0
        self.just_reset = True
        
        print(f"🔄 Loop #{self.loop_count} iniziato!")  # Debug info
    
    def pause(self):
        """Mette in pausa il tempo."""
        self.paused = True
    
    def resume(self):
        """Riprende il tempo."""
        self.paused = False
    
    def format_time(self):
        """
        Formatta il tempo corrente in formato HH:MM.
        
        Returns:
            String nel formato "09:00"
        """
        hours = int(self.current_time)
        minutes = int((self.current_time % 1) * 60)
        return f"{hours:02d}:{minutes:02d}"
    
    def get_time_remaining(self):
        """
        Calcola quanto tempo manca alla fine del loop.
        
        Returns:
            Float: Ore rimanenti
        """
        return self.end_time - self.current_time
    
    def is_near_end(self, threshold=1.0):
        """
        Controlla se siamo vicini alla fine del loop.
        
        Args:
            threshold: Ore prima della fine (default: 1.0 = ultima ora)
            
        Returns:
            Bool: True se manca meno di threshold ore
        """
        return self.get_time_remaining() <= threshold
    
    def draw(self, screen, font):
        """
        Disegna il timer sullo schermo.
        
        Args:
            screen: pygame.Surface dove disegnare
            font: pygame.Font da usare per il testo
        """
        # Formatta il tempo
        time_text = self.format_time()
        
        # Crea superficie di testo
        text_surface = font.render(time_text, True, TIMER_TEXT_COLOR)
        text_rect = text_surface.get_rect()
        
        # Box per il timer
        padding = 10
        box_width = text_rect.width + padding * 2
        box_height = text_rect.height + padding * 2
        box_x, box_y = TIMER_POSITION
        
        # Disegna background semi-trasparente
        timer_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        pygame.draw.rect(timer_surface, TIMER_BG_COLOR, timer_surface.get_rect(), border_radius=5)
        pygame.draw.rect(timer_surface, TIMER_BORDER_COLOR, timer_surface.get_rect(), width=2, border_radius=5)
        
        # Disegna il box sullo schermo
        screen.blit(timer_surface, (box_x, box_y))
        
        # Disegna il testo centrato nel box
        text_x = box_x + padding
        text_y = box_y + padding
        screen.blit(text_surface, (text_x, text_y))