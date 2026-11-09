# energy-storage-dispatch-model-interview

Context
Batteries make money by buying electricity when prices are low and selling it when prices are high.
Electricity prices go up and down throughout the day because supply and demand change. For
example, people use more power in the evening or when it’s cold. There are multiple electricity
markets, each with their own prices that can change at different times. Batteries can take part in more
than one market, letting them find the best times and places to buy or sell electricity and earn a profit.
Task
• Build a Python package that models a battery charging and discharging to maximise profits,
using the data provided
• You may assume the battery is a price taker (i.e. the actions of the battery have no impact on
the market prices)
• In this exercise, there are 2 wholesale electricity markets, with prices included in the attached
files
• The units of the market prices are £/MWh (money per unit energy), Market 1 has half-hourly
prices, and Market 2 has hourly prices
• When the battery chooses to use some portion of its capacity to charge or discharge from one
of the markets, it must commit that capacity for the entire time interval of that market
• For example, if the battery chose to commit 5 MW of discharging into Market 1 when the
market price is 50 £/MWh, it would be paid £125 (5 MW * 0.5h * 50 £/MWh)
• The battery can export any amount of power up to its maximum discharge rate for any
duration of time, so long as it has sufficient energy stored to do so
• Likewise, the battery can import any power up to its maximum charge rate for any duration of
time, so long as it has sufficient remaining storage capacity to do so
• The battery cannot sell the same unit of energy into both markets, but it can divide its power
across both markets
• For example, a battery with a 5 MW maximum discharge rate and 5 MWh of energy stored
could commit 2 MW of discharge into Market 1 for two half-hour intervals, and 3 MW of
discharge into Market 2 for its 1 hour interval, but it could not commit 5 MW to both markets at
the same time, and could not discharge more than 5 MWh of energy over that interval
• The battery cannot charge and discharge at the same time
• This exercise is not designed to mimic realistic battery trading to keep the scope of the
exercise as small as possible
• You are free to decide wither to include or exclude and of your own knowledge about
electricity markets and/or batteries that is beyond the specifications of this exercise
This exercise is simplified and does not fully reflect real-world battery trading, so keep your focus on
the rules and data provided. You do not need to use any data beyond what has been given. You are
free to take any approach to determining the batteries decisions in each time interval.
To simplify the problem, consider focussing on a solution that runs and is structured well, but
compromises in any of the following ways:
• Ignoring some of the market rules or battery behaviours
• Focussing on one market
• Focussing on a subset of time periods
• Simple decision logic for battery decisions, that do not need to be optimal
Deliverables
Please send the following at least a day before your second interview:
• A way to access the source code for your Python package (e.g. a link to a GitHub repository
or similar)
• Instructions for how to set up and run your battery dispatch model
• Reproducible results from your model
• A brief (no more than 1 paragraph) summary of your approach to the challenge
We are looking forward to hearing your response and please let me know if you have any questions.
