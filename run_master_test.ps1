# ----------------------------
# run_master_test.ps1
# ----------------------------

# Ir a la carpeta del proyecto (ajustar si necesario)
Set-Location -Path "C:\Users\Usuario\Desktop\Redes\ProgramacionSobreRedes\PFO3"

# Crear carpetas si no existen
if (!(Test-Path ".\logs")) { mkdir .\logs }
if (!(Test-Path ".\s3_bucket")) { mkdir .\s3_bucket }

# Limpiar carpeta s3_bucket
Remove-Item -Path ".\s3_bucket\*" -Recurse -Force -ErrorAction SilentlyContinue

# Intentar borrar el log (si está en uso, continuar)
try {
    Remove-Item ".\logs\server.log" -Force
} catch {
    Write-Host "[WARN] Log en uso, se continuará."
}

# Ejecutar master_test.py
py master_test.py

Write-Host "`n[INFO] MASTER TEST ejecutado ✅"
