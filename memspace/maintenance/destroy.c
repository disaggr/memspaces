
#ifdef HAVE_CONFIG_H
# include <config.h>
#endif

#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <stdio.h>
#include <errno.h>
#include <libmemspace/libmemspace.h>


int
main (int argc, char *argv[])
{
  if (argc == 1)
    {
      fprintf(stderr, "usage: %s [SHM] ...", argv[0]);
      exit(2);
    }

  unsigned int error = 0;

  int i;
  for (i = 1; i < argc; ++i)
    {
      SPACE *space = memspace_open(argv[i]);
      if (space == NULL)
        {
          perror("memspace_open");
          error = 1;
          errno = 0;
          continue;
        }

      int res = memspace_unlink(space);
      if (res)
        {
          perror("memspace_unlink");
          error = 1;
          errno = 0;
          int res = memspace_close(space);
          if (res)
            {
              perror("memspace_close");
              error = 1;
              errno = 0;
              continue;
            }
        }
    }

  return error;
}
