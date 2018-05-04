#!/usr/bin/python3

"""
Сортировка большого текстового файла, не влезающего в память.
Для проверки работоспособности нужен еще генератор таких файлов,
принимающий в качестве параметров количество строк и их длину.
"""

import time
import os
import re
import resource
import heapq
import argparse
from subprocess import Popen, PIPE

from settings import TMP_DIR, FILE, MEMORY_LIMIT, CHUNK_SIZE


def limit_memory(size=4):
    """ Ограничить общую память, доступную процессу при выполнении """
    Mb = 1024 * 1024
    soft, hard = resource.getrlimit(resource.RLIMIT_AS)
    resource.setrlimit(resource.RLIMIT_AS, (size * Mb, size * Mb))


def get_chunk_list_size(MEMORY_LIMIT, string_size):
    """
    Определить размер списка/chunk для входного файла, который точно поместится в память,
    с учетом средней длины строки в файле string_size
    10/11 - запас 10% на хранение list в памяти
    """
    chunk_size = int((MEMORY_LIMIT * 1024 * 1024 // string_size) * float(10/11.0))
    return chunk_size


def get_memory():
    """ Считать доступную свободную память вместе с кешем и буфером """
    with open('/proc/meminfo', 'r') as mem:
        free_memory = 0
        for i in mem:
            sline = i.split()
            if str(sline[0]) in ('MemFree:', 'Buffers:', 'Cached:'):
                free_memory += int(sline[1])
    return free_memory * 1024


def get_file_strings_number(fname):
    """ Получить число строк в файле через wc """
    fh = os.popen("wc -l {}".format(fname))
    result = fh.read()

    lines = 0
    m = re.search(r'^(\d+)', result)
    if m:
        lines = int(m.group(1))
    return lines


def write_chunk_file(heap, chunks, tmp_dir):
    """ Записать отсортированную кучу heap в chunk файл """
    with open("{}chunk_{}.txt".format(tmp_dir, chunks), "w") as chnk:
        for i in range(len(heap)):
            chnk.write("{}\n".format(heapq.heappop(heap)))


def sort_with_chunks(filename, chunk_size, tmpdir, verbose):
    """ Основная процедура сортировки с chunks """
    chunks = 0
    total_file_size = os.stat(filename).st_size
    estimated_chunks = total_file_size // chunk_size + 1
    start = time.time()

    with open(filename) as f:
        total_list_size = 0
        heap = []
        for line in f:
            line = line.rstrip()

            total_list_size += len(line)
            # разбиваем на chunks с запасом 10% (запас на хранение list в памяти)
            if total_list_size * 1.1 > chunk_size:
                write_chunk_file(heap, chunks, tmpdir)
                heap = []
                total_list_size = 0
                chunks += 1

                if verbose:
                    time_left = (estimated_chunks - chunks) / (chunks / (time.time() - start))
                    print("Обработано {} chunks, осталось времени ~ {:.2f} c".format(chunks, time_left))

            heapq.heappush(heap, line)

        # запишем в файл последний накопленный chunk
        write_chunk_file(heap, chunks, tmpdir)

    if verbose:
        print("Всего {} chunks создано за {:.2f} c. Начинаем merge".format(chunks+1, time.time() - start))
        merge_start = time.time()

    # мержим из полученных отсортированных chunk файлов -
    # в общий отсортированный список, с помощью heapq.merge
    with open("result.txt", "w") as f_res:
        opened_chunks = [open("{}chunk_{}.txt".format(tmpdir, f)) for f in range(chunks + 1)]
        for st in heapq.merge(*opened_chunks):
            f_res.write(st)
        for f in opened_chunks:
            f.close()

    if verbose:
        print("Merge занял {:.2f} c\nСортировка {} строк завершена за {:.2f} с".format(
            time.time() - merge_start, get_file_strings_number(filename), time.time() - start))


if __name__ == "__main__":
    # считать параметры командной строки
    parser = argparse.ArgumentParser(
        description='Отсортировать файл от generator.py с помощью разбиения на chunks,\
                    отсортированные методом heapsort, и объединения полученных\
                    chunks с помощью итератора heapq.merge')
    parser.add_argument('--file', help='входной файл, по умолчанию over_4mb.txt', default=FILE)
    parser.add_argument('--tmpdir', default=TMP_DIR,
        help='путь к временной папке с chunks, по умолчанию {}'.format(TMP_DIR))
    parser.add_argument('--chunksize', help='размер chunk, по умолчанию {} байт'.format(CHUNK_SIZE),
                        default=CHUNK_SIZE, type=int)
    parser.add_argument('--output', help='имя выходного файла, по умолчанию result.txt', default='result.txt')
    parser.add_argument('--tmpfiles', help='не удалять временные файлы chunks, по умолчанию false',
                        dest='tmpfiles', action='store_true')
    parser.add_argument('--verbose', help='не удалять временные файлы chunks, по умолчанию false',
                        dest='verbose', action='store_true')
    args = parser.parse_args()

    if not os.path.exists(args.tmpdir):
        os.system("mkdir {}".format(args.tmpdir))
    os.system("rm -rf {}*".format(args.tmpdir))

    if args.verbose:
        print("Свободный объем ОЗУ: {} байт, размер chunk: {} байт".format(get_memory(), args.chunksize))

    sort_with_chunks(args.file, args.chunksize, args.tmpdir, args.verbose)

    if not args.tmpfiles:
        os.system("rm -rf {}".format(args.tmpdir))
