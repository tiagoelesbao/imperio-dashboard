"""
Error Handler - Tratamento centralizado de erros
"""
import logging
import traceback
from typing import Dict, Any, Optional
from datetime import datetime
from functools import wraps
import json

logger = logging.getLogger(__name__)


class ImperioError(Exception):
    """Classe base para erros do sistema Imperio"""
    
    def __init__(self, message: str, error_code: str = "UNKNOWN", details: Dict[str, Any] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.timestamp = datetime.now().isoformat()
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converter erro para dicionário"""
        return {
            "error": True,
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp
        }


class DataCollectionError(ImperioError):
    """Erro durante coleta de dados"""
    def __init__(self, message: str, source: str = None, details: Dict[str, Any] = None):
        super().__init__(
            message=message,
            error_code="DATA_COLLECTION_ERROR",
            details={**(details or {}), "source": source}
        )


class APIError(ImperioError):
    """Erro de API externa"""
    def __init__(self, message: str, api_name: str = None, status_code: int = None, details: Dict[str, Any] = None):
        super().__init__(
            message=message,
            error_code="API_ERROR",
            details={
                **(details or {}),
                "api_name": api_name,
                "status_code": status_code
            }
        )


class DatabaseError(ImperioError):
    """Erro de banco de dados"""
    def __init__(self, message: str, operation: str = None, details: Dict[str, Any] = None):
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            details={**(details or {}), "operation": operation}
        )


class ValidationError(ImperioError):
    """Erro de validação de dados"""
    def __init__(self, message: str, field: str = None, value: Any = None, details: Dict[str, Any] = None):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details={
                **(details or {}),
                "field": field,
                "value": str(value) if value else None
            }
        )


class ErrorHandler:
    """Tratamento centralizado de erros"""
    
    @staticmethod
    def handle_error(error: Exception, context: str = None) -> Dict[str, Any]:
        """
        Tratar erro e retornar resposta padronizada
        
        Args:
            error: Exceção ocorrida
            context: Contexto onde ocorreu o erro
        
        Returns:
            Dicionário com informações do erro
        """
        # Log do erro completo
        logger.error(f"Erro em {context or 'desconhecido'}: {str(error)}", exc_info=True)
        
        # Se for um erro customizado
        if isinstance(error, ImperioError):
            return error.to_dict()
        
        # Para outros erros
        error_response = {
            "error": True,
            "error_code": "SYSTEM_ERROR",
            "message": str(error),
            "context": context,
            "timestamp": datetime.now().isoformat()
        }
        
        # Em desenvolvimento, incluir traceback
        import os
        if os.getenv("ENV", "production") == "development":
            error_response["traceback"] = traceback.format_exc()
        
        return error_response
    
    @staticmethod
    def log_error(error: Exception, context: str = None, extra_data: Dict[str, Any] = None):
        """
        Logar erro com contexto adicional
        
        Args:
            error: Exceção ocorrida
            context: Contexto onde ocorreu o erro
            extra_data: Dados adicionais para log
        """
        error_data = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context,
            "timestamp": datetime.now().isoformat(),
            **(extra_data or {})
        }
        
        # Log estruturado
        logger.error(json.dumps(error_data, ensure_ascii=False, indent=2))
        
        # Traceback completo em debug
        logger.debug(f"Traceback:\n{traceback.format_exc()}")
    
    @staticmethod
    def create_error_response(message: str, error_code: str = "ERROR", status_code: int = 500, details: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Criar resposta de erro padronizada
        
        Args:
            message: Mensagem de erro
            error_code: Código do erro
            status_code: Status HTTP
            details: Detalhes adicionais
        
        Returns:
            Resposta formatada
        """
        return {
            "success": False,
            "error": True,
            "error_code": error_code,
            "message": message,
            "status_code": status_code,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }


def handle_exceptions(context: str = None):
    """
    Decorator para tratamento automático de exceções
    
    Args:
        context: Contexto da função
    
    Usage:
        @handle_exceptions(context="coleta_vendas")
        def coletar_vendas():
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_handler = ErrorHandler()
                error_response = error_handler.handle_error(e, context=context or func.__name__)
                
                # Se a função espera retornar um dict
                if func.__annotations__.get('return') in [dict, Dict, Dict[str, Any]]:
                    return error_response
                
                # Caso contrário, re-raise
                raise
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                error_handler = ErrorHandler()
                error_response = error_handler.handle_error(e, context=context or func.__name__)
                
                # Se a função espera retornar um dict
                if func.__annotations__.get('return') in [dict, Dict, Dict[str, Any]]:
                    return error_response
                
                # Caso contrário, re-raise
                raise
        
        # Retornar wrapper apropriado
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return wrapper
    
    return decorator


# Instância global do error handler
error_handler = ErrorHandler()