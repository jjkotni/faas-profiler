import sys
import os
from optparse import OptionParser

def createDirs(expt, bmk, machine):

    log_dir = os.environ['FAAS_ROOT'] + '/logs/' + machine + '/' + expt + '/' + bmk

    if not os.path.exists(log_dir):
        os.makedirs(log_dir, 0o777)
    plot_dir = os.environ['FAAS_ROOT'] + '/plots/' + machine + '/' + expt

    if not os.path.exists(plot_dir):
        os.makedirs(plot_dir, 0o777)

def checkForExptScripts(expt):
    expt_dir      = os.environ['FAAS_ROOT'] + '/experiments/' + expt
    expt_script   = expt_dir + '/expt.sh'
    config_script = expt_dir + '/config.json'

    if not os.path.exists(expt_script):
        raise FileNotFoundError(expt_script)

    #Make the expt script executable
    os.chmod(expt_script, 0o777)

    if not os.path.exists(config_script):
        raise FileNotFoundError(config_script)

def main(argv):
    parser = OptionParser()
    parser.add_option("-e", "--expt",    dest="expt",    metavar="FILE")
    parser.add_option("-b", "--bmk",     dest="bmk",     metavar="FILE")
    parser.add_option("-m", "--machine", dest="machine", metavar="FILE")
    (options, args) = parser.parse_args()

    #Create logs and plots folder
    createDirs(options.expt, options.bmk, options.machine)

    #Check whether expt.sh script exists in experiments folder
    checkForExptScripts(options.expt)
	
if __name__ == "__main__":
    main(sys.argv)