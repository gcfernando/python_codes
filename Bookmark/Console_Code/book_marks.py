# Developer ::> Gehan Fernando
import sqlite3, webbrowser
from rich.console import Console
c = Console()

db = sqlite3.connect("links.db")
db.execute("create table if not exists links(id integer primary key, title text, url text, note text)")
try: db.execute("alter table links add column note text")
except sqlite3.OperationalError: pass

def FindRows():
    q = f"%{input('Keyword (Title): ').strip()}%"
    rows = list(db.execute(
        "select id,title,url,coalesce(note,'') from links where lower(title) like lower(?)", (q,)))
    for i,t,u,n in rows:
        c.print(f"[cyan][{i}][/cyan] [bold]{t}[/bold] → {u}\n[dim]{n}[/dim]")
    if not rows: c.print("[red]No matches.[/red]")
    return rows

try:
    while True:
        c.print("\n[green]COMMAND >>[/green]", end="")
        cmd = input(" ").strip().lower()

        if cmd == "help":
            c.print("[green]Commands:[/green] ADD/ EDIT/ DELETE/ OPEN/ SEARCH"); continue

        if cmd == "add":
            t = input("Title: ").strip()
            u = input("URL: ").strip()
            n = input("Summary: ").strip()
            db.execute("insert into links(title,url,note) values(?,?,?)", (t,u,n))
            db.commit(); c.print("[green]Saved ✅[/green]")

        elif cmd in ("search","edit","delete","open"):
            rows = FindRows()
            if cmd == "search" or not rows: continue
            i = input("Choose ID: ").strip()

            if cmd == "delete":
                db.execute("delete from links where id=?", (i,))
                db.commit(); c.print("[yellow]Deleted 🗑️[/yellow]")

            elif cmd == "open":
                u = db.execute("select url from links where id=?", (i,)).fetchone()
                c.print("[magenta]Opening...[/magenta]")
                webbrowser.open(u[0] if u else "")

            else:
                t = input("New Title: ").strip()
                u = input("New URL: ").strip()
                n = input("New Summary: ").strip()
                db.execute("update links set title=?,url=?,note=? where id=?", (t,u,n,i))
                db.commit(); c.print("[blue]Updated ✏️[/blue]")

        else:
            c.print("[dim]Type HELP[/dim]")

except KeyboardInterrupt:
    c.print("\n[bold]Exit ✔[/bold]")
finally:
    db.close()
