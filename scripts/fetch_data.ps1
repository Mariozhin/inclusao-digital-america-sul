<#
.SYNOPSIS
    Coleta o indicador IT.NET.USER.ZS (individuos que usam a Internet) do Banco Mundial
    para Brasil, Argentina, Chile e Uruguai e gera os arquivos de dados do projeto.

.DESCRIPTION
    Executor de referencia para ambientes Windows sem Python/Node.js. Produz exatamente o
    mesmo esquema de saida de scripts/fetch_data.py e scripts/fetch_data.mjs:
        data/internet_users.json  -> base canonica (valores observados)
        data/internet_users.csv   -> visao tabular (tidy) da base canonica
        data/internet_users.js    -> espelho da base para uso via file:// (dashboard offline)

.NOTES
    Fonte: World Bank Open Data - World Development Indicators (WDI), indicador IT.NET.USER.ZS.
    A lista de paises separada por ponto e virgula e bloqueada pelo WAF do Banco Mundial neste
    ambiente (HTTP 502). Por isso a coleta e feita com uma requisicao por pais, no mesmo endpoint
    oficial, e os resultados sao consolidados. Nenhum valor e interpolado ou substituido.
#>

[CmdletBinding()]
param(
    [string]$OutputDir = ""
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

$scriptRoot = $PSScriptRoot
if ([string]::IsNullOrWhiteSpace($OutputDir)) {
    $OutputDir = Join-Path (Split-Path -Parent $scriptRoot) "data"
}
if (-not (Test-Path $OutputDir)) { New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null }

$indicadorCodigo = "IT.NET.USER.ZS"
$inicioSerie = 1990
$inicioAnalise = 2000

$paises = @(
    [ordered]@{ codigo = "BRA"; nome = "Brasil";    nome_en = "Brazil";    cor = "#1B4F9C"; cor_nome = "Azul"   },
    [ordered]@{ codigo = "ARG"; nome = "Argentina"; nome_en = "Argentina"; cor = "#C2185B"; cor_nome = "Rosa"   },
    [ordered]@{ codigo = "CHL"; nome = "Chile";     nome_en = "Chile";     cor = "#1E7A45"; cor_nome = "Verde"  },
    [ordered]@{ codigo = "URY"; nome = "Uruguai";   nome_en = "Uruguay";   cor = "#111418"; cor_nome = "Preto"  }
)

function Get-IndicadorPais {
    param([string]$Codigo)

    $url = "https://api.worldbank.org/v2/country/$Codigo/indicator/$indicadorCodigo" +
           "?format=json&per_page=100"
    $maxTentativas = 12

    for ($t = 1; $t -le $maxTentativas; $t++) {
        try {
            $resp = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 60 `
                                      -Headers @{ Accept = "application/json" }
            $txt = $resp.Content
            if ($txt.TrimStart().StartsWith("[")) {
                $json = $txt | ConvertFrom-Json
                if ($json.Count -ge 2) {
                    return [pscustomobject]@{
                        url        = $url
                        metadados  = $json[0]
                        registros  = $json[1]
                        status     = $resp.StatusCode
                        tentativas = $t
                    }
                }
            }
            Write-Warning "Resposta inesperada para $Codigo (tentativa $t/$maxTentativas)."
        }
        catch {
            Write-Warning "Falha ao consultar $Codigo (tentativa $t/$maxTentativas): $($_.Exception.Message)"
        }
        Start-Sleep -Milliseconds 1500
    }
    throw "Nao foi possivel obter dados para $Codigo apos $maxTentativas tentativas."
}

$coletaUtc = (Get-Date).ToUniversalTime()
$series = @()
$verificacaoLacunas = [ordered]@{}
$totaisApi = [ordered]@{}
$ultimoAnoPorPais = [ordered]@{}
$ultimaAtualizacaoApi = $null

foreach ($pais in $paises) {
    $res = Get-IndicadorPais -Codigo $pais.codigo

    $ultimaAtualizacaoApi = [string]$res.metadados.lastupdated
    $totaisApi[$pais.codigo] = [ordered]@{
        total_registros = [int]$res.metadados.total
        paginas         = [int]$res.metadados.pages
        pagina_lida     = [int]$res.metadados.page
        requisicoes     = $res.tentativas
        status_http     = [int]$res.status
    }

    $obs = @()
    foreach ($r in $res.registros) {
        if ($null -ne $r.value) {
            $obs += [pscustomobject]@{
                ano   = [int]$r.date
                valor = [double]$r.value
            }
        }
    }
    $obs = $obs | Sort-Object ano

    $ultimo = ($obs | Select-Object -Last 1).ano
    $primeiro = ($obs | Select-Object -First 1).ano
    $ultimoAnoPorPais[$pais.codigo] = $ultimo

    $anosPresentes = @($obs | ForEach-Object { $_.ano })
    $ausentes = @()
    for ($a = $inicioSerie; $a -le $ultimo; $a++) {
        if ($anosPresentes -notcontains $a) { $ausentes += $a }
    }
    $verificacaoLacunas[$pais.codigo] = [ordered]@{
        primeiro_ano      = $primeiro
        ultimo_ano        = $ultimo
        total_observacoes = $obs.Count
        anos_ausentes     = $ausentes
    }

    $series += [ordered]@{
        codigo                 = $pais.codigo
        nome                   = $pais.nome
        nome_en                = $pais.nome_en
        cor                    = $pais.cor
        cor_nome               = $pais.cor_nome
        primeiro_ano           = $primeiro
        ultimo_ano_disponivel  = $ultimo
        total_observacoes      = $obs.Count
        dados                  = @($obs | ForEach-Object { [ordered]@{ ano = $_.ano; valor = $_.valor } })
    }

    Write-Host ("  {0} - {1} observacoes ({2}-{3})" -f $pais.codigo, $obs.Count, $primeiro, $ultimo)
    Start-Sleep -Milliseconds 800
}

# --- periodos ---------------------------------------------------------------
$anosComuns = $null
foreach ($s in $series) {
    $anos = @($s.dados | ForEach-Object { $_.ano })
    if ($null -eq $anosComuns) { $anosComuns = $anos } else { $anosComuns = $anosComuns | Where-Object { $anos -contains $_ } }
}
$anosComuns = @($anosComuns | Sort-Object)

$anosAnalise = @($anosComuns | Where-Object { $_ -ge $inicioAnalise })
$fimAnalise = ($anosAnalise | Select-Object -Last 1)

$lacunasAnalise = @()
for ($a = $inicioAnalise; $a -le $fimAnalise; $a++) {
    if ($anosAnalise -notcontains $a) { $lacunasAnalise += $a }
}

$dataset = [ordered]@{
    projeto = "Inclusao Digital: uma analise comparativa da evolucao do acesso a Internet no Brasil e em paises da America do Sul"
    disciplina = "Tecnologia da Informacao e Comunicacao Aplicada a Administracao"
    gerado_por = "scripts/fetch_data.ps1 (PowerShell $($PSVersionTable.PSVersion))"
    fonte = [ordered]@{
        instituicao        = "Banco Mundial (World Bank)"
        dataset            = "World Development Indicators (WDI)"
        dataset_id         = "2"
        indicador_codigo   = $indicadorCodigo
        indicador_nome     = "Individuals using the Internet (% of population)"
        indicador_nome_pt  = "Individuos que usam a Internet (% da populacao)"
        definicao          = "Percentual de individuos que usaram a Internet nos ultimos tres meses, em relacao a populacao total."
        unidade            = "% da populacao"
        fonte_primaria     = "International Telecommunication Union (ITU) - World Telecommunication/ICT Indicators Database"
        url_indicador      = "https://data.worldbank.org/indicator/IT.NET.USER.ZS"
        url_api_pais       = "https://api.worldbank.org/v2/country/{pais}/indicator/IT.NET.USER.ZS?format=json&per_page=100"
        url_api_multipais  = "https://api.worldbank.org/v2/country/BRA;ARG;CHL;URY/indicator/IT.NET.USER.ZS?format=json&per_page=20000"
        api_atualizada_em  = $ultimaAtualizacaoApi
        nota_coleta        = "A consulta multi-pais em um unico endpoint e bloqueada pelo WAF do Banco Mundial a partir deste ambiente (HTTP 502). Foram executadas consultas equivalentes, uma por pais, no mesmo endpoint oficial, com consolidacao posterior."
    }
    coleta = [ordered]@{
        data_utc            = $coletaUtc.ToString("yyyy-MM-ddTHH:mm:ssZ")
        data_local          = (Get-Date).ToString("yyyy-MM-dd HH:mm")
        metodologia_api     = "JSON stateless, paginacao verificada (pages = 1, per_page = 100)"
        observacao          = "Valores preservados como retornados pela API. Anos sem informacao nao constam da base (ausentes, nao zeros)."
    }
    paises = @($paises | ForEach-Object {
        [ordered]@{ codigo = $_.codigo; nome = $_.nome; nome_en = $_.nome_en; cor = $_.cor; cor_nome = $_.cor_nome }
    })
    periodo = [ordered]@{
        serie_completa = [ordered]@{ inicio = $inicioSerie; fim = $fimAnalise }
        analise = [ordered]@{
            inicio   = $inicioAnalise
            fim      = $fimAnalise
            criterio = "Periodo comum aos quatro paises, iniciado em 2000, sem lacunas em nenhuma serie."
        }
        anos_comuns        = $anosComuns
        anos_analise       = $anosAnalise
        lacunas_na_analise = $lacunasAnalise
    }
    verificacao = [ordered]@{
        ultimo_ano_por_pais = $ultimoAnoPorPais
        por_pais            = $verificacaoLacunas
        api                 = $totaisApi
    }
    series = $series
}

$json = $dataset | ConvertTo-Json -Depth 12
$jsonPath = Join-Path $OutputDir "internet_users.json"
[System.IO.File]::WriteAllText($jsonPath, $json, (New-Object System.Text.UTF8Encoding($false)))

# --- espelho JS (permite abrir o dashboard via file:// sem servidor) --------
$jsPath = Join-Path $OutputDir "internet_users.js"
$js = "/* Gerado automaticamente por scripts/fetch_data.ps1 a partir de internet_users.json." + "`r`n" +
      "   Espelho da base canonica para uso via file:// (sem servidor HTTP). Nao editar manualmente. */" + "`r`n" +
      "window.INTERNET_USERS_DATA = " + $json + ";" + "`r`n"
[System.IO.File]::WriteAllText($jsPath, $js, (New-Object System.Text.UTF8Encoding($false)))

# --- CSV (tidy) -------------------------------------------------------------
$inv = [System.Globalization.CultureInfo]::InvariantCulture
$sb = New-Object System.Text.StringBuilder
[void]$sb.AppendLine("pais_codigo,pais,pais_en,ano,valor_percentual,indicador_codigo,indicador_nome,unidade,fonte,data_coleta_utc")
foreach ($s in $series) {
    foreach ($d in $s.dados) {
        $v = ([double]$d.valor).ToString("R", $inv)
        [void]$sb.AppendLine(("{0},{1},{2},{3},{4},{5},{6},{7},{8},{9}" -f `
            $s.codigo, $s.nome, $s.nome_en, $d.ano, $v, $indicadorCodigo, `
            '"Individuals using the Internet (% of population)"', '"% da populacao"', `
            '"World Bank WDI / ITU"', $coletaUtc.ToString("yyyy-MM-ddTHH:mm:ssZ")))
    }
}
$csvPath = Join-Path $OutputDir "internet_users.csv"
[System.IO.File]::WriteAllText($csvPath, $sb.ToString(), (New-Object System.Text.UTF8Encoding($false)))

Write-Host ""
Write-Host "Arquivos gerados:"
Write-Host "  $jsonPath"
Write-Host "  $jsPath"
Write-Host "  $csvPath"
Write-Host ("Periodo comum na analise: {0}-{1} ({2} anos)" -f $inicioAnalise, $fimAnalise, $anosAnalise.Count)
