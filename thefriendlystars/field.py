from .imports import *
from . import io

class Field(Talker):

    def __repr__(self):

        # what's the name of this survey?
        name = self.__class__.__name__

        # what's the target of this particular image
        if type(self.center) == str:
            target = self.center.replace(' ','')
        elif isinstance(self.center, coord.SkyCoord):
            target = self.center.to_string('hmsdms').replace(' ', '')
        elif self.center is None:
            target='allsky'
        else:
            raise ValueError("It's not totally clear what the center should be!")

        # what's the radius out to which this image searched?
        if np.isfinite(self.radius):
            size = self.radius.to('arcsec')
        else:
            size = np.inf # maybe replace with search criteria?

        return f'{name}-{target}-{size:.0f}'.replace(' ', '')

    @property
    def filename(self):
        '''
        What's the default filename for this object?
        '''

        return os.path.join(io.cache_directory, f'{self}.pickled')

    def save(self):
        '''
        Save the hard-to-load data.
        '''
        if io.cache:
            mkdir(io.cache_directory)
            with open(self.filename, 'wb') as file:
                pickle.dump(self._downloaded, file)
                print(f'saved file to {self.filename}')

    def load(self):
        '''
        Load the hard-to-download data.
        '''
        with open(self.filename, 'rb') as file:
            self._downloaded = pickle.load(file)
            print(f'loaded file from {self.filename}')

    def populate(self):
        '''
        Populate the data of this object,
        either by loading a pre-existing local file
        or by downloading from the web.
        '''
        try:
            # load from a local file
            self.load()
        except (IOError, EOFError):
            # download the necessary data from online
            print(f'downloading new data to initialize {self}')
            self.download()
            self.save()
