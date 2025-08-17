<#
.SYNOPSIS
  Start a Gemini-labeled session (recording off by default).
#>
[CmdletBinding()]
param(
  [switch]$Spawn,
  [switch]$Extras
)

$here = Split-Path -Parent $PSCommandPath
. "$here\scripts\session_launcher.ps1" -Agent gemini -Spawn:$Spawn -Extras:$Extras

