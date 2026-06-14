$ErrorActionPreference = "Stop"

$outDir = "C:\Users\jiang\Documents\Codex\2026-06-14\d-cdrivearchive-desktop-contest-2026\work\rendered_application_enhanced_word"
$docx = Join-Path $outDir "application_enhanced.docx"
$pdf = Join-Path $outDir "application_enhanced.pdf"

New-Item -ItemType Directory -Force -Path $outDir | Out-Null

$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
$doc = $null
try {
    $doc = $word.Documents.Open($docx, $false, $true)
    $doc.ExportAsFixedFormat($pdf, 17)
}
finally {
    if ($null -ne $doc) {
        $doc.Close($false)
    }
    $word.Quit()
}

Write-Output $pdf
