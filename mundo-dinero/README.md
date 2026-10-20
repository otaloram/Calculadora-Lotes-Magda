# MUNDO DINERO — fábrica de documentales

Convierte un guion en un documental financiero listo para YouTube: voz rioplatense, gráficos bursátiles con datos
reales, motion graphics con identidad propia, música original, subtítulos, miniatura, descripción con capítulos y
subida automática al canal.

```
episode.yaml ──► voz (es-AR-TomasNeural) ──► escenas animadas ──► montaje + música + loudnorm ──► MP4
                     │                                                                             │
                     └─ marcas por palabra ─► subtítulos .srt                      YouTube (privado) ◄┘
```

## Producir un episodio nuevo

1. Copiá `episodes/nvidia/` a `episodes/<tema>/` y editá `episode.yaml`:
   cada escena tiene `text` (lo que se narra) y `visual` (qué se ve).
2. Hacé push. GitHub Actions renderiza el video (~10 min) y lo publica en **Releases** para descargar.
3. Para subirlo directo al canal: **Actions → Mundo Dinero → Run workflow**, marcá *Subir a YouTube*.
   Se sube como **privado** para que lo revises antes de publicar.

## Tipos de visual disponibles

| Tipo | Uso |
|---|---|
| `title` | Apertura de capítulo (kicker, titular, bajada) |
| `statement` | Frase fuerte a pantalla completa |
| `chart` | Cotización real animada: `start`, `end`, `marks`, `drop`, `hline`, `shade`, `log` |
| `invest` | Simulación de USD 10.000 |
| `calendar` | Años de espera con eventos |
| `counter` / `checklist` / `definition` / `timeline` / `runway` | Cifras y conceptos |
| `location` | Mapa esquemático con marcador |
| `people` | Tarjetas de protagonistas (con `photos:` si tenés fotos con licencia) |
| `product` | Producto: usa la foto de `assets/` si existe, si no una ilustración rotulada |
| `image` | Archivo auténtico a pantalla completa con crédito (`recreation: true` la rotula) |
| `diagram` | `datacenter`, `parallel` (CPU vs GPU), `network`, `fabless`, `fork`, `moat`, `science`, `crowd` |
| `brand` | Cierre MUNDO DINERO |

Gráficos de otra empresa: agregá su CSV en `data/` y apuntalo desde `data:` en el YAML.
Pronunciación: el bloque `pronunciation:` cambia solo lo que lee la voz, no los subtítulos.

## Configurar la subida a YouTube (una sola vez)

1. En [Google Cloud Console](https://console.cloud.google.com/): creá un proyecto, habilitá **YouTube Data API v3**,
   configurá la pantalla de consentimiento OAuth y creá un **ID de cliente OAuth** de tipo *Aplicación de escritorio*.
2. En tu computadora, obtené el refresh token con la cuenta del canal:
   ```bash
   pip install google-auth-oauthlib
   python -c "from google_auth_oauthlib.flow import InstalledAppFlow as F; c=F.from_client_secrets_file('client_secret.json',['https://www.googleapis.com/auth/youtube.upload','https://www.googleapis.com/auth/youtube.force-ssl']).run_local_server(port=0); print(c.refresh_token)"
   ```
3. En GitHub → *Settings → Secrets and variables → Actions*, creá `YT_CLIENT_ID`, `YT_CLIENT_SECRET` y `YT_REFRESH_TOKEN`.

Nota: los proyectos de API sin verificar por Google suben los videos como privados hasta pasar la auditoría;
la miniatura personalizada requiere un canal verificado por teléfono.

## Correr en tu computadora

```bash
cd mundo-dinero
pip install -r requirements.txt     # y ffmpeg instalado
python -m md.build episodes/nvidia               # versión final
python -m md.build episodes/nvidia --preview     # borrador rápido 540p
python -m md.build episodes/nvidia --only s05,s07  # revisar escenas sueltas
python -m md.upload_youtube build/nvidia-dos-derrumbes --privacy private
```

Entregables en `build/<slug>/`: MP4, `.srt`, `thumbnail.jpg`, `youtube_description.txt` (con capítulos y fuentes),
`produccion_planos.csv` (desglose de planos con tiempos reales), `guion.txt` y `qc_report.json` (control técnico:
resolución, códec, duración, cuadros negros, silencios, loudness −14 LUFS, pico real).

## Límites honestos

- No hay generación de imágenes con IA ni búsqueda automática de fotos: el material auténtico se agrega a mano en
  `assets/` (con su licencia). Sin él, el video usa gráficos e ilustraciones rotuladas, nunca falsas fotos.
- La exactitud editorial (fechas, cifras) se revisa en `verificacion.md`; el QC automático solo cubre lo técnico.
- La voz `edge` usa el servicio gratuito de Microsoft Edge; si dejara de funcionar se puede cambiar el motor en `md/tts.py`.
