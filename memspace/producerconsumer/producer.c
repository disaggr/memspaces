
#ifdef HAVE_CONFIG_H
# include <config.h>
#endif

#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <time.h>
#include <stdio.h>
#include <libmemspace/libmemspace.h>


int
main (void)
{
  srand(time(NULL));

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
      res = memspace_write(space, "%u%u", i++, rand());
      if (res)
        {
          perror("memspace_write");
          exit(res);
        }

      sleep(1);
    }

  return 0;
}
