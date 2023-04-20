#!/usr/bin/env python3
from utils import *
from helper import *
from data import DATA
from utils import *
from tabulate import tabulate


def main():
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
                top_table['top']['data'].append(DATA(data, betters))
                top_table['xpln1']['data'].append(DATA(data, selects(rule, data.rows)))
                top_table['xpln2']['data'].append(DATA(data, selects(rule, data.rows)))
                top_table['all']['data'].append(data)
                top_table['sway1']['data'].append(best)
                top_table['sway2']['data'].append(best)
                top_table['all']['evals'] += 0
                top_table['sway1']['evals'] += evals
                top_table['sway2']['evals'] += evals
                top_table['xpln1']['evals'] += evals
                top_table['xpln2']['evals'] += evals
                top_table['top']['evals'] += len(data.rows)

                for i in range(len(bottom_table)):
                    [base, diff], result = bottom_table[i]
                    if result is None:
                        bottom_table[i][1] = ['=' for _ in range(len(data.cols.y))]
                    for k in range(len(data.cols.y)):
                        if bottom_table[i][1][k] == '=':
                            y0, z0 = top_table[base]['data'][count].cols.y[k], top_table[diff]['data'][count].cols.y[k]
                            is_equal = bootstrap(y0.vals(), z0.vals()) and cliffsDelta(y0.vals(), z0.vals())
                            if not is_equal:
                                bottom_table[i][1][k] = '≠'
                count += 1

        with open(options['file'].replace('/data', '/out').replace('.csv', '.out'), 'w') as outfile:
            headers = [y.txt for y in data.cols.y]
            table = []

            for k, v in top_table.items():
                stats = [k] + [stats_average(v['data'])[y] for y in headers]
                stats += [v['evals'] / 20]
                table.append(stats)

            print(tabulate(table, headers=headers + ["n_evals avg"], numalign="right"))
            print()
            outfile.write(tabulate(table, headers=headers + ["n_evals avg"], numalign="right"))
            outfile.write('\n')

            table = []
            for [base, diff], result in bottom_table:
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