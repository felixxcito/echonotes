# Fuentes de los diagramas de clase

Los PNG de la carpeta superior (`diagrama clase.png`, `diagrama clase aplicacion.png`,
`diagrama clase dominio.png`) se generan desde estos archivos Mermaid:

| Archivo fuente | Imagen generada | Contenido |
|---|---|---|
| `diagrama_clase.mmd` | `diagrama clase.png` | Vista general: frontend, aplicación y dominio |
| `diagrama_clase_aplicacion.mmd` | `diagrama clase aplicacion.png` | CLI, API FastAPI, servicios y componentes React |
| `diagrama_clase_dominio.mmd` | `diagrama clase dominio.png` | Modelo de transcripción, transformer, tokenizer y eventos |

Para regenerarlos (requiere Node.js y Google Chrome):

```bash
npx @mermaid-js/mermaid-cli@11 -i diagrama_clase.mmd -o "../diagrama clase.png" -c mermaid-config.json -w 1800 -s 2 -b white
```

También se pueden pegar en https://mermaid.live para editarlos visualmente.
