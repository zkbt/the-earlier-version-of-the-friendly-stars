'''
Test basic finder capabilities.
'''
from thefriendlystars.imports import *
from thefriendlystars.centers import *

directory = 'examples'
mkdir(directory)

def test_centers():
    '''
    Can we parse some different options for the center of a Field?
    '''
    a = parse_center('TIC101955023')
    b = parse_center('GJ1132')

    with pytest.raises(NameResolveError):
        c = parse_center('TIC some imaginary star')
        d = parse_center('some imaginary star')
        e = parse_center(1234567890)

if __name__ == '__main__':
    # pull out anything that starts with `test_`
    d = locals()
    tests = [x for x in d if 'test_' in x]
    # run those functions and save their output
    outputs = {k.split('_')[-1]:d[k]()
               for k in tests}
