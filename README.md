# Personal Expense Tracker & Budget Planner (FinTracker)

A lightweight, web-based Personal Expense Tracker and Budget Planner built with **Python** and **Flask**. It helps students and individuals record daily transactions, monitor category-wise spending limits, and view monthly financial summaries.

---

## 🚀 Features

* **Income & Expense Logging:** Record financial transactions with titles, amounts, categories, dates, and optional notes.
* **Automated Calculations:** Automatically computes total monthly income, total expenses, and remaining balance.
* **Category Budget Planner:** Set and update monthly spending limits for 9 predefined categories (Food, Transportation, Education, Shopping, Entertainment, Healthcare, Bills, Rent, Other)[cite: 1].
* **Visual Status Indicators:** Color-coded progress bars (Green <75%, Orange 75%–100%, Red >100%) and instant flash warnings when a category exceeds its budget[cite: 1].
* **Filtering & Management:** Filter transaction history by category or transaction type, and easily delete incorrect entries[cite: 1].
* **Financial Summary:** View comprehensive monthly breakdowns highlighting highest spending categories and overall totals[cite: 1].

---

## 🛠️ Tech Stack

* **Backend:** Python 3.9+, Flask 3.0+[cite: 1]
* **Templating:** Jinja2[cite: 1]
* **Frontend:** HTML5, CSS3 (Responsive Grid & Flexbox layout)[cite: 1]
* **Money Handling:** Python `Decimal` module with `ROUND_HALF_UP` for exact financial calculations[cite: 1]
* **Storage:** In-memory Python lists and dictionaries[cite: 1]

---

