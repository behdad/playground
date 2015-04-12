/*
 * Copyright 2015 Google Inc. All rights reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 * Google contributors: Behdad Esfahbod
 */

#include <cairo-ft.h>

#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <assert.h>
#include <string.h>


#define SCALE 1
#define MARGIN 64
#define SIZE 512


static cairo_t *create_image(void) {
  cairo_surface_t *surface = cairo_image_surface_create(CAIRO_FORMAT_ARGB32,
                                                        (SIZE+2*MARGIN)*SCALE,
                                                        (SIZE+2*MARGIN)*SCALE);
  cairo_t *cr = cairo_create(surface);
  cairo_surface_destroy(surface);
  return cr;
}

#if 0
static cairo_surface_t *texture_map(cairo_surface_t *src,
                                    cairo_surface_t *tex) {
  uint32_t *s = (uint32_t *) cairo_image_surface_get_data(src);
  unsigned int width  = cairo_image_surface_get_width(src);
  unsigned int height = cairo_image_surface_get_height(src);
  unsigned int sstride = cairo_image_surface_get_stride(src) / 4;

  cairo_surface_t *dst = cairo_image_surface_create(CAIRO_FORMAT_ARGB32,
                                                    width, height);
  uint32_t *d = (uint32_t *) cairo_image_surface_get_data(dst);
  unsigned int dstride = cairo_image_surface_get_stride(dst) / 4;

  uint32_t *t = (uint32_t *) cairo_image_surface_get_data(tex);
  unsigned int twidth  = cairo_image_surface_get_width(tex);
  unsigned int theight = cairo_image_surface_get_height(tex);
  unsigned int tstride = cairo_image_surface_get_stride(tex) / 4;

  assert(twidth == 256 && theight == 256);

  for (unsigned int y = 0; y < height; y++) {
    for (unsigned int x = 0; x < width; x++) {
      unsigned int pix = s[x];
      unsigned int sa = pix >> 24;
      unsigned int sr = (pix >> 16) & 0xFF;
      unsigned int sg = (pix >> 8) & 0xFF;
      unsigned int sb = pix & 0xFF;
      if (sa == 0) {
        d[x] = 0;
        continue;
      }
      if (sa != 255) {
        sr = sr * 255 / sa;
        sg = sg * 255 / sa;
        sb = sb * 255 / sa;
      }
      assert(sb >= 127 && sb <= 129);
      d[x] = t[tstride * sg + sr];
    }
    s += sstride;
    d += dstride;
  }
  cairo_surface_mark_dirty(dst);

  return dst;
}
#endif

static void
kemmings (cairo_font_face_t *cr_face, uint32_t gid)
{
  cairo_t *cr = create_image ();
  cairo_set_source_rgba (cr, 1, 1, 1, 1);
  cairo_paint (cr);
  cairo_set_source_rgb (cr, 0, 0, 0);

  cairo_translate (cr, MARGIN, MARGIN);
  cairo_set_font_face (cr, cr_face);
  cairo_set_font_size (cr, SIZE);

  cairo_glyph_t glyph = {0, 0, 0};
  glyph.index = gid;
  glyph.y = SIZE * .8;

  cairo_show_glyphs (cr, &glyph, 1);

  cairo_surface_write_to_png (cairo_get_target (cr), "out.png");
  cairo_destroy (cr);
}

int main(int argc, char **argv)
{
  if (argc != 3) {
    fprintf(stderr, "Usage: kemmings font.ttf unichar\n");
    return 1;
  }

  const char *fontfile = argv[1];
  uint32_t unichar = strtol (argv[2], NULL, 16);

  FT_Library library;
  FT_Init_FreeType(&library);

  FT_Face ft_face;
  FT_New_Face(library, fontfile, 0, &ft_face);

  cairo_font_face_t *cr_face = cairo_ft_font_face_create_for_ft_face (ft_face, 0);

  unsigned int gid = FT_Get_Char_Index (ft_face, unichar);

  kemmings (cr_face, gid);

  cairo_font_face_destroy (cr_face);
  FT_Done_Face (ft_face);
  FT_Done_FreeType (library);

  return 0;
}
