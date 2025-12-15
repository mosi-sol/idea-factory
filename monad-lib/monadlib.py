from typing import TypeVar, Generic, Callable, Any, Tuple

T = TypeVar('T')
U = TypeVar('U')
S = TypeVar('S')

class Monad(Generic[T]):
    def bind(self, func: Callable[[T], 'Monad[U]']) -> 'Monad[U]':
        raise NotImplementedError

    def map(self, func: Callable[[T], U]) -> 'Monad[U]':
        return self.bind(lambda x: self.return_type(func(x)))

    @staticmethod
    def return_type(value: T) -> 'Monad[T]':
        raise NotImplementedError

    def __rshift__(self, func: Callable[[T], 'Monad[U]']) -> 'Monad[U]':
        return self.bind(func)

# --- Maybe Monad ---
class Maybe(Monad[T]):
    def __init__(self, value: T | None):
        self.value = value

    def bind(self, func: Callable[[T], 'Maybe[U]']) -> 'Maybe[U]':
        if self.value is None:
            return Maybe(None)
        return func(self.value)

    @staticmethod
    def return_type(value: T) -> 'Maybe[T]':
        return Maybe(value)

    def __repr__(self):
        return f"Maybe({self.value})"

# --- Either Monad ---
class Either(Monad[T]):
    def __init__(self, value: T, is_left: bool = False):
        self.value = value
        self.is_left = is_left

    def bind(self, func: Callable[[T], 'Either[U]']) -> 'Either[U]':
        if self.is_left:
            return self
        return func(self.value)

    @staticmethod
    def return_type(value: T) -> 'Either[T]':
        return Either(value, is_left=False)

    @staticmethod
    def left(value: T) -> 'Either[T]':
        return Either(value, is_left=True)

    def __repr__(self):
        return f"{'Left' if self.is_left else 'Right'}({self.value})"

# --- State Monad ---
class State(Monad[T]):
    def __init__(self, run_state: Callable[[S], Tuple[T, S]]):
        self.run_state = run_state

    def bind(self, func: Callable[[T], 'State[U]']) -> 'State[U]':
        def new_run_state(s: S) -> Tuple[U, S]:
            val, new_s = self.run_state(s)
            return func(val).run_state(new_s)
        return State(new_run_state)

    @staticmethod
    def return_type(value: T) -> 'State[T]':
        return State(lambda s: (value, s))

    def run(self, initial_state: S) -> Tuple[T, S]:
        return self.run_state(initial_state)

# --- IO Monad ---
class IO(Monad[T]):
    def __init__(self, effect: Callable[[], T]):
        self.effect = effect

    def bind(self, func: Callable[[T], 'IO[U]']) -> 'IO[U]':
        def new_effect() -> U:
            val = self.effect()
            return func(val).effect()
        return IO(new_effect)

    @staticmethod
    def return_type(value: T) -> 'IO[T]':
        return IO(lambda: value)

    def run(self) -> T:
        return self.effect()

# --- List Monad ---
class ListMonad(Monad[T]):
    def __init__(self, values: list[T]):
        self.values = values

    def bind(self, func: Callable[[T], 'ListMonad[U]']) -> 'ListMonad[U]':
        result = []
        for val in self.values:
            result.extend(func(val).values)
        return ListMonad(result)

    @staticmethod
    def return_type(value: T) -> 'ListMonad[T]':
        return ListMonad([value])

    def __repr__(self):
        return f"ListMonad({self.values})"

# --- Examples ---
def run_examples():
    # Maybe Example: Safe Division
    def safe_divide(x: float, y: float) -> Maybe[float]:
        return Maybe(x / y if y != 0 else None)

    maybe_result = (
        Maybe(10)
        >> safe_divide(2)
        >> safe_divide(5)
        >> safe_divide(0)
    )
    print("Maybe Example:", maybe_result)  # Maybe(None)

    # Either Example: Error Handling
    def validate_positive(x: int) -> Either[str, int]:
        return Either.left("Negative number") if x < 0 else Either.return_type(x)

    either_result = (
        Either.return_type(10)
        >> validate_positive
        >> validate_positive
    )
    print("Either Example:", either_result)  # Right(10)

    # State Example: Counter
    def increment() -> State[int, int]:
        return State(lambda s: (s, s + 1))

    state_result = (
        State.return_type(0)
        >> increment
        >> increment
        >> increment
    )
    print("State Example:", state_result.run(0))  # (2, 3)

    # IO Example: Print and Read
    def print_and_read(msg: str) -> IO[str]:
        return IO(lambda: (print(msg), input("Enter something: "))[1])

    io_action = (
        IO.return_type("Hello")
        >> print_and_read
        >> print_and_read
    )
    print("IO Example: (Uncomment to run)")
    # io_action.run()

    # List Example: Cartesian Product
    nums = ListMonad([1, 2, 3])
    chars = ListMonad(['a', 'b'])

    list_result = (
        nums
        >> lambda x: chars >> lambda y: ListMonad.return_type((x, y))
    )
    print("List Example:", list_result)  # ListMonad([(1, 'a'), (1, 'b'), ...])

if __name__ == "__main__":
    run_examples()
