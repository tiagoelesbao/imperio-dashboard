@echo off
title Configurar WhatsApp
cd /d "%~dp0"

echo ===============================================
echo    CONFIGURAR WHATSAPP - SISTEMA IMPERIO
echo ===============================================
echo.
echo Pressione ENTER para continuar...
set /p dummy=

echo.
echo Iniciando configuracao...

.\venv\Scripts\python.exe setup_whatsapp_simples.py

echo.
echo Configuracao concluida!
echo.
echo Pressione ENTER para fechar...
set /p dummy=