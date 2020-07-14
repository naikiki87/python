class Pitcher :
    def __init__(self, val) :
        self.val = val

    def test_func(self) :
        self.val = self.val + 1
        print("val : ", self.val)