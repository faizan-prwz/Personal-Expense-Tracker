from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from flask import Flask, flash, redirect, render_template, request, url_for

app = Flask(__name__)
# NOTE: In production, use a secure random secret key and store it in environment variables.
app.secret_key = "your_secret_key_change_before_deployment_in_production"

# In-memory storage for transactions and category budgets
transactions = []
budgets = {
    "Food": Decimal("300.00"),
    "Transportation": Decimal("150.00"),
    "Education": Decimal("200.00"),
    "Shopping": Decimal("100.00"),
    "Entertainment": Decimal("100.00"),
    "Healthcare": Decimal("100.00"),
    "Bills": Decimal("200.00"),
    "Rent": Decimal("800.00"),
    "Other": Decimal("100.00"),
}

CATEGORIES = list(budgets.keys())
transaction_id_counter = 1


def get_current_month_dates():
  now = datetime.now()
  return now.year, now.month


def calculate_totals(txs=None):
  if txs is None:
    txs = transactions
  total_income = sum(
      (Decimal(str(t["amount"])) for t in txs if t["type"] == "Income"),
      Decimal("0.00"),
  )
  total_expenses = sum(
      (Decimal(str(t["amount"])) for t in txs if t["type"] == "Expense"),
      Decimal("0.00"),
  )
  remaining_balance = total_income - total_expenses
  return total_income, total_expenses, remaining_balance


