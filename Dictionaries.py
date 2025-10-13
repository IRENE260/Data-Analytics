#create a function taking two dictionaries, prices: product:price and
                                            #basket: product:quantity
#which returns the total basket cost



def f11(prices,basket):
  total=0
  for product in prices :
    if product in basket:
      total=total+prices[product]*basket[product]
  return total


prices={'apple':13
        ,'orange':8}
basket={'apple':12}
f11(basket,prices)==5.97
