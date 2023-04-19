import sys
from os import listdir
from os.path import join, isfile

from texttable import Texttable

from data import *

sys.path.append("../src")
from utils import *
import re


def cli(options):
    args = sys.argv[1:]
    for k, v in options.items():
        for n, x in enumerate(args):
            if x == '-'+k[0] or x == '--'+k:
                if v == 'false':
                    v = 'true'
                elif v == 'true':
                    v = 'false'
                else:
                    v = args[n+1]
        options[k] = coerce(v)
    return options

def settings(s):
    '''
    Applies regex to identify key value pairs
    '''
    return dict(re.findall("\n[\s]+[-][\S]+[\s]+[-][-]([\S]+)[^\n]+= ([\S]+)", s))


def main_tables():
    y, n, saved = 0, 0, deepcopy(options)
    for k, v in cli(settings(help)).items():
        options[k] = v
        saved[k] = v

    data_file_path = '../etc/data/'
    output_file_path = '../etc/out/'
    files = [f for f in listdir(data_file_path) if isfile(join(data_file_path, f))]

    for file in files:
        table_1, table_1_dict, table_2 = get_tables()

        stdoutOrigin = sys.stdout
        output_file = open("{}{}.out".format(output_file_path, file[:-4]), "w", encoding="utf-8")
        sys.stdout = output_file

        if options['help']:
            print(help)
        else:
            counter = 0
            while counter < 20:
                data = DATA(options['file'])
                best, rest, evals = data.sway()
                xp = DATA.xpln(best, rest)
                rule, temp = xp.xpln(data, best, rest)
                if rule != -1:

                    selects_values = DATA.selects(rule, data.rows)
                    data_selects_values = [s for s in selects_values if s is not None]
                    data_one = data.clone(data_selects_values)

                    values, temp2 = data.betters(len(best.rows))
                    table_1_dict['top'].append(DATA.clone(values))

                    table_1_dict['xpln1'].append(data_one)
                    table_1_dict['xpln2'].append(data_one)
                    table_1_dict['all'].append(data)
                    table_1_dict['sway1'].append(best)
                    table_1_dict['sway2'].append(best)

                    for j in range(len(table_2)):
                        [base, diff], result = table_2[j]
                        if result is None:
                            table_2[j][1] = ['=' for _ in range(len(data.cols.y))]
                        for k in range(len(data.cols.y)):
                            if table_2[j][1][k] == '=':
                                y0, z0 = table_1_dict[base]['data'][counter].cols.y[k], table_1_dict[diff]['data'][counter].cols.y[k]
                                is_equal = bootstrap(y0.vals(), z0.vals()) and cliffsDelta(y0.vals(), z0.vals())
                                if not is_equal:
                                    table_2[j][1][k] = '≠'
                    counter += 1

            table_temp = Texttable()

            headers = [y.txt for y in data.cols.y]
            table1_first_row = [" "] + headers
            table1_rows = [table1_first_row]

            for k, v in table_1_dict.items():
                stats = [k] + [stats_average(v)[y] for y in headers]
                table1_rows.append(stats)

            table_temp.add_rows(table1_rows)

            table_temp_2= Texttable()

            table2_first_row = [" "] + headers
            table2_rows_formatted = [table2_first_row]

            for [base, diff], result in table_2:
                table2_rows_formatted.append([f"{base} to {diff}"] + result)

            print(table2_rows_formatted)
            table_temp_2.add_rows(table2_rows_formatted)

            with open("{}{}.tables".format('./etc/out/', file[:-4]), "w", encoding="utf-8") as table_file:
                table_file.writelines(table_temp.draw())
                table_file.writelines("\n\n\n")
                table_file.writelines(table_temp_2.draw())

            print(table_temp.draw())
            print(table_temp_2.draw())

            sys.stdout = stdoutOrigin
            output_file.close()


def main(options, help, funs):
    '''
    Runs tests and prints output
    '''
    y,n = 0,0
    saved = {}
    fails = 0
    for k,v in cli(settings(help)).items():
        options[k] = v
        saved[k] = v

    if options['help']:
        print(help)
    else:
        for what, fun in funs.items():
            if options['go'] == 'all' or options['go'] == what:
                print("--")
                for k,v in saved.items():
                    options[k] = v
                Seed = options['seed']
                if funs[what]() == False:
                    fails += 1
                    n += 1
                    print("❌ fail:", what)
                else:
                    y += 1
                    print("✅ pass:", what)
    if y+n>0:
        print("🔆",{'pass' : y, 'fail' : n, 'success' :100*y/(y+n)//1})
    sys.exit(n)


def get_tables():
    table_one = []

    table_one_dict = {'all': [], 'sway1': [], 'sway2': [], 'xpln1': [], 'xpln2': [], 'top': []}

    table_two = [[['all', 'all'], None],
                 [['all', 'sway1'], None],
                 [['sway1', 'sway2'], None],
                 [['sway1', 'xpln1'], None],
                 [['sway2', 'xpln2'], None],
                 [['sway1', 'top'], None]]

    return table_one, table_one_dict, table_two