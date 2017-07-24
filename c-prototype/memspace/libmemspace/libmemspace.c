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

#include <errno.h>
#include <stdlib.h>
#include <stdarg.h>
#include <unistd.h>
#include <stdio.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <string.h>
#include <semaphore.h>
#include "libmemspace.h"

#define __unused __attribute__((unused))
#define PAGESIZE (4 * 1024)

struct _space
{
  char *name;
  int fd;
  size_t size;
  void *data;
};


static int
memspace_shm_init (int fd)
{
  // increase shm size to fit the superpage
  int res = ftruncate(fd, PAGESIZE);
  if (res)
    return -1;

  // map the shm superpage
  void *data = mmap(NULL, PAGESIZE, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
  if (!data)
    return -1;

  // produce a semaphore in the shm
  res = sem_init(data, 1, 1);
  if (res)
    {
      munmap(data, PAGESIZE);
      return -1;
    }

  // unmap the shm superpage
  res = munmap(data, PAGESIZE);
  if (res)
    return -1;

  // unset sticky bit and mark initialization as complete
  res = fchmod(fd, 0666);
  if (res)
    return -1;

  return 0;
}

static int
memspace_shm_create (const char *name)
{
  // attempt to exclusively create the shm
  int fd = shm_open(name, O_RDWR | O_CREAT | O_EXCL, 01666);

  // if it fails, determine if it has been created and return accordingly
  if (fd == -1 && errno == EEXIST)
    {
      errno = 0;
      return shm_open(name, O_RDWR, 0);
    }
  else if (fd == -1)
    return -1;

  // attempt to init the newly created shm
  int res = memspace_shm_init(fd);
  if (res)
    {
      close(fd);
      return -1;
    }

  return fd;
}

static int
memspace_shm_open (const char *name)
{
  // attempt to open the shm
  int fd = shm_open(name, O_RDWR, 0);

  // if it fails, determine if it needs to be created, and create if necessary
  if (fd == -1 && errno == ENOENT)
    {
      errno = 0;
      return memspace_shm_create(name);
    }
  else if (fd == -1)
    return -1;

  // sticky bit is used to indicate completed initialization.
  struct stat st;
  int res = fstat(fd, &st);
  if (res)
    {
      close(fd);
      return -1;
    }

  // busy loop up to a second waiting for sticky bit to vanish
  unsigned int i;
  while (i++ < 100 && st.st_mode & S_ISVTX)
    {
      usleep(1000);
      res = fstat(fd, &st);
      if (res)
        {
          close(fd);
          return -1;
        }
    }

  // fail if sticky is still set, and set ETIMEDOUT
  if (st.st_mode & S_ISVTX)
    {
      errno = ETIMEDOUT;
      return -1;
    }

  return fd;
}

SPACE*
memspace_open (const char *name)
{
  // allocate space for the SPACE structure
  SPACE *space = malloc(sizeof(*space));
  if (!space)
    return NULL;

  space->name = strdup(name);
  if (!space->name)
    {
      free(space);
      return NULL;
    }

  // open the space, create if necessary, wait for finished initialization
  space->fd = memspace_shm_open(name);
  if (space->fd == -1)
    {
      free(space);
      return NULL;
    }

  // get the size of the space
  struct stat st;
  int res = fstat(space->fd, &st);
  if (res)
    {
      close(space->fd);
      free(space);
      return NULL;
    }
  space->size = st.st_size;

  // map the space
  space->data = mmap(NULL, space->size, PROT_READ | PROT_WRITE, MAP_SHARED, space->fd, 0);
  if (!space->data)
    {
      close(space->fd);
      free(space);
      return NULL;
    }

  return space;
}

int
memspace_close (SPACE *space)
{
  // attempt to close the shm fd
  int res = close(space->fd);
  if (res)
    {
      munmap(space->data, space->size);
      free(space);
      return -1;
    }

  // attempt to unmap the memory
  res = munmap(space->data, space->size);
  if (res)
    {
      free(space);
      return -1;
    }

  // free the allocated SPACE memory and return
  free(space->name);
  free(space);
  return 0;
}

int
memspace_unlink (SPACE *space)
{
  // destroy the semaphore
  int res = sem_destroy(space->data);
  if (res)
    return -1;

  // destroy the shm
  res = shm_unlink(space->name);
  if (res)
    return -1;

  // close the memspace
  res = memspace_close(space);
  if (res)
    return -1;

  return 0;
}

int
memspace_read (__unused SPACE* space, __unused const char *format, ...)
{
  printf("read: %s\n", format);

  return 0;
}

int
memspace_write (__unused SPACE *space, __unused const char *format, ...)
{
  printf("write: %s\n", format);

  return 0;
}