@app.route("/")
def index():
  year, month = get_current_month_dates()

  current_month_txs = [
      t
      for t in transactions
      if datetime.strptime(t["date"], "%Y-%m-%d").year == year
      and datetime.strptime(t["date"], "%Y-%m-%d").month == month
  ]

  total_income, total_expenses, remaining_balance = calculate_totals(
      current_month_txs
  )
  total_monthly_budget = sum(budgets.values(), Decimal("0.00"))

  if total_monthly_budget > 0:
    budget_used_pct = (
        (total_expenses / total_monthly_budget) * 100
    ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
  else:
    budget_used_pct = Decimal("0.00")

  category_expenses = {cat: Decimal("0.00") for cat in CATEGORIES}
  for t in current_month_txs:
    if t["type"] == "Expense" and t["category"] in category_expenses:
      category_expenses[t["category"]] += Decimal(str(t["amount"]))

  sorted_txs = sorted(
      transactions, key=lambda x: (x["date"], x["id"]), reverse=True
  )
  recent_txs = sorted_txs[:5]

  return render_template(
      "index.html",
      total_income=total_income,
      total_expenses=total_expenses,
      remaining_balance=remaining_balance,
      total_monthly_budget=total_monthly_budget,
      budget_used_pct=budget_used_pct,
      recent_txs=recent_txs,
      category_expenses=category_expenses,
      current_month=datetime.now().strftime("%B %Y"),
  )


@app.route("/add-income", methods=["GET", "POST"])
def add_income():
  global transaction_id_counter
  if request.method == "POST":
    source = request.form.get("source", "").strip()
    amount_str = request.form.get("amount", "").strip()
    date_str = request.form.get("date", "").strip()
    description = request.form.get("description", "").strip()

    if not source or not amount_str or not date_str:
      flash("Please fill in all required fields.", "error")
      return redirect(url_for("add_income"))

    try:
      amount = Decimal(amount_str)
      if amount <= 0:
        raise ValueError
    except Exception:
      flash("Amount must be a positive number.", "error")
      return redirect(url_for("add_income"))

    try:
      datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
      flash("Invalid date format. Use YYYY-MM-DD.", "error")
      return redirect(url_for("add_income"))

    transaction = {
        "id": transaction_id_counter,
        "title": source,
        "type": "Income",
        "category": "Income",
        "amount": amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
        "date": date_str,
        "description": description,
    }
    transactions.append(transaction)
    transaction_id_counter += 1
    flash("Income added successfully!", "success")
    return redirect(url_for("index"))

  return render_template("add_income.html")


@app.route("/add-expense", methods=["GET", "POST"])
def add_expense():
  global transaction_id_counter
  if request.method == "POST":
    title = request.form.get("title", "").strip()
    amount_str = request.form.get("amount", "").strip()
    category = request.form.get("category", "").strip()
    date_str = request.form.get("date", "").strip()
    description = request.form.get("description", "").strip()

    if not title or not amount_str or not category or not date_str:
      flash("Please fill in all required fields.", "error")
      return redirect(url_for("add_expense"))

    if category not in CATEGORIES:
      flash("Invalid category selected.", "error")
      return redirect(url_for("add_expense"))

    try:
      amount = Decimal(amount_str)
      if amount <= 0:
        raise ValueError
    except Exception:
      flash("Amount must be a positive number.", "error")
      return redirect(url_for("add_expense"))

    try:
      tx_date = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
      flash("Invalid date format. Use YYYY-MM-DD.", "error")
      return redirect(url_for("add_expense"))

    transaction = {
        "id": transaction_id_counter,
        "title": title,
        "type": "Expense",
        "category": category,
        "amount": amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
        "date": date_str,
        "description": description,
    }
    transactions.append(transaction)
    transaction_id_counter += 1

    cat_spent = sum(
        (
            t["amount"]
            for t in transactions
            if t["type"] == "Expense"
            and t["category"] == category
            and datetime.strptime(t["date"], "%Y-%m-%d").year == tx_date.year
            and datetime.strptime(t["date"], "%Y-%m-%d").month == tx_date.month
        ),
        Decimal("0.00"),
    )
    cat_budget = budgets.get(category, Decimal("0.00"))

    if cat_budget > 0 and cat_spent > cat_budget:
      flash(
          f"Warning: You have exceeded your budget for {category}! Spent:"
          f" ${cat_spent}, Budget: ${cat_budget}",
          "error",
      )
    else:
      flash("Expense added successfully!", "success")

    return redirect(url_for("index"))

  return render_template("add_expense.html", categories=CATEGORIES)


@app.route("/transactions")
def view_transactions():
  category_filter = request.args.get("category", "").strip()
  type_filter = request.args.get("type", "").strip()

  filtered_txs = transactions

  if category_filter:
    filtered_txs = [
        t for t in filtered_txs if t["category"] == category_filter
    ]

  if type_filter:
    filtered_txs = [t for t in filtered_txs if t["type"] == type_filter]

  sorted_txs = sorted(
      filtered_txs, key=lambda x: (x["date"], x["id"]), reverse=True
  )

  return render_template(
      "transactions.html",
      transactions=sorted_txs,
      categories=CATEGORIES,
      selected_category=category_filter,
      selected_type=type_filter,
  )


@app.route("/delete-transaction/<int:transaction_id>", methods=["POST"])
def delete_transaction(transaction_id):
  global transactions
  initial_len = len(transactions)
  transactions = [t for t in transactions if t["id"] != transaction_id]
  if len(transactions) < initial_len:
    flash("Transaction deleted successfully.", "success")
  else:
    flash("Transaction not found.", "error")
  return redirect(url_for("view_transactions"))


@app.route("/budget", methods=["GET", "POST"])
def budget_planner():
  if request.method == "POST":
    for cat in CATEGORIES:
      b_str = request.form.get(f"budget_{cat}", "").strip()
      if b_str:
        try:
          b_val = Decimal(b_str)
          if b_val < 0:
            raise ValueError
          budgets[cat] = b_val.quantize(
              Decimal("0.01"), rounding=ROUND_HALF_UP
          )
        except Exception:
          flash(f"Invalid budget value for {cat}.", "error")
          return redirect(url_for("budget_planner"))
    flash("Budgets updated successfully!", "success")
    return redirect(url_for("budget_planner"))

  year, month = get_current_month_dates()
  current_month_txs = [
      t
      for t in transactions
      if datetime.strptime(t["date"], "%Y-%m-%d").year == year
      and datetime.strptime(t["date"], "%Y-%m-%d").month == month
  ]

  category_data = {}
  for cat in CATEGORIES:
    spent = sum(
        (
            t["amount"]
            for t in current_month_txs
            if t["type"] == "Expense" and t["category"] == cat
        ),
        Decimal("0.00"),
    )
    b_val = budgets.get(cat, Decimal("0.00"))
    remaining = b_val - spent
    if b_val > 0:
      pct = int(
          min(
              (
                  (spent / b_val) * 100
              ).quantize(Decimal("1"), rounding=ROUND_HALF_UP),
              999,
          )
      )
    else:
      pct = 100 if spent > 0 else 0

    if pct < 75:
      status_class = "progress-green"
    elif pct <= 100:
      status_class = "progress-orange"
    else:
      status_class = "progress-red"

    category_data[cat] = {
        "budget": b_val,
        "spent": spent,
        "remaining": remaining,
        "percentage": pct,
        "status_class": status_class,
        "exceeded": spent > b_val if b_val > 0 else (spent > 0),
    }

  return render_template(
      "budget.html",
      category_data=category_data,
      categories=CATEGORIES,
      current_month=datetime.now().strftime("%B %Y"),
  )


@app.route("/summary")
def financial_summary():
  year, month = get_current_month_dates()
  current_month_txs = [
      t
      for t in transactions
      if datetime.strptime(t["date"], "%Y-%m-%d").year == year
      and datetime.strptime(t["date"], "%Y-%m-%d").month == month
  ]

  total_income, total_expenses, remaining_balance = calculate_totals(
      current_month_txs
  )

  category_expenses = {cat: Decimal("0.00") for cat in CATEGORIES}
  for t in current_month_txs:
    if t["type"] == "Expense" and t["category"] in category_expenses:
      category_expenses[t["category"]] += Decimal(str(t["amount"]))

  highest_category = "None"
  max_val = Decimal("0.00")
  for cat, val in category_expenses.items():
    if val > max_val:
      max_val = val
      highest_category = cat

  num_transactions = len(current_month_txs)

  return render_template(
      "summary.html",
      total_income=total_income,
      total_expenses=total_expenses,
      remaining_balance=remaining_balance,
      highest_category=highest_category,
      category_expenses=category_expenses,
      num_transactions=num_transactions,
      current_month=datetime.now().strftime("%B %Y"),
  )


@app.errorhandler(404)
def page_not_found(e):
  return render_template("error.html"), 404


if __name__ == "__main__":
  app.run(debug=True)