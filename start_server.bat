@echo off
pwsh -Command "Start-Process pwsh -ArgumentList '-NoExit','-File \"%~dp0run_server.ps1\"' -Verb RunAs"
