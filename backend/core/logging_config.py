import os
import logging
from logging.handlers import RotatingFileHandler
from django.conf import settings

# Configurazione del logger principale
def setup_logger():
    # Crea la directory dei log se non esiste
    log_dir = os.path.join(settings.BASE_DIR, 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Configura il logger principale
    logger = logging.getLogger('django')
    logger.setLevel(logging.INFO)

    # Formato del log
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Handler per file con rotazione
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, 'django.log'),
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Handler per console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger

# Logger per le transazioni
def get_transaction_logger():
    logger = logging.getLogger('django.transactions')
    logger.setLevel(logging.INFO)

    # Formato specifico per le transazioni
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - Transaction ID: %(transaction_id)s - %(message)s'
    )

    # Handler per file delle transazioni
    file_handler = RotatingFileHandler(
        os.path.join(settings.BASE_DIR, 'logs', 'transactions.log'),
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

# Logger per gli errori
def get_error_logger():
    logger = logging.getLogger('django.errors')
    logger.setLevel(logging.ERROR)

    # Formato specifico per gli errori
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(pathname)s:%(lineno)d - %(message)s'
    )

    # Handler per file degli errori
    file_handler = RotatingFileHandler(
        os.path.join(settings.BASE_DIR, 'logs', 'errors.log'),
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

# Logger per le attività degli utenti
def get_user_activity_logger():
    logger = logging.getLogger('django.user_activity')
    logger.setLevel(logging.INFO)

    # Formato specifico per le attività degli utenti
    formatter = logging.Formatter(
        '%(asctime)s - User ID: %(user_id)s - Action: %(action)s - %(message)s'
    )

    # Handler per file delle attività
    file_handler = RotatingFileHandler(
        os.path.join(settings.BASE_DIR, 'logs', 'user_activity.log'),
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger 