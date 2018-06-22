'''
Finder object contains one or more Panels,
each with its own image and catalogs.
The Finder object makes sure all the data
get collected and manages the organization
and visualization.
'''

from panels import *



class Finder:
    def __init__(self, panels=['optical']):
        self.panels = constellation


# define som
class Finder(Talker):
    '''
    A Finder object creates a finder chart,
    containing one or more panels. It's centered
    on a particular location.
    '''

    def __init__(self, name, radius=3*u.arcmin):
        self.star = Star(name)
        self.center = self.star.icrs
        self.radius = radius

    def populateImagesFromSurveys(self, surveys=dss2 + twomass):
        '''
        Load images from archives.
        '''

        # what's the coordinate center?
        coordinatetosearch = '{0.ra.deg} {0.dec.deg}'.format(self.center)

        # query sky view for those images
        paths = astroquery.skyview.SkyView.get_images(
                                    position=coordinatetosearch,
                                    radius=self.radius,
                                    survey=surveys)

        # populate the images for each of these
        self.images = [Image(p[0], s) for p, s in zip(paths, surveys)]

    def populateCatalogsFromSurveys(self, surveys=[Gaia, TwoMass, GALEX, TIC]):

        self.catalogs = {}
        for s in surveys:
            this = s(self.center, self.radius)
            self.catalogs[this.name] = this

    def plotGrid(self):

        N = len(self.images)
        fig = plt.figure(figsize=(20, 21*N), dpi=200)
        self.ax = {}
        share = None
        for i, image in enumerate(self.images):
            ax = fig.add_subplot(1, N, i+1, projection=image.wcs)



            norm = plt.matplotlib.colors.SymLogNorm(
                                  linthresh=mad(image.data),
                                  linscale=0.1,
                                  vmin=None,
                                  vmax=None)

            ax.imshow(image.data, origin='lower', cmap='gray_r', norm=norm, alpha=0.5)
            transform = ax.get_transform('world')
            ax.set_title(image.name)
            #ax.grid(color='white', ls='solid')
