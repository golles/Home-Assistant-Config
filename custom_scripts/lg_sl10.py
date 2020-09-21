import sys
import temescal

def setSourceAndVolume(ip, source, volume):
  "Set the source and volume on the soundbar"

  speaker = temescal.temescal(ip)
  speaker.set_func(source)
  speaker.set_volume(volume)

setSourceAndVolume(sys.argv[1], sys.argv[2], sys.argv[3])
