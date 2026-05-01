# 2026 Autonomous Newbie Project

In this project, you are given a simplified autonomous vehicle controller that already runs but behaves incorrectly or unsafely in some scenarios. Your task is to investigate how it behaves, identify issues in the decision logic, improve the controller, and present your reasoning, changes, results, and remaining limitations at the end of the project. This is a one-week individual task, and the goal is not perfect completion but clear engineering reasoning, structured debugging, and honest communication of what you found.

## Rules and expectations

- This is an individual project. Your final submission must represent your own work.
- You have one week to work on the project.
- Independence is expected. You should investigate behaviour, inspect the code, test ideas, and make grounded changes yourself.
- Workshop attendance is strongly encouraged. Being physically present, and engaging with the team environment are positive signals.
- Reasoning, communication, and method matter heavily. You are expected to explain what you observed, what you changed, what improved, and what remains uncertain.
- A final mini interview is done at the end of the project for you to present your work.
- 
## Setup

This project is intended to run with standard Python 3.

Required:
- Python 3
- Tkinter support in your Python install

Optional:
- Pillow (`pip install pillow`) for vehicle sprite rotation
  - If Pillow is not installed, the visualizer will still run, but the vehicle will be shown as a simple drawn shape instead of the image sprite.

Make sure these files are kept in the same folder:
- controller.py
- scenarios.py
- run_scenarios.py
- visualize.py

Also keep the `visualize_assets/` folder beside `visualize.py`.

## What you are given

You are being provided with:
- a simplified controller file containing the main decision logic
- a fixed set of scenarios
- a script that runs those scenarios through the controller
- a visualizer that helps you observe scenario behaviour along with it's asset files
- this brief, which defines the task, deliverables, and presentation expectations

Your task is to work with the provided project structure rather than redesigning the whole system.

**Note** **on the visualizer**; The visualizer is provided to help you observe controller behaviour more easily. It is a support tool, not proof that the controller is correct or robust. Use the visualizer to inspect behaviour, but base your engineering judgement on the controller logic, the fixed scenarios, and your reasoning, not only on whether the playback looks acceptable.

## Deliverables

### Required
1. Final presentation
2. Modified code / files

### Optional but rewardable
1. Extra scenarios you created
2. Additional justification or improvement ideas

Keep the deliverables focused and lightweight. The goal is to show engineering signal, not produce unnecessary paperwork.

## Final presentation structure

Your presentation should clearly cover these seven points:

1. What you think the controller was intended to do
2. What was going wrong
3. How you investigated it
4. What you changed
5. What improved
6. What still fails or remains uncertain
7. What you would do next


## Submission note

Your final submission should be organized clearly enough that someone else can follow:
- what you changed
- how you tested it
- what result you got
- what limitations still remain

You are not expected to produce a perfect controller. You are expected to produce a defensible attempt.

