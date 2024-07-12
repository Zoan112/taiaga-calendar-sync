import zoneinfo

try:
    print(zoneinfo.available_timezones())
except zoneinfo.ZoneInfoNotFoundError:
    print("Timezone data not found")