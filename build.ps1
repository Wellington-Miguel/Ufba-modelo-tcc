<#
.SYNOPSIS
    Script de automação do TCC UFBA para Windows PowerShell.
.DESCRIPTION
    Converte blocos em Markdown da pasta content/ para LaTeX padronizado abnTeX2,
    injeta metadados de metadata.yaml e compila o PDF ou gera o arquivo ZIP para o Overleaf.
.EXAMPLE
    .\build.ps1
    .\build.ps1 -Tex
    .\build.ps1 -Pdf
    .\build.ps1 -Zip
    .\build.ps1 -Clean
#>

[CmdletBinding()]
param (
    [switch]$Tex,
    [switch]$Pdf,
    [switch]$Zip,
    [switch]$Clean
)

$argsList = @()

if ($Tex) { $argsList += "--tex" }
if ($Pdf) { $argsList += "--pdf" }
if ($Zip) { $argsList += "--zip" }
if ($Clean) { $argsList += "--clean" }

python build.py $argsList
