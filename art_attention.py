from collections import defaultdict

# Define art pieces and their respective rectangles
art_pieces = {
    'ArtPiece1': (0, 2, 5, 8),
    'ArtPiece2': (6, 4, 8, 8)
}

# Example data packets with corrected timestamps
data_packets = [
    {'tid': 501, 'posX': 3, 'posY': 5, 'time': 93015},
    {'tid': 501, 'posX': 4, 'posY': 7, 'time': 93025},
    {'tid': 501, 'posX': 6, 'posY': 8, 'time': 93035},
    {'tid': 501, 'posX': 7, 'posY': 8, 'time': 93045},
    {'tid': 502, 'posX': 1, 'posY': 3, 'time': 93015},
    {'tid': 502, 'posX': 2, 'posY': 3, 'time': 93025},
    {'tid': 502, 'posX': 5, 'posY': 2, 'time': 93035},
    {'tid': 502, 'posX': 6, 'posY': 2, 'time': 93045},
    {'tid': 503, 'posX': 4, 'posY': 5, 'time': 93015},
    {'tid': 503, 'posX': 3, 'posY': 5, 'time': 93025},
    {'tid': 503, 'posX': 2, 'posY': 6, 'time': 93035},
    {'tid': 503, 'posX': 1, 'posY': 7, 'time': 93045},
    {'tid': 504, 'posX': 2, 'posY': 6, 'time': 93015},
    {'tid': 504, 'posX': 3, 'posY': 6, 'time': 93025},
    {'tid': 504, 'posX': 4, 'posY': 6, 'time': 93035},
    {'tid': 504, 'posX': 5, 'posY': 6, 'time': 93045},
]

# Initialize a dictionary to store information about visitors and their time spent on each art piece
visitor_info = defaultdict(lambda: defaultdict(int))
art_piece_total_minutes = defaultdict(int)  # New dictionary to store total minutes per art piece

# Process data packets
for i in range(len(data_packets)):
    packet = data_packets[i]
    tid = packet['tid']
    pos_x, pos_y = packet['posX'], packet['posY']
    timestamp = packet['time']

    # Convert timestamp to seconds
    hours = timestamp // 10000
    minutes = (timestamp // 100) % 100
    seconds = timestamp % 100
    time_in_seconds = hours * 3600 + minutes * 60 + seconds

    # Check if the visitor is within the bounds of any art piece
    for art_piece, rect in art_pieces.items():
        x1, y1, x2, y2 = rect

        if x1 <= pos_x <= x2 and y1 <= pos_y <= y2:
            # Calculate time spent until the next packet (assuming 10 seconds per data packet)
            time_spent = 10
            # Update the time spent by the visitor on the art piece
            visitor_info[tid][art_piece] += time_spent
            art_piece_total_minutes[art_piece] += time_spent / 60  # Update total minutes

# Print visitor_info
print("Visitor Information:")
print(visitor_info)

# Print total minutes per art piece
print("\nTotal Minutes per Art Piece:")
for art_piece, total_minutes in art_piece_total_minutes.items():
    print(f"Art Piece '{art_piece}': {total_minutes:.2f} minutes")

# Print results in hours, minutes, and seconds for all possible tid values
possible_tids = set(packet['tid'] for packet in data_packets)
for tid in possible_tids:
    print(f"\nVisitor {tid}:")
    for art_piece, time_spent in visitor_info[tid].items():
        hours = time_spent // 3600
        minutes = (time_spent % 3600) // 60
        seconds = time_spent % 60
        print(f"  Art Piece '{art_piece}': {hours} hours, {minutes} minutes, and {seconds} seconds.")
