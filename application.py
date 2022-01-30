import os
import json

from datetime import datetime
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash


from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    stocks = db.execute("SELECT symbol, shares FROM portfolio WHERE user_id=:user_id ORDER BY symbol ASC", user_id=session["user_id"])
    user = db.execute("SELECT username FROM users WHERE id=:id", id=session["user_id"])[0]["username"]
    grand_total = []



    for stock in stocks:
        symbol = str(stock["symbol"])
        shares = float(stock["shares"])
        name = lookup(stock["symbol"])["name"]
        price = lookup(stock["symbol"])["price"]
        total = shares * price
        stock["name"] = name
        stock["price"] = usd(price)
        stock["total"] = usd(total)
        grand_total.append(float(total))

    #case having cash
    cash = db.execute("SELECT cash FROM users WHERE username=:username", username=user)[0]["cash"]
    cash_total = cash + sum(grand_total)

    return render_template("index.html", stocks=stocks, cash_total=usd(cash_total), cash=usd(cash))


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    if request.method == "POST":
        look = lookup(request.form.get("symbol"))

        try:
            shares = int(request.form.get("shares"))
        except ValueError:
            return apology("shares must be a posative integer", 400)

        if not request.form.get("symbol") or not request.form.get("shares"):
            return apology("Please enter completely")

        elif int(float(request.form.get("shares"))) < 1:
            return apology("shares must be over 1")

        elif look == None:
            return apology("invalid symbol")

        cost = int(float(request.form.get("shares"))) * look["price"]
        cash = db.execute("SELECT cash FROM users WHERE id=:user_id",user_id=session["user_id"])

        if cost > cash[0]["cash"]:
            return apology ("Sorry you don't have much money")

        #update cash on database
        db.execute("UPDATE users SET cash = cash - :cost WHERE id=:user_id", cost=cost, user_id=session["user_id"])

        #case user already have stock on portfolio
        stock = db.execute("SELECT symbol FROM portfolio WHERE symbol=:symbol AND user_id=:user_id", symbol = look["symbol"], user_id=session["user_id"])

        #add data to history

        db.execute("INSERT INTO history (user_id, status, symbol, shares, price, date) VALUES (:user_id, :status, :symbol, :shares, :price, :date)",
        user_id=session["user_id"], status="BUY", symbol=look["symbol"], shares=int(float(request.form.get("shares"))), price=look["price"], date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


        if not stock:
            db.execute("INSERT INTO portfolio (user_id, symbol, shares, total) VALUES (:user_id, :symbol, :shares, :total)",
            user_id=session["user_id"], symbol=look["symbol"], shares=int(float(request.form.get("shares"))), total=cost)

        else:
            db.execute("UPDATE portfolio SET shares=shares+:shares, total = total + :cost WHERE user_id=:user_id AND symbol=:symbol",
            shares=int(float(request.form.get("shares"))), cost=cost, user_id=session["user_id"], symbol=look["symbol"])

        return redirect(url_for("index"))


    return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    stocks = db.execute("SELECT * FROM history WHERE user_id=:user_id", user_id=session["user_id"])

    for stock in stocks:
        user_id = float(stock["user_id"])
        status = str(stock["status"])
        symbol = str(stock["symbol"])
        name = lookup(stock["symbol"])["name"]
        shares = int(stock["shares"])
        total = float(stock["price"]) * shares
        date = str(stock["date"])
        user_name = db.execute("SELECT username FROM users WHERE id=:user_id", user_id=user_id)[0]["username"]
        stock["user_name"] = user_name
        stock["date"] = date
        stock["status"] = status
        stock["name"] = name
        stock["shares"] = shares
        stock["total"] = usd(total)


    return render_template("history.html", stocks=stocks)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    #make SQL table of portfolio and history (if already exists, pass)
    db.execute("CREATE TABLE IF NOT EXISTS portfolio(user_id INTEGER, symbol TEXT, shares INTEGER, total NUMERIC NOT NULL)")
    db.execute("CREATE TABLE IF NOT EXISTS history(user_id INTEGER, status TEXT, symbol TEXT, shares INTEGER, price NUMERIC NOT NULL, date NUMERIC NOT NULL)")

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":

        #case if not fill in
        if not request.form.get("symbol"):
            return apology("Please enter symbol")

        look = lookup(request.form.get("symbol"))

        #case invalid symbol or not in list
        if look == None:
            return apology("Invalid Symbol")

        return render_template("quoted.html", symbol=look["symbol"], name=look["name"], price=usd(look["price"]))

    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":

        #case username was not submitted
        if not request.form.get("username"):
            return apology("Please enter username")

        #case password was not submitted
        elif not request.form.get("password") or not request.form.get("confirmation"):
            return apology("Please enter password")

        #case password != password_confirm
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("Password is not correct")


        #case username is unique
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))
        if len(rows)>=1:
            return apology("username is already exists")

        #add users to SQL
        result = db.execute("INSERT INTO users (username, hash) VALUES(:username, :hash)",username=request.form.get("username"), hash=generate_password_hash(request.form.get("password")))
        if not result:
            return apology("Username unavailable", 400)


        #login users automatically
        rows = db.execute("SELECT * FROM users WHERE username=:username",username=request.form.get("username"))
        session["user_id"] = rows[0]["id"]


        #redirect to homepage(index.html)
        return redirect("/")

    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    stocks = db.execute("SELECT symbol FROM portfolio WHERE user_id=:user_id", user_id=session["user_id"])


    if request.method == 'POST':

        shares = db.execute("SELECT shares FROM portfolio WHERE user_id=:user_id AND symbol=:symbol", user_id=session["user_id"], symbol=request.form.get("symbol"))[0]["shares"]
        look = lookup(request.form.get("symbol"))

        for stock in stocks:
            symbol = str(stock["symbol"])

        #case incorrect enter
        if not request.form.get("symbol") or not request.form.get("shares"):
            return apology("Please enter completely")

        #case shares are not correct range
        elif float(request.form.get("shares")) <= 0:
            return apology("shares must be over 0")

        if float(request.form.get("shares")) > shares:
            return apology("Sorry, you don't have enough shares")

        else:
            cash = db.execute("SELECT cash FROM users WHERE id=:id",id=session["user_id"])[0]["cash"]

            income = float(request.form.get("shares")) * look["price"]

            #add database
            db.execute("UPDATE portfolio SET shares=shares-:shares, total=total-:income WHERE user_id=:user_id AND symbol=:symbol",
            shares=float(request.form.get("shares")), income=income, user_id=session["user_id"], symbol=look["symbol"])
            if db.execute("SELECT shares FROM portfolio WHERE user_id=:user_id AND symbol=:symbol", user_id=session["user_id"], symbol=request.form.get("symbol"))[0]["shares"] == 0:
                db.execute("DELETE FROM portfolio WHERE user_id=:user_id AND symbol=:symbol", user_id=session["user_id"], symbol=request.form.get("symbol"))

            "update cash data"
            db.execute("UPDATE users SET cash=cash+:income", income=income)

            #update history SQL
            db.execute("INSERT INTO history (user_id, status, symbol, shares, price, date) VALUES (:user_id, :status, :symbol, :shares, :price, :date)",
            user_id=session["user_id"], status="SELL", symbol=request.form.get("symbol"), shares=float(request.form.get("shares")), price=look["price"], date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

            return redirect(url_for("index"))

    return render_template("sell.html", stocks=stocks)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)


#user can add cash to user's account free

@app.route("/add_cash", methods=["GET", "POST"])
@login_required
def add_cash():
    if request.method == "POST":
        add_cash = int(request.form.get("add_cash"))
        id = session["user_id"]

        try:
            add_cash
        except ValueError:
            return apology("shares must be a posative integer", 400)

        if not add_cash:
            return apology("Enter cash you want", 400)

        elif add_cash <= 0:
            return apology("cash must be positive integer", 400)

        db.execute("UPDATE users SET cash=cash+:add_cash WHERE id=:id", add_cash=add_cash, id=id)

        return redirect(url_for("index"))

    return render_template("add_cash.html")