# Managing Code Complexity

Complexity is the enemy of maintainability.

## Measuring Complexity

### Cyclomatic Complexity

Number of independent paths through a function.
Count: if, else, for, while, case, and/or, catch.

1-10: simple
11-20: moderate
21-50: complex
50+: untestable

Function with complexity 50+ should be decomposed.

### Cognitive Complexity

How hard is it to understand the code?
Nesting increases cognitive complexity.

Bad (high cognitive complexity):
if a:
    if b:
        for x in items:
            if x.is_valid:
                process(x)
            else:
                skip(x)

Better:
if not a:
    return
if not b:
    return
valid = [x for x in items if x.is_valid]
for x in valid:
    process(x)
invalid = [x for x in items if not x.is_valid]
for x in invalid:
    skip(x)

## Reducing Complexity

### 1. Early Returns

Bad:
if user:
    if user.is_active:
        if user.has_permission:
            return process(user)
        else:
            return error("no permission")
    else:
        return error("inactive")
return error("no user")

Good:
if not user:
    return error("no user")
if not user.is_active:
    return error("inactive")
if not user.has_permission:
    return error("no permission")
return process(user)

### 2. Extract Conditions

Bad:
if user and user.is_active and user.has_permission and not user.is_banned:
    process(user)

Good:
can_process = all([
    user,
    user.is_active,
    user.has_permission,
    not user.is_banned,
])
if can_process:
    process(user)

### 3. Replace Condition with Polymorphism

Instead of:
def calculate_shipping(order, method):
    if method == "standard": ...
    elif method == "express": ...

Use:
strategies = {"standard": StandardShipping(), "express": ExpressShipping()}
strategies[method].calculate(order)

### 4. Command Query Separation

Functions should either:
1. Return a value (query), or
2. Change state (command)

NOT both:
def pop(stack):
    value = stack[-1]
    del stack[-1]
    return value

Better:
def peek(stack): return stack[-1]
def pop(stack): del stack[-1]

## Code Smells

1. Long functions (> 20 lines)
2. Deep nesting (> 3 levels)
3. Too many parameters (> 3)
4. Duplicated code (copy-paste)
5. Large classes (> 200 lines)
6. Feature envy (using data from other classes)
7. Shotgun surgery (one change touches many files)


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.
