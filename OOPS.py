#create a basket class
#with addItem(p,q) and o.getTotalCost(prices) methods


class basket:
    def __init__(self):

        self.items = {}

    def addItem(self, p, q):

        if x in self.items:
            self.items[p] =p+q
        else:
            self.items[p]=q

    def Cost(self, price):

        total = 0
        for x, y in self.items.items():
            if x in price:
                total =total+  price[p] * q

        return total






