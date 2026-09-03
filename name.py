a=int(input("Enter a number for a: "))
b=int(input("Enter a number for b: "))
c=int(input("Enter a number for c: "))
if a>b and a>c:
    print("a is greater than b and c")
if b>a and b>c:
    print("b is greater than a and c")
else:
    print("c is greater than a and b")