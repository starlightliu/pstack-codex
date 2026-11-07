$ErrorActionPreference = 'Stop'

if ($args.Count -ne 6) {
    throw 'Usage: log.ps1 <logfile> <phase> <decision> <why> <evidence> <result>'
}

$log = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($args[0])
$null = [IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($log))
$utf8 = [Text.UTF8Encoding]::new($false)
$tab = [string][char]9

if (!(Test-Path -LiteralPath $log) -or (Get-Item -LiteralPath $log).Length -eq 0) {
    [IO.File]::AppendAllText($log, ('ts','phase','decision','why','evidence','result' -join $tab) + [char]10, $utf8)
}

$cells = foreach ($value in $args[1..5]) {
    $cell = $value -replace '[\t\r\n]', ' '
    if ($cell -match '^[=+@-]') {
        $cell = "'" + $cell
    }
    $cell
}

$timestamp = [DateTime]::UtcNow.ToString("yyyy-MM-ddTHH:mm:ss'Z'")
[IO.File]::AppendAllText($log, ((@($timestamp) + $cells) -join $tab) + [char]10, $utf8)
