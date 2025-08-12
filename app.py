from flask import Flask, render_template, request, redirect, url_for
import webbrowser

app = Flask(__name__)

# ===== In-memory storage (resets on restart) =====
tasks = []  # each: {"id": int, "title": str, "description": str, "effort": int, "done": bool}
_next_id = 1

def next_id():
    global _next_id
    val = _next_id
    _next_id += 1
    return val

# ===== Rule-based sorting (mood logic) =====
def sort_tasks_by_mood(task_list, mood):
    # only pending tasks for the smart list
    filtered = [t for t in task_list if not t["done"]]
    if mood == "Tired":
        return sorted(filtered, key=lambda x: x['effort'])  # light first
    elif mood == "Productive":
        return sorted(filtered, key=lambda x: x['effort'], reverse=True)  # hard first
    elif mood == "Struggling":
        return sorted(filtered, key=lambda x: len(x['description']), reverse=True)  # complex first
    elif mood == "Anxious":
        tasks_sorted = sorted(filtered, key=lambda x: x['effort'])
        return [tasks_sorted[0]] + tasks_sorted[1:] if tasks_sorted else []
    else:  # Neutral
        return filtered

@app.route("/", methods=["GET", "POST"])
def index():
    global tasks
    # Handle add task
    if request.method == "POST" and request.form.get("form_type") == "add":
        title = (request.form.get("title") or "").strip()
        description = request.form.get("description") or ""
        effort = int(request.form.get("effort") or 3)
        if title:
            tasks.append({
                "id": next_id(),
                "title": title,
                "description": description,
                "effort": effort,
                "done": False
            })
        return redirect(url_for("index", mood=request.args.get("mood", "Neutral")))

    # Current mood from query (default Neutral)
    mood = request.args.get("mood", "Neutral")
    moods = ["Neutral", "Tired", "Productive", "Struggling", "Anxious"]

    smart_tasks = sort_tasks_by_mood(tasks, mood)

    return render_template(
        "index.html",
        tasks=tasks,
        smart_tasks=smart_tasks,
        mood=mood,
        moods=moods
    )

@app.route("/done/<int:task_id>", methods=["POST"])
def mark_done(task_id):
    for t in tasks:
        if t["id"] == task_id:
            t["done"] = True
            break
    return redirect(url_for("index", mood=request.args.get("mood", "Neutral")))

@app.route("/delete/<int:task_id>", methods=["POST"])
def delete_task(task_id):
    global tasks
    tasks = [t for t in tasks if t["id"] != task_id]
    return redirect(url_for("index", mood=request.args.get("mood", "Neutral")))

if __name__ == "__main__":
    # auto-open browser on start
    webbrowser.open("http://127.0.0.1:5000")
    app.run(debug=True)
