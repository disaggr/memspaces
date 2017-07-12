
#ifdef HAVE_CONFIG_H
# include <config.h>
#endif

#include <stdlib.h>
#include <fcntl.h>
#include <stdio.h>
#include <libmemspace/libmemspace.h>


int
main (void)
{
  SPACE *space = memspace_open("/ProducerConsumerExample");
  if (space == NULL)
    {
      perror("memspace_open");
      exit(-1);
    }

  unsigned int i = 0;

  int res;
  while (1)
    {
      unsigned int data;
      res = memspace_read(space, "%u%?u", i++, &data);
      if (res)
        {
          perror("memspace_read");
          exit(res);
        }

      printf("%u: %u\n", i, data);
    }

  return 0;
}
