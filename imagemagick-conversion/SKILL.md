---
model: haiku
created: 2025-12-16
modified: 2025-12-16
reviewed: 2025-12-16
name: imagemagick-conversion
description: |
  Convert and manipulate images with ImageMagick. Covers format conversion,
  resizing, batch processing, quality adjustment, and image transformations.
  Use when user mentions image conversion, resizing images, ImageMagick,
  magick command, batch image processing, or thumbnail generation.
---

# ImageMagick Image Conversion

**Project:** Project-independent
**Gitignored:** Yes

## Trigger

Use this skill when users request image manipulation tasks including:
- Converting between image formats (PNG, JPEG, WebP, GIF, TIFF, etc.)
- Resizing images (dimensions, percentages, aspect ratios)
- Batch processing multiple images
- Adjusting image quality and compression
- Creating thumbnails
- Basic image transformations (rotate, flip, crop)

## Overview

ImageMagick is a powerful command-line tool for image processing. This skill provides guidance for using the `magick` command to perform common image conversion and manipulation tasks.

**Key Command Pattern:**
```bash
magick input-file [options] output-file
```

## Common Use Cases

### Format Conversion

**Basic format conversion:**
```bash
magick image.jpg image.png
magick photo.png photo.webp
```

**Batch convert all JPEGs to PNG:**
```bash
magick mogrify -format png *.jpg
```

**Convert with specific output directory:**
```bash
mkdir -p output
magick mogrify -format webp -path output/ *.jpg
```

### Resizing Images

**Resize by percentage:**
```bash
magick image.jpg -resize 50% output.jpg
```

**Resize to specific width (maintain aspect ratio):**
```bash
magick image.jpg -resize 800x output.jpg
```

**Resize to specific height (maintain aspect ratio):**
```bash
magick image.jpg -resize x600 output.jpg
```

**Resize to fit within dimensions (maintain aspect ratio):**
```bash
magick image.jpg -resize 800x600 output.jpg
```

**Resize to exact dimensions (ignore aspect ratio):**
```bash
magick image.jpg -resize 800x600! output.jpg
```

**Resize only if larger:**
```bash
magick image.jpg -resize '800x600>' output.jpg
```

**Resize only if smaller:**
```bash
magick image.jpg -resize '800x600<' output.jpg
```

### Quality and Compression

**Set JPEG quality (1-100, default 92):**
```bash
magick image.jpg -quality 85 output.jpg
```

**Optimize PNG compression:**
```bash
magick image.png -quality 95 output.png
```

**Create high-quality WebP:**
```bash
magick image.jpg -quality 90 output.webp
```

### Thumbnails

**Generate thumbnail (fast, lower quality):**
```bash
magick image.jpg -thumbnail 200x200 thumb.jpg
```

**Generate thumbnail with padding:**
```bash
magick image.jpg -thumbnail 200x200 -background white -gravity center -extent 200x200 thumb.jpg
```

### Batch Operations

**Resize all images in directory:**
```bash
magick mogrify -resize 800x600 -path resized/ *.jpg
```

**Convert and resize in one operation:**
```bash
magick mogrify -resize 1200x -format webp -quality 85 -path output/ *.jpg
```

**Process specific file types:**
```bash
magick mogrify -resize 50% -path smaller/ *.{jpg,png,gif}
```

### Image Information

**Display image information:**
```bash
magick identify image.jpg
```

**Detailed image information:**
```bash
magick identify -verbose image.jpg
```

### Advanced Transformations

**Rotate image:**
```bash
magick image.jpg -rotate 90 rotated.jpg
```

**Flip horizontally:**
```bash
magick image.jpg -flop flipped.jpg
```

**Flip vertically:**
```bash
magick image.jpg -flip flipped.jpg
```

**Crop to specific region:**
```bash
magick image.jpg -crop 800x600+100+100 cropped.jpg
```

**Auto-orient based on EXIF:**
```bash
magick image.jpg -auto-orient output.jpg
```

**Strip metadata (reduce file size):**
```bash
magick image.jpg -strip output.jpg
```

## Important Notes

### mogrify vs convert

- **`magick mogrify`**: Modifies files in-place or writes to specified path
  - Use `-path` option to preserve originals
  - Efficient for batch operations

- **`magick convert`** (or just `magick`): Creates new files
  - Always preserves original
  - Better for single-file operations

### Performance Tips

1. **Use `-thumbnail` for thumbnails**: Faster than `-resize` for small previews
2. **Use `-strip` to remove metadata**: Reduces file size significantly
3. **Batch operations**: Process multiple files in one `mogrify` command
4. **Quality settings**: 85-90 is usually optimal for JPEG (balances size/quality)

### Format Recommendations

- **JPEG**: Photos, complex images with gradients (lossy)
- **PNG**: Screenshots, graphics with transparency (lossless)
- **WebP**: Modern format, excellent compression (lossy or lossless)
- **GIF**: Simple animations, limited colors
- **TIFF**: Archival, high-quality storage

## Safety Considerations

**Always test commands on copies first:**
```bash
# Create test directory
mkdir -p test-output

# Test on single file
magick original.jpg -resize 50% test-output/test.jpg

# Verify result before batch processing
```

**Use `-path` with mogrify to preserve originals:**
```bash
# This preserves originals in current directory
magick mogrify -resize 800x -path resized/ *.jpg
```

**Quote wildcards in shell:**
```bash
# Prevents premature shell expansion
magick mogrify -resize '800x600>' -path output/ '*.jpg'
```

## Common Patterns

### Web Optimization Workflow

```bash
# Create optimized versions for web
mkdir -p web-optimized

# Convert to WebP with quality 85, resize to max 1920px width
magick mogrify -resize 1920x -quality 85 -format webp -path web-optimized/ *.jpg

# Strip metadata to reduce size
magick mogrify -strip web-optimized/*.webp
```

### Thumbnail Generation

```bash
# Create thumbnail directory
mkdir -p thumbnails

# Generate 300x300 thumbnails with white padding
for img in *.jpg; do
  magick "$img" -thumbnail 300x300 -background white -gravity center -extent 300x300 "thumbnails/${img%.jpg}_thumb.jpg"
done
```

### Multi-Format Export

```bash
# Export to multiple formats for compatibility
mkdir -p exports/{png,webp,jpg}

for img in source/*.png; do
  name=$(basename "$img" .png)
  magick "$img" -quality 90 "exports/png/$name.png"
  magick "$img" -quality 85 "exports/webp/$name.webp"
  magick "$img" -quality 85 "exports/jpg/$name.jpg"
done
```

## Troubleshooting

**Check ImageMagick version:**
```bash
magick -version
```

**Verify supported formats:**
```bash
magick identify -list format
```

**Test command on single file first:**
```bash
# Always test before batch operations
magick test-image.jpg -resize 50% test-output.jpg
```

## When to Use This Skill

**✓ Use this skill for:**
- Format conversions between standard image types
- Resizing operations (dimensions, percentages)
- Quality adjustments and compression
- Batch processing workflows
- Generating thumbnails or previews
- Basic transformations (rotate, crop, flip)

**✗ Don't use this skill for:**
- Advanced photo editing (use GIMP, Photoshop)
- Complex filters or effects (consider dedicated tools)
- Video processing (use FFmpeg)
- Vector graphics (use Inkscape, Illustrator)

## Integration with Workflows

This skill complements other development workflows:
- **Web development**: Optimize images for deployment
- **Documentation**: Generate screenshots and diagrams
- **CI/CD**: Automate image processing in pipelines
- **Content creation**: Prepare images for various platforms

The `magick` command is typically available via Homebrew (`brew install imagemagick`) or system package managers.