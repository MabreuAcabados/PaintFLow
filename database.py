# -*- coding: utf-8 -*-
"""
Database Pool - Gestión de conexiones a PostgreSQL
"""

import psycopg2
from psycopg2 import pool
import logging
from typing import Generator

logger = logging.getLogger(__name__)

class DatabasePool:
    """Pool de conexiones a PostgreSQL"""
    
    _pool = None
    
    @classmethod
    def init_pool(cls):
        """Inicializar pool de conexiones"""
        try:
            cls._pool = psycopg2.pool.SimpleConnectionPool(
                1, 10,
                host="dpg-d1b18u8dl3ps73e68v1g-a.oregon-postgres.render.com",
                port=5432,
                database="labels_app_db",
                user="admin",
                password="KCFjzM4KYzSQx63ArufESIXq03EFXHz3"
            )
            logger.info("✅ DatabasePool initialized")
        except Exception as e:
            logger.error(f"❌ Error initializing DatabasePool: {e}")
            raise
    
    @classmethod
    def get_connection(cls):
        """Obtener conexión del pool"""
        if cls._pool is None:
            cls.init_pool()
        return cls._pool.getconn()
    
    @classmethod
    def return_connection(cls, conn):
        """Devolver conexión al pool"""
        if cls._pool is not None:
            cls._pool.putconn(conn)
    
    @classmethod
    def close_pool(cls):
        """Cerrar pool de conexiones"""
        if cls._pool is not None:
            cls._pool.closeall()
            logger.info("✅ DatabasePool closed")

def get_db() -> Generator:
    """Dependency para FastAPI que proporciona una conexión a la BD"""
    conn = DatabasePool.get_connection()
    try:
        yield conn
    except Exception as e:
        # En caso de error, hacer rollback
        try:
            conn.rollback()
        except:
            pass
        raise
    finally:
        # Siempre devolver conexión al pool
        DatabasePool.return_connection(conn)
