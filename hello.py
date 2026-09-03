def calculate(x, y, operator):
    if operator == '+':
        return x + y
    if operator == '-':
        return x - y
    if operator == '*':
        return x * y
    if operator == '/':
        if y == 0:
            raise ZeroDivisionError('Cannot divide by zero')
        return x / y
    if operator == '%':
        if y == 0:
            raise ZeroDivisionError('Cannot modulo by zero')
        return x % y
    raise ValueError(f"Unsupported operator: {operator}")


def main():
    print('Basic Calculator')
    print('Supported operations: +, -, *, /, %')

    try:
        x = float(input('Enter the first number: '))gi
        operator = input('Enter an operator (+, -, *, /, %): ').strip()
        y = float(input('Enter the second number: '))
        result = calculate(x, y, operator)
    except ValueError as exc:
        print('Input error:', exc)
        return
    except ZeroDivisionError as exc:
        print('Math error:', exc)
        return

    print(f'{x} {operator} {y} = {result}')


if __name__ == '__main__':
    main()








