# TablingScheduling
A simple tabling scheduling program that takes multiple people's available
times through scraping WhenIsGood.net, and outputs a fair schedule of members at the table, within the
constraints given by each member's available times.

Makes use of dynamic programming to get as close to the optimal fairness
solution as possible.

Partial Credit is the best!
# Usage
``` python main.py <WhenIsGood URL> <# of people at table> <length of shift in half hours>```
