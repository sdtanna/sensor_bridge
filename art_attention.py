from collections import Counter, defaultdict

# time between frames in seconds
frametime = 10

# time in seconds that he is considered actually viewing the art piece
buffer_time = 10

# number of packets to ignore.
# if frametime = 10, 2 packets in a row is enough, if frametime = 1, we need to skip 15 packets.
# the lower frametime is the higher time in packets should be.
packets_to_skip = buffer_time / frametime

def convert_timestamp_to_seconds(timestamp):
    hours = timestamp // 10000
    minutes = (timestamp // 100) % 100
    seconds = timestamp % 100
    return hours * 3600 + minutes * 60 + seconds

def find_visited_art_piece(pos_x, pos_y, art_pieces):
    for art_piece, rect in art_pieces.items():
        x1, y1, x2, y2 = rect
        if x1 <= pos_x <= x2 and y1 <= pos_y <= y2:
            return art_piece
    return None

def process_data_packets(data_packets, art_pieces):
    visitor_info = defaultdict(lambda: defaultdict(int))
    art_piece_total_minutes = defaultdict(int)
    visitor_routes = defaultdict(list)
    filtered_visitor_routes = defaultdict(list)  # Initialize filtered routes

    for packet in data_packets:
        tid = packet['tid']
        pos_x, pos_y = packet['posX'], packet['posY']
        timestamp = packet['time']
        time_in_seconds = convert_timestamp_to_seconds(timestamp)

        art_piece = find_visited_art_piece(pos_x, pos_y, art_pieces)
        if art_piece:
            visitor_info[tid][art_piece] += frametime
            art_piece_total_minutes[art_piece] += frametime / 60
            visitor_routes[tid].append(art_piece)

    # Filter out art pieces that appear less than "packets_to_skip" consecutive times for each visitor
    for tid, route in visitor_routes.items():
        current_piece = None
        consecutive_count = 0
        filtered_route = []
        double_check = 0

        for art_piece in route:
            if art_piece != current_piece:
                double_check = 0 
                current_piece = art_piece
                consecutive_count = 0
            consecutive_count += 1

            if consecutive_count >= packets_to_skip and double_check != 1:
                double_check = 1
                filtered_route.append(art_piece)
            

        filtered_visitor_routes[tid] = filtered_route

    return visitor_info, art_piece_total_minutes, visitor_routes, filtered_visitor_routes

def print_visitor_info(visitor_info):
    print("Visitor Information:")
    print(visitor_info)

def print_total_minutes_per_art_piece(art_piece_total_minutes):
    print("\nTotal Minutes per Art Piece:")
    for art_piece, total_minutes in art_piece_total_minutes.items():
        print(f"Art Piece '{art_piece}': {total_minutes:.2f} minutes")

def print_visitor_routes(visitor_routes):
    print("\nVisitor Routes:")
    for tid, route in visitor_routes.items():
        print(f"Visitor {tid} visited the following art pieces: {', '.join(route)}")

def print_filtered_visitor_routes(filtered_visitor_routes):
    print("\nFiltered Visitor Routes:")
    for tid, route in filtered_visitor_routes.items():
        print(f"Visitor {tid} visited the following art pieces: {', '.join(route)}")

def print_results(visitor_info, possible_tids):
    for tid in possible_tids:
        print(f"\nVisitor {tid}:")
        for art_piece, time_spent in visitor_info[tid].items():
            hours = time_spent // 3600
            minutes = (time_spent % 3600) // 60
            seconds = time_spent % 60
            print(f"  Art Piece '{art_piece}': {hours} hours, {minutes} minutes, and {seconds} seconds.")

if __name__ == "__main__":
    art_pieces = {
        'ArtPiece1': (0, 2, 5, 8),
        'ArtPiece2': (6, 4, 8, 8),
        'ArtPiece3': (6, 1, 8, 3)
    }
    data_packets = [ # Example data packets with corrected timestamps
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
        {'tid': 505, 'posX': 8, 'posY': 1, 'time': 93015},
        {'tid': 505, 'posX': 7, 'posY': 6, 'time': 93025},
        {'tid': 505, 'posX': 2, 'posY': 6, 'time': 93035},
        {'tid': 505, 'posX': 7, 'posY': 2, 'time': 93045},
        {'tid': 505, 'posX': 7, 'posY': 2, 'time': 93055}
    ]

    visitor_info, art_piece_total_minutes, visitor_routes, filtered_visitor_routes = process_data_packets(data_packets, art_pieces)
    print_total_minutes_per_art_piece(art_piece_total_minutes)
    print_visitor_routes(visitor_routes)
    print_filtered_visitor_routes(filtered_visitor_routes)
    possible_tids = set(packet['tid'] for packet in data_packets)
    print_results(visitor_info, possible_tids)
