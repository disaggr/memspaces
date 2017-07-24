/******************************************************************************
 *    memspaces - tuple spaces in shared memory                               *
 *    Copyright (C) 2017  Andreas Grapentin                                   *
 *                                                                            *
 *    This program is free software: you can redistribute it and/or modify    *
 *    it under the terms of the GNU General Public License as published by    *
 *    the Free Software Foundation, either version 3 of the License, or       *
 *    (at your option) any later version.                                     *
 *                                                                            *
 *    This program is distributed in the hope that it will be useful,         *
 *    but WITHOUT ANY WARRANTY; without even the implied warranty of          *
 *    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the           *
 *    GNU General Public License for more details.                            *
 *                                                                            *
 *    You should have received a copy of the GNU General Public License       *
 *    along with this program.  If not, see <http://www.gnu.org/licenses/>.   *
 ******************************************************************************/

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
      fprintf(stderr, "usage: %s [SHM...]\n", argv[0]);
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
