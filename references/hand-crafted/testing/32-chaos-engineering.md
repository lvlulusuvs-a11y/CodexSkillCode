# Chaos Engineering: Break Things on Purpose

Chaos engineering tests system resilience by deliberately injecting failures.

## Principles

1. Define steady state (normal behavior)
2. Hypothesize the system will stay steady
3. Introduce variables that reflect real-world events
4. Measure against steady state
5. Fix what breaks

## Simple Chaos Experiment

Kill a service instance and check if requests still succeed:

import subprocess
import time
import requests

def chaos_experiment():
    # Step 1: Define steady state
    baseline = measure_error_rate()

    # Step 2: Inject failure
    subprocess.run(["kubectl", "scale", "deploy", "my-service", "--replicas=0"])
    time.sleep(5)

    # Step 3: Measure
    error_rate = measure_error_rate()

    # Step 4: Compare
    if error_rate - baseline > 0.01:
        print("FAIL: Error rate increased by more than 1%")
    else:
        print("PASS: System handled instance failure")

    # Step 5: Restore
    subprocess.run(["kubectl", "scale", "deploy", "my-service", "--replicas=3"])

## Chaos Toolkit

Use the chaos toolkit library:

from chaoslib.experiment import run_experiment

experiment = {
    "title": "Kill payment service instance",
    "method": [
        {
            "type": "action",
            "name": "kill payment pod",
            "provider": {
                "type": "python",
                "module": "chaosk8s.pod.actions",
                "func": "terminate_pods",
                "arguments": {
                    "name_pattern": "payment-service-*",
                    "rand": True,
                }
            }
        }
    ],
    "rollbacks": [
        {
            "type": "action",
            "name": "restore pod",
            "provider": {
                "type": "python",
                "module": "chaosk8s.deployment.actions",
                "func": "rollback_deployment",
            }
        }
    ]
}

run_experiment(experiment)

## Common Experiments

1. Kill a service instance
2. Inject network latency (50ms, 500ms)
3. Simulate CPU pressure
4. Fill up disk space
5. Terminate database connection
6. Delay response from external API
7. Simulate DNS failure
8. Expire certificates

## Game Days

Schedule regular chaos sessions:
1. Friday afternoon (low traffic)
2. Start with simple experiments
3. Gradual escalation
4. Everyone participates
5. Document findings
6. Create fix tickets

## What to Test First

1. Health checks work
2. Graceful shutdown works
3. Circuit breakers open correctly
4. Retries work with backoff
5. Fallback mechanisms work
6. Monitoring detects failures
7. Alerts fire correctly
8. Service restarts cleanly


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.
