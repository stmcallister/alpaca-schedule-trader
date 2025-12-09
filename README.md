# Alpaca Schedule Trader
> *NOTE: This project requires access to an Alpaca account. If you need API keys and secrets to run the code in my sandbox account please contact me.*

Alpaca Schedule Trader is an application that automates time‑based stock trades using the [Alpaca API](https://alpaca.markets/) and the [APScheduler](https://pypi.org/project/APScheduler/) library.

## Running the Project
### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure and Start the Schedule

In the `config.yaml` file make sure there is an entry that will run in the next few minutes. For example, if your current time is 12:30pm PST. Your entry could look something like this:

```yaml
- name: buy_nvda
  action: buy
  ticker: nvda
  quantity: 10
  schedule:
    day_of_week: "mon-fri"
    hour: 12
    minute: 35
```

### 3. Running the Project
```bash
python main.py
```