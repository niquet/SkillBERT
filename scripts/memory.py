import sys
import requests

UNITS_MAPPING = [
    (1<<50, ' PB'),
    (1<<40, ' TB'),
    (1<<30, ' GB'),
    (1<<20, ' MB'),
    (1<<10, ' KB'),
    (1, (' byte', ' bytes')),
]

def pretty_size(bytes, units=UNITS_MAPPING):
    """Get human-readable file sizes.
    simplified version of https://pypi.python.org/pypi/hurry.filesize/
    """
    for factor, suffix in units:
        if bytes >= factor:
            break
    amount = int(bytes / factor)

    if isinstance(suffix, tuple):
        singular, multiple = suffix
        if amount == 1:
            suffix = singular
        else:
            suffix = multiple
    return str(amount) + suffix

total_result_count = int("79,063 results".strip()[:-8].replace(",", ""))
total_result_count += int("176,897 results".strip()[:-8].replace(",", ""))
total_result_count += int("102,169 results".strip()[:-8].replace(",", ""))
total_result_count += int("84,433 results".strip()[:-8].replace(",", ""))
total_result_count += int("234,309 results".strip()[:-8].replace(",", ""))
total_result_count += int("134,918 results".strip()[:-8].replace(",", ""))
total_result_count += int("21,826 results".strip()[:-8].replace(",", ""))
total_result_count += int("9,758 results".strip()[:-8].replace(",", ""))
total_result_count += int("78,219 results".strip()[:-8].replace(",", ""))
total_result_count += int("198,248 results".strip()[:-8].replace(",", ""))
total_result_count += int("12,488 results".strip()[:-8].replace(",", ""))
total_result_count += int("67,007 results".strip()[:-8].replace(",", ""))
total_result_count += int("140,385 results".strip()[:-8].replace(",", ""))
total_result_count += int("246,341 results".strip()[:-8].replace(",", ""))
total_result_count += int("15,554 results".strip()[:-8].replace(",", ""))
# total_result_count += int("1,967,554 results".strip()[:-8].replace(",", ""))
total_result_count += int("43,165 results".strip()[:-8].replace(",", ""))

response = requests.get("https://www.linkedin.com/jobs/view/3010759169/?eBP=CwEAAAGAgML4rEuJb-We6b7I7C92J5Xr1x5anZOdh5Op9DvOGtHDTYl5vZiHTR-LI19qA7PpMA5lKl7bVIFcfovnd3v6KZzkoWk55ltYcuFMbBke9xr_9W3Ul2K2TbPVGbclESnQ8blesVSb8qMkv4s5Y26obPjSHPIMGieSME0NLv9hgiqko58fvPKjQ91z7vzg6CFaQm5uSQPWuCrlmRaR1jyOM6bSwgqCVGxV0aU77-jtdXSeuTsrIz7r9GsM4cJ34eZ4dcj3-kcffLWX7sNLuI93Kb1VAOCe_SJHi0yEHZcTVd7pGj4AlHVazQ-puEUW8fi3GHWfpeAtfxRzObThHQ7Yxg80WDaCkZ6IVkpe4UInaBlc3rPIaL7bKDvR2kc&recommendedFlavor=ACTIVELY_HIRING_COMPANY&refId=Q01wqpf5N%2FCrGcp6XGk8dA%3D%3D&trackingId=gFNq4Gjgdz1ohhhx1GEufA%3D%3D&trk=flagship3_search_srp_jobs&lipi=urn%3Ali%3Apage%3Ad_flagship3_search_srp_jobs%3BBM19X13JTj2wwW9BJ2WOvw%3D%3D&lici=gFNq4Gjgdz1ohhhx1GEufA%3D%3D")
html = response.text

print(html)

batch_size = total_result_count // 16
print(f"Total result count of {total_result_count} with a batch size of {batch_size}")

# batch = [list_[i:i + n] for i in range(0, len(list_), n)]
batch = [[html] * batch_size for i in range(0, total_result_count, batch_size)]
print(f"Size of unused batch array:\t\t{pretty_size(sys.getsizeof(batch))}")
batch_one = batch[0:10]
batch_one = batch[9]
print(f"Actual size of batch array:\t\t{pretty_size(sys.getsizeof(batch_one) * batch_size)}")
print(f"Size of initialized first batch array:\t{pretty_size(sys.getsizeof(batch_one))}")
