import subprocess 
import sys

def main(params):
    workers = int(params.get('workers', '1'))
    script = params.get('script', 'bm_deltablue.py').strip()
    cmd = "python3.6 "+ script + " -l 1"

    output = {}
    for worker in range(workers):
        p = subprocess.run([cmd], shell=True)
        #output[str(worker)] = p.returncode

    output['output'] = 'Executed ' + str(worker) + ' processe(s)!'
    return output

if __name__ == '__main__':
    main({'workers': sys.argv[1], 'script': sys.argv[2]})
