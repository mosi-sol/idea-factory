# Monad Libraries Documentation

---

## Table of Contents
1. [Introduction](#introduction)
2. [Monad Concepts](#monad-concepts)
3. [Python Library](#python-library)
   - [Installation](#python-installation)
   - [Monad Classes](#python-monad-classes)
   - [Examples](#python-examples)
4. [JavaScript Library](#javascript-library)
   - [Installation](#javascript-installation)
   - [Monad Classes](#javascript-monad-classes)
   - [Examples](#javascript-examples)
5. [Use Cases](#use-cases)
6. [Contributing](#contributing)
7. [License](#license)

---

## Introduction

Monads are a functional programming concept used to structure programs in a way that separates pure logic from side effects, handles optional values, manages state, and more. These libraries provide reusable Monad implementations in **Python** and **JavaScript**, including:

- **Maybe**: For handling optional or nullable values.
- **Either**: For error handling and validation.
- **State**: For managing stateful computations.
- **IO**: For encapsulating side effects.
- **List**: For non-deterministic computations.

---

## Monad Concepts

### What is a Monad?
A monad is a design pattern that allows you to chain operations together while managing side effects, optional values, or state in a pure way. Monads wrap values and provide two key operations:

- **`return`/`of`**: Lifts a value into the monad.
- **`bind`/`>>=`**: Chains operations, passing the wrapped value to the next function.

### Why Use Monads?
- **Error Handling**: Use `Maybe` or `Either` to handle failures gracefully.
- **State Management**: Use `State` to pass state through computations.
- **Side Effects**: Use `IO` to encapsulate impure operations.
- **Non-determinism**: Use `List` for computations with multiple results.

---

## Python Library

### Installation

1. Save the code as `monadlib.py`.
2. Import the library in your Python project:
   ```python
   from monadlib import Maybe, Either, State, IO, ListMonad
   ```

---

### Monad Classes

#### `Maybe`
- **Purpose**: Represents optional values.
- **Methods**:
  - `Maybe(value)`: Constructor.
  - `bind(func)`: Applies `func` if the value is not `None`.
  - `return_type(value)`: Lifts a value into `Maybe`.
- **Example**:
  ```python
  def safe_divide(x, y):
      return Maybe(x / y if y != 0 else None)

  result = Maybe(10).bind(lambda x: safe_divide(x, 2))
  print(result)  # Maybe(5.0)
  ```

#### `Either`
- **Purpose**: Represents a value that can be either a success (`Right`) or a failure (`Left`).
- **Methods**:
  - `Either(value, is_left=False)`: Constructor.
  - `bind(func)`: Applies `func` if the value is `Right`.
  - `return_type(value)`: Lifts a value into `Either` as `Right`.
  - `left(value)`: Lifts a value into `Either` as `Left`.
- **Example**:
  ```python
  def validate_positive(x):
      return Either.left("Negative number") if x < 0 else Either.return_type(x)

  result = Either.return_type(10).bind(validate_positive)
  print(result)  # Right(10)
  ```

#### `State`
- **Purpose**: Encapsulates stateful computations.
- **Methods**:
  - `State(run_state)`: Constructor.
  - `bind(func)`: Chains stateful computations.
  - `return_type(value)`: Lifts a value into `State`.
  - `run(initial_state)`: Runs the computation with an initial state.
- **Example**:
  ```python
  def increment():
      return State(lambda s: (s, s + 1))

  result = State.return_type(0).bind(increment).bind(increment)
  print(result.run(0))  # (1, 2)
  ```

#### `IO`
- **Purpose**: Encapsulates side effects.
- **Methods**:
  - `IO(effect)`: Constructor.
  - `bind(func)`: Chains IO actions.
  - `return_type(value)`: Lifts a value into `IO`.
  - `run()`: Executes the IO action.
- **Example**:
  ```python
  def print_and_read(msg):
      return IO(lambda: (print(msg), input("Enter something: "))[1])

  action = IO.return_type("Hello").bind(print_and_read)
  action.run()
  ```

#### `ListMonad`
- **Purpose**: Represents non-deterministic computations.
- **Methods**:
  - `ListMonad(values)`: Constructor.
  - `bind(func)`: Applies `func` to each value and flattens the results.
  - `return_type(value)`: Lifts a value into `ListMonad`.
- **Example**:
  ```python
  nums = ListMonad([1, 2, 3])
  chars = ListMonad(['a', 'b'])
  result = nums.bind(lambda x: chars.bind(lambda y: ListMonad.return_type((x, y))))
  print(result)  # ListMonad([(1, 'a'), (1, 'b'), ...])
  ```

---

### Python Examples

Run the examples by executing:
```bash
python monadlib.py
```

**Output**:
```
Maybe Example: Maybe(None)
Either Example: Right(10)
State Example: (2, 3)
List Example: ListMonad([(1, 'a'), (1, 'b'), (2, 'a'), (2, 'b'), (3, 'a'), (3, 'b')])
```

---

## JavaScript Library

### Installation

1. Save the code as `monadLib.js`.
2. Import the library in your JavaScript project:
   ```javascript
   const { Maybe, Either, State, IO, ListMonad } = require('./monadLib');
   ```

---

### Monad Classes

#### `Maybe`
- **Purpose**: Represents optional values.
- **Methods**:
  - `new Maybe(value)`: Constructor.
  - `bind(func)`: Applies `func` if the value is not `null` or `undefined`.
  - `Maybe.of(value)`: Lifts a value into `Maybe`.
- **Example**:
  ```javascript
  const safeDivide = (x, y) => new Maybe(y === 0 ? null : x / y);
  const result = Maybe.of(10).bind((x) => safeDivide(x, 2));
  console.log(result.toString()); // Maybe(5)
  ```

#### `Either`
- **Purpose**: Represents a value that can be either a success (`Right`) or a failure (`Left`).
- **Methods**:
  - `new Either(value, isLeft)`: Constructor.
  - `bind(func)`: Applies `func` if the value is `Right`.
  - `Either.of(value)`: Lifts a value into `Either` as `Right`.
  - `Either.left(value)`: Lifts a value into `Either` as `Left`.
- **Example**:
  ```javascript
  const validatePositive = (x) =>
      x < 0 ? Either.left("Negative number") : Either.of(x);
  const result = Either.of(10).bind(validatePositive);
  console.log(result.toString()); // Right(10)
  ```

#### `State`
- **Purpose**: Encapsulates stateful computations.
- **Methods**:
  - `new State(runState)`: Constructor.
  - `bind(func)`: Chains stateful computations.
  - `State.of(value)`: Lifts a value into `State`.
  - `run(initialState)`: Runs the computation with an initial state.
- **Example**:
  ```javascript
  const increment = () => new State((s) => [s, s + 1]);
  const result = State.of(0).bind(increment).bind(increment);
  console.log(result.run(0)); // [1, 2]
  ```

#### `IO`
- **Purpose**: Encapsulates side effects.
- **Methods**:
  - `new IO(effect)`: Constructor.
  - `bind(func)`: Chains IO actions.
  - `IO.of(value)`: Lifts a value into `IO`.
  - `run()`: Executes the IO action.
- **Example**:
  ```javascript
  const printAndRead = (msg) => new IO(() => {
      console.log(msg);
      return "Enter something: (simulated)";
  });
  const action = IO.of("Hello").bind(printAndRead);
  console.log(action.run());
  ```

#### `ListMonad`
- **Purpose**: Represents non-deterministic computations.
- **Methods**:
  - `new ListMonad(values)`: Constructor.
  - `bind(func)`: Applies `func` to each value and flattens the results.
  - `ListMonad.of(value)`: Lifts a value into `ListMonad`.
- **Example**:
  ```javascript
  const nums = new ListMonad([1, 2, 3]);
  const chars = new ListMonad(['a', 'b']);
  const result = nums.bind((x) => chars.bind((y) => ListMonad.of([x, y])));
  console.log(result.toString()); // ListMonad([1,a, 1,b, 2,a, 2,b, 3,a, 3,b])
  ```

---

### JavaScript Examples

Run the examples by executing:
```bash
node monadLib.js
```

**Output**:
```
Maybe Example: Maybe(null)
Either Example: Right(10)
State Example: [2, 3]
List Example: ListMonad([1,a, 1,b, 2,a, 2,b, 3,a, 3,b])
```

---

## Use Cases

| Monad      | Use Case                          | Example                          |
|------------|-----------------------------------|----------------------------------|
| **Maybe**  | Handling nullable values          | Safe division, database queries  |
| **Either** | Error handling and validation    | Form validation, parsing         |
| **State**  | Managing stateful computations   | Counters, game state             |
| **IO**     | Encapsulating side effects        | File I/O, network requests       |
| **List**   | Non-deterministic computations   | Cartesian products, permutations |

---

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Submit a pull request with a clear description of your changes.

---

## License

This project is licensed under the **MIT License**. See the [LICENSE](../LICENSE) file for details.

---

> Note: on the examples **IO** commented, because need to user in act in real app.
