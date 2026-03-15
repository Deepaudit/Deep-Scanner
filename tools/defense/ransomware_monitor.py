import os
import time
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configurações do Deep Audit
WATCH_PATH = "./diretorio_protegido" # Pasta que você quer proteger
SUSPICIOUS_EXTENSIONS = ['.crypt', '.locked', '.enc', '.deep', '.ransom']
ALERT_THRESHOLD = 5 # Quantidade de mudanças em segundos para alertar

class RansomwareHandler(FileSystemEventHandler):
    def __init__(self):
        self.change_count = 0
        self.start_time = time.time()

    def process_event(self, event):
        # Verifica se o arquivo foi renomeado para uma extensão suspeita
        if event.is_directory:
            return

        filename, extension = os.path.splitext(event.src_path)
        
        if extension.lower() in SUSPICIOUS_EXTENSIONS or "README" in filename:
            self.change_count += 1
            print(f"[⚠️] ATENÇÃO: Atividade suspeita detectada em: {event.src_path}")

            # Se houver muitas mudanças rápidas, dispara o alerta de integridade
            current_time = time.time()
            if current_time - self.start_time < 10: # Janela de 10 segundos
                if self.change_count >= ALERT_THRESHOLD:
                    print("\n" + "!"*50)
                    print("!!! ALERTA DE POSSÍVEL RANSOMWARE EM EXECUÇÃO !!!")
                    print("!!! BLOQUEANDO ATIVIDADE E NOTIFICANDO TI !!!")
                    print("!"*50 + "\n")
                    # Aqui você poderia adicionar: os.system("taskkill /F /IM process_suspeito.exe")
                    self.change_count = 0 
            else:
                self.start_time = current_time
                self.change_count = 1

    def on_modified(self, event):
        self.process_event(event)

    def on_moved(self, event):
        self.process_event(event)

if __name__ == "__main__":
    if not os.path.exists(WATCH_PATH):
        os.makedirs(WATCH_PATH)

    event_handler = RansomwareHandler()
    observer = Observer()
    observer.schedule(event_handler, WATCH_PATH, recursive=True)
    
    print(f"--- [🛡️] Deep Integrity Guard Ativado ---")
    print(f"--- Monitorando: {os.path.abspath(WATCH_PATH)} ---")
    
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
