import tomli as tomlib 
import argparse 

def get_args():
    argparser = argparse.ArgumentParser(description=__doc__)
    argparser.add_argument(
        '-c', '--config_file',
        metavar='C',
        default='None',
        help='The Configuration file')
    args = argparser.parse_args()
    return args.config_file

def get_configs():
  config_file = get_args()
  with open(str(config_file), 'rb') as f:
    configs = tomlib.load(f)
  return configs

if __name__=='__main__':
  print('whaddup')
  print(get_configs())