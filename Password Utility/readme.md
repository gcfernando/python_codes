# Password Utility

Two command-line tools for generating secure random passwords and evaluating the strength of existing passwords.

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

The generated characters are shuffled to ensure randomness in the final output.

**Usage:**

```bash
python Password_Generator.py
```

**Example output:**
```
aB3!xK#9mZ@2vQ&5nP$7wR%1jS*4uL
```

---

### Password Strength Validator (`PasswordStregth.py`)

Evaluates a password by calculating the total number of possible combinations given its character composition.

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

**Example session:**
```
Enter your password: hello
Very Weak

More ! (Y|N) : Y

Enter your password: P@ssw0rd!2024
Strong

More ! (Y|N) : N
```

## Requirements

No external dependencies. Both scripts use only Python standard library modules (`random`, `string`, `re`, `os`).

## File Structure

```
Password Utility/
└── Cosole_Code/
    ├── Password_Generator.py    # Random password generator
    └── PasswordStregth.py       # Password strength validator
```
