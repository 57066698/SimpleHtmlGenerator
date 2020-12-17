import yaml

with open('conf/singleline.yaml') as f:
    conf = yaml.load(f, Loader=yaml.FullLoader)

class text:
    def __init__(self,
                 line_args,
                 font_family,
                 max_char_number,
                 font_size,
                 **args
                 ):
        print(line_args)
        print(args)

t = text(conf['line'], **conf['text'])

