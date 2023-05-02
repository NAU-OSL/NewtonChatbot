"""Kernel definition"""
import os
import json
from .kernelcomm import KernelComm

COMM = None

def apply_arg(data, arg, value):
    """Change value of dict attribute"""
    args = arg.split('.', 1)
    if len(args) > 1:
        step = args[0]
        if step.startswith('__'):
            step = int(step[2:])
        apply_arg(data[step], args[1], value)
    else:
        data[arg] = value

def init(load_instances=False):
    """Init Notebook communication"""
    # pylint: disable=undefined-variable, global-statement
    global COMM
    if COMM is None:
        COMM = KernelComm(get_ipython(), "newton")
        instances = None
        if load_instances:
            to_load = os.environ["NewtonInstancesPath"].split('?', 1)
            args = json.loads(to_load[1]) if len(to_load) > 1 else {}
            filename = to_load[0]

            with open(filename, 'r', encoding="utf-8") as fil:
                instances = json.load(fil)
                for key, value in args.items():
                    apply_arg(instances, key, value)

        COMM.register(instances)
    else:
        COMM.register()