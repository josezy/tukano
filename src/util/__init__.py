
def getserial():
    # Extract serial from cpuinfo file
    cpuserial = "0000000000000000"
    try:
        with open('/proc/cpuinfo', 'r') as fp:
            for line in fp:
                if line[0:6] == 'Serial':
                    cpuserial = line[10:26]
    except Exception:
        cpuserial = "ERROR000000000"

    return cpuserial
