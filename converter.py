import datetime
def conv_time(string):
    time = datetime.datetime.strptime(string, "%Y-%m-%dT%H:%M:%S.000Z")
    return time
def write_track_point(text, last_distance, speed_run):
    lines = text.splitlines()

    distance = lines[2]
    new_distance = last_distance + speed_run * 1000 / 3600
    start_idx = distance.index(">")
    end_idx = distance.index("</")
    new_distance_string = distance[0:start_idx + 1]
    new_distance_string += str(round(new_distance, 15))
    new_distance_string += distance[end_idx:]
    lines[2] = new_distance_string

    speed = lines[8]
    start_idx = speed.index(">")
    end_idx = speed.index("</")
    new_speed_string = speed[0:start_idx + 1]
    new_speed_string += str(round(speed_run * 1000 / 3600, 15))
    new_speed_string += speed[end_idx:]
    lines[8] = new_speed_string

    return "\n".join(lines)
def write_lap(total_time, speed, intervals):
    distance = round(total_time * speed * 1000 / 3600, 2)
    avg_speed = speed * 1000 / 3600
    start = f"""
      <Lap StartTime="2022-12-20T17:54:21.000Z">
        <TotalTimeSeconds>{total_time}</TotalTimeSeconds>
        <DistanceMeters>{distance}</DistanceMeters>
        <MaximumSpeed>{avg_speed}</MaximumSpeed>
        <Calories>25</Calories>
        <AverageHeartRateBpm>
          <Value>145</Value>
        </AverageHeartRateBpm>
        <MaximumHeartRateBpm>
          <Value>151</Value>
        </MaximumHeartRateBpm>
        <Intensity>Active</Intensity>
        <TriggerMethod>Manual</TriggerMethod>
      <Track>"""
    end = f"""
        </Track>
        <Extensions>
          <ns3:LX>
            <ns3:AvgSpeed>{avg_speed}</ns3:AvgSpeed>
            <ns3:AvgRunCadence>80</ns3:AvgRunCadence>
            <ns3:MaxRunCadence>82</ns3:MaxRunCadence>
          </ns3:LX>
        </Extensions>
      </Lap>"""
    string = start
    for i in intervals:
        string = string + i
    string = string + end
    return string


laps = [
    (90.0, 10),
    (90.0, 12),
    (120.0, 18),
    (120.0, 8),
    (120.0, 18),
    (120.0, 8),
    (120.0, 18),
    (120.0, 8),
    (90.0, 6),
]

text = None
with open("activity_10162883020.tcx", "r") as f:
    text = f.readlines()

lap = {
    "time": None,
    "lap_distance": None,
    "max_speed": 0.0,
    "current_distance": 0.0
}

tp = {
    "time": None,
    "distance": None
}

first_time = None
last_time = None

last_distance = 0.0

is_in_tp = False
lap_count = -1

for i in range(len(text)):
    # Get start time of activity
    if text[i].strip().startswith("<Id"):
        first_time = conv_time(text[i].split("<Id>")[1].split("</Id>")[0])
        last_time = conv_time(text[i].split("<Id>")[1].split("</Id>")[0])

    # Lap Time and Lap Distance
    if text[i].strip().startswith("<Lap "):
        lap_count += 1
        lap["time"] = conv_time(text[i].strip().split('="')[1].split('">')[0])
        lap["distance"] = laps[lap_count][0] * laps[lap_count][1] * 1000 / 3600

    if text[i].strip().startswith("<Trackpoint"):
        is_in_tp = True

    if text[i].strip().startswith("</Trackpoint"):
        is_in_tp = False

    # Lap DistanceMeters
    if text[i].strip().startswith("<DistanceMeters") and not is_in_tp:
        text[i] = f'        <DistanceMeters>{round(lap["distance"], 15)}</DistanceMeters>\n'

    # Lap DistanceMeters
    if text[i].strip().startswith("<MaximumSpeed") and not is_in_tp:
        text[i] = f'        <MaximumSpeed>{round(laps[lap_count][1] / 3.6, 15)}</MaximumSpeed>\n'

    # Trackpoint Time
    if text[i].strip().startswith("<Time>") and is_in_tp:
        tp["time"] = conv_time(text[i].split("<Time>")[1].split("</Time")[0])

    # Trackpoint DistanceMeters
    if text[i].strip().startswith("<DistanceMeters") and is_in_tp:
        current_speed = laps[lap_count][1]
        duration = (tp["time"] - last_time).seconds
        current_distance = float(last_distance) + float(current_speed * duration * 1000 / 3600)
        text[i] = f"            <DistanceMeters>{current_distance}</DistanceMeters>\n"
        last_distance = current_distance
        last_time = tp["time"]

    # Trackpoint Speed
    if text[i].strip().startswith("<ns3:Speed") and is_in_tp:
        text[i] = f"                <ns3:Speed>{float(laps[lap_count][1] / 3.6)}</ns3:Speed>\n"

    if text[i].strip().startswith("<ns3:AvgSpeed"):
        text[i] = f"            <ns3:AvgSpeed>{float(laps[lap_count][1] / 3.6)}</ns3:AvgSpeed>\n"

f = open("activity.tcx", "w")
f.write("".join(text))
f.close()

