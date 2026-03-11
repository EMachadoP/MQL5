import MetaTrader5 as mt5
import time
import pandas as pd
from datetime import datetime
import logging
import os

# Configuração de log
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"{log_dir}/mt5_monitor_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler()
    ]
)

class MT5Monitor:
    def __init__(self, check_interval=5):
        self.check_interval = check_interval
        self.last_positions_ids = set()
        self.last_orders_ids = set()

    def connect(self):
        logging.info("Tentando conectar ao MetaTrader 5...")
        if not mt5.initialize():
            logging.error(f"Falha ao inicializar o MT5. Código de erro: {mt5.last_error()}")
            return False
        
        account_info = mt5.account_info()
        if account_info is None:
            logging.error("Falha ao recuperar as informações da conta. Verifique a conexão do MT5.")
            return False
            
        logging.info(f"Conectado com sucesso! Conta: {account_info.login}, Servidor: {account_info.server}")
        return True

    def check_positions(self):
        positions = mt5.positions_get()
        if positions is None:
            logging.error(f"Falha ao obter posições. Erro: {mt5.last_error()}")
            return

        current_ids = {pos.ticket for pos in positions}
        
        # Novas posições
        new_positions = current_ids - self.last_positions_ids
        if new_positions:
            for pos in positions:
                if pos.ticket in new_positions:
                    logging.info(f"[NOVA POSIÇÃO] Em ticker {pos.symbol}: Tipo={pos.type}, Volume={pos.volume}, Preço={pos.price_open}, SL={pos.sl}, TP={pos.tp}")
        
        # Posições fechadas
        closed_positions = self.last_positions_ids - current_ids
        if closed_positions:
            for ticket in closed_positions:
                logging.info(f"[POSIÇÃO FECHADA] Ticket: {ticket}")

        self.last_positions_ids = current_ids

    def check_orders(self):
        orders = mt5.orders_get()
        if orders is None:
            logging.error(f"Falha ao obter ordens. Erro: {mt5.last_error()}")
            return

        current_ids = {order.ticket for order in orders}
        
        # Novas ordens pendentes
        new_orders = current_ids - self.last_orders_ids
        if new_orders:
            for order in orders:
                if order.ticket in new_orders:
                    logging.info(f"[NOVA ORDEM PENDENTE] Em ticker {order.symbol}: Tipo={order.type}, Volume={order.volume_initial}, Preço={order.price_open}")
        
        # Ordens removidas/executadas
        removed_orders = self.last_orders_ids - current_ids
        if removed_orders:
            for ticket in removed_orders:
                logging.info(f"[ORDEM REMOVIDA/EXECUTADA] Ticket: {ticket}")

        self.last_orders_ids = current_ids

    def run(self):
        if not self.connect():
            return

        logging.info("Iniciando monitoramento. Pressione Ctrl+C para parar.")
        try:
            while True:
                self.check_positions()
                self.check_orders()
                time.sleep(self.check_interval)
        except KeyboardInterrupt:
            logging.info("Monitoramento interrompido pelo usuário.")
        finally:
            mt5.shutdown()
            logging.info("Conexão com MT5 encerrada.")

if __name__ == "__main__":
    monitor = MT5Monitor(check_interval=2)
    monitor.run()
