from com.muse.fmw.platform import PbProperties


class TestContext:
    def __init__(self, properties):
        self.props = PbProperties(properties)

    def setKey(self, key):
        self.key = key
