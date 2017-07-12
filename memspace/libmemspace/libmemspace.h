
#pragma once

typedef struct _space SPACE;

SPACE* memspace_open(const char *name);

int memspace_close(SPACE *space);

int memspace_unlink(SPACE *space);

int memspace_read(SPACE *space, const char *format, ...);

int memspace_write(SPACE *space, const char *format, ...);
