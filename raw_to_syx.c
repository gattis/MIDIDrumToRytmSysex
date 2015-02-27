
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "../libanalogrytm/inc_ar.h"

#define BUF_SIZE  (1024 * 1024 * 4u)

static void load_file(sU8 *syx, const char *fname, sU32 *retSize) {
   FILE *fh;

   *retSize = 0;

   fh = fopen(fname, "rb");
   if(NULL != fh)
   {
      long sz;

      fseek(fh, 0, SEEK_END);
      sz = ftell(fh);
      fseek(fh, 0, SEEK_SET);

      if(sz <= BUF_SIZE)
      {
         *retSize = (sU32) fread(syx, 1, sz, fh);

         if(*retSize > BUF_SIZE)
         {
            *retSize = 0;
         }
      }

      fclose(fh);
   }
}

static void save_file(sU8 *data, sU32 dataSize, const char *fname) {
   FILE *fh;

   fh = fopen(fname, "wb");
   
   if(NULL != fh)
   {
      (void)fwrite(data, 1, dataSize, fh);
      fclose(fh);
   }
}

static void tc_pattern_raw_to_syx(sU8 *raw, sU8 *syx, const char *fname) {
  sU32 rawSz;
  sU32 syxSz;
  ar_sysex_meta_t meta;
  char outfname[2048];
  sprintf(outfname,"%s.syx",fname);
  S_U16_SET(meta.container_version,257);
  meta.dev_id = 0;
  meta.obj_type = 2;
  meta.obj_nr = 128;  
  ar_error_t err;
  load_file(raw, fname, &rawSz);
  err = ar_pattern_raw_to_syx(syx, raw, rawSz, &syxSz, &meta);
  if (AR_ERR_OK == err) {
    save_file(syx, syxSz, outfname);
    printf("done\n");
  } else {
    printf("error: %u\n", err);
  }
}

int main(int argc, char**argv) {
   sU8 *buf   = malloc(BUF_SIZE * 3);
   sU8 *syx   = buf + BUF_SIZE;
   sU8 *resyx = buf + (BUF_SIZE * 2);

   (void)argc;
   (void)argv;

   memset(buf, 0xCC, BUF_SIZE * 3);

   for (int i = 1; i < argc; i++) {
     tc_pattern_raw_to_syx(buf, syx, argv[i]);
   }

   free(buf);

   return 0;
}
