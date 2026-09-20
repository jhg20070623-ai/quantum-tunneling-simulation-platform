param(
    [Parameter(Mandatory = $true)]
    [string]$Pptx,
    [Parameter(Mandatory = $true)]
    [string]$OutDir
)

$ErrorActionPreference = "Stop"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$app = New-Object -ComObject PowerPoint.Application
$app.Visible = [Microsoft.Office.Core.MsoTriState]::msoTrue
$pres = $null
try {
    $pres = $app.Presentations.Open($Pptx, $true, $false, $false)
    $count = $pres.Slides.Count
    $pres.Export($OutDir, "PNG", 1920, 1080)
    Write-Output "slides=$count"
    Write-Output "out=$OutDir"
}
finally {
    if ($null -ne $pres) {
        $pres.Close()
    }
    $app.Quit()
}
