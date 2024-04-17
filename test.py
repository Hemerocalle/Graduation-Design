class Aa():

    def bb(self):
        pass


class Cc():
    dd: Aa


class Ee(Cc):

    def ff(self):
        self.dd.bb()
