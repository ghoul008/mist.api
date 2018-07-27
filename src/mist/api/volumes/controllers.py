class StorageController(object):
    def __init__(self, volume):
        """
        Initialize the `StorageController` given a volume.
        """
        self.volume = volume
        self.cloud = volume.cloud

    def create(self, **kwargs):
        """Create `self.volume`."""
        return self.cloud.ctl.volume.create_volume(self.volume, **kwargs)

    def delete(self):
        """Delete `self.volume`."""
        return self.cloud.ctl.volume.delete_volume(self.volume)

    def attach(self, node, **kwargs):
        """Attach `self.volume` to a node"""
        return self.cloud.ctl.volume.attach_volume(self.volume, node, **kwargs)

    def detach(self, node):
        """Detach `self.volume` from a node"""
        return self.cloud.ctl.volume.detach_volume(self.volume, node)
