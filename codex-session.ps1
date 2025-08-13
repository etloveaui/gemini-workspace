<#
.SYNOPSIS
  Start a Codex-labeled session with auto recording.
#>
[CmdletBinding()]
param([switch]$Spawn)

$here = Split-Path -Parent $PSCommandPath
. "$here\scripts\session_launcher.ps1" -Agent codex -Spawn:$Spawn

