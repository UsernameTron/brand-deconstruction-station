# Desktop Application Assets

This directory contains icons and assets for the Brand Deconstruction Station desktop application.

## Required Icons

- `icon.png` - 512x512 PNG icon for Linux
- `icon.icns` - macOS icon bundle  
- `icon.ico` - Windows icon file

## Icon Design

The icon should reflect the cyberpunk theme with:
- Dark background (#000011)
- Neon green accents (#00ff41)
- Brand deconstruction imagery (mask, circuits, etc.)

## Creating Icons

You can use online converters or tools like:
- PNG to ICNS: https://cloudconvert.com/png-to-icns
- PNG to ICO: https://cloudconvert.com/png-to-ico

Or use electron-icon-builder:
```bash
npm install -g electron-icon-builder
electron-icon-builder --input=icon.png --output=./
```
