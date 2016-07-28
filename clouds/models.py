"""Definition of Cloud mongoengine models"""

import uuid
import json

import mongoengine as me

from mist.core.tag.models import Tag
from mist.core.keypair.models import Keypair
from mist.core.user.models import Organization

import mist.io.clouds.controllers as controllers


class Cloud(me.Document):
    """Abstract base class for every cloud/provider mongoengine model

    This class defines the fields common to all clouds of all types. For each
    different cloud type, a subclass should be created adding any cloud
    specific fields and methods.

    Documents of all Cloud subclasses will be stored on the same mongo
    collection.

    One can perform a query directly on Cloud to fetch all cloud types, like
    this:

        Cloud.objects(owner=owner).count()

    This will return an iterable of clouds for that owner. Each cloud will be
    an instance of its respective Cloud subclass, like AmazonCloud and
    LinodeCloud instances.

    Clouds of a specific type can be queried like this:

        AmazonCloud.objects(owner=owner).count()

    This will return an iterable of AmazonCloud instances.

    To create a new cloud, one should initialize a Cloud subclass like
    AmazonCloud. Intializing directly a Cloud instance won't have any
    credential fields or associated handler to work with.

    Each Cloud subclass should define a `_controller_cls` class attribute. Its
    value should be a subclass of `mist.io.clouds.base.BaseController`. These
    subclasses are stored in `mist.io.clouds.controllers`. When a cloud is
    instanciated, it is given a `ctl` attribute which gives access to the
    clouds controller. This way it is possible to do things like:

        cloud = Cloud.objects.get(id=cloud_id)
        print cloud.ctl.list_machines()

    """

    id = me.StringField(primary_key=True, default=lambda: uuid.uuid4().hex)
    owner = me.ReferenceField(Organization, required=True)

    title = me.StringField(required=True, unique_with="owner")
    enabled = me.BooleanField(default=True)

    machine_count = me.IntField(default=0)

    starred = me.ListField()
    unstarred = me.ListField()

    meta = {
        'allow_inheritance': True,
        'collection': 'clouds',  # collection 'cloud' is used by core's model
        'indexes': ['owner'],
    }

    _controller_cls = None

    def __init__(self, *args, **kwargs):
        super(Cloud, self).__init__(*args, **kwargs)

        # Set attribute `ctl` to an instance of the appropriate controller.
        if self._controller_cls is None:
            raise NotImplementedError(
                "Can't initialize %s. Cloud is an abstract base class and "
                "shouldn't be used to create cloud instances. All Cloud "
                "subclasses should define a `_controller_cls` class attribute "
                "pointing to a `BaseController` subclass." % self
            )
        elif not issubclass(self._controller_cls, controllers.BaseController):
            raise TypeError(
                "Can't initialize %s.  All Cloud subclasses should define a "
                "`_controller_cls` class attribute pointing to a "
                "`BaseController` subclass." % self
            )
        self.ctl = self._controller_cls(self)

    def delete(self):
        super(Cloud, self).delete()
        Tag.objects(resource=self).delete()

    def as_dict(self):
        # TODO: This is just plain stupid.
        return json.loads(self.to_json())

    def __str__(self):
        return '%s cloud %s (%s) of %s' % (type(self), self.title,
                                           self.id, self.owner)


class AmazonCloud(Cloud):

    apikey = me.StringField(required=True)
    apisecret = me.StringField(required=True)
    region = me.StringField(required=True)

    _controller_cls = controllers.AmazonController


class DigitalOceanCloud(Cloud):

    token = me.StringField(required=True)

    _controller_cls = controllers.DigitalOceanController


class DigitalOceanFirstGenCloud(Cloud):

    apikey = me.StringField(required=True)
    apisecret = me.StringField(required=True)

    _controller_cls = controllers.DigitalOceanFirstGenController


class LinodeCloud(Cloud):

    apikey = me.StringField(required=True)

    _controller_cls = controllers.LinodeController


class RackSpaceCloud(Cloud):

    username = me.StringField(required=True)
    apikey = me.StringField(required=True)
    region = me.StringField(required=True)

    _controller_cls = controllers.RackSpaceController


class SoftLayerCloud(Cloud):

    username = me.StringField(required=True)
    apikey = me.StringField(required=True)

    _controller_cls = controllers.SoftLayerController


class NephoScaleCloud(Cloud):

    username = me.StringField(required=True)
    password = me.StringField(required=True)

    _controller_cls = controllers.NephoScaleController


class AzureCloud(Cloud):

    subscription_id = me.StringField(required=True)
    certificate = me.StringField(required=True)

    _controller_cls = controllers.AzureController


class GoogleCloud(Cloud):

    email = me.StringField(required=True)
    private_key = me.StringField(required=True)
    project_id = me.StringField(required=True)

    _controller_cls = controllers.GoogleController


class HostVirtualCloud(Cloud):

    apikey = me.StringField(required=True)

    _controller_cls = controllers.HostVirtualController


class PacketCloud(Cloud):

    apikey = me.StringField(required=True)
    project_id = me.StringField(required=False)

    _controller_cls = controllers.PacketController


class VultrCloud(Cloud):

    apikey = me.StringField(required=True)

    _controller_cls = controllers.VultrController


class VSphereCloud(Cloud):

    host = me.StringField(required=True)
    username = me.StringField(required=True)
    password = me.StringField(required=True)

    _controller_cls = controllers.VSphereController


class VCloud(Cloud):

    host = me.StringField(required=True)
    username = me.StringField(required=True)
    password = me.StringField(required=True)

    _controller_cls = controllers.VCloudController


class OpenStackCloud(Cloud):

    username = me.StringField(required=True)
    password = me.StringField(required=True)
    url = me.StringField(required=True)
    tenant = me.StringField(required=True)
    region = me.StringField(required=False)
    compute_endpoint = me.StringField(required=False)

    _controller_cls = controllers.OpenStackController


class DockerCloud(Cloud):

    host = me.StringField(required=True)
    port = me.IntField(required=True, default=4243)

    # User/Password Authentication (optional)
    username = me.StringField(required=False)
    password = me.StringField(required=False)

    # TLS Authentication (optional)
    key_file = me.StringField(required=False)
    cert_file = me.StringField(required=False)
    ca_cert_file = me.StringField(required=False)

    _controller_cls = controllers.DockerController


class LibvirtCloud(Cloud):

    host = me.StringField(required=True)
    username = me.StringField(default='root')
    port = me.IntField(required=True, default=22)
    key = me.ReferenceField(Keypair, required=False)
    images_location = me.StringField(default="/var/lib/libvirt/images")

    _controller_cls = controllers.LibvirtController


# FIXME
class CoreOSCloud(Cloud):

    _controller_cls = controllers.CoreOSController


# FIXME
class OtherCloud(Cloud):

    _controller_cls = controllers.OtherController
