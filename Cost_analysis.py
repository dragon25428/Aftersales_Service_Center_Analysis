import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# Import Customer data
customer = pd.read_excel('dataset/201801-05德里工单明细_with_coordinates.xlsx', encoding='utf-8')
customer['coordinate'] = customer[['latitude', 'longitude']].apply(tuple, axis=1)

# Filter DSC Delhi only
customer = customer[(customer.center == 'DSC Delhi') | (customer.center == 'DSC Delhi 2')]
customer = customer[['SR', 'date', 'center', 'distance']]
customer.head()

# Label Distance
cond = [customer.distance <= 5, (customer.distance > 5) & (customer.distance <= 10), (customer.distance > 10) & (customer.distance <= 15),
            (customer.distance > 15) & (customer.distance <= 20), customer.distance > 20]
choice = ['< 5 km', '5-10 km', '10-15 km', '15-20 km', '> 20 km']
customer['label'] = np.select(cond, choice)

# Cost input
customer = customer.assign(油费成本=customer.distance * 3.75 * 2, 时间成本=customer.distance * 10 * 2)
customer.head()

# Cost Aggregation
cost_summary = customer.groupby('label')[['油费成本', '时间成本']].sum()
cost_summary = cost_summary.reindex(choice)
cost_summary_melt = cost_summary.reset_index().melt(id_vars='label', var_name='type', value_name='cost')

# Cost Plot
fig, ax = plt.subplots(figsize=(9, 5))
cost_summary.plot(kind='bar', stacked=True, ax=ax)
fig.autofmt_xdate(rotation=0)
ax.legend(loc=2)
ax.set_xlabel('')
ax.set_ylabel('开支总额（卢比）')
plt.tight_layout()
fig.savefig('figures/成本分析.png', dpi=500)
