param(
    [Parameter(Mandatory = $true)]
    [string]$Docx,
    [Parameter(Mandatory = $true)]
    [string]$Pdf
)

$ErrorActionPreference = "Stop"
$outDir = Split-Path -Parent $Pdf
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
$doc = $null
try {
    $confirmConversions = $false
    $readOnly = $true
    $addToRecent = $false
    $password = ""
    $revert = $false
    $writePassword = ""
    $format = 0
    $encoding = 0
    $visible = $false
    $openAndRepair = $true
    $doc = $word.Documents.Open(
        [ref]$Docx,
        [ref]$confirmConversions,
        [ref]$readOnly,
        [ref]$addToRecent,
        [ref]$password,
        [ref]$password,
        [ref]$revert,
        [ref]$password,
        [ref]$writePassword,
        [ref]$format,
        [ref]$encoding,
        [ref]$visible,
        [ref]$openAndRepair
    )
    $doc.ExportAsFixedFormat($Pdf, 17)
    Write-Output $Pdf
}
finally {
    if ($null -ne $doc) {
        $doc.Close($false)
    }
    $word.Quit()
}
