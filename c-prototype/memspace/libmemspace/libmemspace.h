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

#pragma once

typedef struct _space SPACE;

SPACE* memspace_open(const char *name);

int memspace_close(SPACE *space);

int memspace_unlink(SPACE *space);

int memspace_read(SPACE *space, const char *format, ...);

int memspace_write(SPACE *space, const char *format, ...);
