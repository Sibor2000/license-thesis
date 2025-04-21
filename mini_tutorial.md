## MGTS mini tutorial

### A mini tutorial for people who want to run the microgrid trading simulator

This tutorial only includes the trading logic. No web stuff here.

#### Prerequisites
- python 3.11

#### Set up

1. Create a virtual environment

```
python -m venv <myVenv>
```

2. Activate venv

```
<myVenv>/Scripts/activate
```

3. Installing packages using pip
```
pip install -r requitements.txt
```

#### Inner workings explained

Currently, most of the logic resides in two classes. Microgrid and MicrogridNetwork.

A microgrid network is just a list of microgrids and a set of methods that can be called on them.

In order to easily understand the workings of the system let's look into Microgrid first. Each MG has a list of stored, produced, and post trade stored energy. There are two methods that are concerned with trade. One calculates how much energy the MG is willing to trade. We call this **desire**. Another function that is concerned with trade is resolve trade. This simply tells an MG to execute the effects of a trade on itself.

Now let's move on to **MicrgridNetwork**. An easy way to understand how the flow of the simulation goes is to look at ```step_time```.

Every time step_time is called, the following things happen

1. Internal energy calculation

At the start of every time step, each microgrid resolves their inner energy state. They take the state from the previous moment (or the starting energy if the simulation is at the beginning) and calculate an intermediary state.

2. Circumstance calculation

Based on each MGs desire, the circumstance matrix is calculated. For efficiency reasons, the circumstance matrix is stored as a list of Trades. This is because for n MGs, there are at most n*(n-1)/2 trades, which would result in a sparse matrix.

3. Trade optimization

Based on the Trades in the circumstance the optimizer is built. Since this is work in progress, there will be many changes here and even now changes are being made.

4. Optimal trade execution

The best trade from the previous step is executed, each MG is notified about the energy they have to transact.

5. Role calculation

The role of each MG for the next moment is determined.

6. Time stepping

The network is prepared for the next step, by adjusting the time.

#### Example scenario

By looking at ```example_scenario.py``` we can see one method MGs can be created and added to an MGN. Simply run the scenario with:

```
python example_scenario.py
```

In order to adjust GA and other params, look into ```constants.py``` and ```ga_constants.py```.