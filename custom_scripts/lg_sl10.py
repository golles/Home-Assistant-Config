import sys
import temescal
import time

class LGSoundbar:
  def __init__(self, ip):
    '''Initialize a connection to the soundbar.'''
    self._speaker = temescal.temescal(ip, callback=self.handle_callback)
    self._volume = None
    self._source = None

    self._speaker.get_info()
    self._speaker.get_func()

    time.sleep(2) # Sleep a little to get the data.

  def setSource(self, source):
    '''Set the source of the soundbar.'''
    if self._source is None:
      # We don't know the current source, let's serve the request.
      self._speaker.set_func(source)
    elif not self._source is None and not self._source is int(source):
      self._speaker.set_func(source)

  def setVolume(self, volume):
    '''Set the volume of the soundbar.'''
    if self._volume is None:
      # We don't know the current volume, let's serve the request.
      self._speaker.set_volume(volume)
    elif not self._volume is None and not self._volume is int(volume):
      self._speaker.set_volume(volume)

  def setSourceAndVolume(self, source, volume):
    '''Set the source and volume of the soundbar.'''
    self.setSource(source)
    self.setVolume(volume)

  def handle_callback(self, callback):
    '''Handle callbacks from the soundbar.'''
    data = callback['data']
    if 'i_vol' in data:
        self._volume = int(data['i_vol'])
    if 'i_curr_func' in data:
        self._source = int(data['i_curr_func'])

soundbar = LGSoundbar(sys.argv[1])
soundbar.setSourceAndVolume(sys.argv[2], sys.argv[3])
