# Python Password Generator and Password Strength Checker

Two small Python command-line tools: a **random password generator** with guaranteed numbers of digits, uppercase, lowercase, and special characters, and a **password strength checker** that rates a password by the number of possible character combinations.

## Overview

This project contains two independent scripts:

- **Password Generator** — creates a random password of configurable length and character composition
- **Password Strength Validator** — assesses how strong a given password is based on its character variety

## Scripts

### Password Generator (`Password_Generator.py`)

Generates a random password based on specified requirements.

**Default settings (hardcoded in `__main__`):**

| Parameter | Value |
|---|---|
| Total length | 30 characters |
| Digits | 5 |
| Uppercase letters | 5 |
| Lowercase letters | 5 |
| Special characters | 5 |
| Remaining | Random mix of all character types |

The generated characters are shuffled so the guaranteed characters are not grouped at the start.

> **Security note:** the generator uses Python's `random` module, which is designed for simulations, not security. For real passwords, use the `secrets` module (for example `secrets.choice(...)` and `secrets.SystemRandom().shuffle(...)`) or a password manager.

**Usage** (from the `Cosole_Code` folder):

```bash
python Password_Generator.py
```

The script prints one 30-character password; every run produces a different one.

---

### Password Strength Validator (`PasswordStregth.py`)

Evaluates a password by calculating the total number of possible combinations given its character composition: 26 options for each lowercase letter, 26 for each uppercase letter, 10 for each digit, and the size of the special-character set for each special character, multiplied together.

**Strength levels:**

| Strength | Threshold (combinations) |
|---|---|
| Very Strong | ≥ 10¹⁶ |
| Strong | ≥ 10¹² |
| Moderate | ≥ 10⁸ |
| Weak | ≥ 10⁴ |
| Very Weak | < 10⁴ |

**Usage:**

```bash
python PasswordStregth.py
```

The script runs in a loop, letting you check multiple passwords until you choose to exit.

**Example session** (results confirmed by running the script):
```text
Enter your password: hello
Weak

More ! (Y|N) : Y

Enter your password: P@ssw0rd!2024
Very Strong

More ! (Y|N) : N
```

> The rating only considers length and character types. `P@ssw0rd!2024` scores **Very Strong** even though it follows a very common pattern that password crackers try early. For a realistic estimate, use a library such as `zxcvbn`, which also checks dictionary words and common substitutions.

## Requirements

No external dependencies. Both scripts use only Python standard library modules (`random`, `string`, `re`, `os`).

## File Structure

```text
Password Utility/
└── Cosole_Code/
    ├── Password_Generator.py    # Random password generator
    └── PasswordStregth.py       # Password strength validator
```

## Related Projects

- [Use Windows Login — verify Windows credentials](../Use%20Windows%20Login/readme.md)
- [Steganography — hide text in images](../Stenography/readme.md)
- [Back to all Python projects](../README.md)

---

## Documentation links

[Read all Python Projects and Code Examples guides online](https://gcfernando.github.io/python_codes/documentation/) · [Project overview](https://gcfernando.github.io/python_codes/) · [All developer projects](https://gcfernando.github.io/gcfernando/projects/)
