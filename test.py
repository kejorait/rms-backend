# Data extracted from the table
import json

total_bl = [
    71333, 80000, 66000, 120000, 0, 26667, 48000, 0, 100000, 100000, 58667, 100000, 40000, 100000
]

total_resto = [
    61000, 0, 0, 9000, 67000, 0, 112000, 42000, 0, 103000, 50000, 20000, 22000, 233000
]

# Calculate the sum for each column
sum_total_bl = sum(total_bl)
sum_total_resto = sum(total_resto)

# Calculate the grand total as the sum of both columns
grand_total = sum_total_bl + sum_total_resto

# print(sum_total_bl, sum_total_resto, grand_total)

with open("summary.json", "r") as f:
    data = json.load(f)

billiard_total = data["billiard_total"]
bill_total = data["bill_total"]
total = data["total"]

count_billiard = 0
count_bill = 0
count_total = 0
for mdl in data["data"]:
    count_billiard += mdl["dsc_billiard_total"]
    count_bill += mdl["dsc_bill_total"]
    count_total += mdl["total"]

print(count_billiard, count_bill, count_total)
print(billiard_total, bill_total, total)