// --- Base Monad Class ---
class Monad {
    bind(func) {
        throw new Error("Not implemented");
    }

    map(func) {
        return this.bind((x) => this.constructor.returnType(func(x)));
    }

    static returnType(value) {
        throw new Error("Not implemented");
    }

    static of(value) {
        return this.returnType(value);
    }
}

// --- Maybe Monad ---
class Maybe extends Monad {
    constructor(value) {
        super();
        this.value = value;
    }

    bind(func) {
        if (this.value === null || this.value === undefined) {
            return new Maybe(null);
        }
        return func(this.value);
    }

    static returnType(value) {
        return new Maybe(value);
    }

    toString() {
        return `Maybe(${this.value})`;
    }
}

// --- Either Monad ---
class Either extends Monad {
    constructor(value, isLeft = false) {
        super();
        this.value = value;
        this.isLeft = isLeft;
    }

    bind(func) {
        if (this.isLeft) {
            return this;
        }
        return func(this.value);
    }

    static returnType(value) {
        return new Either(value, false);
    }

    static left(value) {
        return new Either(value, true);
    }

    toString() {
        return `${this.isLeft ? "Left" : "Right"}(${this.value})`;
    }
}

// --- State Monad ---
class State extends Monad {
    constructor(runState) {
        super();
        this.runState = runState;
    }

    bind(func) {
        return new State((s) => {
            const [val, newS] = this.runState(s);
            return func(val).runState(newS);
        });
    }

    static returnType(value) {
        return new State((s) => [value, s]);
    }

    run(initialState) {
        return this.runState(initialState);
    }
}

// --- IO Monad ---
class IO extends Monad {
    constructor(effect) {
        super();
        this.effect = effect;
    }

    bind(func) {
        return new IO(() => {
            const val = this.effect();
            return func(val).effect();
        });
    }

    static returnType(value) {
        return new IO(() => value);
    }

    run() {
        return this.effect();
    }
}

// --- List Monad ---
class ListMonad extends Monad {
    constructor(values) {
        super();
        this.values = values;
    }

    bind(func) {
        const result = [];
        for (const val of this.values) {
            result.push(...func(val).values);
        }
        return new ListMonad(result);
    }

    static returnType(value) {
        return new ListMonad([value]);
    }

    toString() {
        return `ListMonad([${this.values.join(", ")}])`;
    }
}

// --- Examples ---
function runExamples() {
    // Maybe Example: Safe Division
    const safeDivide = (x, y) => new Maybe(y === 0 ? null : x / y);

    const maybeResult = Maybe.of(10)
        .bind((x) => safeDivide(x, 2))
        .bind((x) => safeDivide(x, 5))
        .bind((x) => safeDivide(x, 0));

    console.log("Maybe Example:", maybeResult.toString()); // Maybe(null)

    // Either Example: Error Handling
    const validatePositive = (x) =>
        x < 0 ? Either.left("Negative number") : Either.of(x);

    const eitherResult = Either.of(10)
        .bind(validatePositive)
        .bind(validatePositive);

    console.log("Either Example:", eitherResult.toString()); // Right(10)

    // State Example: Counter
    const increment = () =>
        new State((s) => [s, s + 1]);

    const stateResult = State.of(0)
        .bind(increment)
        .bind(increment)
        .bind(increment);

    console.log("State Example:", stateResult.run(0)); // [2, 3]

    // IO Example: Print and Read
    const printAndRead = (msg) =>
        new IO(() => {
            console.log(msg);
            return "Enter something: (simulated)";
        });

    const ioAction = IO.of("Hello")
        .bind(printAndRead)
        .bind(printAndRead);

    console.log("IO Example: (Uncomment to run)");
    // console.log(ioAction.run());

    // List Example: Cartesian Product
    const nums = new ListMonad([1, 2, 3]);
    const chars = new ListMonad(["a", "b"]);

    const listResult = nums.bind((x) =>
        chars.bind((y) => ListMonad.of([x, y]))
    );

    console.log("List Example:", listResult.toString()); // ListMonad([1,a, 1,b, 2,a, 2,b, 3,a, 3,b])
}

// Run examples
runExamples();
