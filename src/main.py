#!/usr/bin/env python3
from utils import *
from helper import *
from data import DATA
from utils import *
from tabulate import tabulate

def main(options, help, funs):
    y, n = 0, 0
    saved = {}
    fails = 0
    for k, v in cli(settings(help)).items():
        options[k] = v
        saved[k] = v

    if options['help']:
        print(help)
    else:
        for what, fun in funs.items():
            if options['go'] == 'all' or options['go'] == what:
                print("--")
                for k, v in saved.items():
                    options[k] = v
                Seed = options['seed']
                if not funs[what]():
                    fails += 1
                    n += 1
                    print("❌ fail:", what)
                else:
                    y += 1
                    print("✅ pass:", what)
    if y + n > 0:
        print("🔆", {'pass': y, 'fail': n, 'success': 100 * y / (y + n) // 1})
    sys.exit(n)

def generate_tables():
    y, n, saved = 0, 0, deepcopy(options)
    for k, v in cli(settings(help)).items():
        options[k] = v
        saved[k] = v
    if options['help']:
        print(help)
    else:
        count = 0
        while count < 20:
            data = DATA(options['file'])
            best, rest, evals = data.sway()
            xp = Helper(best, rest)
            rule, _ = xp.xpln(data, best, rest)
            if rule != -1:
                betters, _ = data.betters(len(best.rows))
                table_one['top']['data'].append(DATA(data, betters))
                table_one['xpln1']['data'].append(DATA(data, selects(rule, data.rows)))
                table_one['xpln2']['data'].append(DATA(data, selects(rule, data.rows)))
                table_one['all']['data'].append(data)
                table_one['sway1']['data'].append(best)
                table_one['sway2']['data'].append(best)

                for i in range(len(table_two)):
                    [base, diff], result = table_two[i]
                    if result is None:
                        table_two[i][1] = ['=' for _ in range(len(data.cols.y))]
                    for k in range(len(data.cols.y)):
                        if table_two[i][1][k] == '=':
                            y0, z0 = table_one[base]['data'][count].cols.y[k], table_one[diff]['data'][count].cols.y[k]
                            is_equal = bootstrap(y0.vals(), z0.vals()) and cliffsDelta(y0.vals(), z0.vals())
                            if not is_equal:
                                table_two[i][1][k] = '≠'
                count += 1

        with open(options['file'].replace('/data', '/out').replace('.csv', '.out'), 'w') as outfile:
            headers = [y.txt for y in data.cols.y]
            table = []

            for k, v in table_one.items():
                stats = [k] + [stats_average(v['data'])[y] for y in headers]
                stats += [v['evals'] / 20]
                table.append(stats)

            print(tabulate(table, headers=headers, numalign="right"))
            print()
            outfile.write(tabulate(table, headers=headers, numalign="right"))
            outfile.write('\n')

            table = []
            for [base, diff], result in table_two:
                table.append([f"{base} to {diff}"] + result)
            print(tabulate(table, headers=headers, numalign="right"))
            outfile.write(tabulate(table, headers=headers, numalign="right"))

        for what, fun in egs.items():
            if options['go'] == 'all' or options['go'] == what:
                for k, v in saved.items():
                    options[k] = v
                print('▶️ ', what, ('-') * (60))
                if not egs[what]():
                    n += 1
                    print('❌ fail:', what)
                else:
                    y += 1
                    print('✅ pass:', what)
    if y + n > 0:
        print("🔆", {'pass': y, 'fail': n, 'success': 100 * y / (y + n) // 1})
    sys.exit(n)


if __name__ == '__main__':
    main()