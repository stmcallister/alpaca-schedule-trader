# Alpaca Schedule Trader

> *NOTE: This project requires access to an Alpaca account. If you need API keys and secrets to run the code in my sandbox account please contact me.*


Alpaca Schedule Trader is an application that automates time‑based stock trades using the [Alpaca API](https://alpaca.markets/) and the **Temporal** workflow engine.

## What Problem Does This Solve?

Traditional cron‑based trading scripts are brittle, difficult to scale, and lack reliability guarantees.  
This project uses **Temporal Schedules + Actvities + Workers + Workflows** to provide:

- **Reliable, fault‑tolerant execution** of trade actions  
- **Config‑driven scheduling** (via YAML)
- **Flexible workflows** for buying and selling stocks
- **Safe retries and visibility** into trade state and history

By separating trading logic from scheduling logic, the system becomes easier to maintain, extend, and observe.

## How It Works

1. A YAML configuration file defines scheduled trade actions.
2. A Temporal Schedule Worker loads the YAML file and creates/update schedules.
3. Each schedule triggers a `TradeWorkflow` run.
4. The workflow performs the required trading action (buy, sell, etc.) using the Alpaca API.

## Example YAML Entry

```yaml
- name: sell_tsla_1034
  action: sell
  ticker: TSLA
  quantity: 100
  schedule:
    day_of_week: "mon-fri"
    hour: 10
    minute: 34
```

## Running the Project

### 1. Start Temporal locally

You can use Temporal CLI:

```bash
temporal server start-dev
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure and Start the Schedule

In the `start_schedule.yaml` file make sure there is an entry that will run in the next few minutes. For example, if your current time is 12:30pm PST. Your entry could look something like this:

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

With that entry you can create and star the schedule knowing that the `TradeWorkflow` will have a chance to run. To create and start the schedule run the following:

```bash
python start_schedule.py
```

### 4. Start Trade Worker
Run the trade worker:

```bash
python run_worker.py
```

### 5. View Schedules

Check all registered schedules:

```bash
temporal schedule list
```

Or, you can look at the schedules in the [Temporal Dashboard](http://localhost:8233/namespaces/default/schedules).

### 6. Trigger a trade manually (optional)
You can let the schedule trigger a trade, or you can trigger a trade manually by running the following:

```bash
temporal workflow start   --task-queue TRADE_TASK_QUEUE   --type TradeWorkflow   --input '{"ticker": "TSLA", "action": "buy", "quantity": 10}'
```