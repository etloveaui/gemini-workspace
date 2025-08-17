<#
.SYNOPSIS
  Start a Codex-labeled session (recording off by default).
#>
[CmdletBinding()]
param([switch]$Spawn)

$here = Split-Path -Parent $PSCommandPath
. "$here\scripts\session_launcher.ps1" -Agent codex -Spawn:$Spawn

