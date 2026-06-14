param(
    [Parameter(Mandatory = $true)]
    [string]$AssetsDir,
    [Parameter(Mandatory = $true)]
    [string]$OutPptx
)

$ErrorActionPreference = "Stop"
$outDir = Split-Path -Parent $OutPptx
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

$app = New-Object -ComObject PowerPoint.Application
$app.Visible = [Microsoft.Office.Core.MsoTriState]::msoTrue
$pres = $null
try {
    $pres = $app.Presentations.Add([Microsoft.Office.Core.MsoTriState]::msoTrue)
    $pres.PageSetup.SlideWidth = 960
    $pres.PageSetup.SlideHeight = 540

    $images = Get-ChildItem -LiteralPath $AssetsDir -Filter "slide*.png" | Sort-Object Name
    foreach ($img in $images) {
        $slide = $pres.Slides.Add($pres.Slides.Count + 1, 12)
        [void]$slide.Shapes.AddPicture($img.FullName, $false, $true, 0, 0, $pres.PageSetup.SlideWidth, $pres.PageSetup.SlideHeight)
    }

    $pres.SaveAs($OutPptx, 24)
    Write-Output "saved=$OutPptx"
    Write-Output "slides=$($pres.Slides.Count)"
}
finally {
    if ($null -ne $pres) { $pres.Close() }
    $app.Quit()
}
