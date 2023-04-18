import sys
sys.path.append("./src")
from utils import *
import re

def cli(options):
    '''
    Parses help string into options
    '''
    args = sys.argv[1:]
    for key, value in options.items():

        for n, x in enumerate(args):
            if x == '-'+ key[0] or x == '--'+ key:
                  value = "false" if value == "true" else "true" if value == "false" else args[n+1]
        options[key] = coerce(value)
    return options

def settings(s):
    '''
    Applies regex to identify key value pairs
    '''
    return dict(re.findall("\n[\s]+[-][\S]+[\s]+[-][-]([\S]+)[^\n]+= ([\S]+)", s))

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