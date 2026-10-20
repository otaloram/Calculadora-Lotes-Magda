# Material de archivo (opcional)

Colocá acá fotos auténticas con licencia que permita su uso (p. ej. Wikimedia Commons con CC BY / CC BY-SA,
material de prensa de Nvidia). Si un archivo referenciado en `episode.yaml` no existe, la escena usa
automáticamente una ilustración rotulada «Ilustración».

Nombres esperados por el episodio de Nvidia:

| Archivo | Escena | Qué debe mostrar |
|---|---|---|
| `nv1.jpg` | s22 | Chip NV1 o tarjeta Diamond Edge 3D |
| `riva128.jpg` | s29 | Chip/tarjeta RIVA 128 |
| `geforce256.jpg` | s32 | Tarjeta GeForce 256 |

Para agregar créditos, sumá `credit: "Foto: Autor, CC BY-SA 4.0, Wikimedia Commons"` en la escena.
Para fotos de los fundadores: `photos: [assets/huang.jpg, assets/malachowsky.jpg, assets/priem.jpg]` en s18.
Para una escena de archivo a pantalla completa: `visual: {type: image, file: assets/x.jpg, credit: "...", caption: "..."}`
(agregá `recreation: true` si es una recreación).
