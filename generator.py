#!/usr/bin/python3

from random import choice
import argparse
import time
import string

from settings import TMP_DIR

"""
Генератор файла для сортировки с заданной длиной строки и числом строк
"""


def generate_string(size, random_length=False):
    """ Случайная строка длиной size """
    res = ""
    if random_length:
        size = choice(list(range(1, size)))
    for i in range(size):
        res += choice(string.ascii_letters)
    return res


def generate_file(n_strings, string_size, fname=None, random_length=False, verbose=None):
    """ Сгенерировать файл с n_strings случайными строками длиной string_size """
    fname = fname if fname else "rnd_{}.dat".format(time.time())
    with open(fname, "w") as file_out:
        start = time.time()
        for k in range(n_strings):
            if k > 0 and k % 5000 == 0:
                time_left = (n_strings - k) / (k / (time.time() - start))
                if verbose:
                    print("Сгенерировано {} строк, осталось времени ~ {:.2f} c".format(k, time_left))
            file_out.write(generate_string(string_size - 1, random_length) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Сгенерировать файл для сортировки со строками из случайных символов,\
                    число строк num, длина строки len')
    parser.add_argument('--num', help='число строк в файле, по умолчанию 10000', type=int, default=10000)
    parser.add_argument('--len', help='длина строки в файле, по умолчанию 100', type=int, default=100)
    parser.add_argument('--output', help='имя выходного файла, по умолчанию sort_[num]_[len]_[time].txt')
    parser.add_argument('--rnd', help='рандомизировать длину строки, по умолчанию отключено',
                        dest='rnd', action='store_true')
    parser.add_argument('--verbose', help='отчет по каждому шагу, по умолчанию false',
                        dest='verbose', action='store_true')
    args = parser.parse_args()

    filename = "sort_{}_{}_{}.txt".format(args.num, args.len, int(time.time()))
    if args.output:
        filename = args.output

    generate_file(args.num, args.len, filename, args.rnd, args.verbose)
    if args.verbose:
        print("Сгенерирован файл {} на {} строк".format(filename, args.num))
