import glob


def get_files():
    conf_files = glob.glob('/home/pi/openocd/tcl/target/*.cfg')
    conf_files = sorted(list(map(lambda x: x.split('/')[-1], conf_files)))
    bin_files = glob.glob('/home/pi/bin_files/*')
    bin_files = sorted(list(map(lambda x: x.split('/')[-1], bin_files)))
    return {'boards': conf_files, 'binary': bin_files}


if __name__ == '__main__':
    print(get_files())
