def createDir(machine, expt, bmk):
    machine_dir = 'logs/' + test_name


    if not os.path.exists(FAAS_ROOT + '/' + log_dir):
        os.makedirs(log_dir, 0o777)

    log_file = log_dir+'/SWI.log'
    Path(FAAS_ROOT + '/' + log_file).touch()
    os.chmod(log_file, 0o777)

    return log_dir, log_file


def main(machine, expt, bmk):
    createLogsDir()

    checkForExptScripts()
	
