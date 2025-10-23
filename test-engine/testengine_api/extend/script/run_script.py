def exec_script(script, context):
    if script is None: return

    # script = "from apirunner.extend.functions import * \n" + script
    # print(script)
    exec(script, {"context": context})
    print(context)
