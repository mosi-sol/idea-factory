# Y Combinator Library Documentation

## Overview
The **Y Combinator** is a higher-order function in lambda calculus that enables recursion without using named functions. 
This library provides reusable implementations in **Python** and **JavaScript**, allowing you to define recursive functions anonymously.

---

## Installation

### Python
1. Save the library as `ycombinator.py` in your project directory.
2. Import it into your Python script:
   ```python
   from ycombinator import y_combinator
   ```

### JavaScript
1. Save the library as `ycombinator.js` in your project directory.
2. Import it into your JavaScript/Node.js project:
   ```javascript
   const { Y } = require('./ycombinator');
   ```

---

## Library Code

### Python (`ycombinator.py`)
```python
def y_combinator(f):
    """
    The Y combinator in Python.
    Allows for anonymous recursion in lambda calculus.

    Args:
        f: A function that takes a recursive function as its argument.

    Returns:
        A fixed-point combinator that enables recursion.
    """
    return (lambda x: x(x))(lambda y: f(lambda *args: y(y)(*args)))
```

### JavaScript (`ycombinator.js`)
```javascript
/**
 * The Y combinator in JavaScript.
 * Allows for anonymous recursion in lambda calculus.
 *
 * @param {Function} f - A function that takes a recursive function as its argument.
 * @returns {Function} - A fixed-point combinator that enables recursion.
 */
const Y = f => (x => x(x))(y => f((...args) => y(y)(...args)));

module.exports = { Y };
```

---

## Usage Examples

### Python Example: Factorial Function
```python
from ycombinator import y_combinator

# Define a factorial function using the Y combinator
factorial = y_combinator(
    lambda rec: lambda n: 1 if n == 0 else n * rec(n - 1)
)

print(factorial(5))  # Output: 120
```

### JavaScript Example: Factorial Function
```javascript
const { Y } = require('./ycombinator');

// Define a factorial function using the Y combinator
const factorial = Y(rec => n => n === 0 ? 1 : n * rec(n - 1));

console.log(factorial(5)); // Output: 120
```

---

## Key Features
- **Reusable**: Both implementations are self-contained and can be imported into any project.
- **Functional**: Follows the principles of lambda calculus and functional programming.
- **Modular**: Easy to extend or modify for specific use cases.

---

## How It Works
The Y Combinator works by creating a **fixed-point combinator**, which allows a function to call itself recursively without a name. This is particularly useful in languages or contexts where named functions are not available or desired.

### Mathematical Explanation
The Y Combinator is defined as:
\[ Y = \lambda f. (\lambda x. f (x x)) (\lambda x. f (x x)) \]

In code, this translates to:
```python
Y = lambda f: (lambda x: x(x))(lambda y: f(lambda *args: y(y)(*args)))
```

---

## Use Cases
- **Anonymous Recursion**: Define recursive functions without naming them.
- **Functional Programming**: Useful in pure functional languages or contexts.
- **Lambda Calculus**: Explore and implement lambda calculus concepts.

---

## License
This library is provided as-is and is free to use for any purpose. No warranty is provided.

---

> Older better :)
