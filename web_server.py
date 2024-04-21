from requests import post
from flask import Flask, request, render_template_string, render_template
# from bot import token as bot_token
from host import token as bot_token
from host import SECRET_KEY, web_server_host, web_host, web_port
import query
from flask_wtf.csrf import CSRFProtect
from uuid import uuid4

app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY
csrf = CSRFProtect(app)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Страница оплаты</title>
    <style>
        body {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            flex-direction: column;
        }
        .payment-form {
            display: flex;
            flex-direction: column;
            width: 300px;
        }
        input, button {
            margin: 10px 0;
            padding: 10px;
        }
    </style>
</head>
<body>
<div class="payment-form">
    <form method="post" action="/process_payment">
        {{ csrf_token() }}
        <input type="hidden" name="user_id" value="{{ user_id }}">
        <input type="hidden" name="transaction_id" value="{{ transaction_id }}">
        <label for="amount">Сумма оплаты:</label>
        <input type="number" id="amount" name="amount" required>
        <button type="submit">Подтвердить</button>
</form>

</div>

<script>
document.getElementById('confirmPayment').addEventListener('click', function() {
    const amount = document.getElementById('amount').value; // Получаем значение суммы из поля ввода
    if(amount) {
        alert('Оплата подтверждена: ' + amount + ' руб.');
    } else {
        alert('Сумма не введена.');
    }
});
</script>
</body>
</html>
"""


def generate_payment_link(user_id):
    unique_transaction_id = str(uuid4())
    return f"{web_server_host}/payment?user_id={user_id}&transaction_id={unique_transaction_id}"


@app.route("/payment")
def payment_page():
    user_id = request.args.get("user_id")
    transaction_id = request.args.get("transaction_id")
    return render_template(
        "payment.html", user_id=user_id, transaction_id=transaction_id
    )


@app.route("/process_payment", methods=["POST"])
def process_payment():
    user_id = request.form["user_id"]
    amount = float(request.form["amount"])

    # Обновляем баланс пользователя
    query.add_balance(user_id, amount)

    # Отправляем сообщение в Telegram
    response = send_telegram_notification(
        user_id,
        f"Ваш баланс был пополнен на {amount} рублей.",
    )
    print(response)

    success_html = """
    <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Оплата прошла успешно!</title>
    <style>
        body {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            flex-direction: column;
            font-family: 'Arial', sans-serif;
        }
        .message {
            font-size: 2em; 
            margin-bottom: 20px;
        }
        .gif-container {
        }
    </style>
</head>
<body>

<div class="message">
    Оплата прошла успешно!
</div>
<div class="gif-container">
    <img src="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExdXdjMTVrZTExbG1rY2tna2tzeTRmYTg2eDRjams3azIyNXh0cjBjZSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/kj41Ti8GLVs1STX0bH/giphy.gif" alt="Success Animation">
</div>

</body>
</html>
    """
    return render_template_string(success_html)


def send_telegram_notification(chat_id, message):
    # URL для отправки сообщений через Telegram API
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    if not chat_id:
        raise ValueError("chat_id is empty")
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
    response = post(url, json=payload)


if __name__ == "__main__":
    app.run(host=web_host, port=web_port)
