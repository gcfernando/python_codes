# Smart Memory Watcher 🧠💙

Keep an eye on what’s quietly growing in the background.

**Smart Memory Watcher** is a simple, beautiful terminal companion that helps you notice when an app keeps consuming more and more memory over time — the kind of slow growth that can eventually cause freezes, crashes, or unexpected slowdowns.

It refreshes live, stays clean, and makes it easy to spot trouble early.

---

## ✨ What it does

- **Shows a live list** of the biggest memory users right now
- **Tracks memory changes over time** so you can see what’s steadily growing
- **Flags suspicious behavior** with clear status labels:
  - ✅ **OK** — stable usage
  - 👀 **WATCH** — growing faster than usual
  - 🚨 **LEAK** — consistent growth that needs attention

---

## 🖥️ What you’ll see

A live dashboard in your terminal with:

- Process ID
- Process name
- Current memory usage
- Memory growth
- Status (OK / WATCH / LEAK)

And a footer that tells you whether anything suspicious has been found.

---

## 🚀 Run it

```bash
python3 monitor.py
