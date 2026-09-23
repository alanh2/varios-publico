#!/usr/bin/env bash
# Genera el video de fondo del hero desde el reel original. Correr de nuevo si cambia el fuente.
set -e
FF=${FF:-ffmpeg}                      # binario estático en ~/.local/bin
REEL="../Renders torre y amenidades/LUXOR 500 VIDEO AJUSTADO.mp4"
mkdir -p video

# sin audio (autoplay muted) y a 1440 de alto: alcanza porque va desenfocado y bajo la sombra
"$FF" -y -v warning -i "$REEL" -vf "scale=-2:'min(1440,ih)'" \
  -c:v libx264 -preset slow -crf 32 -profile:v high -pix_fmt yuv420p -movflags +faststart -an video/hero.mp4

# webm de respaldo para navegadores sin decodificador H.264 (Firefox sin el ffmpeg del sistema)
"$FF" -y -v warning -i video/hero.mp4 -c:v libvpx-vp9 -crf 44 -b:v 0 -row-mt 1 -speed 3 -an video/hero.webm

ls -lh video
